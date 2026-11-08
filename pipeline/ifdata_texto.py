"""Texto de los CSV de IF.Data (OLinda): limpieza, nulos, saldos y periodos. Sin red.

- Los nombres de cuenta vienen con saltos de línea dentro de las comillas del CSV.
- ``null`` literal (y ``NI``, «no informado», en los saldos) significa sin dato, nunca 0.
- Los saldos usan coma decimal brasileña; si no hay coma, un punto seguido de grupos de 3 dígitos es separador
  de miles.
"""
from __future__ import annotations

import re
import unicodedata

import pandas as pd


def limpiar(s):
    """Colapsa saltos de línea y espacios repetidos."""
    return " ".join((s or "").split())


def nulo(s):
    """'null' literal del CSV -> ''."""
    v = limpiar(s)
    return "" if v.lower() == "null" else v


def normalizar(s):
    """Minúsculas sin acentos, para búsquedas."""
    s = limpiar(s).casefold()
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def a_valor(s):
    """Saldo con coma decimal (formato brasileño) -> texto con punto; '' si no hay dato."""
    s = (s or "").strip()
    if not s or s.lower() in ("null", "ni"):
        return ""
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "." in s:
        partes = s.split(".")
        if len(partes) > 1 and all(len(p) == 3 for p in partes[1:]):
            s = "".join(partes)
    return s


def saldo(columna: pd.Series) -> pd.Series:
    """Columna Saldo del CSV -> número (NaN sin dato)."""
    return pd.to_numeric(columna.map(a_valor), errors="coerce")


def parsear_periodo(s, que="periodo"):
    """Trimestre AAAAMM (acepta 2026-03 y 2026/03); falla si no es fin de trimestre."""
    p = str(s).strip().replace("-", "").replace("/", "")
    if not re.fullmatch(r"(19|20)\d{4}", p):
        raise ValueError(f"{que} invalido: '{s}' (se espera AAAAMM, ej. 202603)")
    if p[4:] not in ("03", "06", "09", "12"):
        raise ValueError(f"{que} invalido: '{s}' (el mes debe ser 03, 06, 09 o 12)")
    return p
