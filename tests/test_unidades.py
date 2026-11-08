# -*- coding: utf-8 -*-
"""Pruebas unitarias con datos sintéticos (no leen datos/): las reglas de cálculo del pipeline, una por una."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import periodos as PER
import preparar_bancos_powerbi as PB
import preparar_credito_paginas_powerbi as CP
import preparar_gold_bancos as G
import preparar_metricas_bancos as PM
import registro_metricas as R
import tabla_estandar as T

PERIODOS = ["202403", "202406", "202409", "202412", "202503", "202506", "202509", "202512"]


# --- periodos --------------------------------------------------------------------------------------------- #

def test_previo_y_rango_de_trimestres():
    assert PER.previo("202503") == "202412"
    assert PER.previo("202503", 4) == "202403"
    assert PER.previo("202412", -1) == "202503"
    assert PER.rango_trimestres("202409", "202506") == ["202409", "202412", "202503", "202506"]


def test_variacion_valida_anomalo_y_quiebre(monkeypatch):
    # Reglas con un trimestre anómalo fijado aquí, sin depender de la definición del día.
    monkeypatch.setattr(PER, "ANOMALOS", ("202412",))
    monkeypatch.setattr(PER, "QUIEBRE_2025", "202503")
    p = pd.Series(PERIODOS)
    ok = PER.variacion_valida(p, 1)
    assert list(ok) == [True, True, True, False, False, True, True, True]   # 2024-T4 como t y como t−1
    quiebre = pd.Series(True, index=p.index)
    cruza = PER.variacion_valida(p, 4, quiebre, "cruza")
    # t−4 anómalo vacía 2025-T4; cruzar 2025-T1 vacía 2025-T1..2025-T3 para un banco con quiebre
    assert list(cruza) == [True, True, True, False, False, False, False, False]
    toca = PER.variacion_valida(p, 1, quiebre, "toca")
    assert list(toca) == [True, True, True, False, False, False, True, True]   # 2025-T2 también, contra 2025-T1


# --- tabla estándar --------------------------------------------------------------------------------------- #

def _mensual(valores, inicio="2024-01"):
    return pd.Series(np.asarray(valores, dtype=float), index=pd.period_range(inicio, periods=len(valores), freq="M"))


def test_variaciones_saldo_y_flujo():
    x = _mensual(range(1, 25))          # 1..24
    v = T.variaciones_saldo(x)
    assert v["ultimo"] == 24 and v["corte"] == "dic-25"
    assert v["d1"] == pytest.approx(24 / 23 - 1)
    assert v["d3"] == pytest.approx(23 / 20 - 1)                     # (22,23,24) contra (19,20,21)
    assert v["d12"] == pytest.approx(24 / 12 - 1)
    assert v["dventana"] == pytest.approx(18.5 / 6.5 - 1)            # promedios de 13..24 y 1..12
    assert T.variaciones_saldo(x, flujo=True)["dventana"] == pytest.approx(sum(range(13, 25)) / sum(range(1, 13)) - 1)


def test_variaciones_tasa_en_pp_y_minimo_de_historia():
    x = _mensual([0.01 * i for i in range(1, 25)])
    v = T.variaciones_tasa(x, escala=100)
    assert v["d1"] == pytest.approx(1.0) and v["d12"] == pytest.approx(12.0)
    corta = T.variaciones_tasa(x.iloc[:10], escala=100, minimo=24)
    assert corta["ultimo"] == pytest.approx(0.10) and np.isnan(corta["d1"])


def test_variaciones_trimestrales():
    v = T.variaciones_trimestrales([1, 2, 3, 4, 5, 6, 7, 8], 8, "4T25")
    assert (v["d1"], v["d12"], v["dventana"]) == (1, 4, 4) and np.isnan(v["d3"])


# --- TTM y razones por banco (preparar_metricas_bancos + registro) ----------------------------------------- #

def _tabla_banco() -> pd.DataFrame:
    n = len(PERIODOS)
    t = pd.DataFrame({"cod_inst": "C1", "periodo": PERIODOS, "era": "cosif_pre2025"})
    for c in R.TITULOS_TTM:
        t[c] = 1.0
    t["lucro_liquido_q"] = [10.0] * n
    t["resultado_transacoes_pagamento_q"] = np.nan
    t["ativo_total"] = [100.0 + i for i in range(n)]
    t["patrimonio_liquido"] = [10.0] * n
    t.loc[5, "patrimonio_liquido"] = np.nan          # 202506: sin PL
    for c in ("credito_liquido", "arrendamento", "outras_concessao", "depositos", "credito_bruto", "ecl_saldo"):
        t[c] = 50.0
    t["pagos_receber"] = np.nan                      # solo existe en la era COSIF 2025
    return t


def test_ttm_suma_cuatro_trimestres_consecutivos():
    t = PM._ttm(_tabla_banco())
    assert t["lucro_liquido_ttm"].isna().iloc[:3].all()
    assert t["lucro_liquido_ttm"].iloc[3:].eq(40.0).all()
    assert t["resultado_transacoes_pagamento_ttm"].isna().all()       # sin dato no es 0


def test_razones_medios_exigen_los_dos_extremos():
    t = PM._razones(PM._ttm(_tabla_banco()))
    pl = t.set_index("periodo")["pl_medio_ttm"]
    assert np.isnan(pl["202412"])                      # sin t−4
    assert pl["202503"] == pytest.approx(10.0)
    assert np.isnan(pl["202506"])                      # sin PL en t: no vale el de t−4 solo (bug B1)
    roe = t.set_index("periodo")["roe_ttm"]
    assert roe["202503"] == pytest.approx(40.0 / 10.0)


def test_margen_sin_componentes_queda_vacio():
    t = _tabla_banco()
    t["resultado_intermediacao_financeira_q"] = np.nan
    t = PM._razones(PM._ttm(t))
    assert t["margem_intermediacao_ttm"].isna().all()  # antes 0 (bug B1)


def test_registro_razon_con_signo_y_denominador_positivo():
    d = pd.DataFrame({"provisoes_credito_ttm": [-5.0, -5.0, np.nan], "credito_total": [100.0, 0.0, 100.0]})
    assert list(R.valor_banco(d, "costo_riesgo_ttm").round(6).fillna(-1)) == [0.05, -1, -1]


# --- agregados por grupo ---------------------------------------------------------------------------------- #

def test_grupo_es_cociente_de_sumas_con_muestra_constante():
    fb = pd.DataFrame({
        "inst_key": "g", "periodo": "202506", "cod_inst": ["A", "B", "C"],
        "roe_ttm": [0.1, 0.3, np.nan],
        "lucro_liquido_ttm": [10.0, 30.0, 5.0], "pl_medio_ttm": [100.0, 100.0, np.nan],
        "lucro_liquido_ttm__4": [5.0, np.nan, 1.0], "pl_medio_ttm__4": [100.0, 100.0, 10.0],
        "lucro_liquido_ttm__1": [8.0, 20.0, 1.0], "pl_medio_ttm__1": [100.0, 100.0, 10.0],
    })
    r = G.agregar_grupo(fb, "roe_ttm", "ratio", "ratio").set_index("inst_key").loc["g"]
    assert r["valor"] == pytest.approx(40 / 200)                     # C sin PL no entra
    assert r["valor_aa"] == pytest.approx((10 / 100 - 5 / 100) * 100)   # a/a solo con A (B sin t−4)
    assert r["valor_tt"] == pytest.approx((40 / 200 - 28 / 200) * 100)
    assert r["unidad_aa"] == "pp"


# --- des-acumulación y apilados --------------------------------------------------------------------------- #

def test_desacumular_resetea_en_julio():
    h = pd.DataFrame({"cod_inst": "C1", "cuenta_id": "r4_x", "anio": 2025, "trimestre": [1, 2, 3, 4],
                      "tipo_valor": "flujo", "valor_publicado": [10.0, 25.0, 12.0, 30.0]})
    assert list(PB.desacumular(h)["valor"]) == [10.0, 15.0, 12.0, 18.0]


def test_apilado_aportes_suman_la_variacion_y_base_cero_no_da_infinito():
    per = ["202403", "202406"]
    a = pd.DataFrame({"B1": [100.0, 110.0]}, index=per)
    b = pd.DataFrame({"B1": [0.0, 5.0]}, index=per)
    s = CP.apilado({"a": a, "b": b}, 1)
    assert s["_padre_var"].iloc[1] == pytest.approx(115 / 100 - 1)
    aportes = s["a"]["aporte"].iloc[1] + s["b"]["aporte"].iloc[1]
    assert aportes == pytest.approx(s["_padre_var"].iloc[1])
    assert np.isnan(s["b"]["var"].iloc[1])           # base cero: sin variación propia
    vacio = CP.apilado({"a": pd.DataFrame({"B1": [0.0, 5.0]}, index=per)}, 1)
    assert not np.isinf(vacio["_padre_var"].to_numpy(dtype=float)).any()   # bug B2
    assert not np.isinf(vacio["a"]["aporte"].to_numpy(dtype=float)).any()
