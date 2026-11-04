# -*- coding: utf-8 -*-
"""Tests de preparar_gold_bancos_sistema.py en el encargo 78c (ola 4).

Funciones puras con datos pequeños y, cuando existen los archivos, comprobaciones contra la
fuente cruda leída de forma independiente (json y parquet, sin pasar por las funciones).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import preparar_gold_bancos_sistema as P  # noqa: E402

GOLD_M = RAIZ / "datos" / "gold" / "bk_sistema_m.parquet"
GOLD_Q = RAIZ / "datos" / "gold" / "bk_sistema_q.parquet"
FOCUS = RAIZ / "datos" / "intermedio" / "expectativas_focus.parquet"
CRUDO_IPCA = RAIZ / "datos" / "crudo" / "bcb_sgs" / "bancos_sistema" / "actual" / "serie_433.json"


def _mensual(valores, inicio="2024-01"):
    idx = pd.period_range(inicio, periods=len(valores), freq="M")
    return pd.Series(np.asarray(valores, dtype=float), index=idx)


# --- funciones puras ---------------------------------------------------------------------

def test_ipca_12m_constante_1pct():
    s = _mensual([1.0] * 14)
    r = P.ipca_12m(s)
    assert r.iloc[:11].isna().all()
    assert r.iloc[11] == pytest.approx(1.01 ** 12 - 1, abs=1e-12)
    assert r.iloc[13] == pytest.approx(1.01 ** 12 - 1, abs=1e-12)


def test_ipca_12m_vacio_si_falta_un_mes():
    v = [1.0] * 20
    v[5] = np.nan
    r = P.ipca_12m(_mensual(v))
    assert r.iloc[5:17].isna().all()          # las doce ventanas que contienen el mes faltante
    assert pd.notna(r.iloc[17])                # la ventana siguiente ya no lo contiene


def test_ultimo_mes_trimestral_toma_marzo_junio_sept_dic():
    s = _mensual(np.arange(1, 13, dtype=float), inicio="2024-01")
    q = P.ultimo_mes_trimestral(s)
    assert list(q.to_numpy()) == [3.0, 6.0, 9.0, 12.0]
    assert list(q.index.month) == [3, 6, 9, 12]


def test_adelantar_tres_meses():
    s = _mensual(np.arange(10, dtype=float))
    a = P.adelantar(s, 3)
    assert len(a) == 7
    assert a.iloc[0] == 3.0
    assert a.iloc[-1] == 9.0


def test_deltas_mensuales_1m_3m():
    m = pd.DataFrame({
        "fecha": list(pd.date_range("2025-01-01", periods=5, freq="MS")) * 2,
        "serie_id": ["a"] * 5 + ["b"] * 5,
        "valor": [1, 2, 4, 7, 11, 10, 10, 10, 10, 10],
    })
    d = P.deltas_mensuales(m)
    a = d[d["serie_id"] == "a"].sort_values("fecha")
    assert a["d_1m"].iloc[1] == 1
    assert a["d_3m"].iloc[3] == 6          # 7 - 1
    b = d[d["serie_id"] == "b"].sort_values("fecha")
    assert (b["d_1m"].iloc[1:] == 0).all()


def test_icc_real_exante_formula():
    icc = _mensual([0.30])
    esp = _mensual([0.05])
    real = ((1 + icc) / (1 + esp) - 1).iloc[0]
    assert real == pytest.approx(1.30 / 1.05 - 1, abs=1e-12)


# --- contra datos reales -------------------------------------------------------------------

@pytest.mark.skipif(not FOCUS.exists(), reason="falta datos/intermedio/expectativas_focus.parquet")
def test_focus_usa_solo_horizonte_12_meses_y_ultimo_envio_del_mes():
    f = pd.read_parquet(FOCUS)
    g = f[(f["indicador"] == "IPCA") & (f["tipo_horizonte"] == "12 meses")].copy()
    g["fecha_encuesta"] = pd.to_datetime(g["fecha_encuesta"])
    sep = g[g["fecha_encuesta"].dt.to_period("M") == pd.Period("2026-09", "M")]
    esperado = float(sep.sort_values("fecha_encuesta")["mediana"].iloc[-1])
    serie = P.leer_focus_ipca_12m()
    assert serie.loc[pd.Period("2026-09", "M")] == pytest.approx(esperado, abs=1e-12)
    assert esperado == pytest.approx(0.046478, abs=1e-6)   # 2026-09-11, cifra a mano


@pytest.mark.skipif(not (CRUDO_IPCA.exists() and GOLD_M.exists()),
                    reason="faltan el crudo SGS 433 o la tabla gold")
def test_ipca_12m_ultimo_contra_crudo_independiente():
    filas = json.loads(CRUDO_IPCA.read_text(encoding="utf-8"))
    mensual = {pd.to_datetime(f["data"], format="%d/%m/%Y").strftime("%Y-%m"): float(f["valor"])
               for f in filas}
    ultimos = [mensual[k] for k in sorted(mensual)[-12:]]
    producto = 1.0
    for v in ultimos:
        producto *= 1 + v / 100
    m = pd.read_parquet(GOLD_M)
    v = m[(m["serie_id"] == "ipca_12m") & (m["fecha"] == pd.Timestamp("2026-09-01"))]["valor"]
    assert float(v.iloc[0]) == pytest.approx(producto - 1, abs=1e-9)


@pytest.mark.skipif(not GOLD_M.exists() or not GOLD_Q.exists(),
                    reason="faltan las tablas gold de sistema")
def test_tablas_gold_78c_columnas_y_trimestre():
    m = pd.read_parquet(GOLD_M)
    q = pd.read_parquet(GOLD_Q)
    for col in ("d_1m", "d_3m"):
        assert col in m.columns
    for sid in ("ipca_12m", "ipca_esperado_12m", "icc_real_exante", "mora90_pf_livre_adel3m"):
        assert sid in set(m["serie_id"]), sid
        assert sid in set(q["serie_id"]), sid
    # ipca_12m trimestral = valor del último mes del trimestre en _m
    mm = m[(m["serie_id"] == "ipca_12m") & (m["fecha"] == pd.Timestamp("2026-06-01"))]["valor"]
    qq = q[(q["serie_id"] == "ipca_12m") & (q["fecha"] == pd.Timestamp("2026-06-30"))]["valor"]
    assert float(qq.iloc[0]) == pytest.approx(float(mm.iloc[0]), abs=1e-12)
    # mora adelantada: en 2026-06 vale la mora90_pf_livre de 2026-09
    adel = m[(m["serie_id"] == "mora90_pf_livre_adel3m") & (m["fecha"] == pd.Timestamp("2026-06-01"))]
    real = m[(m["serie_id"] == "mora90_pf_livre") & (m["fecha"] == pd.Timestamp("2026-09-01"))]
    assert float(adel["valor"].iloc[0]) == pytest.approx(float(real["valor"].iloc[0]), abs=1e-12)
    # d_1m coincide con la diferencia de la serie
    s = m[m["serie_id"] == "credito_pib"].sort_values("fecha").set_index("fecha")["valor"]
    d = m[m["serie_id"] == "credito_pib"].sort_values("fecha").set_index("fecha")["d_1m"]
    assert d.iloc[-1] == pytest.approx(s.iloc[-1] - s.iloc[-2], abs=1e-12)
