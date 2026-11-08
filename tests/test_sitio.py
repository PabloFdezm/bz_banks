# -*- coding: utf-8 -*-
"""El sitio repite nombres del gold y lee sus unidades: aquí se comprueba que coincidan con el pipeline.

Lee los módulos del sitio con herramientas/inventario_paginas.mjs (Node); sin Node, se omite.
"""
from __future__ import annotations

import json
import shutil
import subprocess

import pandas as pd
import pytest

import bancos as B
import manifiesto_gold as MG
from conftest import GOLD, RAIZ

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="sin Node no se pueden leer los módulos del sitio")


@pytest.fixture(scope="module")
def inventario() -> dict:
    salida = subprocess.run(["node", str(RAIZ / "herramientas" / "inventario_paginas.mjs")], capture_output=True,
                            text=True, encoding="utf-8", check=True).stdout
    return json.loads(salida)


def test_nombres_del_panel_iguales_al_pipeline(inventario):
    g = inventario["GOLD"]
    assert g["OPTICA_PANEL"] == B.OPTICA_PANEL
    assert g["OPTICA_MODELO"] == B.OPTICA_MODELO
    assert g["GRUPO_PANEL"] == B.TODOS
    assert g["INST_PANEL"] == B.CLAVE_PANEL
    assert g["ROTULO_PANEL"] == B.PANEL
    assert g["UNIVERSO_PANEL"] in {nombre for nombre, _, _ in MG.UNIVERSOS}


def test_modelos_de_negocio_y_sus_claves(inventario):
    g = inventario["GOLD"]
    modelos = next(grupos for oid, _, _, grupos in B.OPTICAS if oid == "modelo")
    assert set(g["GRUPOS"]) == {codigo for codigo, _ in modelos}
    claves = {f"modelo|{codigo}" for codigo, _ in modelos}
    assert set(g["INST_GRUPO"].values()) == claves


@pytest.mark.integracion
@pytest.mark.parametrize("tabla", ["bk_portada_tablas", "bk_cred_tablas", "bk_scr_tablas"])
def test_unidades_de_las_tablas_estandar_las_conoce_el_sitio(inventario, tabla):
    t = pd.read_parquet(GOLD / f"{tabla}.parquet", columns=["unidad_ultimo", "unidad_cambio"])
    usadas = set(t["unidad_ultimo"].dropna()) | set(t["unidad_cambio"].dropna())
    assert usadas <= set(inventario["NOMBRES_UNIDAD"]), usadas - set(inventario["NOMBRES_UNIDAD"])


def _node(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["node", *args], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")


def test_modulos_del_sitio_cargan_sin_dom():
    """Las herramientas importan los módulos en Node: si uno toca el DOM al importarse, dejan de funcionar."""
    r = _node("herramientas/inventario_paginas.mjs", "--sin-dom")
    assert r.returncode == 0, r.stdout + r.stderr


def test_paginas_coinciden_con_el_esqueleto():
    r = _node("herramientas/contar_tarjetas.mjs")
    assert r.returncode == 0, r.stdout + r.stderr
