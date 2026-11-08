"""Rutas de importación de los tests y marca de integración.

pipeline/ y herramientas/ no son paquetes: se importan sus módulos por nombre, como al correrlos.
Las pruebas marcadas `integracion` leen datos/ (fuera de git) y se omiten si no está.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
GOLD = DATOS / "gold"

for carpeta in ("pipeline", "herramientas"):
    sys.path.insert(0, str(RAIZ / carpeta))



def pytest_collection_modifyitems(config, items):
    if GOLD.exists():
        return
    saltar = pytest.mark.skip(reason="no hay datos/gold: se omiten las pruebas de integración")
    for item in items:
        if "integracion" in item.keywords:
            item.add_marker(saltar)


@pytest.fixture(scope="session")
def ultimo_periodo() -> str:
    """Último trimestre AAAAMM del panel, tomado de los datos (no de un literal que envejece)."""
    return str(pd.read_parquet(GOLD / "bank_periodos.parquet", columns=["periodo"])["periodo"].astype(str).max())

