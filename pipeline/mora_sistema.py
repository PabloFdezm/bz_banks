"""Mora del sistema (SGS > 90 días, bk_sistema_q) para cada modalidad de la cartera IF.Data del panel.

Las equivalencias modalidad → serie del SGS están en ``definiciones/bancos__equivalencias_mora.json``. Las
definiciones no son iguales (panel ≥ 15 días; SGS > 90 días): se comparan en evolución, nunca en nivel.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import almacen as A


def equivalencias_mora() -> dict:
    return A.leer_definicion("bancos__equivalencias_mora")["equivalencias"]


def mora_sistema(periodos: pd.Series, modalidades: pd.Series) -> list[float]:
    """Mora del sistema del trimestre (último mes, de bk_sistema_q) equivalente a cada modalidad; NaN si no hay."""
    eq = equivalencias_mora()
    sis = pd.read_parquet(A.GOLD / "bk_sistema_q.parquet")
    sis["periodo"] = pd.to_datetime(sis["fecha"]).dt.strftime("%Y%m")
    mora = sis.set_index(["periodo", "serie_id"])["valor"]
    return [mora.get((p, eq[m]["serie_id"]), np.nan) if m in eq and eq[m]["serie_id"] else np.nan
            for p, m in zip(periodos, modalidades)]
