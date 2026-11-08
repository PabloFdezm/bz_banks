# -*- coding: utf-8 -*-
"""Tests de preparar_gold_bancos_sistema.py en el encargo 78c (ola 4).

Funciones puras con datos pequeños y, cuando existen los archivos, comprobaciones contra la
fuente cruda leída de forma independiente (json y parquet, sin pasar por las funciones).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

import preparar_gold_bancos_sistema as P
from conftest import DATOS, GOLD

GOLD_M = GOLD / "bk_sistema_m.parquet"
GOLD_Q = GOLD / "bk_sistema_q.parquet"
CRUDO_IPCA = DATOS / "crudo" / "bcb_sgs" / "bancos_sistema" / "actual" / "serie_433.json"


def _mensual(valores, inicio="2024-01"):
    idx = pd.period_range(inicio, periods=len(valores), freq="M")
    return pd.Series(np.asarray(valores, dtype=float), index=idx)


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


@pytest.mark.integracion
def test_ipca_12m_ultimo_contra_crudo_independiente():
    """El último ipca_12m del gold, recalculado desde el crudo SGS 433 hasta ese mismo mes."""
    m = pd.read_parquet(GOLD_M)
    gold = m[m["serie_id"] == "ipca_12m"].dropna(subset=["valor"]).sort_values("fecha").iloc[-1]
    hasta = pd.Timestamp(gold["fecha"]).strftime("%Y-%m")
    filas = json.loads(CRUDO_IPCA.read_text(encoding="utf-8"))
    mensual = {pd.to_datetime(f["data"], format="%d/%m/%Y").strftime("%Y-%m"): float(f["valor"])
               for f in filas}
    ultimos = [mensual[k] for k in sorted(mensual) if k <= hasta][-12:]
    producto = 1.0
    for v in ultimos:
        producto *= 1 + v / 100
    assert float(gold["valor"]) == pytest.approx(producto - 1, abs=1e-9)


@pytest.mark.integracion
def test_tablas_gold_78c_columnas_y_trimestre():
    m = pd.read_parquet(GOLD_M)
    q = pd.read_parquet(GOLD_Q)
    for col in ("d_1m", "d_3m"):
        assert col in m.columns
    for sid in ("ipca_12m", "ipca_esperado_12m", "icc_real_exante", "mora90_pf_livre_adel3m"):
        assert sid in set(m["serie_id"]), sid
        assert sid in set(q["serie_id"]), sid
    mm = m[(m["serie_id"] == "ipca_12m") & (m["fecha"] == pd.Timestamp("2026-06-01"))]["valor"]
    qq = q[(q["serie_id"] == "ipca_12m") & (q["fecha"] == pd.Timestamp("2026-06-30"))]["valor"]
    assert float(qq.iloc[0]) == pytest.approx(float(mm.iloc[0]), abs=1e-12)
    # mora adelantada: en 2026-06 vale la mora90_pf_livre de 2026-09
    adel = m[(m["serie_id"] == "mora90_pf_livre_adel3m") & (m["fecha"] == pd.Timestamp("2026-06-01"))]
    real = m[(m["serie_id"] == "mora90_pf_livre") & (m["fecha"] == pd.Timestamp("2026-09-01"))]
    assert float(adel["valor"].iloc[0]) == pytest.approx(float(real["valor"].iloc[0]), abs=1e-12)
