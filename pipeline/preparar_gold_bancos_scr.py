#!/usr/bin/env python3
"""bk_scr: SCR.data 2012-2026 agregado en tres cortes para el dashboard de bancos.

POR QUÉ EXISTE
--------------
El spec de datos (``docs/dashboard_bancos/SPEC_DATOS_BANCOS_v0.1.md`` §3.10) pide
publicar del SCR.data solo tres cortes agregados — mes × segmento × cliente,
mes × porte (solo PJ) y mes × UF — y no el cubo granular, porque el sitio
grafica series de sistema y el cubo entero son cientos de MB por año. Este
módulo lee los ZIP anuales crudos (``datos/crudo/bcb_scr/scrdata/actual/``)
**por partes** (``chunksize``): un año no cabe entero en memoria y
``credito_garantizado.py scr`` ya estableció el patrón de lectura por chunks
desde el ZIP sin descomprimir a disco.

La tasa es la oficial del BCB (docs/fuentes_datos_sector_bancario_brasil.md §15):
``tasa = Σ carteira_inadimplencia / Σ carteira_ativa``. La columna
``carteira_inadimplencia`` del SCR.data está en R$, NO en %; escribirla como
porcentaje es el error que §15 corrige. Las tasas van como fracción (0,05 = 5 %),
igual que el resto de la capa gold.

Decisiones del encargo 67 (03-11-2026) registradas para el que relea:

- **Los CSV del SCR.data son UTF-8 con BOM**, verificado byte a byte en 2012 y
  2024 (el encargo decía cp1252, que es lo normal en los archivos del gobierno
  brasileño, pero estos no: leerlos como cp1252 mojibakea «mínimos» y las UFs).
  La lectura prueba UTF-8 estricto sobre una muestra y cae a cp1252 solo si
  falla, por si el BCB cambia de era otra vez.
- **La descarga de 2012-2023 va streameada a disco con ``almacen.registrar_crudo``**,
  no con ``extraer_fuentes.py scrdata``: ese comando publica en el crudo un CSV
  combinado re-codificado (con nombre que colisiona entre años), no el ZIP anual
  que este preparador y ``credito_garantizado.py`` leen. Misma URL, misma
  procedencia; el patrón streameado es el del repo para archivos de decenas de
  MB (``ifdata.py``). Política de reintentos del encargo: 3 intentos por año,
  30 s de pausa; un año que falla 3 veces se anota y se sigue.
- **``numero_de_operacoes`` == -1 es secreto estadístico**, no un número; no se
  suma (aquí ni se usa: los cortes son de saldo). Las filas con -1 sí traen
  valores en R$ y entran a las sumas de cartera.
- **``porte`` del corte PJ va tal cual lo publica el BCB** (Micro, Pequeno,
  Médio, Grande, Indisponível): traducirlo es una decisión de presentación que
  no pide el encargo y mejor la toma quien consume la tabla.
- **``modalidad`` va siempre vacía**: el contrato gold del verificador la exige
  (y §3.10 la lista), pero los tres cortes publicados no abren por modalidad.

Receta::

    python -X utf8 preparar_gold_bancos_scr.py                # baja 2012-2023 y deriva
    python -X utf8 preparar_gold_bancos_scr.py --solo-descargar
"""

from __future__ import annotations

PORTE_ES = {"Micro": "Micro", "Pequeno": "Pequeña", "Médio": "Mediana", "Grande": "Grande", "Indisponível": "Sin dato"}  # arquitecto, 2026-11-03
import argparse
import os
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import pandas as pd

import almacen as A

BASE = Path(__file__).resolve().parents[1]
CRUDO = A.ruta_cruda("bcb_scr", "scrdata")            # .../scrdata/actual/
SALIDA = BASE / "datos" / "gold" / "bk_scr.parquet"

ANIOS_NUEVOS = range(2012, 2024)      # 2024-2026 ya están en el crudo
URL = "https://www.bcb.gov.br/pda/desig/scrdata_{}.zip"
UA = {"User-Agent": "Mozilla/5.0 extraer-fuentes/1.0"}
INTENTOS, PAUSA_S = 3, 30             # política de reintentos del encargo 67
CHUNK = 500_000

# Lo único que hace falta para los tres cortes; el resto del esquema no se lee.
COLS_LEER = ["data_base", "uf", "segmento", "cliente", "porte",
             "vencido_de_15_ate_90_dias", "vencido_acima_de_90_dias",
             "carteira_ativa", "carteira_inadimplencia", "ativo_problematico"]
RENOMBRE = {"segmento": "segmento_inst", "vencido_de_15_ate_90_dias": "vencido_15_90",
            "vencido_acima_de_90_dias": "vencido_90",
            "carteira_inadimplencia": "inadimplencia_brl"}
SUMAS = ["carteira_ativa", "vencido_15_90", "vencido_90",
         "inadimplencia_brl", "ativo_problematico"]
COLUMNAS = ["corte", "fecha", "segmento_inst", "cliente", "modalidad", "porte", "uf",
            "carteira_ativa", "vencido_15_90", "vencido_90", "inadimplencia_brl",
            "ativo_problematico", "tasa_inad", "tasa_ap"]


# --- descarga de los ZIP anuales --------------------------------------------------------- #

def asegurar_anios() -> list[str]:
    """Baja al crudo los ZIP 2012-2023 que falten. Devuelve los años que fallaron 3 veces."""
    import certificados  # noqa: F401  CA del proxy; antes de requests (ver CLAUDE.md)
    import requests

    CRUDO.mkdir(parents=True, exist_ok=True)
    fallidos: list[str] = []
    for anio in ANIOS_NUEVOS:
        destino = CRUDO / f"scrdata_{anio}.zip"
        if destino.exists() and destino.stat().st_size > 0:
            print(f"[=] {destino.name} ya está en el crudo")
            continue
        url = URL.format(anio)
        parcial = destino.with_name(destino.name + ".part")
        for intento in range(1, INTENTOS + 1):
            print(f"[~] bajando {url} (intento {intento}/{INTENTOS})...")
            try:
                with requests.get(url, stream=True, timeout=(30, 300), headers=UA) as r:
                    r.raise_for_status()
                    with open(parcial, "wb") as f:
                        for bloque in r.iter_content(1 << 20):
                            f.write(bloque)
                zipfile.ZipFile(parcial).namelist()      # ZIP truncado -> excepción
                parcial.replace(destino)
                A.registrar_crudo("bcb_scr", "scrdata", destino, url)
                print(f"[+] {destino.name} ({destino.stat().st_size / 1e6:.0f} MB)")
                break
            except Exception as e:                       # red, HTTP o ZIP roto
                parcial.unlink(missing_ok=True)
                print(f"[!] {destino.name}: {e}")
                if intento == INTENTOS:
                    fallidos.append(str(anio))          # se anota y se sigue
                else:
                    time.sleep(PAUSA_S)
    return fallidos


# --- lectura por partes y agregación ----------------------------------------------------- #

def _codificacion(z: zipfile.ZipFile, nombre: str) -> str:
    """UTF-8 (con BOM) si la muestra decodifica estricta; cp1252 si no.

    La muestra se corta 4 bytes antes del final: una secuencia multibyte
    partida justo en el borde del buffer hace fallar el decode estricto
    aunque el archivo entero sea UTF-8 válido (pasó con scrdata_201412).
    """
    with z.open(nombre) as f:
        muestra = f.read(65536)
    if muestra.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    try:
        muestra[:-4].decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "cp1252"


def _numeros(ch: pd.DataFrame) -> pd.DataFrame:
    """Coma decimal a punto, sin separadores de miles (verificado 2012 y 2024).

    ``errors="raise"`` a propósito: un valor que no se pueda leer debe romper
    la corrida, no quedar en 0 en silencio (misma regla que las sentinelas del
    SIDRA en CLAUDE.md).
    """
    for col in ("vencido_de_15_ate_90_dias", "vencido_acima_de_90_dias",
                "carteira_ativa", "carteira_inadimplencia", "ativo_problematico"):
        ch[col] = pd.to_numeric(ch[col].str.replace(",", ".", regex=False), errors="raise")
    return ch


def agregar_anio(ruta: Path) -> tuple[list[pd.DataFrame], list[pd.DataFrame], list[pd.DataFrame]]:
    """Un ZIP anual -> listas de agregados parciales de los tres cortes."""
    partes_a: list[pd.DataFrame] = []   # fecha × segmento × cliente
    partes_b: list[pd.DataFrame] = []   # fecha × porte (solo PJ)
    partes_c: list[pd.DataFrame] = []   # fecha × uf
    with zipfile.ZipFile(ruta) as z:
        for nombre in sorted(n for n in z.namelist() if n.endswith(".csv")):
            cod = _codificacion(z, nombre)
            with z.open(nombre) as f:
                for bruto in pd.read_csv(f, sep=";", dtype=str, usecols=COLS_LEER,
                                         encoding=cod, chunksize=CHUNK):
                    ch = _numeros(bruto).rename(columns=RENOMBRE)
                    ch["fecha"] = pd.to_datetime(ch["data_base"], format="%Y-%m-%d",
                                                 errors="raise")
                    sumas = ch.groupby(["fecha", "segmento_inst", "cliente"],
                                       as_index=False)[SUMAS].sum()
                    partes_a.append(sumas)
                    pj = ch[ch["cliente"] == "PJ"]
                    partes_b.append(pj.groupby(["fecha", "porte"], as_index=False)[SUMAS].sum())
                    partes_c.append(ch.groupby(["fecha", "uf"], as_index=False)[SUMAS].sum())
            print(f"   leído {nombre} ({cod})")
    return partes_a, partes_b, partes_c


def _corte(df: pd.DataFrame, dims: list[str], etiqueta: str) -> pd.DataFrame:
    """Tabla del corte con las columnas comunes; lo que no aplica queda vacío (None)."""
    df = df.groupby(["fecha"] + dims, as_index=False)[SUMAS].sum()
    activa, inad, ap = df["carteira_ativa"], df["inadimplencia_brl"], df["ativo_problematico"]
    df["tasa_inad"] = inad / activa.where(activa > 0)
    df["tasa_ap"] = ap / activa.where(activa > 0)
    df.insert(0, "corte", etiqueta)
    for col in ("segmento_inst", "cliente", "modalidad", "porte", "uf"):
        if col not in df.columns:
            df[col] = None
    return df[COLUMNAS]


def construir() -> pd.DataFrame:
    zips = sorted(CRUDO.glob("scrdata_*.zip"))
    if not zips:
        sys.exit(f"[scr] no hay ZIP en {CRUDO}; corre primero la descarga")
    partes_a, partes_b, partes_c = [], [], []
    for ruta in zips:
        print(f"[scr] {ruta.name}")
        a, b, c = agregar_anio(ruta)
        partes_a.extend(a)
        partes_b.extend(b)
        partes_c.extend(c)
    cortes = [
        _corte(pd.concat(partes_a, ignore_index=True), ["segmento_inst", "cliente"],
               "segmento_cliente"),
        _corte(pd.concat(partes_b, ignore_index=True), ["porte"], "porte_pj"),
        _corte(pd.concat(partes_c, ignore_index=True), ["uf"], "uf"),
    ]
    return pd.concat(cortes, ignore_index=True).sort_values(
        ["corte", "fecha", "segmento_inst", "cliente", "porte", "uf"],
        na_position="first").reset_index(drop=True)


# --- verificación (define «terminado» en el encargo 67) ---------------------------------- #

def verificar(df: pd.DataFrame) -> int:
    problemas = 0
    clave = ["fecha", "segmento_inst", "cliente", "modalidad", "porte", "uf"]
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

    print("\njun-2026, corte segmento_cliente: tasa de inadimplencia por segmento (encargo: "
          "Banco 4,42 · Financeira 12,31 · Fintech 16,42 · Cooperativa 5,20, ±0,01 pp)")
    jun = a[a["fecha"] == "2026-06-30"]
    tabla = jun.pivot_table(index="segmento_inst", columns="cliente",
                            values="tasa_inad", aggfunc="first") * 100
    tot = jun.groupby("segmento_inst")[["inadimplencia_brl", "carteira_ativa"]].sum()
    tabla["total"] = tot["inadimplencia_brl"] / tot["carteira_ativa"] * 100
    print(tabla.round(2).to_string())
    return problemas


def escribir_parquet_atomico(tabla: pd.DataFrame, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporal = tempfile.mkstemp(dir=destino.parent, suffix=".parquet.tmp")
    os.close(descriptor)
    try:
        if "porte" in tabla.columns:   # etiqueta del sitio (arquitecto, 2026-11-03)
            tabla = tabla.assign(porte_es=tabla["porte"].map(PORTE_ES))
        tabla.to_parquet(temporal, index=False)
        os.replace(temporal, destino)
    except BaseException:
        Path(temporal).unlink(missing_ok=True)
        raise


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--solo-descargar", action="store_true",
                    help="solo baja los ZIP 2012-2023 que falten, no deriva")
    args = ap.parse_args(argv)

    fallidos = asegurar_anios()
    if fallidos:
        print(f"[!] años que fallaron {INTENTOS} intentos: {', '.join(fallidos)}")
    if args.solo_descargar:
        return 1 if fallidos else 0

    df = construir()
    escribir_parquet_atomico(df, SALIDA)
    print(f"\n[+] {SALIDA.relative_to(BASE)}: {len(df):,} filas, "
          f"{df['fecha'].min().date()} a {df['fecha'].max().date()}")
    return verificar(df)


if __name__ == "__main__":
    sys.exit(main())


# Etiqueta en castellano para el sitio (decisión del arquitecto, revisión del encargo 67). Se aplica al
# escribir; la columna original «porte» conserva el texto del BCB.
