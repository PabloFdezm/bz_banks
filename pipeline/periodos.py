"""Periodos AAAAMM (trimestres de IF.Data y meses del SGS/SCR): aritmética, etiquetas y quiebres conocidos.

Los quiebres de la fuente viven aquí una sola vez:

- ``QUIEBRE_2025`` (2025-T1): el BCB renumeró las cuentas COSIF y movió los informes de crédito del
  escopo financeiro al prudencial. Los bancos con cambio de cobertura (``quiebre_2025`` en bk_cartera)
  quedan fuera de las variaciones que cruzan este trimestre.
- ``ANOMALOS``: trimestres que el BCB sirve con saltos imposibles; se dejan vacíos, nunca interpolados.
  La lista y el motivo están en ``definiciones/bcb_ifdata__credito_modalidades.json`` (``trimestres_anomalos``).
"""
from __future__ import annotations

import pandas as pd

import almacen as A

QUIEBRE_2025 = "202503"
ANOMALOS: tuple[str, ...] = tuple(A.leer_definicion("bcb_ifdata__credito_modalidades").get("trimestres_anomalos", {}))

ANOMALOS_TEXTO = ", ".join(  # «2024-T4», para mensajes
    f"{p[:4]}-T{int(p[4:]) // 3}" for p in ANOMALOS)

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def qi(periodo: str) -> int:
    """Índice trimestral consecutivo de un periodo AAAAMM (fin de trimestre)."""
    return int(periodo[:4]) * 4 + int(periodo[4:]) // 3 - 1


def periodo_de_qi(indice: int) -> str:
    return f"{indice // 4}{(indice % 4 + 1) * 3:02d}"


def previo(periodo: str, k: int = 1) -> str:
    """El trimestre k trimestres antes (k negativo: después)."""
    return periodo_de_qi(qi(periodo) - k)


def rango_trimestres(desde: str, hasta: str) -> list[str]:
    """Trimestres AAAAMM de ``desde`` a ``hasta``, ambos inclusive."""
    return [periodo_de_qi(i) for i in range(qi(desde), qi(hasta) + 1)]


def previo_serie(periodos: pd.Series, k: int = 1) -> pd.Series:
    mapa = {p: previo(p, k) for p in periodos.unique()}
    return periodos.map(mapa)


def fin_de_mes(periodos: pd.Series) -> pd.Series:
    """AAAAMM (texto o Series) → último día del mes."""
    return pd.to_datetime(periodos, format="%Y%m") + pd.offsets.MonthEnd(0)


def etiqueta_trimestre(periodo: str) -> str:
    """202503 → «1T25»."""
    return f"{int(periodo[4:]) // 3}T{periodo[2:4]}"


def etiqueta_anio_trimestre(periodos: pd.Series) -> pd.Series:
    """202503 → «2025 T1»."""
    return periodos.str[:4] + " T" + (periodos.str[4:].astype(int) // 3).astype(str)


def mes_corto(p: pd.Period) -> str:
    """Period mensual → «sep-26»."""
    return f"{MESES[p.month - 1]}-{str(p.year)[2:]}"


def variacion_valida(periodo: pd.Series, k: int, con_quiebre: pd.Series | None = None,
                     regla_quiebre: str = "cruza") -> pd.Series:
    """True donde la variación t contra t−k es publicable.

    - Ningún extremo (t ni t−k) puede ser un trimestre anómalo (ANOMALOS se aplica a todas las tablas, aunque
      la definición lo motiva con los informes 8, 11 y 13).
    - En las filas con ``con_quiebre`` True (bancos con cambio de cobertura en 2025-T1), según ``regla_quiebre``:
      «cruza» = vacía si t ≥ 2025-T1 > t−k (bk_panel.valor_tt, bk_grupo, bk_cartera.d_cuota_aa);
      «toca» = vacía si t o t−k es 2025-T1 (bk_qcambio; para k = 1 vacía también 2025-T2). Son reglas
      distintas hasta que Pablo elija una.
    """
    previo = previo_serie(periodo, k)
    ok = ~(periodo.isin(ANOMALOS) | previo.isin(ANOMALOS))
    if con_quiebre is not None:
        if regla_quiebre == "cruza":
            afectada = (periodo >= QUIEBRE_2025) & (previo < QUIEBRE_2025)
        elif regla_quiebre == "toca":
            afectada = periodo.eq(QUIEBRE_2025) | previo.eq(QUIEBRE_2025)
        else:
            raise ValueError(f"regla_quiebre desconocida: {regla_quiebre}")
        ok &= ~(afectada & con_quiebre)
    return ok.astype(bool)
