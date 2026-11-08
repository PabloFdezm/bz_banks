"""Reglas de la capa gold que comparten los preparadores, el exportador y herramientas/verificar_gold.py:
tolerancias y umbrales, marcas de dato con licencia, rango de fechas de una tabla y la comprobación de mix7.

Va aparte para que el verificador no tenga que importar los scripts que producen las tablas.
"""
from __future__ import annotations

import pandas as pd

import periodos as PER

# Marcas que delatan dato con licencia en el nombre de una columna (spec web §9, criterio 17).
LICENCIAS = ("px_", "pbv", "pe_", "bbg", "bloomberg", "consenso", "target")

MIN_GRUPO_PERCENTIL = 3       # percentiles y medianas de grupo solo con n >= 3 (spec §3.3)
TOL_ROA_ARBOL = 1e-6          # Σ líneas 1–9 del árbol del ROE = ROA = roa_ttm (spec §3.7)
TOL_ROE_ARBOL = 0.001         # ROA × apalancamiento = roe_ttm (0,1 pp)
MIN_TRIMESTRES_BETA = 16      # bk_sensibilidad: con menos, beta, IC y R² nulos (spec §3.8)
TOLERANCIA_TOTAL = 0.005      # Σ modalidades (informes 11 y 13) contra el total publicado por el BCB
COBERTURA_MIN = 0.5           # bk_exposicion: con menos cartera cubierta, la mora implícita queda vacía

COLUMNAS_FECHA = ("fecha", "periodo")   # para el rango de una tabla, la primera que exista


def rango(df: pd.DataFrame) -> tuple[str, object, object] | None:
    """(columna, mínimo, máximo) de la primera columna de fecha que exista; None si no hay o está vacía."""
    for col in COLUMNAS_FECHA:
        if col in df.columns and len(df):
            return col, df[col].min(), df[col].max()
    return None


def div(a, b):
    """a / b, vacío donde b es 0."""
    return a / b.where(b != 0)


def verificar_mix7(mix: pd.DataFrame, cartera_saldo: pd.DataFrame | None = None) -> list[str]:
    """Σ peso = 1 en cada banco, grupo y panel con saldo; Σ saldo de banco = cartera_saldo de bk_panel (si se pasa);
    dirigido_peso en [0, 1]; trimestres anómalos ausentes."""
    errores = []
    k = ["nivel", "optica", "grupo", "cod_inst", "periodo"]
    r = mix.groupby(k, dropna=False).agg(peso=("peso", "sum"), total=("total", "first"), saldo=("saldo", "sum")).reset_index()
    r = r[r["total"] > 0]
    malos = r[(r["peso"] - 1).abs() > 1e-9]
    if len(malos):
        errores.append(f"{len(malos)} filas con Σ peso ≠ 1 en bk_cartera_mix7; ej.:\n{malos.head(5).to_string(index=False)}")
    if cartera_saldo is not None:
        b = r[r["nivel"] == "banco"].merge(cartera_saldo, on=["cod_inst", "periodo"], how="inner")
        dif = (b["saldo"] / b["valor"] - 1).abs()
        dif = dif[b["valor"] > 0]
        if (dif > 1e-6).any():
            errores.append(f"{(dif > 1e-6).sum()} bancos con Σ saldo mix7 ≠ cartera_saldo de bk_panel")
    d = mix["dirigido_peso"].dropna()
    if ((d < 0) | (d > 1)).any():
        errores.append("dirigido_peso fuera de [0, 1] en bk_cartera_mix7")
    if mix["periodo"].isin(PER.ANOMALOS).any():
        errores.append(f"bk_cartera_mix7 tiene filas de {PER.ANOMALOS_TEXTO} (trimestre anómalo) y debía quedar vacío")
    return errores
