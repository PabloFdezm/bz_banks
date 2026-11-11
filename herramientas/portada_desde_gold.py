# -*- coding: utf-8 -*-
"""Recarga los datos incrustados de las hojas de la Portada (diseno/canvas/Seccion01–03.dc.html) desde gold.

Las hojas de la Portada llevan sus datos dentro (``const D``, ``const T`` o ``const LARGO`` y ``const FALTA``); el
sitio no las lee de JSON (herramientas/construir_v2.py). Este script reemplaza esas líneas con las cifras de:
- Sección 01: bk_concesiones y bk_concesiones_tablas (bloque «12m»): a/a de las concesiones de 12 meses (``aa_<seg>``),
  índice de concesiones reales sobre actividad (``ci_<seg>``) y la tabla de la página (``LARGO``).
- Secciones 02 y 03: bk_portada_m y bk_portada_m_tablas (frente 9): tasa y spread (02), mora y atraso (03) por los
  nueve segmentos; ``T`` = [último, m/m, 3m/3m, a/a, 12m/12m, Z 10 años] en % y pp.
Lo que el SGS no publica (spread dirigido de personas) queda fuera de ``D`` y en ``NO_PUB`` de la hoja.
Las demás claves de D y T (referencias, productos, empresas) no se tocan.

    Set-Location C:\\dev\\bz_banks; python -X utf8 herramientas/portada_desde_gold.py [--revisar]

Con --revisar solo informa qué cambiaría (no escribe).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CANVAS = RAIZ / "diseno" / "canvas"
GOLD = RAIZ / "datos" / "gold"
SEGMENTOS = ["tot", "pf", "pj", "li", "di", "pfli", "pfdi", "pjli", "pjdi"]
INICIO = "2014-01"


def meses(n: int) -> pd.PeriodIndex:
    return pd.period_range(INICIO, periods=n, freq="M")


def lista(s: pd.Series, ix: pd.PeriodIndex, escala=1.0, dec=2) -> list:
    v = s.reindex(ix)
    return [None if pd.isna(x) or math.isinf(x) else round(float(x) * escala, dec) for x in v]


def serie(df: pd.DataFrame, col: str = "valor") -> pd.Series:
    return pd.Series(df[col].to_numpy(), index=pd.PeriodIndex(pd.to_datetime(df["fecha"]), freq="M"))


def linea(texto: str, nombre: str) -> tuple[int, int]:
    """Posición (inicio, fin) de la línea «const <nombre> = …;» de la hoja (una sola línea)."""
    m = re.search(rf"^(\s*)const {nombre} = .*;$", texto, re.M)
    if not m:
        raise ValueError(f"la hoja no tiene «const {nombre} = …;» en una línea")
    return m.start(), m.end()


def leer_const(texto: str, nombre: str):
    i, j = linea(texto, nombre)
    cuerpo = texto[i:j].split("=", 1)[1].strip().rstrip(";")
    return json.loads(cuerpo)


def poner_const(texto: str, nombre: str, valor, js: str | None = None) -> str:
    i, j = linea(texto, nombre)
    sangria = re.match(r"\s*", texto[i:j]).group(0)
    cuerpo = js if js is not None else json.dumps(valor, ensure_ascii=False, separators=(",", ":"))
    return texto[:i] + f"{sangria}const {nombre} = {cuerpo};" + texto[j:]


def num_es(x: float, dec: int = 1) -> str:
    s = f"{abs(x):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if x < 0 else "") + s


def pct_signo(x: float) -> str:
    return ("+" if x > 0 else "−" if x < 0 else "") + num_es(abs(x) * 100) + " %"


# ---------------------------------------------------------------- sección 01

def seccion01(texto: str) -> str:
    D = leer_const(texto, "D")
    ix = meses(len(D["aa_tot"]))
    c = pd.read_parquet(GOLD / "bk_concesiones.parquet")
    for seg in SEGMENTOS:
        x = c[c["segmento"] == seg]
        D[f"aa_{seg}"] = lista(serie(x, "conc_12m_aa"), ix, 100)
        D[f"ci_{seg}"] = lista(serie(x, "indice"), ix, 1)
    t = pd.read_parquet(GOLD / "bk_concesiones_tablas.parquet")
    t = t[t["bloque"] == "12m"].sort_values("orden")
    largo = {}
    for seg, (_, r) in zip(SEGMENTOS, t.iterrows()):
        largo[seg] = [num_es(r["ultimo"]), num_es(r["share"] * 100) + " %", pct_signo(r["d1"]), pct_signo(r["d3"]),
                      pct_signo(r["d12"]), pct_signo(r["dventana"])]
    texto = poner_const(texto, "D", D)
    texto = poner_const(texto, "LARGO", largo)
    return poner_const(texto, "FALTA", [])


# ---------------------------------------------------------------- secciones 02 y 03

def fila_t(r) -> list:
    return [round(r["ultimo"] * 100, 2), round(r["d1"], 2), round(r["d3"], 2), round(r["d12"], 2),
            round(r["dventana"], 2), None if pd.isna(r["z120"]) else round(r["z120"], 2)]


def seccion_m(texto: str, mapa: dict[str, str]) -> tuple[str, dict[str, list[str]]]:
    """``mapa``: clave de D (mo, at) → indicador de bk_portada_m. Devuelve el texto y los segmentos no publicados."""
    D, T = leer_const(texto, "D"), leer_const(texto, "T")
    clave0 = next(iter(mapa))
    ix = meses(len(next(iter(D[clave0].values()))))
    largo = pd.read_parquet(GOLD / "bk_portada_m.parquet")
    tab = pd.read_parquet(GOLD / "bk_portada_m_tablas.parquet").set_index(["indicador", "segmento"])
    no_pub = {}
    for clave, indicador in mapa.items():
        D[clave] = {}
        for seg in SEGMENTOS:
            x = largo[(largo["indicador"] == indicador) & (largo["segmento"] == seg)]
            if x.empty:
                no_pub.setdefault(clave, []).append(seg)
                T.pop(f"{clave}_{seg}", None)
                continue
            D[clave][seg] = lista(serie(x), ix, 100)
            T[f"{clave}_{seg}"] = fila_t(tab.loc[(indicador, seg)])
    texto = poner_const(texto, "D", D)
    texto = poner_const(texto, "T", T)
    return texto, no_pub


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--revisar", action="store_true", help="informa sin escribir")
    a = ap.parse_args(argv)
    for hoja, f in (("Seccion01", None), ("Seccion02", {"mo": "tasa", "at": "spread"}),
                    ("Seccion03", {"mo": "mora90", "at": "atraso15_90"})):
        p = CANVAS / f"{hoja}.dc.html"
        antes = p.read_text(encoding="utf-8")
        if f is None:
            nuevo, no_pub = seccion01(antes), {}
        else:
            nuevo, no_pub = seccion_m(antes, f)
            pares = {"mo": "va", "at": "vb"}
            nuevo = poner_const(nuevo, "FALTA", {pares[k]: [] for k in f},
                                js="{ " + ", ".join(f"{pares[k]}: []" for k in f) + " }")
            nuevo = poner_const(nuevo, "NO_PUB", {pares[k]: v for k, v in no_pub.items()})
        print(f"{hoja}: {'cambia' if nuevo != antes else 'sin cambios'}"
              + (f"; no publicados: {no_pub}" if no_pub else ""))
        if not a.revisar and nuevo != antes:
            p.write_text(nuevo, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
