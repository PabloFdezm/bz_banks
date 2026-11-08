"""Encuesta Focus del BCB (API Olinda): el único lector y descargador de expectativas del pipeline.

Solo se usa la mediana del IPCA a 12 meses adelante (``ExpectativasMercadoInflacao12Meses``), en la variante
suavizada (``Suavizada = 'S'``) y con todas las respuestas de los últimos 30 días (``baseCalculo = 0``). Es la
que usaba el dashboard macro: cuadra al decimal con la entrada que estaba congelada en
``datos/intermedio/expectativas_focus.parquet`` (validado el 8-nov-2026).

Vive en ``datos/crudo/bcb_focus/expectativas/actual/ipca_12m.json`` tal como lo devuelve la API (la lista
``value``), con su URL en el manifiesto del almacén.
"""
from __future__ import annotations

import json
import sys
import urllib.parse

import pandas as pd

import almacen as A
import red

FUENTE = "bcb_focus"
DATASET = "expectativas"
ARCHIVO = "ipca_12m.json"
DESDE = "2021-01-01"   # mismo inicio que la entrada congelada; antes no hay quien la use
URL = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoInflacao12Meses"


def url_ipca_12m(desde: str = DESDE) -> str:
    q = {"$filter": f"Indicador eq 'IPCA' and Suavizada eq 'S' and baseCalculo eq 0 and Data ge '{desde}'",
         "$orderby": "Data", "$top": "100000", "$format": "json"}
    return URL + "?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


def bajar(desde: str = DESDE):
    """Baja la mediana diaria del IPCA a 12 meses y la guarda en el crudo con su procedencia."""
    red.exigir_red("la encuesta Focus")
    import certificados  # noqa: F401  CA del proxy corporativo; antes de requests
    import requests

    url = url_ipca_12m(desde)
    print("[~] bajando Focus IPCA 12 meses...", file=sys.stderr)

    def una_vez():
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        if "json" not in r.headers.get("content-type", ""):
            raise ValueError(f"Focus: la API respondió {r.headers.get('content-type')} y no JSON")
        return r.json()["value"]

    filas = red.reintentar(una_vez, 3, lambda n, e: 2.0 * n)
    if not filas:
        raise ValueError("Focus: la API no devolvió observaciones")
    return A.guardar_crudo(FUENTE, DATASET, ARCHIVO, json.dumps(filas, ensure_ascii=False).encode("utf-8"), url)


def ipca_12m(descargar: bool = False) -> pd.Series:
    """Mediana Focus del IPCA a 12 meses, diaria por fecha de encuesta, en fracción (0,046 = 4,6 %)."""
    p = A.ruta_cruda(FUENTE, DATASET) / ARCHIVO
    if descargar or not p.exists():
        bajar()
    d = pd.DataFrame(json.loads(p.read_text(encoding="utf-8")))
    d = d[(d["Indicador"] == "IPCA") & (d["Suavizada"] == "S") & (d["baseCalculo"] == 0)]
    s = pd.Series(d["Mediana"].to_numpy(dtype=float) / 100, index=pd.to_datetime(d["Data"]))
    if s.index.duplicated().any():
        raise ValueError("Focus IPCA 12 meses: fechas repetidas")
    return s.sort_index().rename("ipca_esperado_12m")


def refrescar(argv: list[str] | None = None) -> int:
    """El paso focus de actualizar.py."""
    bajar()
    return 0


if __name__ == "__main__":
    sys.exit(refrescar())
