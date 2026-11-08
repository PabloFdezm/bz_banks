# -*- coding: utf-8 -*-
"""Tests del verificador read-only del pipeline de bancos.

No prueban la API: comprueban que el "dry run" que se corre antes de promover
un trimestre acepte los datos actuales y que sus detectores no sean decorativos.
"""
from __future__ import annotations

import pandas as pd
import pytest

import verificar_gold as V
from conftest import DATOS, GOLD


def _metricas(bancos=("C1", "C2"), periodos=("202603", "202606")) -> pd.DataFrame:
    """Tabla larga mínima con el contrato de metricas_bancos.parquet."""
    filas = [{"periodo": p, "fecha": pd.Period(p, "M").end_time.normalize(), "cod_inst": b,
              "nombre_corto": b, "categoria": "balance", "metrica": "ativo_total", "valor": 100.0}
             for b in bancos for p in periodos]
    return pd.DataFrame(filas, columns=V.COLUMNAS_METRICAS)


def test_detecta_duplicados():
    df = _metricas()
    r = V.verificar_metricas(pd.concat([df, df.iloc[[0]]], ignore_index=True))
    assert any("duplicadas" in e for e in r.errores), r.errores


def test_detecta_infinito():
    df = _metricas()
    df.loc[0, "valor"] = float("inf")
    r = V.verificar_metricas(df)
    assert any("no finitos" in e for e in r.errores), r.errores


def test_detecta_periodo_invalido():
    df = _metricas()
    df.loc[0, "periodo"] = "2026"
    r = V.verificar_metricas(df)
    assert any("períodos inválidos" in e for e in r.errores), r.errores


def test_comparar_detecta_banco_perdido():
    actual = _metricas()
    r = V.comparar_metricas(actual, actual[actual["cod_inst"] != "C2"])
    assert any("pierde bancos" in e for e in r.errores), r.errores


def test_comparar_acepta_trimestre_nuevo():
    actual = _metricas()
    candidato = pd.concat([actual, _metricas(periodos=("202609",))], ignore_index=True)
    r = V.comparar_metricas(actual, candidato)
    assert not r.errores, r.errores
    assert any("agrega períodos: 202609" in a for a in r.advertencias), r.advertencias


@pytest.mark.integracion
def test_datos_actuales_pasan_el_verificador(ultimo_periodo):
    r = V.verificar_todo()
    assert not r.errores, "\n".join(r.errores)
    assert r.resumen["bancos"] == len(pd.read_parquet(GOLD / "bk_banco.parquet", columns=["cod_inst"]))
    assert r.resumen["ultimo_periodo"] == ultimo_periodo
    assert r.resumen["credito_ultimo"] == ultimo_periodo
    assert r.resumen["validacion_filas"] >= 20


@pytest.mark.integracion
def test_sin_segmento_solo_si_la_fuente_no_lo_trae(ultimo_periodo):
    """Tarea 1.1: un banco va «Sin segmento» solo si ninguna fila de su conglomerado en el cadastro trae Sr.

    Daycoval y XP traen Sr nulo en la fila propia desde 2025-T4, pero sus instituciones sí lo traen.
    """
    banco = pd.read_parquet(GOLD / "bk_banco.parquet")
    cad = pd.read_parquet(DATOS / "crudo" / "bcb_ifdata" / "cadastro" / "actual" / f"cadastro_{ultimo_periodo}.parquet",
                          columns=["CodInst", "CodConglomeradoPrudencial", "Sr"])
    cad = cad[cad["Sr"].fillna("").str.strip().str.lower().ne("null") & cad["Sr"].fillna("").str.strip().ne("")]
    con_sr = set(cad["CodInst"]) | set(cad["CodConglomeradoPrudencial"])
    mal = banco.loc[banco["segmento_reg"].eq("Sin segmento") & banco["cod_inst"].isin(con_sr), "nombre_corto"].tolist()
    assert not mal, f"«Sin segmento» pero la fuente trae Sr: {mal}"


@pytest.mark.integracion
def test_panel_sin_valores_nulos():
    """Tarea 1.5: bk_panel no depende de la versión de pandas (stack() con o sin NaN)."""
    p = pd.read_parquet(GOLD / "bk_panel.parquet", columns=["valor"])
    assert p["valor"].notna().all()
