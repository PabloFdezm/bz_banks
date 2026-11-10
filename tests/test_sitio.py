"""Sitio (rediseño, desde el 10-nov-2026): hojas del canvas en diseno/canvas montadas por sitio/assets/v2.

Reemplaza a las pruebas del sitio anterior (inventario de páginas con Node), que se retiró junto con su código.
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess

import pytest

from conftest import RAIZ

CANVAS = RAIZ / "diseno" / "canvas"
CFG = json.loads((CANVAS / "paginas.json").read_text(encoding="utf-8"))


def _construir():
    spec = importlib.util.spec_from_file_location("construir_v2", RAIZ / "herramientas" / "construir_v2.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_cada_pagina_tiene_sus_hojas():
    rutas = [p["ruta"] for p in CFG["paginas"]]
    assert len(rutas) == len(set(rutas)), "rutas repetidas en paginas.json"
    for p in CFG["paginas"]:
        for h in p["hojas"]:
            assert (CANVAS / f"{h}.dc.html").exists(), f"falta diseno/canvas/{h}.dc.html ({p['ruta']})"
    for c in CFG["componentes"]:
        assert (CANVAS / f"{c}.dc.html").exists()


def test_las_hojas_del_repo_no_traen_datos():
    """Los datos van en sitio/data/v2; la hoja versionada lleva `const X = {};`."""
    for f in CANVAS.glob("*.dc.html"):
        for linea in f.read_text(encoding="utf-8").splitlines():
            if linea.lstrip().startswith("const X = {"):
                assert linea.lstrip().startswith("const X = {};"), f"{f.name} trae datos incrustados"


def test_modulo_y_parches_del_sitio():
    m = _construir()
    html = (CANVAS / "Tarjeta.dc.html").read_text(encoding="utf-8")
    js = m.modulo("Tarjeta", html, True)
    assert "registrar('Tarjeta', PLANTILLA, Component)" in js
    assert "const X = DATOS;" in js
    assert js.count("v2-excel") >= 2, "falta el botón Excel en tarjetas o en Agrandar"
    assert "etiquetasTodas: lab" in js and "nombre: s.nombre, todo: s.datos" in js
    assert not re.search(r"(?<!\\)`", js.split("const PLANTILLA = `", 1)[1].split("`;\n", 1)[0]), "comilla invertida sin escapar"


@pytest.mark.skipif(shutil.which("node") is None, reason="sin Node")
def test_javascript_del_sitio_compila():
    for f in ("dc.js", "sitio.js"):
        r = subprocess.run(["node", "--check", str(RAIZ / "sitio" / "assets" / "v2" / f)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr


def test_redirecciones_del_sitio_anterior():
    txt = (RAIZ / "sitio" / "_redirects").read_text(encoding="utf-8")
    rutas = {p["ruta"] for p in CFG["paginas"]}
    for linea in txt.splitlines():
        if not linea.strip() or linea.startswith("#"):
            continue
        _, destino, codigo = linea.split()
        assert codigo in ("301", "302")
        if destino != "/:splat":
            assert destino.strip("/") in rutas, f"redirección a una página que no existe: {destino}"
