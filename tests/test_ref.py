# -*- coding: utf-8 -*-
"""Pruebas de la fuente REF (Anexo Estatístico del BCB) y de bk_ref.

Las unitarias usan hojas sintéticas con las formas reales del anexo (encabezado de dos niveles con celdas combinadas,
fechas «Jun\\n2023» seguidas de «Jul», meses en inglés, columna «Observada» que no es una nota, tramos numéricos en la
primera columna). Las marcadas `integracion` leen datos/ y se omiten si no está.
"""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

import almacen as A
import ref as R
from conftest import GOLD

TITULO = ("Capítulo 1",)


def _hoja(*filas):
    return [TITULO, (), *filas]


@pytest.mark.parametrize("hoja,esperado", [
    ("Graf 1.2.2.16", "1.2.2.16"), ("Graf 1.2.2.21.a", "1.2.2.21.a"), ("Tab 1.2.4.1", "T1.2.4.1"),
    ("Gráf 1.2.1.10", "1.2.1.10"), ("Grafs 1.2.5.1 a 1.2.5.5", "1.2.5.1-1.2.5.5"),
])
def test_grafico_de_hoja(hoja, esperado):
    assert R.grafico_de_hoja(hoja) == esperado


def test_fechas_con_contexto_y_en_ingles():
    f = R._Fechas()
    assert [f.leer(x) for x in ["Jun\n2023", "Jul", "Dez", "Jan", "Feb"]] == \
        ["2023-06", "2023-07", "2023-12", "2024-01", "2024-02"]
    assert R._Fechas().leer(datetime(2026, 6, 1)) == "2026-06"
    assert R._Fechas().leer("2025-12") == "2025-12"
    assert R._Fechas().leer(202606) == "2026-06"
    assert R._Fechas().leer("Jul") is None                 # sin año de contexto no es fecha


def test_hoja_simple_con_unidad_y_columna_vacia():
    filas = _hoja(("Gráfico 1.2.2.21.a - Inadimplência",), ("Fonte: Banco Central do Brasil",), (),
                  (None, "%"), (None, "Observada", "Contrafactual"),
                  ("2022-12", 3.02, None), ("2023-01", 3.19, 3.0))
    df = R.leer_hoja(filas, "Graf 1.2.2.21.a", "202610", [])
    assert set(df["serie"]) == {"Observada", "Contrafactual"}     # «Observada» no se descarta como nota
    assert df["unidad"].iloc[0] == "%"
    assert len(df) == 3                                             # la celda vacía no genera fila
    assert df.loc[df["serie"] == "Contrafactual", "fecha_ref"].tolist() == ["2023-01"]


def test_encabezado_de_dos_niveles_con_celdas_combinadas():
    filas = _hoja(("Gráfico 1.2.2.17 – Ativos problemáticos – Por segmento",), ("Fonte: BCB",), (None, "%"),
                  (None, "Público", "Privado", None, "SNCC"),
                  (None, None, "S1", "Demais", None),
                  (datetime(2018, 12, 1), 5.6, 7.81, 6.98, 5.38))
    df = R.leer_hoja(filas, "Graf 1.2.2.17", "202610", [])
    assert df["serie"].tolist() == ["Público", "Privado | S1", "Privado | Demais", "SNCC"]
    assert df["fecha_ref"].unique().tolist() == ["2018-12"]


def test_hoja_por_categorias_con_tramos_numericos():
    filas = _hoja(("Gráfico 1.2.2.25 - AP coorte por CRI",), ("Fonte: BCB",), (),
                  ("Faixa de CRI", "Consignado", "Cartões (Esq.)"), (0, 2.54, 5.84), (1, 2.0, 12.27))
    df = R.leer_hoja(filas, "Graf 1.2.2.25", "202610", [])
    assert (df["tipo"] == "categorias").all() and df["fecha_ref"].isna().all()
    assert sorted(df["categoria"].unique()) == ["0", "1"]


def test_candidatas_de_la_edicion_siguiente():
    meses = {"primer_semestre": ["03", "04"], "segundo_semestre": ["09", "10"]}
    assert R.candidatas_siguientes("202605", meses) == ["202609", "202610"]
    assert R.candidatas_siguientes("202610", meses) == ["202703", "202704"]


# ---------------------------------------------------------------- integración

@pytest.fixture(scope="module")
def bk_ref():
    return pd.read_parquet(GOLD / "bk_ref.parquet")


@pytest.mark.integracion
def test_graficos_usados_existen_en_la_ultima_edicion(bk_ref):
    """Si el BCB renombra una hoja o una serie usada, falla aquí y no en una tarjeta vacía."""
    assert R.controlar_usados(bk_ref, []) == []


@pytest.mark.integracion
def test_clave_unica_y_ediciones_de_la_definicion(bk_ref):
    assert not bk_ref.duplicated(R.CLAVE).any()
    assert set(R.definicion()["ediciones"]) <= set(bk_ref["edicion"])


@pytest.mark.integracion
def test_1_2_2_16_calza_con_la_serie_propia_del_scr(bk_ref):
    """La página Mora replica el 1.2.2.16 con SCR.data: desde 2025 difiere en promedio menos de 0,1 pp."""
    ultima = bk_ref["edicion"].max()
    ref = bk_ref[(bk_ref["edicion"] == ultima) & (bk_ref["grafico"] == "1.2.2.16") & (bk_ref["serie"] == "Total")]
    propio = pd.read_parquet(GOLD / "bk_scr_series.parquet")
    propio = propio[propio["serie"] == "ap|Total personas"].copy()
    propio["fecha_ref"] = pd.to_datetime(propio["fecha"]).dt.strftime("%Y-%m")
    j = ref.merge(propio[["fecha_ref", "valor"]], on="fecha_ref", suffixes=("_ref", "_propio"))
    j = j[j["fecha_ref"] >= "2025-01"]
    assert len(j) >= 12
    assert (j["valor_ref"] - j["valor_propio"] * 100).abs().mean() < 0.1
