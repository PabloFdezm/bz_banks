# -*- coding: utf-8 -*-
"""Pruebas del encargo 78a (gold post-MVP, rentabilidad y variaciones), sobre las tablas que publica el pipeline.

Cubre: valor_tt vacío en 2024-T4 y 2025-T1 e igual a d_tt en el resto; variación de grupo con muestra
constante (ratio y monto); la identidad gasto / ingreso = eficiencia; y que medios, margen y eficiencia no
inventen datos (bug B1). Todas leen datos/gold.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from conftest import GOLD

pytestmark = pytest.mark.integracion

SIN_TT = ["202412", "202503"]   # 2024-T4 sin dato y 2025-T1, cuya variación parte de 2024-T4


@pytest.fixture(scope="module")
def panel() -> pd.DataFrame:
    return pd.read_parquet(GOLD / "bk_panel.parquet",
                           columns=["cod_inst", "periodo", "metrica", "valor", "d_tt", "valor_tt"])


@pytest.fixture(scope="module")
def total_panel() -> pd.DataFrame:
    g = pd.read_parquet(GOLD / "bk_grupo.parquet")
    return g[g["optica"] == "Total panel"].set_index(["metrica", "periodo"])


def test_valor_tt_vacio_al_tocar_2024t4_e_igual_a_d_tt_en_el_resto(panel):
    toca = panel["periodo"].isin(SIN_TT)
    assert panel.loc[toca, "valor_tt"].isna().all()
    resto = panel[~toca & panel["d_tt"].notna()]
    assert len(resto) > 1000
    assert np.allclose(resto["valor_tt"], resto["d_tt"], rtol=0, atol=1e-12)


def test_grupo_sin_variacion_tt_al_tocar_2024t4(total_panel):
    assert total_panel.loc[total_panel.index.get_level_values("periodo").isin(SIN_TT), "valor_tt"].isna().all()


def _pares(panel: pd.DataFrame, metricas: list[str]) -> list[tuple[str, str, pd.DataFrame, pd.DataFrame]]:
    """(t, t−1, ancho en t, ancho en t−1) para cada trimestre con variación válida."""
    w = panel[panel["metrica"].isin(metricas)].pivot_table(index=["periodo", "cod_inst"], columns="metrica",
                                                            values="valor")
    periodos = sorted(w.index.get_level_values("periodo").unique())
    return [(t, t1, w.loc[t].dropna(), w.loc[t1].dropna())
            for t1, t in zip(periodos, periodos[1:]) if t not in SIN_TT]


def test_grupo_ratio_tt_con_muestra_constante(panel, total_panel):
    """roe_ttm de grupo: Σ lucro / Σ PL medio; la variación t/t usa solo los bancos con dato en t y t−1."""
    for t, t1, a, b in _pares(panel, ["lucro_liquido_ttm", "pl_medio_ttm"]):
        comun = a.index.intersection(b.index)
        if comun.empty:
            continue
        ratio = lambda x: x.loc[comun, "lucro_liquido_ttm"].sum() / x.loc[comun, "pl_medio_ttm"].sum()  # noqa: E731
        assert total_panel.loc[("roe_ttm", t), "valor_tt"] == pytest.approx((ratio(a) - ratio(b)) * 100, abs=1e-9), t


def test_grupo_monto_tt_con_muestra_constante(panel, total_panel):
    for t, t1, a, b in _pares(panel, ["gasto_total_ttm"]):
        comun = a.index.intersection(b.index)
        if comun.empty:
            continue
        esperado = a.loc[comun, "gasto_total_ttm"].sum() / b.loc[comun, "gasto_total_ttm"].sum() - 1
        assert total_panel.loc[("gasto_total_ttm", t), "valor_tt"] == pytest.approx(esperado, rel=1e-9), t


def test_gasto_sobre_ingreso_reproduce_eficiencia(panel):
    """gasto e ingreso (gold) y eficiencia (preparar_metricas_bancos) salen de módulos distintos."""
    w = panel[panel["metrica"].isin(["gasto_total_ttm", "ingreso_total_ttm", "eficiencia_ttm"])].pivot_table(
        index=["cod_inst", "periodo"], columns="metrica", values="valor")
    ok = w["ingreso_total_ttm"].gt(0) & w["eficiencia_ttm"].notna()
    assert ok.sum() > 0
    ratio = w.loc[ok, "gasto_total_ttm"] / w.loc[ok, "ingreso_total_ttm"]
    assert (ratio - w.loc[ok, "eficiencia_ttm"]).abs().max() <= 1e-9
    # Una suma sin ningún término no es 0 (bug B1): sin gasto o sin ingreso, eficiencia vacía.
    assert not (w["eficiencia_ttm"].notna() & (w["ingreso_total_ttm"].isna() | w["gasto_total_ttm"].isna())).any()


def test_medios_y_margen_no_inventan_datos(panel):
    """Bug B1: el activo / PL medio exige t y t−4, y el margen sin ningún componente queda vacío (no 0)."""
    w = panel[panel["metrica"].isin(["ativo_total", "ativo_medio_ttm", "patrimonio_liquido", "pl_medio_ttm",
                                     "margem_intermediacao_ttm", "resultado_intermediacao_financeira_ttm",
                                     "resultado_transacoes_pagamento_ttm"])].pivot_table(
        index=["cod_inst", "periodo"], columns="metrica", values="valor")
    for nivel, medio in (("ativo_total", "ativo_medio_ttm"), ("patrimonio_liquido", "pl_medio_ttm")):
        previo = w[nivel].groupby(level="cod_inst").shift(4)
        assert not (w[medio].notna() & (w[nivel].isna() | previo.isna())).any(), medio
    sin_componentes = (w["resultado_intermediacao_financeira_ttm"].isna()
                       & w["resultado_transacoes_pagamento_ttm"].isna())
    assert not (w["margem_intermediacao_ttm"].notna() & sin_componentes).any()
