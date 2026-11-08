"""Registro único de las métricas del panel (``definiciones/metricas_bancos.json``).

De aquí salen los valores por banco (preparar_metricas_bancos.py y preparar_gold_bancos.py), los agregados por
grupo (Σ numerador / Σ denominador) y el texto de ``bk_metrica``. Cambiar una fórmula es cambiar el JSON.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import almacen as A

_DEF = A.leer_definicion("metricas_bancos")

METRICAS: dict[str, dict] = _DEF["metricas"]
ORDEN_FAMILIAS: list[str] = _DEF["orden_familias"]
FONDEO: list[str] = _DEF["fondeo"]
CODIGOS_COSIF: dict[str, dict[str, str]] = {"cosif_2025": _DEF["cosif_2025"], "cosif_pre2025": _DEF["cosif_pre2025"]}
FLUJOS: dict[str, str] = _DEF["flujos"]          # métrica trimestral → columna de bank_resultados
TITULOS_TTM: list[str] = _DEF["ttm"]             # flujos trimestrales que se suman a 12 meses

RAZONES = {m: d["razon"] for m, d in METRICAS.items() if "razon" in d}
CRECIMIENTOS = {m: d["crecimiento_de"] for m, d in METRICAS.items() if "crecimiento_de" in d}
RANKEABLES = {m for m, d in METRICAS.items() if d.get("ranking")}
SOLO_GRUPO = [m for m, d in METRICAS.items() if d.get("solo_grupo")]


def _suma(d: pd.DataFrame, columnas: list[str], sufijo: str = "") -> pd.Series:
    """Σ de las columnas; vacía si ningún término tiene dato (nunca 0 por falta de datos)."""
    return d[[c + sufijo for c in columnas]].sum(axis=1, min_count=1)


def numerador(d: pd.DataFrame, metrica: str, sufijo: str = "", *, banco: bool = False) -> pd.Series:
    """Σ numerador con signo. Por banco (``banco=True``) se aplica ``num_nulo_es_cero`` del registro; por grupo no,
    para que el banco sin numerador quede fuera de la muestra."""
    r = RAZONES[metrica]
    n = _suma(d, r["num"], sufijo)
    if banco and r.get("num_nulo_es_cero"):
        n = n.fillna(0)
    return r.get("signo_num", 1) * n


def denominador(d: pd.DataFrame, metrica: str, sufijo: str = "") -> pd.Series:
    return _suma(d, RAZONES[metrica]["den"], sufijo)


def valor_banco(d: pd.DataFrame, metrica: str) -> pd.Series:
    """La razón para cada fila (banco × trimestre) de ``d``."""
    den = denominador(d, metrica)
    if RAZONES[metrica].get("den_positivo", True):
        den = den.where(den > 0)
    return numerador(d, metrica, banco=True) / den


def unidad_variacion(unidad: str | None) -> str | None:
    return {"ratio": "pp", "brl": "fraccion", "indice": "abs"}.get(unidad)


def tabla_metricas(metricas: list[str]) -> pd.DataFrame:
    """bk_metrica: una fila por métrica, ordenada por familia y nombre de métrica."""
    faltan = [m for m in metricas if m not in METRICAS]
    if faltan:
        raise KeyError(f"métricas sin definición en definiciones/metricas_bancos.json: {faltan}")
    columnas = ["nombre", "familia", "unidad", "formato", "signo", "signo_fuente", "fuente", "definicion", "en_ficha"]
    df = pd.DataFrame([{"metrica": m, **{c: METRICAS[m][c] for c in columnas}} for m in metricas])
    df["_f"] = df["familia"].map({f: i for i, f in enumerate(ORDEN_FAMILIAS)})
    df = df.sort_values(["_f", "metrica"]).drop(columns="_f").reset_index(drop=True)
    df["orden"] = np.arange(1, len(df) + 1)
    df["en_ficha"] = df["en_ficha"].astype(bool)
    return df
