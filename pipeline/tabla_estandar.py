"""La tabla estándar del sitio (Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m): sus variaciones.

Mensuales:
- saldos: m/m y a/a punta contra punta; 3m/3m y 12m/12m = promedio de la ventana sobre el de la ventana
  anterior (en flujos, 12m/12m compara sumas de doce meses);
- tasas: las mismas ventanas como diferencias (en la unidad de la serie × ``escala``).
Trimestrales: d1 = t/t, d3 vacío, d12 = a/a, dventana = 4T/4T, como diferencias.

Las variaciones son un dict con ultimo, d1, d3, d12, dventana y corte; ``fila`` les antepone las columnas propias
de cada tabla, en el orden en que se pasan (ese es el orden de las columnas del parquet), y exige ``COLUMNAS``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import periodos as PER


def _vacia(x: pd.Series) -> dict:
    return {"ultimo": x.iloc[-1] if len(x) else np.nan, "d1": np.nan, "d3": np.nan, "d12": np.nan,
            "dventana": np.nan, "corte": PER.mes_corto(x.index[-1]) if len(x) else None}


def variaciones_saldo(x: pd.Series, minimo: int = 0, flujo: bool = False) -> dict:
    """Saldo (o flujo) mensual con índice Period. Con menos de ``minimo`` meses, solo el último."""
    x = x.dropna()
    if len(x) < minimo:
        return _vacia(x)
    ventana = (x.iloc[-12:].sum() / x.iloc[-24:-12].sum() if flujo
               else x.iloc[-12:].mean() / x.iloc[-24:-12].mean())
    return {"ultimo": x.iloc[-1], "d1": x.iloc[-1] / x.iloc[-2] - 1,
            "d3": x.iloc[-3:].mean() / x.iloc[-6:-3].mean() - 1, "d12": x.iloc[-1] / x.iloc[-13] - 1,
            "dventana": ventana - 1, "corte": PER.mes_corto(x.index[-1])}


def variaciones_tasa(x: pd.Series, escala: float = 1.0, minimo: int = 0) -> dict:
    """Tasa mensual con índice Period: último en su unidad, cambios × ``escala`` (100 = fracción → pp)."""
    x = x.dropna()
    if len(x) < minimo:
        return _vacia(x)
    return {"ultimo": x.iloc[-1], "d1": (x.iloc[-1] - x.iloc[-2]) * escala,
            "d3": (x.iloc[-3:].mean() - x.iloc[-6:-3].mean()) * escala,
            "d12": (x.iloc[-1] - x.iloc[-13]) * escala,
            "dventana": (x.iloc[-12:].mean() - x.iloc[-24:-12].mean()) * escala,
            "corte": PER.mes_corto(x.index[-1])}


def variaciones_trimestrales(x, ultimo, corte: str) -> dict:
    """Serie trimestral (array o Series, ya en la unidad de los cambios): diferencias t/t, a/a y 4T/4T."""
    x = np.asarray(x, dtype=float)
    return {"ultimo": ultimo, "d1": x[-1] - x[-2], "d3": np.nan, "d12": x[-1] - x[-5],
            "dventana": x[-4:].mean() - x[-8:-4].mean(), "corte": corte}


def fecha_fin(p):
    """Period (o PeriodIndex) → último día del período en texto AAAA-MM-DD."""
    return p.to_timestamp(how="end").strftime("%Y-%m-%d")


def series_largas(datos: pd.Series | pd.DataFrame, nombre: str, desde: str | None = None) -> list[dict]:
    """Serie (o columnas de un DataFrame) con índice Period → filas serie|fecha|valor, sin vacíos.

    Una Series se llama ``nombre``; cada columna de un DataFrame, ``nombre|columna``. ``desde`` (AAAA-MM) recorta
    el comienzo.
    """
    df = datos.to_frame(nombre) if isinstance(datos, pd.Series) else datos.add_prefix(f"{nombre}|")
    if desde:
        df = df[df.index >= pd.Period(desde, "M")]
    return [{"serie": col, "fecha": fecha_fin(p), "valor": float(v)}
            for col in df.columns for p, v in df[col].dropna().items()]


# Columnas que toda tabla estándar trae (bk_portada_tablas, bk_cred_tablas, bk_scr_tablas); el sitio arma la
# cabecera y el formato con unidad_ultimo, unidad_cambio y trimestral.
COLUMNAS = ["bloque", "orden", "fila", "unidad_ultimo", "unidad_cambio", "trimestral",
            "ultimo", "d1", "d3", "d12", "dventana", "corte"]


def fila(var: dict, **columnas) -> dict:
    """Fila de la tabla: primero las columnas propias (en orden), después las variaciones."""
    faltan = [c for c in COLUMNAS if c not in columnas and c not in var]
    if faltan:
        raise ValueError(f"fila de tabla estándar sin {faltan}")
    return {**columnas, **var}
