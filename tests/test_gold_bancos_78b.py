# -*- coding: utf-8 -*-
"""Tests de la cartera post-MVP (encargo 78b): mix en 7 categorías y peso del dirigido aproximado.

Pruebas sintéticas (con el error a propósito que la comprobación debe detectar) y pruebas sobre los datos reales
de datos/gold, que se saltan mientras bk_cartera_mix7 no exista.
Correr: python3 -X utf8 -m pytest tests/test_gold_bancos_78b.py -q
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
import preparar_gold_bancos_cartera as G  # noqa: E402

BANKS = RAIZ / "datos" / "gold"
MIX = BANKS / "bk_cartera_mix7.parquet"
necesita_datos = pytest.mark.skipif(not MIX.exists(), reason="bk_cartera_mix7 todavía no existe en datos/gold")


def _cartera_sintetica(filas: list[tuple]) -> pd.DataFrame:
    """filas: (cod_inst, periodo, tipo, modalidad_id, saldo)."""
    df = pd.DataFrame(filas, columns=["cod_inst", "periodo", "tipo", "modalidad_id", "saldo"])
    df["fecha"] = pd.to_datetime(df["periodo"], format="%Y%m") + pd.offsets.MonthEnd(0)
    df["trimestre"] = df["periodo"].map(G._trimestre)
    return df


def test_mapeo_cubre_todas_las_modalidades_de_personas():
    defs = json.loads((RAIZ / "definiciones" / "bcb_ifdata__credito_modalidades.json").read_text(encoding="utf-8"))
    ids_pf = {m["id"] for m in defs["tipos"]["PF"]["modalidades"]}
    assert ids_pf == set(G.MIX7_PF), "toda modalidad de personas debe tener categoría de 7"
    assert set(G.MIX7_PF.values()) <= set(G.ETIQUETA_MIX7)
    # Empresas: todas van a PJ, incluida la rural de empresas, que también es dirigido.
    assert G.categoria_mix7("PJ", "pj_rural") == "PJ"
    assert "pj_rural" in G.DIRIGIDO and "pf_rural" in G.DIRIGIDO


def test_modalidad_desconocida_no_se_adivina():
    with pytest.raises(KeyError):
        G.categoria_mix7("PF", "pf_inventada")


def test_otros_personas_se_suma_a_personal():
    c = _cartera_sintetica([("A", "202506", "PF", "pf_personal", 60.0), ("A", "202506", "PF", "pf_otros", 40.0)])
    m = G.mix7(c)
    fila = m[(m.nivel == "banco") & (m.categoria == "personal")]
    assert len(fila) == 1 and fila["saldo"].iloc[0] == pytest.approx(100.0)
    assert fila["peso"].iloc[0] == pytest.approx(1.0)


def test_dirigido_aproximado_sintetico():
    # hipotecario PF 100 + infra PJ 100 = dirigido 200 de un total de 500 → 0,4.
    c = _cartera_sintetica([
        ("A", "202506", "PF", "pf_hipotecario", 100.0),
        ("A", "202506", "PF", "pf_tarjeta", 300.0),
        ("A", "202506", "PJ", "pj_infra", 100.0),
    ])
    m = G.mix7(c)
    b = m[(m.nivel == "banco") & (m.cod_inst == "A")]
    assert b["dirigido_peso"].dropna().eq(0.4).all()
    assert b["total"].eq(500.0).all()


def test_verificar_mix7_detecta_suma_de_peso_distinta_de_uno():
    c = _cartera_sintetica([("A", "202506", "PF", "pf_tarjeta", 300.0), ("A", "202506", "PF", "pf_consignado", 100.0)])
    m = G.mix7(c)
    assert G.verificar_mix7(m) == []
    roto = m.copy()
    roto.loc[roto["categoria"] == "tarjeta", "peso"] = 0.5  # rota a propósito
    errores = G.verificar_mix7(roto)
    assert any("Σ peso" in e for e in errores)


def test_verificar_mix7_detecta_saldo_distinto_del_panel():
    c = _cartera_sintetica([("A", "202506", "PF", "pf_tarjeta", 300.0)])
    m = G.mix7(c)
    panel = pd.DataFrame({"cod_inst": ["A"], "periodo": ["202506"], "valor": [999.0]})
    assert any("cartera_saldo" in e for e in G.verificar_mix7(m, panel))


def test_verificar_mix7_detecta_2024_t4():
    c = _cartera_sintetica([("A", "202412", "PF", "pf_tarjeta", 300.0)])
    assert any("2024-T4" in e for e in G.verificar_mix7(G.mix7(c)))


@necesita_datos
def test_datos_reales_suman_uno_y_cuadran_con_bk_panel():
    m = pd.read_parquet(MIX)
    assert (m["periodo"] != "202412").all()
    assert G.verificar_mix7(m, pd.read_parquet(BANKS / "bk_panel.parquet").query("metrica == 'cartera_saldo'")
                            [["cod_inst", "periodo", "valor"]]) == []
    dp = m["dirigido_peso"].dropna()
    assert ((dp >= 0) & (dp <= 1)).all()


@necesita_datos
def test_cifras_contrastadas_contra_bk_cartera():
    """Tres cifras recalculadas por otro camino (directo desde bk_cartera) contra bk_cartera_mix7."""
    c = pd.read_parquet(BANKS / "bk_cartera.parquet")
    m = pd.read_parquet(MIX)
    # 1) Panel, PJ, 2026-06: suma de todas las modalidades de empresas.
    esperado = c[(c.periodo == "202606") & (c.tipo == "PJ")]["saldo"].sum()
    obtenido = m[(m.nivel == "panel") & (m.periodo == "202606") & (m.categoria == "PJ")]["saldo"].iloc[0]
    assert obtenido == pytest.approx(esperado, rel=1e-12)
    # 2) Banco C0080075, 2026-06: dirigido aproximado = saldo de las cinco modalidades / total.
    d = c[(c.cod_inst == "C0080075") & (c.periodo == "202606")]
    esperado = d[d["modalidad_id"].isin(G.DIRIGIDO)]["saldo"].sum() / d["saldo"].sum()
    obtenido = m[(m.nivel == "banco") & (m.cod_inst == "C0080075") & (m.periodo == "202606")]["dirigido_peso"].iloc[0]
    assert obtenido == pytest.approx(esperado, rel=1e-12)
    # 3) Panel, 2026-06: peso de tarjeta igual a la suma de tarjetas / cartera total de Brasil del panel.
    esperado = c[(c.periodo == "202606") & (c.modalidad_id == "pf_tarjeta")]["saldo"].sum() / c[c.periodo == "202606"]["saldo"].sum()
    obtenido = m[(m.nivel == "panel") & (m.periodo == "202606") & (m.categoria == "tarjeta")]["peso"].iloc[0]
    assert obtenido == pytest.approx(esperado, rel=1e-12)


@necesita_datos
def test_grupo_dirigido_coincide_con_mix7():
    g = pd.read_parquet(BANKS / "bk_cartera_grupo.parquet")
    m = pd.read_parquet(MIX)
    a = g[(g.optica == "Total panel") & (g.periodo == "202606") & (g.modalidad_id == "total_total")]["dirigido_peso"].iloc[0]
    b = m[(m.nivel == "panel") & (m.periodo == "202606")]["dirigido_peso"].iloc[0]
    assert a == pytest.approx(b, rel=1e-12)
