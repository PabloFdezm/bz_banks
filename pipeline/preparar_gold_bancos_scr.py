#!/usr/bin/env python3
"""bk_scr: SCR.data 2012-2026 agregado en tres cortes para el dashboard de bancos.

POR QUÉ EXISTE
--------------
El spec de datos (``docs/SPEC_DATOS_BANCOS_v0.1.md`` §3.10) pide
publicar del SCR.data solo tres cortes agregados — mes × segmento × cliente,
mes × porte (solo PJ) y mes × UF — y no el cubo granular, porque el sitio
grafica series de sistema y el cubo entero son cientos de MB por año. Este
módulo lee los ZIP anuales crudos **por partes**: un año no cabe entero en memoria.

La tasa es la oficial del BCB: ``tasa = Σ carteira_inadimplencia / Σ carteira_ativa``. La columna
``carteira_inadimplencia`` del SCR.data está en R$, NO en %; escribirla como porcentaje es un error. Las tasas van como fracción (0,05 = 5 %),
igual que el resto de la capa gold.

Decisiones del encargo 67 (03-11-2026):

- Descarga y codificación de los ZIP: ver ``scr_zip.py``. Un año que falla 3 veces corta la corrida.
- **``numero_de_operacoes`` == -1 es secreto estadístico**, no un número; no se
  suma (aquí ni se usa: los cortes son de saldo). Las filas con -1 sí traen
  valores en R$ y entran a las sumas de cartera.
- **``porte`` del corte PJ va tal cual lo publica el BCB** (Micro, Pequeno,
  Médio, Grande, Indisponível); la etiqueta del sitio va aparte en ``porte_es``.
- Cada ZIP se agrega una vez y queda en ``datos/intermedio/scr/scrdata_<año>.parquet``; se recalcula si el ZIP
  es más nuevo (el del año en curso cambia cada mes).

Receta::

    python -X utf8 pipeline/preparar_gold_bancos_scr.py                # baja 2012-2023 y deriva
    python -X utf8 pipeline/preparar_gold_bancos_scr.py --solo-descargar
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import pandas as pd

import almacen as A
import scr_zip as Z

ANIOS_HISTORIA = range(2012, 2024)    # 2024 en adelante los baja preparar_gold_bancos_scr_productos.py
PORTE_ES = {"Micro": "Micro", "Pequeno": "Pequeña", "Médio": "Mediana", "Grande": "Grande", "Indisponível": "Sin dato"}

COLS_LEER = ["data_base", "uf", "segmento", "cliente", "porte",
             "vencido_de_15_ate_90_dias", "vencido_acima_de_90_dias",
             "carteira_ativa", "carteira_inadimplencia", "ativo_problematico"]
RENOMBRE = {"segmento": "segmento_inst", "vencido_de_15_ate_90_dias": "vencido_15_90",
            "vencido_acima_de_90_dias": "vencido_90",
            "carteira_inadimplencia": "inadimplencia_brl"}
SUMAS = ["carteira_ativa", "vencido_15_90", "vencido_90",
         "inadimplencia_brl", "ativo_problematico"]
CACHE = A.INTERMEDIO / "scr"
COLUMNAS = ["corte", "fecha", "segmento_inst", "cliente", "porte", "uf",
            "carteira_ativa", "vencido_15_90", "vencido_90", "inadimplencia_brl",
            "ativo_problematico", "tasa_inad", "tasa_ap"]


def asegurar_anios() -> list[str]:
    """Baja al crudo los ZIP de ANIOS_HISTORIA que falten. Devuelve los años que fallaron tres veces."""
    fallidos: list[str] = []
    for anio in ANIOS_HISTORIA:
        destino = Z.ruta(anio)
        if destino.exists() and destino.stat().st_size > 0:
            print(f"[=] {destino.name} ya está en el crudo")
            continue
        try:
            Z.descargar(anio)
        except RuntimeError:
            fallidos.append(str(anio))
    return fallidos


def agregar_anio(ruta: Path) -> tuple[list[pd.DataFrame], list[pd.DataFrame], list[pd.DataFrame]]:
    """Un ZIP anual -> listas de agregados parciales de los tres cortes."""
    partes_a: list[pd.DataFrame] = []
    partes_b: list[pd.DataFrame] = []
    partes_c: list[pd.DataFrame] = []
    with zipfile.ZipFile(ruta) as z:
        for nombre in sorted(n for n in z.namelist() if n.endswith(".csv")):
            for bruto in Z.leer_csv(z, nombre, COLS_LEER):
                for col in ("vencido_de_15_ate_90_dias", "vencido_acima_de_90_dias",
                            "carteira_ativa", "carteira_inadimplencia", "ativo_problematico"):
                    bruto[col] = Z.numero(bruto[col])
                ch = bruto.rename(columns=RENOMBRE)
                ch["fecha"] = pd.to_datetime(ch["data_base"], format="%Y-%m-%d", errors="raise")
                partes_a.append(ch.groupby(["fecha", "segmento_inst", "cliente"], as_index=False)[SUMAS].sum())
                pj = ch[ch["cliente"] == "PJ"]
                partes_b.append(pj.groupby(["fecha", "porte"], as_index=False)[SUMAS].sum())
                partes_c.append(ch.groupby(["fecha", "uf"], as_index=False)[SUMAS].sum())
            print(f"   leído {nombre}")
    return partes_a, partes_b, partes_c


def agregado_anio(ruta: Path) -> pd.DataFrame:
    """Agregados parciales de un ZIP (columna ``_parte``: a = segmento × cliente, b = porte PJ, c = UF), del
    caché si el ZIP no cambió."""
    destino = CACHE / f"{ruta.stem}.parquet"
    if destino.exists() and destino.stat().st_mtime >= ruta.stat().st_mtime:
        return pd.read_parquet(destino)
    print(f"[scr] {ruta.name}")
    a, b, c = agregar_anio(ruta)
    df = pd.concat([pd.concat(p, ignore_index=True).groupby(["fecha", *dims], as_index=False)[SUMAS].sum()
                    .assign(_parte=parte)
                    for parte, p, dims in (("a", a, ["segmento_inst", "cliente"]), ("b", b, ["porte"]),
                                           ("c", c, ["uf"]))], ignore_index=True)
    A.escribir_parquet(df, destino)
    return df


def _corte(df: pd.DataFrame, dims: list[str], etiqueta: str) -> pd.DataFrame:
    """Tabla del corte con las columnas comunes; lo que no aplica queda vacío (None)."""
    df = df.groupby(["fecha"] + dims, as_index=False)[SUMAS].sum()
    activa, inad, ap = df["carteira_ativa"], df["inadimplencia_brl"], df["ativo_problematico"]
    df["tasa_inad"] = inad / activa.where(activa > 0)
    df["tasa_ap"] = ap / activa.where(activa > 0)
    df.insert(0, "corte", etiqueta)
    for col in ("segmento_inst", "cliente", "porte", "uf"):
        if col not in df.columns:
            df[col] = None
    return df[COLUMNAS]


def construir() -> pd.DataFrame:
    zips = sorted(Z.CRUDO.glob("scrdata_*.zip"))
    if not zips:
        sys.exit(f"[scr] no hay ZIP en {Z.CRUDO}; corre primero «preparar_gold_bancos_scr.py --solo-descargar»")
    partes = pd.concat([agregado_anio(ruta) for ruta in zips], ignore_index=True)
    cortes = [_corte(partes[partes["_parte"] == parte].drop(columns="_parte"), dims, etiqueta)
              for parte, dims, etiqueta in (("a", ["segmento_inst", "cliente"], "segmento_cliente"),
                                            ("b", ["porte"], "porte_pj"), ("c", ["uf"], "uf"))]
    df = pd.concat(cortes, ignore_index=True).sort_values(
        ["corte", "fecha", "segmento_inst", "cliente", "porte", "uf"],
        na_position="first").reset_index(drop=True)
    return df.assign(porte_es=df["porte"].map(PORTE_ES))


def verificar(df: pd.DataFrame) -> int:
    problemas = 0
    clave = ["fecha", "segmento_inst", "cliente", "porte", "uf"]
    if df.duplicated(clave).any():
        print(f"[!] {int(df.duplicated(clave).sum())} filas repetidas en la clave gold")
        problemas += 1
    for col in ("tasa_inad", "tasa_ap"):
        fuera = df[col].dropna()
        if not fuera.between(0, 1).all():
            print(f"[!] {col} fuera de [0, 1]")
            problemas += 1

    print("\nCobertura: año → meses con dato (corte segmento_cliente)")
    a = df[df["corte"] == "segmento_cliente"]
    por_anio = a.groupby(a["fecha"].dt.year)["fecha"].apply(
        lambda s: sorted(int(m) for m in s.dt.month.unique()))
    for anio, meses in por_anio.items():
        print(f"  {anio}: {len(meses)}  ({', '.join(map(str, meses))})")
    todos = sorted(a["fecha"].dt.to_period("M").unique())
    esperados = pd.period_range(todos[0], todos[-1], freq="M")
    huecos = [str(p) for p in esperados if p not in todos]
    print(f"  continuidad {todos[0]}–{todos[-1]}: "
          + ("sin huecos" if not huecos else f"HUECOS {huecos}"))
    if huecos:
        problemas += 1

    ultima = a["fecha"].max()
    print(f"\n{ultima:%b-%Y}, corte segmento_cliente: tasa de inadimplencia por segmento (%)")
    ult = a[a["fecha"] == ultima]
    tabla = ult.pivot_table(index="segmento_inst", columns="cliente",
                            values="tasa_inad", aggfunc="first") * 100
    tot = ult.groupby("segmento_inst")[["inadimplencia_brl", "carteira_ativa"]].sum()
    tabla["total"] = tot["inadimplencia_brl"] / tot["carteira_ativa"] * 100
    print(tabla.round(2).to_string())
    return problemas


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--solo-descargar", action="store_true",
                    help="solo baja los ZIP 2012-2023 que falten, no deriva")
    args = ap.parse_args(argv)

    fallidos = asegurar_anios()
    if fallidos:
        print(f"[!] años que fallaron {Z.INTENTOS} intentos: {', '.join(fallidos)}", file=sys.stderr)
        return 1
    if args.solo_descargar:
        return 0

    df = construir()
    if verificar(df):
        print("[!] bk_scr no se publica: la verificación falló", file=sys.stderr)
        return 1
    A.publicar_gold("bk_scr", df, fuente="bcb_scr", dataset="bancos_gold_scr",
                    desde=["crudo/bcb_scr/scrdata"])
    print(f"[+] gold/bk_scr.parquet: {len(df):,} filas, {df['fecha'].min().date()} a {df['fecha'].max().date()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
