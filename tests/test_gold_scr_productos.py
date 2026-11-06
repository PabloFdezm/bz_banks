"""Invariantes del gold del SCR por producto (preparar_gold_bancos_scr_productos.py)."""
from pathlib import Path

import pandas as pd
import pytest

GOLD = Path(__file__).resolve().parents[1] / "datos" / "gold"
T, S, SCR = GOLD / "bk_scr_tablas.parquet", GOLD / "bk_scr_series.parquet", GOLD / "bk_scr.parquet"
pytestmark = pytest.mark.skipif(not (T.exists() and S.exists()), reason="falta el gold del SCR por producto")


@pytest.fixture(scope="module")
def t():
    return pd.read_parquet(T)


@pytest.fixture(scope="module")
def s():
    return pd.read_parquet(S)


def test_shares_de_saldo_suman_uno(t):
    sal = t[(t.bloque == "saldo") & ~t.destacar]
    for prod, g in sal.groupby("producto"):
        assert abs(g["share"].sum() - 1) < 1e-9, prod


def test_productos_suman_el_total_personas(t):
    tot = t[(t.bloque == "saldo") & t.destacar].set_index("producto")["ultimo"]
    productos = tot.drop("Total personas")
    otros = t[(t.bloque == "cartera_mod") & (t.fila == "Otros")]["ultimo"].iloc[0]
    assert abs(productos.sum() + otros - tot["Total personas"]) < 1e-6


def test_mix_suma_cien(s):
    mx = s[s.serie.str.startswith("mix|") & ~s.serie.str.endswith("|Hasta 3 SM")].copy()
    mx["prod"] = mx.serie.str.split("|").str[1]
    assert ((mx.groupby(["prod", "fecha"])["valor"].sum() - 1).abs() < 1e-9).all()


def test_tasas_en_rango(t):
    tasas = t[t.unidad_ultimo == "pct"]["ultimo"].dropna()
    assert ((tasas >= 0) & (tasas <= 1)).all()


def test_total_personas_calza_con_bk_scr(t):
    """El total PF del cubo por producto es el mismo saldo PF del corte por segmento de bk_scr."""
    if not SCR.exists():
        pytest.skip("falta bk_scr")
    scr = pd.read_parquet(SCR)
    pf = scr[(scr["corte"] == "segmento_cliente") & (scr["cliente"] == "PF")]
    ult = pf["fecha"].max()
    total_scr = pf[pf["fecha"] == ult]["carteira_ativa"].sum() / 1e9
    fila = t[(t.bloque == "saldo") & (t.producto == "Total personas") & t.destacar].iloc[0]
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    if fila["corte"] != f"{meses[ult.month - 1]}-{str(ult.year)[2:]}":
        pytest.skip("bk_scr y el gold por producto tienen distinto último mes")
    assert abs(fila["ultimo"] - total_scr) / total_scr < 1e-6
