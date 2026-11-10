# -*- coding: utf-8 -*-
"""Hojas por producto de personas (pipeline/preparar_gold_bancos_producto_pf.py, frente 12).

Las unitarias usan un cubo SCR sintético y series SGS sintéticas. Las marcadas `integracion` leen datos/gold.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import preparar_gold_bancos_producto_pf as P
from conftest import GOLD

TOL = 1e-6


def _mensual(valores, inicio="2020-01"):
    return pd.Series(np.asarray(valores, dtype=float), index=pd.period_range(inicio, periods=len(valores), freq="M"))


# --- unitarias: SGS ------------------------------------------------------------------------------------------------

def test_descomponer_tasa_suma_la_variacion_de_la_tasa_media():
    n = 24
    rng = np.random.default_rng(1)
    tasas = {"a": _mensual(rng.uniform(1, 4, n)), "b": _mensual(rng.uniform(0.1, 0.5, n))}
    conc = {"a": _mensual(rng.uniform(10, 50, n)), "b": _mensual(rng.uniform(10, 50, n))}
    d = P.descomponer_tasa(tasas, conc)
    suma = d[("a", "efecto_tasa")] + d[("b", "efecto_tasa")] + d[("media", "efecto_mezcla")]
    assert (suma - d[("media", "d_tasa_media")]).dropna().abs().max() < TOL
    assert len(d[("media", "d_tasa_media")].dropna()) == n - 12
    assert ((d[("a", "peso_conc")] + d[("b", "peso_conc")]) - 1).abs().max() < TOL


def test_descomponer_tasa_a_mano():
    # mes 0: pesos 50/50, tasas 2 y 1 → media 1,5; mes 12: pesos 25/75, tasas 2 y 1 → media 1,25 (solo mezcla)
    tasas = {"a": _mensual([2.0] * 13), "b": _mensual([1.0] * 13)}
    conc = {"a": _mensual([1.0] + [1.0] * 11 + [1.0]), "b": _mensual([1.0] + [1.0] * 11 + [3.0])}
    d = P.descomponer_tasa(tasas, conc)
    assert d[("media", "d_tasa_media")].iloc[-1] == pytest.approx(-0.25)
    assert d[("a", "efecto_tasa")].iloc[-1] == pytest.approx(0.0)
    assert d[("media", "efecto_mezcla")].iloc[-1] == pytest.approx(-0.25)


def test_total_de_personal_no_suma_la_renegociacion():
    valores = {}

    def leer(codigo):
        valores.setdefault(codigo, _mensual(np.full(24, float(codigo % 997 + 10))))
        return valores[codigo]

    cods = P.SG.CODIGOS
    sub = P.PRODUCTOS_SGS["personal"]
    tot = P._serie(sub["total"]["saldo"], leer)
    esperado = leer(cods["credito_pf_personal"]) + leer(cods["credito_pf_cheque_especial"])
    assert (tot - esperado).abs().max() == 0
    assert "credito_pf_personal_renegociacion" not in sub["total"]["saldo"]


# --- unitarias: SCR ------------------------------------------------------------------------------------------------

def _cubo_sintetico(meses=26, semilla=3):
    rng = np.random.default_rng(semilla)
    filas = []
    for i, mes in enumerate(pd.period_range("2018-01", periods=meses, freq="M")):
        for porte in ["Até 1 salário mínimo", "Mais de 3 a 5 salários mínimos", "Indisponível"]:
            for seg in ["Banco", "Financeira", "Instituição de pagamento"]:
                for ocu in ["Autônomo", "Outros"]:
                    if seg == "Instituição de pagamento" and i < 14:      # celda nueva a mitad de la historia
                        continue
                    cart = rng.uniform(50, 150)
                    ops = int(rng.integers(1, 20))
                    filas.append(dict(fecha=mes.to_timestamp(), cliente="PF", segmento=seg, porte=porte,
                                      cnae_ocupacao=ocu, producto="Tarjeta", carteira_ativa=cart,
                                      carteira_inadimplencia=cart * rng.uniform(0, 0.2),
                                      vencido_de_15_ate_90_dias=cart * rng.uniform(0, 0.1),
                                      ativo_problematico=cart * rng.uniform(0, 0.3), ops=ops, cart_ops=cart))
    return pd.DataFrame(filas)


@pytest.fixture(scope="module")
def scr_sintetico():
    cubo = _cubo_sintetico()
    meses = pd.period_range("2017-01", "2020-12", freq="M")
    sm = pd.Series(1000.0, index=meses)
    defl = pd.Series(1.0, index=meses)
    c = P.preparar_cubo(cubo)
    return pd.concat(P.construir_producto_scr(c, sm, defl), ignore_index=True)


def _piv(df, dimension, medida):
    x = df[(df.dimension == dimension) & (df.medida == medida)]
    return x.pivot(index="fecha", columns="segmento", values="valor")


def _total(df, medida):
    return df[(df.dimension == "total") & (df.medida == medida)].set_index("fecha")["valor"]


def _comprobar_aportes(df):
    sa = _total(df, "saldo_aa")
    for dim in ("renta", "institucion", "ocupacion"):
        assert ((_piv(df, dim, "aporte_crec").sum(axis=1) - sa).dropna().abs().max()) < TOL
        for nombre, num in (("mora", "tasa_mora"), ("atraso", "tasa_atraso")):
            nivel = _total(df, num)
            var = (nivel - nivel.shift(12)).dropna()
            ap = _piv(df, dim, f"aporte_{nombre}").sum(axis=1).reindex(var.index)
            assert (ap - var).abs().max() < TOL, (dim, nombre)
            ef = (_piv(df, dim, f"efecto_tasa_{nombre}").sum(axis=1)
                  + _piv(df, dim, f"efecto_mezcla_{nombre}").sum(axis=1)).reindex(var.index)
            assert (ef - var).abs().max() < TOL, (dim, nombre)


def _comprobar_tres_partes(df):
    for dim in ("descomp_renta_primero", "descomp_institucion_primero"):
        for nombre in ("mora", "atraso"):
            x = df[(df.dimension == dim) & (df.medida == nombre)].pivot(index="fecha", columns="segmento", values="valor")
            partes = x.drop(columns="variacion_total").sum(axis=1)
            assert (partes - x["variacion_total"]).abs().max() < TOL, (dim, nombre)


def _comprobar_pesos_y_ticket(df):
    for dim in ("renta", "institucion", "ocupacion", "tope_3sm", "renta_institucion", "renta_ocupacion"):
        assert (_piv(df, dim, "peso").sum(axis=1) - 1).abs().max() < TOL, dim
    tk = _total(df, "ticket")
    assert (tk - _total(df, "cart_ops") / _total(df, "ops")).abs().max() < TOL


def test_scr_aportes_suman_el_total(scr_sintetico):
    _comprobar_aportes(scr_sintetico)


def test_scr_tres_partes_suman_la_variacion(scr_sintetico):
    _comprobar_tres_partes(scr_sintetico)
    # sin año anterior no hay descomposición (el borrador mostraba 0)
    x = scr_sintetico[scr_sintetico.dimension == "descomp_renta_primero"]
    assert x.fecha.min() == "2019-01-31"


def test_scr_pesos_suman_uno_y_ticket_total(scr_sintetico):
    _comprobar_pesos_y_ticket(scr_sintetico)


def test_scr_meses_de_renta_con_salario_minimo(scr_sintetico):
    df = scr_sintetico
    tk = df[(df.dimension == "renta") & (df.segmento == "Hasta 1 SM") & (df.medida == "ticket")].set_index("fecha")["valor"]
    mm = df[(df.dimension == "renta") & (df.segmento == "Hasta 1 SM") & (df.medida == "meses_renta_medio")].set_index("fecha")["valor"]
    assert (mm - tk / (1000 * 0.75)).abs().max() < TOL
    assert not ((df.medida == "meses_renta_medio") & (df.segmento == P.SIN_RENTA)).any()


# --- integración ---------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def gold_sgs():
    return pd.read_parquet(GOLD / "bk_producto_pf_m.parquet")


@pytest.fixture(scope="module")
def gold_scr():
    return pd.read_parquet(GOLD / "bk_producto_pf_scr_m.parquet")


@pytest.mark.integracion
def test_gold_scr_identidades_por_producto(gold_scr):
    assert set(gold_scr.producto) == set(P.PRODUCTOS_SCR)
    for _, df in gold_scr.groupby("producto"):
        _comprobar_aportes(df)
        _comprobar_tres_partes(df)
        _comprobar_pesos_y_ticket(df)


@pytest.mark.integracion
def test_gold_sgs_descomposicion_suma(gold_sgs):
    for producto, subs in P.DESCOMPONER.items():
        x = gold_sgs[gold_sgs.producto == producto]
        piv = x.pivot_table(index="fecha", columns=["sub", "medida"], values="valor")
        suma = sum(piv[(s, "efecto_tasa")] for s in subs) + piv[("media", "efecto_mezcla")]
        assert (suma - piv[("media", "d_tasa_media")]).dropna().abs().max() < TOL, producto


@pytest.mark.integracion
def test_gold_sgs_totales_cuadran(gold_sgs):
    v = gold_sgs.set_index(["producto", "sub", "medida", "fecha"])["valor"]

    def s(p, sub, m):
        return v.xs((p, sub, m), level=["producto", "sub", "medida"])
    # personal: total = personal (que ya incluye la renegociación) + sobregiro; la renegociación es parte del personal
    d = s("personal", "total", "saldo") - s("personal", "personal", "saldo") - s("personal", "sobregiro", "saldo")
    assert d.abs().max() == 0
    assert (s("personal", "renegociacion", "saldo") < s("personal", "personal", "saldo")).all()
    # planilla y tarjeta: las partes suman el total publicado (± 1 R$ millón por redondeo)
    for p, partes in (("planilla", ["privados", "publico", "inss"]), ("tarjeta", ["rotativo", "cuotas", "contado"])):
        for m in ("saldo", "concesiones"):
            d = sum(s(p, x, m) for x in partes) - s(p, "total", m)
            assert d.dropna().abs().max() <= 1, (p, m)
