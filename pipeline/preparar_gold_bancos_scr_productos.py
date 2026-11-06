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
   (dims: fecha, cliente, segmento, porte, cnae_ocupacao, producto). Un mes se recalcula si falta o si su
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
  (salto del mix); ago-26 ~R$ 15 mil millones de tarjeta pasan de «más de 20 SM» a «Indisponível».

Uso (desde pipeline/, Windows con -X utf8):
    python -X utf8 preparar_gold_bancos_scr_productos.py [--descargar] [--desde AAAA]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

import almacen as A

BASE = Path(__file__).resolve().parents[1]
CRUDO = A.ruta_cruda("bcb_scr", "scrdata")
DEF = BASE / "definiciones" / "scr_productos.json"
CACHE_RAIZ = BASE / "datos" / "intermedio" / "scr_productos"
GOLD = BASE / "datos" / "gold"
COMANDO = "python -X utf8 preparar_gold_bancos_scr_productos.py"
URL = "https://www.bcb.gov.br/pda/desig/scrdata_{}.zip"
UA = {"User-Agent": "Mozilla/5.0 extraer-fuentes/1.0"}
CHUNK = 500_000

COLS = ["data_base", "segmento", "cliente", "cnae_ocupacao", "porte", "modalidade", "submodalidade",
        "numero_de_operacoes", "carteira_ativa", "carteira_inadimplencia", "vencido_de_15_ate_90_dias",
        "ativo_problematico"]
NUM = ["carteira_ativa", "carteira_inadimplencia", "vencido_de_15_ate_90_dias", "ativo_problematico"]
DIMS = ["fecha", "cliente", "segmento", "porte", "cnae_ocupacao", "producto"]
MEDIDAS = NUM + ["ops", "cart_ops"]

DESDE_SERIES = "2023-01"      # historia de las series por producto (mora, a/a, temprana)
DESDE_MIX = "2025-01"         # historia del mix mensual (como la fig. 2 de Bradesco)
DESDE_MORA = "2019-01"        # historia de las series de la página Mora
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
TOTAL_PF = "Total personas"


# --- definiciones ------------------------------------------------------------------------------ #

def definiciones() -> tuple[dict, str]:
    defs = json.loads(DEF.read_bytes())
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
            if any(k in sl for k in r.get("submodalidade", [])) or any(k in ml for k in r.get("modalidade", [])):
                prod = r["producto"]
                break
        out[(m, s)] = prod
    return out


# --- descarga del año en curso ----------------------------------------------------------------- #

def descargar_vigentes() -> None:
    import certificados  # noqa: F401  CA del proxy, antes de requests
    import requests

    hoy = pd.Timestamp.today()
    anios = [hoy.year] + ([hoy.year - 1] if hoy.month <= 2 else [])
    for anio in anios:
        destino = CRUDO / f"scrdata_{anio}.zip"
        parcial = destino.with_name(destino.name + ".part")
        url = URL.format(anio)
        for intento in range(1, 4):
            try:
                print(f"[~] bajando {url} (intento {intento}/3)")
                with requests.get(url, stream=True, timeout=(30, 300), headers=UA) as r:
                    r.raise_for_status()
                    with open(parcial, "wb") as f:
                        for b in r.iter_content(1 << 20):
                            f.write(b)
                nuevos = zipfile.ZipFile(parcial).namelist()
                viejos = zipfile.ZipFile(destino).namelist() if destino.exists() else []
                if len(nuevos) < len(viejos):
                    raise ValueError(f"el ZIP nuevo trae menos meses ({len(nuevos)}) que el actual ({len(viejos)})")
                parcial.replace(destino)
                A.registrar_crudo("bcb_scr", "scrdata", destino, url)
                print(f"[+] {destino.name}: {len(nuevos)} meses")
                break
            except Exception as e:
                parcial.unlink(missing_ok=True)
                print(f"[!] {destino.name}: {e}")
                if intento < 3:
                    time.sleep(30)


# --- agregado mensual incremental -------------------------------------------------------------- #

def _codificacion(z: zipfile.ZipFile, nombre: str) -> str:
    with z.open(nombre) as f:
        muestra = f.read(65536)
    if muestra.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    try:
        muestra[:-4].decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "cp1252"


def agregar_mes(z: zipfile.ZipFile, nombre: str, defs: dict) -> pd.DataFrame:
    partes = []
    cod = _codificacion(z, nombre)
    with z.open(nombre) as f:
        for ch in pd.read_csv(f, sep=";", dtype=str, usecols=COLS, encoding=cod, chunksize=CHUNK,
                              keep_default_na=False):
            for c in NUM:
                ch[c] = pd.to_numeric(ch[c].str.replace(",", ".", regex=False), errors="raise")
            ops = pd.to_numeric(ch["numero_de_operacoes"], errors="raise")
            ch["ops"] = ops.where(ops > 0, 0)
            ch["cart_ops"] = ch["carteira_ativa"].where(ops > 0, 0.0)
            mp = mapa_producto(defs, ch[["modalidade", "submodalidade"]].drop_duplicates())
            ch["producto"] = [mp[k] for k in zip(ch["modalidade"], ch["submodalidade"])]
            ch["fecha"] = pd.to_datetime(ch["data_base"], format="%Y-%m-%d", errors="raise")
            partes.append(ch.groupby(DIMS, as_index=False)[MEDIDAS].sum())
    return pd.concat(partes).groupby(DIMS, as_index=False)[MEDIDAS].sum()


def cubo(defs: dict, version: str, desde: int) -> pd.DataFrame:
    cache = CACHE_RAIZ / version
    cache.mkdir(parents=True, exist_ok=True)
    zips = sorted(p for p in CRUDO.glob("scrdata_*.zip") if int(p.stem[-4:]) >= desde)
    if not zips:
        raise FileNotFoundError(f"no hay ZIP del SCR.data en {CRUDO}")
    partes = []
    for zp in zips:
        with zipfile.ZipFile(zp) as z:
            for nombre in sorted(n for n in z.namelist() if n.endswith(".csv")):
                destino = cache / f"scr_{nombre[8:14]}.parquet"
                if not destino.exists() or destino.stat().st_mtime < zp.stat().st_mtime:
                    t = time.time()
                    g = agregar_mes(z, nombre, defs)
                    b = io.BytesIO()
                    g.to_parquet(b, index=False)
                    A.escribir_atomico(destino, b.getvalue())
                    print(f"   {nombre}: {len(g):,} filas ({time.time() - t:.1f} s)")
                partes.append(pd.read_parquet(destino))
    return pd.concat(partes, ignore_index=True)


# --- utilidades de variación ------------------------------------------------------------------- #

def mes(p: pd.Period) -> str:
    return f"{MESES[p.month - 1]}-{str(p.year)[2:]}"


def var_nivel(x: pd.Series) -> dict:
    x = x.dropna()
    if len(x) < 24:
        return {"ultimo": x.iloc[-1] if len(x) else np.nan, "d1": np.nan, "d3": np.nan, "d12": np.nan,
                "dventana": np.nan, "corte": mes(x.index[-1]) if len(x) else None}
    return {"ultimo": x.iloc[-1], "d1": x.iloc[-1] / x.iloc[-2] - 1,
            "d3": x.iloc[-3:].mean() / x.iloc[-6:-3].mean() - 1, "d12": x.iloc[-1] / x.iloc[-13] - 1,
            "dventana": x.iloc[-12:].mean() / x.iloc[-24:-12].mean() - 1, "corte": mes(x.index[-1])}


def var_tasa(x: pd.Series) -> dict:
    """Tasa en fracción -> último en fracción y cambios en pp."""
    x = x.dropna()
    if len(x) < 24:
        return {"ultimo": x.iloc[-1] if len(x) else np.nan, "d1": np.nan, "d3": np.nan, "d12": np.nan,
                "dventana": np.nan, "corte": mes(x.index[-1]) if len(x) else None}
    return {"ultimo": x.iloc[-1], "d1": (x.iloc[-1] - x.iloc[-2]) * 100,
            "d3": (x.iloc[-3:].mean() - x.iloc[-6:-3].mean()) * 100, "d12": (x.iloc[-1] - x.iloc[-13]) * 100,
            "dventana": (x.iloc[-12:].mean() - x.iloc[-24:-12].mean()) * 100, "corte": mes(x.index[-1])}


def fila(bloque, producto, orden, nombre, grupo, var, uu, uc, share=np.nan, destacar=False) -> dict:
    return {"bloque": bloque, "producto": producto, "orden": orden, "fila": nombre, "grupo": grupo,
            "unidad_ultimo": uu, "unidad_cambio": uc, "trimestral": False, "destacar": destacar,
            "share": share, **var}


def _div(a, b):
    return a / b.where(b != 0)


def series_largas(df: pd.DataFrame, prefijo: str, desde: str) -> list[dict]:
    """DataFrame (index Period mensual, columnas = nombre) -> filas largas serie|fecha|valor."""
    out = []
    df = df[df.index >= pd.Period(desde, "M")]
    for col in df.columns:
        for p, v in df[col].dropna().items():
            out.append({"serie": f"{prefijo}|{col}", "fecha": p.to_timestamp(how="end").strftime("%Y-%m-%d"),
                        "valor": float(v)})
    return out


# --- gold -------------------------------------------------------------------------------------- #

def construir(c: pd.DataFrame, defs: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    c = c.copy()
    c["mes"] = c["fecha"].dt.to_period("M")
    tramos = defs["tramos_pf"]
    orden_tramos = list(tramos.values())
    con_renta = orden_tramos[:7]
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

    # ---------------- Personas: por producto ---------------- #
    for prod in productos + [TOTAL_PF]:
        x = pf if prod == TOTAL_PF else pf[pf["producto"] == prod]
        g = x.groupby(["mes", "tramo"])[MEDIDAS].sum()
        tot = x.groupby("mes")[MEDIDAS].sum()
        cart = g["carteira_ativa"].unstack().reindex(columns=orden_tramos)
        cart["Total"] = tot["carteira_ativa"]
        mora = _div(g["carteira_inadimplencia"].unstack(), g["carteira_ativa"].unstack()).reindex(columns=orden_tramos)
        mora["Total"] = _div(tot["carteira_inadimplencia"], tot["carteira_ativa"])
        temp = _div(g["vencido_de_15_ate_90_dias"].unstack(), g["carteira_ativa"].unstack()).reindex(columns=orden_tramos)
        temp["Total"] = _div(tot["vencido_de_15_ate_90_dias"], tot["carteira_ativa"])
        tick = _div(g["cart_ops"].unstack(), g["ops"].unstack()).reindex(columns=orden_tramos)
        tick["Total"] = _div(tot["cart_ops"], tot["ops"])
        mix = cart[con_renta].div(cart[con_renta].sum(axis=1), axis=0)
        aa = cart / cart.shift(12) - 1

        for i, t in enumerate(orden_tramos + ["Total"]):
            tot_flag = t == "Total"
            nombre = (TOTAL_PF if prod == TOTAL_PF else f"Total {prod.lower()}") if tot_flag else t
            share = cart[t].iloc[-1] / cart["Total"].iloc[-1]
            v = var_nivel(cart[t]); v["ultimo"] = v["ultimo"] / 1e9
            tablas.append(fila("saldo", prod, i, nombre, "Tramo", v, "brl_mm", "pct", share, tot_flag))
            if tick[t].notna().any():
                tablas.append(fila("ticket", prod, i, nombre, "Tramo", var_nivel(tick[t]), "brl", "pct", np.nan, tot_flag))
            if not cart[t].dropna().empty and cart[t].iloc[-1] > 0:
                tablas.append(fila("mora", prod, i, nombre, "Tramo", var_tasa(mora[t]), "pct", "pp", share, tot_flag))
                tablas.append(fila("temprana", prod, i, nombre, "Tramo", var_tasa(temp[t]), "pct", "pp", share, tot_flag))

        series += series_largas(aa[con_renta + ["Total"]], f"aa|{prod}", DESDE_SERIES)
        series += series_largas(mora[con_renta + ["Total"]], f"mora|{prod}", DESDE_SERIES)
        series += series_largas(temp[con_renta + ["Total"]], f"temprana|{prod}", DESDE_SERIES)
        series += series_largas(mix, f"mix|{prod}", DESDE_MIX)
        series += series_largas(pd.DataFrame({"Hasta 3 SM": mix[hasta3].sum(axis=1)}), f"mix|{prod}", DESDE_MIX)

        # exposición hasta 3 SM por tipo de institución
        gi = x.groupby(["mes", "inst", "tramo"])["carteira_ativa"].sum().unstack()
        gi = gi.reindex(columns=orden_tramos).fillna(0.0)
        cart_i = gi.sum(axis=1).unstack()
        exp = (gi[hasta3].sum(axis=1) / gi[con_renta].sum(axis=1).where(lambda s: s > 0)).unstack()
        exp["Todas"] = mix[hasta3].sum(axis=1)
        cart_i["Todas"] = cart_i.sum(axis=1)
        for i, inst in enumerate(["Bancos", "Financieras", "Inst. de pago", "Cooperativas", "Otras", "Todas"]):
            if inst not in exp or len(exp[inst].dropna()) < 24 or cart_i[inst].iloc[-1] < 1e8:
                continue
            tablas.append(fila("inst", prod, i, inst, "Institución", var_tasa(exp[inst]), "pct", "pp",
                               cart_i[inst].iloc[-1] / cart_i["Todas"].iloc[-1], inst == "Todas"))
        series += series_largas(exp[[k for k in exp.columns if cart_i[k].iloc[-1] >= 1e8]], f"exp|{prod}", DESDE_SERIES)

    # ---------------- Mora: PF por modalidad (grupos del REF) ---------------- #
    g = pf.groupby(["mes", "producto"])[MEDIDAS].sum()
    tot = pf.groupby("mes")[MEDIDAS].sum()
    orden_mod = productos + ["Otros"]
    cart = g["carteira_ativa"].unstack().reindex(columns=orden_mod)
    cart["Total personas"] = tot["carteira_ativa"]
    ap_stock = g["ativo_problematico"].unstack().reindex(columns=orden_mod)
    ap_stock["Total personas"] = tot["ativo_problematico"]
    ap = ap_stock / cart
    mora = _div(g["carteira_inadimplencia"].unstack(), g["carteira_ativa"].unstack()).reindex(columns=orden_mod)
    mora["Total personas"] = _div(tot["carteira_inadimplencia"], tot["carteira_ativa"])
    temp = _div(g["vencido_de_15_ate_90_dias"].unstack(), g["carteira_ativa"].unstack()).reindex(columns=orden_mod)
    temp["Total personas"] = _div(tot["vencido_de_15_ate_90_dias"], tot["carteira_ativa"])
    for i, m in enumerate(orden_mod + ["Total personas"]):
        es_tot = m == "Total personas"
        share_ap = ap_stock[m].iloc[-1] / ap_stock["Total personas"].iloc[-1]
        v = var_nivel(ap_stock[m]); v["ultimo"] = v["ultimo"] / 1e9
        tablas.append(fila("ap_stock", "_mora", i, m, "Modalidad", v, "brl_mm", "pct", share_ap, es_tot))
        tablas.append(fila("mora_mod", "_mora", i, m, "Modalidad", var_tasa(mora[m]), "pct", "pp",
                           cart[m].iloc[-1] / cart["Total personas"].iloc[-1], es_tot))
        v = var_nivel(cart[m]); v["ultimo"] = v["ultimo"] / 1e9
        tablas.append(fila("cartera_mod", "_mora", i, m, "Modalidad", v, "brl_mm", "pct",
                           cart[m].iloc[-1] / cart["Total personas"].iloc[-1], es_tot))
    series += series_largas(ap.drop(columns=["Otros"]), "ap", DESDE_MORA)
    series += series_largas(temp.drop(columns=["Otros"]), "temprana_mod", DESDE_MORA)
    menor = cart[["Inmobiliario", "Consignado", "Vehículos", "Rural"]].sum(axis=1)
    mayor = cart[["Tarjeta", "Personal no consignado", "Cheque especial", "Otros"]].sum(axis=1)
    riesgo = pd.DataFrame({"Menor riesgo": menor, "Mayor riesgo": mayor, "Total personas": menor + mayor})
    series += series_largas(riesgo / riesgo.shift(12) - 1, "aa_riesgo", DESDE_MORA)

    # ---------------- Mora: PJ por sector CNAE ---------------- #
    pj = c[c["cliente"] == "PJ"].copy()
    sec = defs.get("sectores_cnae", {})
    faltan = sorted(set(pj["cnae_ocupacao"]) - set(sec))
    if faltan:
        print(f"AVISO: sectores sin traducción (quedan en portugués): {faltan}")
    pj["cnae_ocupacao"] = pj["cnae_ocupacao"].map(lambda x: sec.get(x, x))
    gs = pj.groupby(["mes", "cnae_ocupacao"])[MEDIDAS].sum()
    ts = pj.groupby("mes")[MEDIDAS].sum()
    cs = gs["carteira_ativa"].unstack()
    aps = _div(gs["ativo_problematico"].unstack(), gs["carteira_ativa"].unstack())
    ultimo = cs.iloc[-1].sort_values(ascending=False)
    top = [s for s in ultimo.index if s != "No informado"][:10]
    resto = cs.drop(columns=top).sum(axis=1)
    for i, s in enumerate(top):
        v = var_nivel(cs[s]); v["ultimo"] = v["ultimo"] / 1e9
        tablas.append(fila("sector", "_mora", i, s, "Sector", v, "brl_mm", "pct", cs[s].iloc[-1] / ts["carteira_ativa"].iloc[-1]))
    v = var_nivel(resto); v["ultimo"] = v["ultimo"] / 1e9
    tablas.append(fila("sector", "_mora", 98, "Resto de sectores", "Sector", v, "brl_mm", "pct", resto.iloc[-1] / ts["carteira_ativa"].iloc[-1]))
    v = var_nivel(ts["carteira_ativa"]); v["ultimo"] = v["ultimo"] / 1e9
    tablas.append(fila("sector", "_mora", 99, "Total empresas", "Sector", v, "brl_mm", "pct", 1.0, True))
    aps["Total empresas"] = _div(ts["ativo_problematico"], ts["carteira_ativa"])
    series += series_largas(aps[top + ["Total empresas"]], "ap_sector", DESDE_MORA)

    t = pd.DataFrame(tablas)
    s = pd.DataFrame(series)
    return t, s


def verificar(t: pd.DataFrame, s: pd.DataFrame, c: pd.DataFrame) -> None:
    """Controles que deben romper la corrida si fallan."""
    # el total PF del cubo es la suma de los productos
    pf = c[c["cliente"] == "PF"]
    ult = pf["fecha"].max()
    x = pf[pf["fecha"] == ult]
    assert abs(x["carteira_ativa"].sum() - x.groupby("producto")["carteira_ativa"].sum().sum()) < 1, "productos no suman"
    # shares del bloque saldo de cada producto suman 1 (tramos sin el total)
    sal = t[(t.bloque == "saldo") & ~t.destacar]
    for p, g in sal.groupby("producto"):
        assert abs(g["share"].sum() - 1) < 1e-9, f"shares de saldo no suman 1 en {p}"
    # mix suma 100 % en cada mes y producto
    mx = s[s.serie.str.startswith("mix|") & ~s.serie.str.endswith("|Hasta 3 SM")].copy()
    mx["prod"] = mx.serie.str.split("|").str[1]
    sumas = mx.groupby(["prod", "fecha"])["valor"].sum()
    assert ((sumas - 1).abs() < 1e-9).all(), "el mix no suma 100 %"
    assert t[["ultimo"]].notna().all().all(), "hay filas sin último"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--descargar", action="store_true", help="baja de nuevo el ZIP del año en curso")
    ap.add_argument("--desde", type=int, default=2018, help="primer año del cubo (default 2018)")
    a = ap.parse_args(argv)
    if a.descargar:
        descargar_vigentes()
    defs, version = definiciones()
    c = cubo(defs, version, a.desde)
    t, s = construir(c, defs)
    verificar(t, s, c)
    for nombre, df in (("bk_scr_tablas", t), ("bk_scr_series", s)):
        b = io.BytesIO()
        df.to_parquet(b, index=False)
        A.guardar_derivado("bcb_scr", "bancos_gold_scr_productos", f"{nombre}.parquet", b.getvalue(),
                           desde=["bcb_scr"], como=COMANDO, nota="Páginas Personas y Mora")
        A.escribir_atomico(GOLD / f"{nombre}.parquet", b.getvalue())
        print(f"{nombre}: {len(df):,} filas")
    print(f"último mes: {c['fecha'].max():%Y-%m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
