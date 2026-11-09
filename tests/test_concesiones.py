# -*- coding: utf-8 -*-
"""Concesiones libre / dirigido e índice frente al IBC-Br (pipeline/preparar_gold_bancos_concesiones.py).

Las unitarias usan series sintéticas mensuales con índice Period (cálculos a mano). Las marcadas `integracion` leen
datos/gold y se omiten si no está.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import preparar_gold_bancos_concesiones as C
import sgs as SG
import tabla_estandar as T
from conftest import GOLD


def _mensual(valores, inicio="2013-01"):
    return pd.Series(np.asarray(valores, dtype=float),
                     index=pd.period_range(inicio, periods=len(valores), freq="M"))


# --- unitarias ---------------------------------------------------------------------------------------------------

def test_deflactor_encadena_la_variacion_mensual_y_normaliza_al_ultimo_mes():
    ipca = _mensual([10.0, 10.0, 0.0])           # % mensual: índice 1,10 · 1,21 · 1,21
    d = SG.deflactor(ipca)                        # normalizado al último mes (1,21 → 1)
    assert d.iloc[-1] == pytest.approx(1.0)
    assert d.iloc[1] == pytest.approx(1.0)       # el mes sin inflación no cambia el índice
    assert d.iloc[0] == pytest.approx(1.10 / 1.21)


def test_segmentos_dirigido_es_total_menos_libre_y_las_partes_suman():
    s = {"total": _mensual([100.0, 110.0]), "pf": _mensual([40.0, 45.0]), "pj": _mensual([60.0, 65.0]),
         "li": _mensual([70.0, 80.0]), "pjli": _mensual([35.0, 40.0]), "pfli": _mensual([35.0, 40.0])}
    seg = C.segmentos(s)
    assert seg["di"].tolist() == [30.0, 30.0]                       # total − libre
    assert seg["li"].add(seg["di"]).tolist() == seg["tot"].tolist()  # libre + dirigido = total
    assert seg["pfdi"].tolist() == [5.0, 5.0] and seg["pjdi"].tolist() == [25.0, 25.0]
    assert seg["pfli"].add(seg["pjli"]).tolist() == seg["li"].tolist()


def test_deflactar_divide_cada_mes_por_su_indice():
    nominal = _mensual([100.0, 100.0])
    d = _mensual([1.0, 0.5])
    assert C.deflactar(nominal, d).tolist() == pytest.approx([100.0, 200.0])


def test_suma_movil_de_doce_meses_y_vacio_con_huecos():
    x = _mensual(np.ones(14))
    m = C.suma_movil(x)
    assert m.iloc[:11].isna().all() and m.iloc[11] == 12 and m.iloc[-1] == 12
    hueco = x.copy()
    hueco.iloc[3] = np.nan                        # cualquier ventana que cubra el hueco queda vacía
    assert C.suma_movil(hueco).iloc[11:].isna().all()


def test_indice_vale_100_en_el_promedio_de_2014():
    meses = pd.period_range("2013-01", "2015-12", freq="M")
    real = pd.Series(np.linspace(100, 200, len(meses)), index=meses)
    ibc = pd.Series(np.full(len(meses), 50.0), index=meses)
    i = C.indice_real(real, ibc)
    assert i[i.index.year == 2014].mean() == pytest.approx(100.0)
    assert i.iloc[-1] == pytest.approx(100 * (real.iloc[-1] / 50) / (real[real.index.year == 2014] / 50).mean())


def test_indice_falla_si_al_año_base_le_faltan_meses():
    meses = pd.period_range("2013-01", "2015-12", freq="M")
    real = pd.Series(np.ones(len(meses)), index=meses)
    real.loc[pd.Period("2014-06", "M")] = np.nan
    with pytest.raises(ValueError, match="12 meses de 2014"):
        C.indice_real(real, pd.Series(np.ones(len(meses)), index=meses))


def test_zscore_usa_los_120_meses_que_terminan_en_t_con_desviacion_muestral():
    rng = np.random.default_rng(7)
    x = _mensual(rng.normal(100, 5, 130), inicio="2000-01")
    z = C.zscore(x)
    assert z.iloc[:119].isna().all() and z.iloc[119:].notna().all()
    ventana = x.iloc[-120:]
    esperado = (x.iloc[-1] - ventana.mean()) / ventana.std(ddof=1)
    assert z.iloc[-1] == pytest.approx(esperado)


def test_construir_tabla_mes_del_total_es_la_variacion_de_flujo_de_la_serie():
    n = 48                                       # 2012–2015: el año base 2014 con sus doce meses
    base = np.linspace(1000, 1500, n)
    s = {"total": _mensual(base, "2012-01"), "pf": _mensual(base * 0.4, "2012-01"),
         "pj": _mensual(base * 0.6, "2012-01"), "li": _mensual(base * 0.9, "2012-01"),
         "pjli": _mensual(base * 0.3, "2012-01"), "pfli": _mensual(base * 0.6, "2012-01"),
         "ibc": _mensual(np.linspace(100, 110, n), "2012-01")}
    deflactor = _mensual(np.ones(n), "2012-01")
    larga, tablas = C.construir(s, deflactor)
    tot = tablas[(tablas.bloque == "mes") & (tablas.fila == "Total")].iloc[0]
    v = T.variaciones_saldo(s["total"], flujo=True)
    for c in ("ultimo", "d1", "d3", "d12", "dventana"):
        ref = v["ultimo"] / 1e3 if c == "ultimo" else v[c]
        assert tot[c] == pytest.approx(ref)
    assert tot["share"] == pytest.approx(1.0)
    assert set(tablas.bloque) == {"mes", "12m", "indice"}
    assert len(tablas) == 27 and tablas.groupby("bloque").size().to_dict() == {"12m": 9, "indice": 9, "mes": 9}


# --- integración -------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def larga():
    return pd.read_parquet(GOLD / "bk_concesiones.parquet")


@pytest.fixture(scope="module")
def tablas():
    return pd.read_parquet(GOLD / "bk_concesiones_tablas.parquet")


@pytest.fixture(scope="module")
def cred():
    return pd.read_parquet(GOLD / "bk_cred_tablas.parquet")


@pytest.mark.integracion
def test_contrato_y_clave_unicas(larga, tablas):
    assert not larga.duplicated(["segmento", "fecha"]).any()
    assert not tablas.duplicated(["bloque", "orden"]).any()
    assert set(larga.segmento) == {"tot", "pf", "pj", "li", "di", "pfli", "pfdi", "pjli", "pjdi"}


@pytest.mark.integracion
def test_total_de_la_tabla_calza_con_concesiones_totales_de_bk_cred_tablas(tablas, cred):
    a = cred[cred.fila == "Concesiones totales"].iloc[0]
    b = tablas[(tablas.bloque == "mes") & (tablas.fila == "Total")].iloc[0]
    assert a["corte"] == b["corte"]
    for c in ("ultimo", "d1", "d3", "d12", "dventana"):
        assert b[c] == pytest.approx(a[c], abs=1e-9), c


@pytest.mark.integracion
def test_identidades_del_sgs_cuadran_con_redondeo_de_un_millon(larga):
    p = larga.pivot(index="fecha", columns="segmento", values="concesiones").dropna()
    # 20631 = 20632 (pj) + 20633 (pf); 20634 = 20635 (pjli) + 20662 (pfli). Las series vienen en R$ millones enteros.
    assert (p["tot"] - p["pf"] - p["pj"]).abs().max() <= 1
    assert (p["li"] - p["pfli"] - p["pjli"]).abs().max() <= 1
    assert (p["li"] + p["di"] - p["tot"]).abs().max() < 1e-9      # dirigido = total − libre, exacto por construcción


@pytest.mark.integracion
def test_indice_base_2014_y_z_solo_con_ventana_completa(larga):
    tot = larga[larga.segmento == "tot"]
    base = tot[tot["fecha"].str.startswith("2014")]["indice"]
    assert base.mean() == pytest.approx(100.0)
    con_indice = tot.dropna(subset=["indice"])
    assert con_indice["fecha"].max() < tot["fecha"].max()              # el IBC-Br va atrasado: sin índice del último mes
    primero = tot.dropna(subset=["indice_z120"]).iloc[0]["fecha"]
    primer_indice = con_indice.iloc[0]["fecha"]
    meses = (int(primero[:4]) - int(primer_indice[:4])) * 12 + int(primero[5:7]) - int(primer_indice[5:7])
    assert meses >= 119


@pytest.mark.integracion
def test_fechas_son_fin_de_mes_sin_huecos(larga):
    f = pd.to_datetime(larga["fecha"])
    assert f.dt.is_month_end.all()
    for _, g in larga.groupby("segmento"):
        ordinales = pd.to_datetime(g["fecha"]).dt.to_period("M").map(lambda m: m.ordinal)
        assert (ordinales.diff().dropna() == 1).all(), "hay meses faltantes o repetidos"
