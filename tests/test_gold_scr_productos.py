"""Invariantes del gold del SCR por producto (preparar_gold_bancos_scr_productos.py).

Las sumas de shares y del mix ya las exige el propio preparador al escribir (`verificar()`); aquí quedan
los cruces que el preparador no hace.
"""
import pandas as pd
import pytest

import periodos
from conftest import GOLD

T, SCR = GOLD / "bk_scr_tablas.parquet", GOLD / "bk_scr.parquet"
pytestmark = pytest.mark.integracion


@pytest.fixture(scope="module")
def t():
    return pd.read_parquet(T)


def test_productos_suman_el_total_personas(t):
    tot = t[(t.bloque == "saldo") & t.destacar].set_index("producto")["ultimo"]
    productos = tot.drop("Total personas")
    otros = t[(t.bloque == "cartera_mod") & (t.fila == "Otros")]["ultimo"].iloc[0]
    assert abs(productos.sum() + otros - tot["Total personas"]) < 1e-6


def test_tasas_en_rango(t):
    tasas = t[t.unidad_ultimo == "pct"]["ultimo"].dropna()
    assert ((tasas >= 0) & (tasas <= 1)).all()


def test_total_personas_calza_con_bk_scr(t):
    """El total PF del cubo por producto es el mismo saldo PF del corte por segmento de bk_scr."""
    scr = pd.read_parquet(SCR)
    pf = scr[(scr["corte"] == "segmento_cliente") & (scr["cliente"] == "PF")]
    ult = pf["fecha"].max()
    total_scr = pf[pf["fecha"] == ult]["carteira_ativa"].sum() / 1e9
    fila = t[(t.bloque == "saldo") & (t.producto == "Total personas") & t.destacar].iloc[0]
    assert fila["corte"] == periodos.mes_corto(ult.to_period("M")),         "bk_scr y bk_scr_tablas tienen distinto último mes: correr actualizar.py (paso scr)"
    assert abs(fila["ultimo"] - total_scr) / total_scr < 1e-6
