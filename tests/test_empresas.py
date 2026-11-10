# -*- coding: utf-8 -*-
"""Hojas de empresas MPME y Grandes (pipeline/preparar_gold_bancos_empresas.py, frente 13).

Las unitarias usan un cubo SCR sintético y series SGS sintéticas. Las marcadas `integracion` leen datos/gold.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import preparar_gold_bancos_empresas as E
from conftest import GOLD

TOL = 1e-6


def _mensual(valores, inicio="2020-01"):
    return pd.Series(np.asarray(valores, dtype=float), index=pd.period_range(inicio, periods=len(valores), freq="M"))


# --- unitarias: SGS ------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sgs_sintetico():
    rng = np.random.default_rng(7)
    cache = {}

    def leer(codigo):
        if codigo not in cache:
            cache[codigo] = _mensual(rng.uniform(1, 100, 30))
        return cache[codigo]
    return E.construir_sgs(leer)


def _piv_sgs(df, segmento):
    x = df[df.segmento == segmento]
    return x.pivot_table(index="fecha", columns=["sub", "medida"], values="valor")


def _comprobar_sgs(df):
    p = df[(df.segmento.isin(["mpme", "grandes"])) & (df.medida == "peso")].pivot(index="fecha", columns="segmento",
                                                                                   values="valor")
    assert (p.sum(axis=1) - 1).abs().max() < TOL
    piv = _piv_sgs(df, "modalidad")
    suma = sum(piv[(m, "efecto_tasa")] for m in E.DESCOMPONER) + piv[("media", "efecto_mezcla")]
    assert (suma - piv[("media", "d_tasa_media")]).dropna().abs().max() < TOL
    pc = sum(piv[(m, "peso_saldo")] for m in E.DESCOMPONER)
    assert (pc - 1).dropna().abs().max() < TOL


def test_sgs_pesos_y_descomposicion(sgs_sintetico):
    _comprobar_sgs(sgs_sintetico)
    # las tasas y moras se guardan en fracción
    x = sgs_sintetico[(sgs_sintetico.segmento == "empresas") & (sgs_sintetico.medida == "tasa")]
    assert x.valor.max() <= 1


def test_sgs_direccionados_y_saldos_reutilizados():
    assert "direccionado" not in E.SEGMENTOS_SGS["modalidad"]
    assert E.SEGMENTOS_SGS["empresas"]["direccionados"]["saldo"] == "credito_pj_direccionado"
    assert E.SEGMENTOS_SGS["modalidad"]["bndes"]["saldo"] == "credito_pj_bndes"
    for m in E.DESCOMPONER:
        assert {"tasa", "saldo"} <= set(E.SEGMENTOS_SGS["modalidad"][m])


# --- unitarias: SCR ------------------------------------------------------------------------------------------------

def _cubo_sintetico(meses=26, semilla=5):
    rng = np.random.default_rng(semilla)
    filas = []
    for i, mes in enumerate(pd.period_range("2018-01", periods=meses, freq="M")):
        for porte in ["Micro", "Pequeno", "Médio", "Grande", "Indisponível"]:
            for seg in ["Banco", "Cooperativa", "Desenvolvimento/Fomento"]:
                for cnae in ["Indústrias de transformação", "Construção", "Outra cosa"]:
                    if seg == "Cooperativa" and cnae == "Construção" and i < 14:     # celda nueva a mitad de la historia
                        continue
                    cart = rng.uniform(50, 150)
                    filas.append(dict(fecha=mes.to_timestamp(), cliente="PJ", segmento=seg, porte=porte,
                                      cnae_ocupacao=cnae, producto="Otros", carteira_ativa=cart,
                                      carteira_inadimplencia=cart * rng.uniform(0, 0.2),
                                      vencido_de_15_ate_90_dias=cart * rng.uniform(0, 0.1),
                                      ativo_problematico=cart * rng.uniform(0, 0.3),
                                      ops=int(rng.integers(1, 20)), cart_ops=cart))
    # una fila PF que debe ignorarse
    filas.append(dict(filas[0], cliente="PF", carteira_ativa=1e12))
    return pd.DataFrame(filas)


@pytest.fixture(scope="module")
def scr_sintetico():
    meses = pd.period_range("2017-01", "2020-12", freq="M")
    return E.construir_scr(_cubo_sintetico(), pd.Series(1.0, index=meses))


def _piv(df, dimension, medida):
    x = df[(df.dimension == dimension) & (df.medida == medida)]
    return x.pivot(index="fecha", columns="segmento", values="valor")


def _total(df, medida):
    return df[(df.dimension == "total") & (df.medida == medida)].set_index("fecha")["valor"]


def _comprobar_hoja(df, hoja):
    _, dims, (a, b) = E.HOJAS[hoja]
    sa = _total(df, "saldo_aa")
    for dim in dims:
        assert (_piv(df, dim, "aporte_crec").sum(axis=1) - sa).dropna().abs().max() < TOL, dim
        for nombre, num in (("mora", "tasa_mora"), ("atraso", "tasa_atraso")):
            nivel = _total(df, num)
            var = (nivel - nivel.shift(12)).dropna()
            ap = _piv(df, dim, f"aporte_{nombre}").sum(axis=1).reindex(var.index)
            assert (ap - var).abs().max() < TOL, (dim, nombre)
            ef = (_piv(df, dim, f"efecto_tasa_{nombre}").sum(axis=1)
                  + _piv(df, dim, f"efecto_mezcla_{nombre}").sum(axis=1)).reindex(var.index)
            assert (ef - var).abs().max() < TOL, (dim, nombre)
    for dim in dims + [f"{a}_{b}"]:
        assert (_piv(df, dim, "peso").sum(axis=1) - 1).abs().max() < TOL, dim
    for dim in (f"descomp_{a}_primero", f"descomp_{b}_primero"):
        for nombre in ("mora", "atraso"):
            x = df[(df.dimension == dim) & (df.medida == nombre)].pivot(index="fecha", columns="segmento",
                                                                        values="valor")
            assert set(x.columns) == {"efecto_tasa", f"mezcla_{a}", f"mezcla_{b}", "variacion_total"}
            assert (x.drop(columns="variacion_total").sum(axis=1) - x["variacion_total"]).abs().max() < TOL
    # los dos órdenes comparten el efecto tasa y la variación total
    e1 = df[(df.dimension == f"descomp_{a}_primero") & (df.segmento == "efecto_tasa")].valor.to_numpy()
    e2 = df[(df.dimension == f"descomp_{b}_primero") & (df.segmento == "efecto_tasa")].valor.to_numpy()
    assert np.allclose(e1, e2)
    tk = _total(df, "ticket")
    assert (tk - _total(df, "cart_ops") / _total(df, "ops")).abs().max() < TOL


@pytest.mark.parametrize("hoja", list(E.HOJAS))
def test_scr_identidades_por_hoja(scr_sintetico, hoja):
    _comprobar_hoja(scr_sintetico[scr_sintetico.hoja == hoja], hoja)


def test_scr_portes_de_cada_hoja(scr_sintetico):
    mp = scr_sintetico[(scr_sintetico.hoja == "mpme") & (scr_sintetico.dimension == "porte")]
    assert set(mp.segmento) == {"Micro", "Pequeña", "Mediana"}
    gr = scr_sintetico[scr_sintetico.hoja == "grandes"]
    assert "porte" not in set(gr.dimension)
    # sin año anterior no hay descomposición
    assert scr_sintetico[scr_sintetico.dimension == "descomp_porte_primero"].fecha.min() == "2019-01-31"
    # «Outra cosa» va a «Otros sectores»; la fila PF no entra (el total es del orden del cubo sintético)
    assert E.OTROS_SECTORES in set(scr_sintetico[scr_sintetico.dimension == "sector"].segmento)
    assert _total(scr_sintetico[scr_sintetico.hoja == "mpme"], "saldo").max() < 1e6


# --- integración ---------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def gold_sgs():
    return pd.read_parquet(GOLD / "bk_empresas_m.parquet")


@pytest.fixture(scope="module")
def gold_scr():
    return pd.read_parquet(GOLD / "bk_empresas_scr_m.parquet")


@pytest.mark.integracion
def test_gold_scr_identidades(gold_scr):
    assert set(gold_scr.hoja) == set(E.HOJAS)
    for hoja, df in gold_scr.groupby("hoja"):
        _comprobar_hoja(df, hoja)


@pytest.mark.integracion
def test_gold_sgs_identidades(gold_sgs):
    _comprobar_sgs(gold_sgs)
    v = gold_sgs.set_index(["segmento", "sub", "medida", "fecha"])["valor"]
    # E–H por porte termina en dic-24 (serie desactivada); la 4.966 empieza en ene-25
    eh = v.xs(("mpme", "total", "riesgo_eh"), level=["segmento", "sub", "medida"])
    r4 = v.xs(("mpme", "total", "riesgo_4966"), level=["segmento", "sub", "medida"])
    assert eh.index.max() <= "2024-12-31" < r4.index.min()
    # libres + direccionados = total de empresas (± 2 R$ millones por redondeo)
    s = lambda sub: v.xs(("empresas", sub, "saldo"), level=["segmento", "sub", "medida"])
    assert (s("libres") + s("direccionados") - s("total")).dropna().abs().max() <= 2
