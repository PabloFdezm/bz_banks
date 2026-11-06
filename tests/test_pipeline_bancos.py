# -*- coding: utf-8 -*-
"""Tests del verificador read-only del pipeline de bancos.

No prueban la API: comprueban que el "dry run" que se corre antes de promover
un trimestre acepte los datos actuales y que sus detectores no sean decorativos.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "herramientas"))
import verificar_gold as V  # noqa: E402


def test_datos_actuales_pasan_el_verificador():
    r = V.verificar_todo()
    assert not r.errores, "\n".join(r.errores)
    assert r.resumen["bancos"] == 34
    assert r.resumen["ultimo_periodo"] == "202606"
    assert r.resumen["credito_ultimo"] == "202606"
    assert r.resumen["validacion_filas"] >= 20


def test_metricas_no_tienen_infinitos():
    """Un crecimiento con base cero debe ser NaN, no inf (rompe el JSON)."""
    df = pd.read_parquet(V.METRICAS)
    assert not df["valor"].isin([float("inf"), float("-inf")]).any()


def test_detecta_duplicados():
    df = pd.read_parquet(V.METRICAS)
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    r = V.verificar_metricas(df)
    assert any("duplicadas" in e for e in r.errores), r.errores


def test_detecta_infinito():
    df = pd.read_parquet(V.METRICAS).copy()
    df.loc[0, "valor"] = float("inf")
    r = V.verificar_metricas(df)
    assert any("no finitos" in e for e in r.errores), r.errores


def test_detecta_periodo_invalido():
    df = pd.read_parquet(V.METRICAS).copy()
    df.loc[0, "periodo"] = "2026"
    r = V.verificar_metricas(df)
    assert any("períodos inválidos" in e for e in r.errores), r.errores


def test_comparar_detecta_banco_perdido():
    actual = pd.read_parquet(V.METRICAS)
    candidato = actual[actual["cod_inst"] != "C0080075"].copy()
    r = V.comparar_metricas(actual, candidato)
    assert any("pierde bancos" in e for e in r.errores), r.errores


def test_comparar_acepta_trimestre_nuevo():
    actual = pd.read_parquet(V.METRICAS)
    nuevo = actual[actual["periodo"] == "202606"].copy()
    nuevo["periodo"] = "202609"
    candidato = pd.concat([actual, nuevo], ignore_index=True)
    r = V.comparar_metricas(actual, candidato)
    assert not r.errores, r.errores
    assert any("agrega períodos" in a for a in r.advertencias), r.advertencias


def test_sin_segmento_solo_si_la_fuente_no_lo_trae():
    """Tarea 1.1: un banco va «Sin segmento» solo si ninguna fila de su conglomerado en el cadastro trae Sr.

    Daycoval y XP traen Sr nulo en la fila propia desde 2025-T4, pero sus instituciones sí lo traen.
    """
    banco = pd.read_parquet(RAIZ / "datos" / "gold" / "bk_banco.parquet")
    periodo = pd.read_parquet(RAIZ / "datos" / "gold" / "bank_periodos.parquet")["periodo"].astype(str).max()
    cad = pd.read_parquet(RAIZ / "datos" / "crudo" / "bcb_ifdata" / "cadastro" / "actual" / f"cadastro_{periodo}.parquet",
                          columns=["CodInst", "CodConglomeradoPrudencial", "Sr"])
    cad = cad[cad["Sr"].fillna("").str.strip().str.lower().ne("null") & cad["Sr"].fillna("").str.strip().ne("")]
    con_sr = set(cad["CodInst"]) | set(cad["CodConglomeradoPrudencial"])
    mal = banco.loc[banco["segmento_reg"].eq("Sin segmento") & banco["cod_inst"].isin(con_sr), "nombre_corto"].tolist()
    assert not mal, f"«Sin segmento» pero la fuente trae Sr: {mal}"


def test_panel_sin_valores_nulos():
    """Tarea 1.5: bk_panel no depende de la versión de pandas (stack() con o sin NaN)."""
    p = pd.read_parquet(RAIZ / "datos" / "gold" / "bk_panel.parquet", columns=["valor"])
    assert p["valor"].notna().all()
