#!/usr/bin/env python3
"""Gold del SCR.data por producto, tramo de renta, tipo de institución y sector (páginas Personas y Mora).

POR QUÉ EXISTE
--------------
`bk_scr` (preparar_gold_bancos_scr.py) publica tres cortes sin modalidad. Las páginas Personas y Mora
necesitan el SCR abierto por producto (tarjeta, consignado, personal, vehículos, inmobiliario, rural, cheque
especial), por tramo de renta del deudor PF, por tipo de institución y, en PJ, por sección CNAE. Es la base
de la réplica de crédito por renta (tarea 3; detalle en referencias/, fuera de git) y de los gráficos
1.2.2.15/1.2.2.16 del REF.

FLUJO
-----
1. (opcional, --descargar) baja de nuevo el ZIP del año en curso (y del anterior en enero-febrero): el BCB
   lo reescribe cada mes con el mes nuevo.
2. Agregado mensual incremental en `datos/intermedio/scr_productos/<version>/scr_AAAAMM.parquet`
   (dims: fecha, cliente, segmento, porte, cnae_ocupacao, producto; un producto con «partes» se guarda
   abierto, p. ej. la tarjeta en contado y con interés, y se junta antes de construir). Un mes se recalcula si falta o si su
   ZIP es más nuevo que el agregado. <version> = sha corto de las reglas de producto de definiciones/scr_productos.json:
   cambiar el mapa de productos invalida el caché entero; cambiar traducciones no.
3. Gold:
   - bk_scr_tablas: filas de la tabla estándar (bloque, producto, orden, fila, grupo, ultimo, share, d1, d3,
     d12, dventana, corte, unidad_ultimo, unidad_cambio, trimestral, destacar).
   - bk_scr_series: serie, fecha, valor (largo).

REGLAS
------
- Mora = carteira_inadimplencia / carteira_ativa (fracción). La columna está en R$, no en %.
- Mora temprana = vencido_de_15_ate_90_dias / carteira_ativa.
- Activo problemático = ativo_problematico / carteira_ativa. Desde ene-25 rige la Res. 4.966 (otra definición).
- Ticket = cartera de las celdas con numero_de_operacoes > 0 / Σ operaciones. −1 es secreto estadístico
  (menos de 15 operaciones): esas celdas entran al saldo pero no al ticket.
- Mix por renta: sobre los 7 tramos con renta declarada (sin «N.D.» ni «Sin renta»).
- Cambios de saldo y ticket en % (m/m, 3m/3m con promedios, a/a, 12m/12m con promedios); de tasas en pp.
- Quiebres conocidos de la fuente (no se suavizan; van en las notas del sitio): jul-25 reclasificación de renta
  (salto del mix); jul-26 pico de un mes en «más de 20 SM» de tarjeta (+R$ 14 mil millones, se revierte en
  ago-26); ene–feb-26 la mora de «Indisponível» en tarjeta salta de ~9 % a ~28 % (revisado el 10-nov).

Uso (desde pipeline/, Windows con -X utf8):
    python -X utf8 pipeline/preparar_gold_bancos_scr_productos.py [--descargar] [--desde AAAA]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import zipfile

import numpy as np
import pandas as pd

import almacen as A
import reglas_gold as RG
import scr_zip as Z
import tabla_estandar as T

DEF = A.DEFINICIONES / "scr_productos.json"
CACHE_RAIZ = A.INTERMEDIO / "scr_productos"

COLS = ["data_base", "segmento", "cliente", "cnae_ocupacao", "porte", "modalidade", "submodalidade",
        "numero_de_operacoes", "carteira_ativa", "carteira_inadimplencia", "vencido_de_15_ate_90_dias",
        "ativo_problematico"]
NUM = ["carteira_ativa", "carteira_inadimplencia", "vencido_de_15_ate_90_dias", "ativo_problematico"]
DIMS = ["fecha", "cliente", "segmento", "porte", "cnae_ocupacao", "producto"]
MEDIDAS = NUM + ["ops", "cart_ops"]

DESDE_SERIES = "2023-01"      # historia de las series por producto (mora, a/a, temprana)
DESDE_MIX = "2025-01"         # historia del mix mensual (como la fig. 2 de Bradesco)
DESDE_MORA = "2019-01"        # historia de las series de la página Mora
MIN_MESES = 24                # con menos historia la fila muestra solo el último valor
MIN_CARTERA_INST = 1e8        # R$; un tipo de institución con menos cartera no se muestra
TOTAL_PF = "Total personas"
# Los nombres de producto, institución y sector salen de definiciones/scr_productos.json (sus traducciones).
INSTITUCIONES = ["Bancos", "Financieras", "Inst. de pago", "Cooperativas", "Otras"]
MENOR_RIESGO = ["Inmobiliario", "Consignado", "Vehículos", "Rural"]
MAYOR_RIESGO = ["Tarjeta", "Personal no consignado", "Cheque especial", "Otros"]
SECTOR_SIN_DATO = "No informado"
TRAMOS_CON_RENTA = 7          # los primeros 7 tramos de tramos_pf; después vienen «Sin dato» y «Sin renta»


def definiciones(ruta=DEF) -> tuple[dict, str]:
    """Reglas de producto y versión del caché. ``ruta`` permite otro mapa con el mismo formato (p. ej. las
    modalidades PJ de definiciones/scr_modalidades_pj.json, frente 13)."""
    defs = json.loads(ruta.read_bytes())
    # la versión del caché depende solo de lo que cambia el agregado (las reglas de producto)
    clave = json.dumps([defs["productos"], defs["otros"]], ensure_ascii=False, sort_keys=True)
    return defs, hashlib.sha256(clave.encode("utf-8")).hexdigest()[:10]


def mapa_producto(defs: dict, pares: pd.DataFrame) -> dict:
    """(modalidade, submodalidade) -> producto, con las reglas en orden."""
    out = {}
    for m, s in pares.itertuples(index=False, name=None):
        ml, sl = str(m).lower(), str(s).lower()
        prod = defs["otros"]["producto"]
        for r in defs["productos"]:
            if any(k in sl for k in r.get("excluir", [])):     # p. ej. «arrendamento ... exceto veículos»
                continue
            if any(k in sl for k in r.get("submodalidade", [])) or any(k in ml for k in r.get("modalidade", [])):
                prod = r["producto"]
                for parte in r.get("partes", []):          # la primera parte que calza; la última es el resto
                    if not parte.get("submodalidade") or any(k in sl for k in parte["submodalidade"]):
                        prod = parte["producto"]
                        break
                break
        out[(m, s)] = prod
    return out


def padres(defs: dict) -> dict:
    """Parte del cubo -> producto de las páginas (p. ej. «Tarjeta · contado» -> «Tarjeta»)."""
    return {parte["producto"]: r["producto"] for r in defs["productos"] for parte in r.get("partes", [])}


def juntar_partes(c: pd.DataFrame, defs: dict) -> pd.DataFrame:
    """El cubo con las partes de un producto sumadas en su producto (lo que usan Personas y Mora)."""
    mapa = padres(defs)
    if not mapa:
        return c
    c = c.assign(producto=c["producto"].replace(mapa))
    return c.groupby(DIMS, as_index=False)[MEDIDAS].sum()


def descargar_vigentes() -> None:
    """Baja de nuevo el ZIP del año en curso (y el del anterior en enero-febrero): el BCB lo reescribe cada mes.
    Si falla tres veces, la corrida se corta: seguir con el ZIP viejo publicaría un mes atrasado sin aviso."""
    hoy = pd.Timestamp.today()
    for anio in [hoy.year] + ([hoy.year - 1] if hoy.month <= 2 else []):
        Z.descargar(anio, no_menos_meses=True)


def agregar_mes(z: zipfile.ZipFile, nombre: str, defs: dict, solo_cliente: str | None = None) -> pd.DataFrame:
    partes = []
    for ch in Z.leer_csv(z, nombre, COLS, keep_default_na=False):
        if solo_cliente:
            ch = ch[ch["cliente"] == solo_cliente].copy()
        for c in NUM:
            ch[c] = Z.numero(ch[c])
        ops = pd.to_numeric(ch["numero_de_operacoes"], errors="raise")
        ch["ops"] = ops.where(ops > 0, 0)
        ch["cart_ops"] = ch["carteira_ativa"].where(ops > 0, 0.0)
        mp = mapa_producto(defs, ch[["modalidade", "submodalidade"]].drop_duplicates())
        ch["producto"] = [mp[k] for k in zip(ch["modalidade"], ch["submodalidade"])]
        ch["fecha"] = pd.to_datetime(ch["data_base"], format="%Y-%m-%d", errors="raise")
        partes.append(ch.groupby(DIMS, as_index=False)[MEDIDAS].sum())
    return pd.concat(partes).groupby(DIMS, as_index=False)[MEDIDAS].sum()


def cubo(defs: dict, version: str, desde: int, raiz=CACHE_RAIZ, solo_cliente: str | None = None) -> pd.DataFrame:
    """Cubo mensual con caché por versión del mapa. ``raiz`` y ``solo_cliente`` sirven a otros cubos con el mismo
    esquema (el de empresas: intermedio/scr_empresas, solo PJ)."""
    cache = raiz / version
    cache.mkdir(parents=True, exist_ok=True)
    zips = sorted(p for p in Z.CRUDO.glob("scrdata_*.zip") if int(p.stem[-4:]) >= desde)
    if not zips:
        raise FileNotFoundError(f"no hay ZIP del SCR.data en {Z.CRUDO}")
    partes = []
    for zp in zips:
        with zipfile.ZipFile(zp) as z:
            for nombre in sorted(n for n in z.namelist() if n.endswith(".csv")):
                destino = cache / f"scr_{nombre[8:14]}.parquet"   # los CSV del ZIP se llaman scrdata_AAAAMM.csv
                if not destino.exists() or destino.stat().st_mtime < zp.stat().st_mtime:
                    t = time.time()
                    g = agregar_mes(z, nombre, defs, solo_cliente)
                    A.escribir_parquet(g, destino)
                    print(f"   {nombre}: {len(g):,} filas ({time.time() - t:.1f} s)")
                partes.append(pd.read_parquet(destino))
    return pd.concat(partes, ignore_index=True)


def fila(bloque, producto, orden, nombre, grupo, var, uu, uc, share=np.nan, destacar=False) -> dict:
    return T.fila(var, bloque=bloque, producto=producto, orden=orden, fila=nombre, grupo=grupo, unidad_ultimo=uu,
                  unidad_cambio=uc, trimestral=False, destacar=destacar, share=share)


def construir(c: pd.DataFrame, defs: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    c = c.copy()
    c["mes"] = c["fecha"].dt.to_period("M")
    tramos = defs["tramos_pf"]
    orden_tramos = list(tramos.values())
    con_renta = orden_tramos[:TRAMOS_CON_RENTA]
    hasta3 = defs["hasta_3sm"]
    insts = defs["instituciones"]
    productos = [r["producto"] for r in defs["productos"]]
    tablas, series = [], []

    pf = c[c["cliente"] == "PF"].copy()
    pf["tramo"] = pf["porte"].map(tramos)
    sin_mapa = sorted(set(pf.loc[pf["tramo"].isna(), "porte"]))
    if sin_mapa:
        raise ValueError(f"tramos PF sin traducción en scr_productos.json: {sin_mapa}")
    pf["inst"] = pf["segmento"].map(insts)
    if pf["inst"].isna().any():
        raise ValueError(f"segmentos sin traducción: {sorted(set(pf.loc[pf['inst'].isna(), 'segmento']))}")

    # Personas: por producto.
    for prod in productos + [TOTAL_PF]:
        x = pf if prod == TOTAL_PF else pf[pf["producto"] == prod]
        g = x.groupby(["mes", "tramo"])[MEDIDAS].sum()
        tot = x.groupby("mes")[MEDIDAS].sum()
        cart = g["carteira_ativa"].unstack().reindex(columns=orden_tramos)
        cart["Total"] = tot["carteira_ativa"]
        mora = RG.div(g["carteira_inadimplencia"].unstack(), g["carteira_ativa"].unstack()).reindex(columns=orden_tramos)
        mora["Total"] = RG.div(tot["carteira_inadimplencia"], tot["carteira_ativa"])
        temp = RG.div(g["vencido_de_15_ate_90_dias"].unstack(), g["carteira_ativa"].unstack()).reindex(columns=orden_tramos)
        temp["Total"] = RG.div(tot["vencido_de_15_ate_90_dias"], tot["carteira_ativa"])
        tick = RG.div(g["cart_ops"].unstack(), g["ops"].unstack()).reindex(columns=orden_tramos)
        tick["Total"] = RG.div(tot["cart_ops"], tot["ops"])
        mix = cart[con_renta].div(cart[con_renta].sum(axis=1), axis=0)
        aa = cart / cart.shift(12) - 1

        for i, t in enumerate(orden_tramos + ["Total"]):
            tot_flag = t == "Total"
            nombre = (TOTAL_PF if prod == TOTAL_PF else f"Total {prod.lower()}") if tot_flag else t
            share = cart[t].iloc[-1] / cart["Total"].iloc[-1]
            v = T.variaciones_saldo(cart[t], minimo=MIN_MESES); v["ultimo"] = v["ultimo"] / 1e9
            tablas.append(fila("saldo", prod, i, nombre, "Tramo", v, "brl_mm", "pct", share, tot_flag))
            if tick[t].notna().any():
                tablas.append(fila("ticket", prod, i, nombre, "Tramo", T.variaciones_saldo(tick[t], minimo=MIN_MESES), "brl", "pct", np.nan, tot_flag))
            if not cart[t].dropna().empty and cart[t].iloc[-1] > 0:
                tablas.append(fila("mora", prod, i, nombre, "Tramo", T.variaciones_tasa(mora[t], escala=100, minimo=MIN_MESES), "pct", "pp", share, tot_flag))
                tablas.append(fila("temprana", prod, i, nombre, "Tramo", T.variaciones_tasa(temp[t], escala=100, minimo=MIN_MESES), "pct", "pp", share, tot_flag))

        series += T.series_largas(aa[con_renta + ["Total"]], f"aa|{prod}", DESDE_SERIES)
        series += T.series_largas(mora[con_renta + ["Total"]], f"mora|{prod}", DESDE_SERIES)
        series += T.series_largas(temp[con_renta + ["Total"]], f"temprana|{prod}", DESDE_SERIES)
        series += T.series_largas(mix, f"mix|{prod}", DESDE_MIX)
        series += T.series_largas(pd.DataFrame({"Hasta 3 SM": mix[hasta3].sum(axis=1)}), f"mix|{prod}", DESDE_MIX)

        # exposición hasta 3 SM por tipo de institución
        gi = x.groupby(["mes", "inst", "tramo"])["carteira_ativa"].sum().unstack()
        gi = gi.reindex(columns=orden_tramos).fillna(0.0)
        cart_i = gi.sum(axis=1).unstack()
        exp = (gi[hasta3].sum(axis=1) / gi[con_renta].sum(axis=1).where(lambda s: s > 0)).unstack()
        exp["Todas"] = mix[hasta3].sum(axis=1)
        cart_i["Todas"] = cart_i.sum(axis=1)
        for i, inst in enumerate(INSTITUCIONES + ["Todas"]):
            if inst not in exp or len(exp[inst].dropna()) < MIN_MESES or cart_i[inst].iloc[-1] < MIN_CARTERA_INST:
                continue
            tablas.append(fila("inst", prod, i, inst, "Institución", T.variaciones_tasa(exp[inst], escala=100, minimo=MIN_MESES), "pct", "pp",
                               cart_i[inst].iloc[-1] / cart_i["Todas"].iloc[-1], inst == "Todas"))
        series += T.series_largas(exp[[k for k in exp.columns if cart_i[k].iloc[-1] >= MIN_CARTERA_INST]],
                                f"exp|{prod}", DESDE_SERIES)

    # Mora: PF por modalidad (grupos del REF).
    g = pf.groupby(["mes", "producto"])[MEDIDAS].sum()
    tot = pf.groupby("mes")[MEDIDAS].sum()
    orden_mod = productos + ["Otros"]
    cart = g["carteira_ativa"].unstack().reindex(columns=orden_mod)
    cart["Total personas"] = tot["carteira_ativa"]
    ap_stock = g["ativo_problematico"].unstack().reindex(columns=orden_mod)
    ap_stock["Total personas"] = tot["ativo_problematico"]
    ap = ap_stock / cart
    mora = RG.div(g["carteira_inadimplencia"].unstack(), g["carteira_ativa"].unstack()).reindex(columns=orden_mod)
    mora["Total personas"] = RG.div(tot["carteira_inadimplencia"], tot["carteira_ativa"])
    temp = RG.div(g["vencido_de_15_ate_90_dias"].unstack(), g["carteira_ativa"].unstack()).reindex(columns=orden_mod)
    temp["Total personas"] = RG.div(tot["vencido_de_15_ate_90_dias"], tot["carteira_ativa"])
    for i, m in enumerate(orden_mod + ["Total personas"]):
        es_tot = m == "Total personas"
        share_ap = ap_stock[m].iloc[-1] / ap_stock["Total personas"].iloc[-1]
        v = T.variaciones_saldo(ap_stock[m], minimo=MIN_MESES); v["ultimo"] = v["ultimo"] / 1e9
        tablas.append(fila("ap_stock", "_mora", i, m, "Modalidad", v, "brl_mm", "pct", share_ap, es_tot))
        tablas.append(fila("mora_mod", "_mora", i, m, "Modalidad", T.variaciones_tasa(mora[m], escala=100, minimo=MIN_MESES), "pct", "pp",
                           cart[m].iloc[-1] / cart["Total personas"].iloc[-1], es_tot))
        v = T.variaciones_saldo(cart[m], minimo=MIN_MESES); v["ultimo"] = v["ultimo"] / 1e9
        tablas.append(fila("cartera_mod", "_mora", i, m, "Modalidad", v, "brl_mm", "pct",
                           cart[m].iloc[-1] / cart["Total personas"].iloc[-1], es_tot))
    series += T.series_largas(ap.drop(columns=["Otros"]), "ap", DESDE_MORA)
    series += T.series_largas(temp.drop(columns=["Otros"]), "temprana_mod", DESDE_MORA)
    menor = cart[MENOR_RIESGO].sum(axis=1)
    mayor = cart[MAYOR_RIESGO].sum(axis=1)
    riesgo = pd.DataFrame({"Menor riesgo": menor, "Mayor riesgo": mayor, "Total personas": menor + mayor})
    series += T.series_largas(riesgo / riesgo.shift(12) - 1, "aa_riesgo", DESDE_MORA)

    # Mora: PJ por sector CNAE.
    pj = c[c["cliente"] == "PJ"].copy()
    sec = defs.get("sectores_cnae", {})
    faltan = sorted(set(pj["cnae_ocupacao"]) - set(sec))
    if faltan:
        print(f"AVISO: sectores sin traducción (quedan en portugués): {faltan}")
    pj["cnae_ocupacao"] = pj["cnae_ocupacao"].map(lambda x: sec.get(x, x))
    gs = pj.groupby(["mes", "cnae_ocupacao"])[MEDIDAS].sum()
    ts = pj.groupby("mes")[MEDIDAS].sum()
    cs = gs["carteira_ativa"].unstack()
    aps = RG.div(gs["ativo_problematico"].unstack(), gs["carteira_ativa"].unstack())
    ultimo = cs.iloc[-1].sort_values(ascending=False)
    top = [s for s in ultimo.index if s != SECTOR_SIN_DATO][:10]
    resto = cs.drop(columns=top).sum(axis=1)
    for i, s in enumerate(top):
        v = T.variaciones_saldo(cs[s], minimo=MIN_MESES); v["ultimo"] = v["ultimo"] / 1e9
        tablas.append(fila("sector", "_mora", i, s, "Sector", v, "brl_mm", "pct", cs[s].iloc[-1] / ts["carteira_ativa"].iloc[-1]))
    v = T.variaciones_saldo(resto, minimo=MIN_MESES); v["ultimo"] = v["ultimo"] / 1e9
    tablas.append(fila("sector", "_mora", 98, "Resto de sectores", "Sector", v, "brl_mm", "pct", resto.iloc[-1] / ts["carteira_ativa"].iloc[-1]))
    v = T.variaciones_saldo(ts["carteira_ativa"], minimo=MIN_MESES); v["ultimo"] = v["ultimo"] / 1e9
    tablas.append(fila("sector", "_mora", 99, "Total empresas", "Sector", v, "brl_mm", "pct", 1.0, True))
    aps["Total empresas"] = RG.div(ts["ativo_problematico"], ts["carteira_ativa"])
    series += T.series_largas(aps[top + ["Total empresas"]], "ap_sector", DESDE_MORA)

    t = pd.DataFrame(tablas)
    s = pd.DataFrame(series)
    return t, s


def verificar(t: pd.DataFrame, s: pd.DataFrame, c: pd.DataFrame) -> None:
    """Controles que deben romper la corrida si fallan."""
    pf = c[c["cliente"] == "PF"]
    x = pf[pf["fecha"] == pf["fecha"].max()]
    if not abs(x["carteira_ativa"].sum() - x.groupby("producto")["carteira_ativa"].sum().sum()) < 1:
        raise ValueError("los productos no suman el total PF del cubo")
    sal = t[(t.bloque == "saldo") & ~t.destacar]   # tramos, sin el total
    for p, g in sal.groupby("producto"):
        if not abs(g["share"].sum() - 1) < 1e-9:
            raise ValueError(f"shares de saldo no suman 1 en {p}")
    mx = s[s.serie.str.startswith("mix|") & ~s.serie.str.endswith("|Hasta 3 SM")].copy()
    mx["prod"] = mx.serie.str.split("|").str[1]
    sumas = mx.groupby(["prod", "fecha"])["valor"].sum()
    if not ((sumas - 1).abs() < 1e-9).all():
        raise ValueError("el mix no suma 100 %")
    if not t[["ultimo"]].notna().all().all():
        raise ValueError("hay filas sin último")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--descargar", action="store_true", help="baja de nuevo el ZIP del año en curso")
    ap.add_argument("--desde", type=int, default=2018, help="primer año del cubo (default 2018)")
    a = ap.parse_args(argv)
    if a.descargar:
        descargar_vigentes()
    defs, version = definiciones()
    c = juntar_partes(cubo(defs, version, a.desde), defs)
    t, s = construir(c, defs)
    verificar(t, s, c)
    for nombre, df in (("bk_scr_tablas", t), ("bk_scr_series", s)):
        A.publicar_gold(nombre, df, fuente="bcb_scr", dataset="bancos_gold_scr_productos",
                        desde=["crudo/bcb_scr/scrdata", f"intermedio/scr_productos/{version}"],
                        nota="Páginas Personas y Mora")
        print(f"{nombre}: {len(df):,} filas")
    print(f"último mes: {c['fecha'].max():%Y-%m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
