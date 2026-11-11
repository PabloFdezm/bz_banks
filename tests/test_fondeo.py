# -*- coding: utf-8 -*-
"""Hoja «Fondeo y liquidez» (pipeline/preparar_gold_bancos_fondeo.py, frente 14).

Las unitarias usan series SGS sintéticas que cumplen las identidades de la fuente. Las marcadas `integracion` leen
datos/gold.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import preparar_gold_bancos_fondeo as F
from conftest import GOLD

TOL = 1e-9
# Las series de la fuente están en R$ mil enteros: cada identidad puede fallar en ±2 R$ mil = 0,002 R$ millones.
TOL_REDONDEO = 0.0025


def _sinteticas(n=30, semilla=7, residuo_m3=5.0):
    """Códigos SGS → series en R$ mil que cumplen M1..M4 (M3 con un residuo sin desglose)."""
    rng = np.random.default_rng(semilla)
    idx = pd.period_range("2002-01", periods=n, freq="M")
    h = {k: pd.Series(rng.uniform(100, 1000, n).round(), index=idx) for k in
         ("moneda", "depositos_vista", "depositos_plazo", "letras_financieras", "letras_credito",
          "otros_titulos_privados", "ahorro", "fondos_monetarios", "compromisadas_privados", "titulos_federales")}
    h["m1"] = h["moneda"] + h["depositos_vista"]
    h["titulos_privados"] = sum(h[k] for k in F.PARTES["titulos_privados"])
    h["m2"] = h["m1"] + h["titulos_privados"] + h["ahorro"]
    h["m3"] = h["m2"] + h["fondos_monetarios"] + h["compromisadas_privados"] + residuo_m3
    h["m4"] = h["m3"] + h["titulos_federales"]
    return {F.SG.CODIGOS[clave]: h[serie] for serie, clave in F.COMPONENTES.items()}


def _piv(df, medida):
    return df[df.medida == medida].pivot(index="fecha", columns="serie", values="valor")


def _comprobar_cuadres(df, tol):
    s = _piv(df, "saldo")
    for agregado, partes in F.PARTES.items():
        d = s[partes].sum(axis=1) - s[agregado]
        assert d.abs().max() <= tol, (agregado, d.abs().max())
    d = s[F.HOJAS_M2].sum(axis=1) - s["m2"]
    assert d.abs().max() <= tol, ("hojas de M2", d.abs().max())


def _comprobar_participaciones(df):
    for medida, hojas in (("share_m2", F.HOJAS_M2), ("share_m4", F.HOJAS_M4)):
        p = _piv(df, medida)
        assert set(p.columns) == set(hojas), medida
        assert (p.sum(axis=1) - 1).abs().max() < 1e-9, medida
        assert (p >= 0).all().all(), medida


# --- unitarias -----------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sintetico():
    datos = _sinteticas()
    return F.construir_sgs(leer=lambda c: datos[c], existe=lambda c: False)


def test_unidades_r_mil_a_millones(sintetico):
    datos = _sinteticas()
    s = _piv(sintetico, "saldo")
    assert (s["ahorro"].to_numpy() - datos[F.SG.CODIGOS["mp_ahorro"]].to_numpy() / 1e3).max() < TOL
    assert (s["m2"].to_numpy() - datos[F.SG.CODIGOS["mp_m2"]].to_numpy() / 1e3).max() < TOL


def test_componentes_cuadran_con_los_agregados(sintetico):
    _comprobar_cuadres(sintetico, TOL)
    assert (_piv(sintetico, "saldo")[F.RESTO_M3] - 0.005).abs().max() < TOL      # 5 R$ mil = 0,005 R$ millones


def test_participaciones_suman_uno(sintetico):
    _comprobar_participaciones(sintetico)


def test_aa_a_mano(sintetico):
    s = _piv(sintetico, "saldo")["m2"]
    aa = _piv(sintetico, "aa")["m2"].reindex(s.index)
    assert aa.iloc[:12].isna().all() and aa.iloc[12:].notna().all()
    assert aa.iloc[12] == pytest.approx(s.iloc[12] / s.iloc[0] - 1)


def test_tasas_solo_si_hay_crudo():
    datos = _sinteticas()
    tasa = pd.Series(12.5, index=pd.period_range("2020-01", periods=6, freq="M"))
    df = F.construir_sgs(leer=lambda c: tasa if c == 28583 else datos[c], existe=lambda c: c == 28583)
    t = df[df.medida == "tasa"]
    assert set(t.serie) == {"tasa_plazo_personas"}
    assert t.valor.eq(0.125).all()
    assert not F.construir_sgs(leer=lambda c: datos[c], existe=lambda c: False).medida.eq("tasa").any()


# --- integración ---------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def gold():
    return pd.read_parquet(GOLD / "bk_fondeo_m.parquet")


@pytest.mark.integracion
def test_gold_componentes_cuadran(gold):
    _comprobar_cuadres(gold, TOL_REDONDEO)


@pytest.mark.integracion
def test_gold_participaciones_suman_100(gold):
    _comprobar_participaciones(gold)


@pytest.mark.integracion
def test_gold_poupanca_en_r_mil(gold):
    # 1835 en R$ mil: saldo del orden de R$ 1 billón (10^6 R$ millones) desde 2020; si viniera en R$ sería 10^3 menor
    s = _piv(gold, "saldo")["ahorro"]
    assert s.loc["2020-01-31":].between(5e5, 2e6).all()
    assert (_piv(gold, "share_m2")["ahorro"].loc["2020-01-31":].between(0.08, 0.35)).all()


def test_flujo_mensual_suma_dias_y_descarta_mes_incompleto():
    idx = pd.to_datetime(["2026-07-01", "2026-07-31", "2026-08-03", "2026-08-31", "2026-09-01", "2026-09-15"])
    m = F.flujo_mensual(pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], index=idx))
    assert list(m.index.astype(str)) == ["2026-07", "2026-08"]      # septiembre llega al 15: fuera
    assert list(m) == [3.0, 7.0]
