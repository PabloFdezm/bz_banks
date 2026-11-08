# -*- coding: utf-8 -*-
"""Tests de preparar_gold_bancos_qcambio.py (encargo 78d), por su entrada pública `calcular`.

`calcular` devuelve el cambio del último trimestre del panel: cada regla de ruptura se prueba con un panel
sintético que termina en el trimestre que la regla afecta. Las pruebas sobre datos reales llevan la marca
`integracion`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import periodos
import preparar_gold_bancos_qcambio as Q
from conftest import GOLD as BANKS

GRILLA = ["202306", "202309", "202312", "202403", "202406", "202409", "202412", "202503", "202506", "202509"]


def _panel(valores: dict[str, list[float]], metrica: str, grilla=GRILLA) -> pd.DataFrame:
    filas = []
    for cod, serie in valores.items():
        for p, v in zip(grilla, serie):
            filas.append({"cod_inst": cod, "periodo": p, "fecha": p, "trimestre": p, "metrica": metrica, "valor": v})
    return pd.DataFrame(filas)


META = pd.DataFrame({
    "nombre": ["Retorno sobre PL (12m)", "Mora 15 a 90 dias", "Costo del riesgo"],
    "signo": ["mejora_sube", "mejora_baja", "mejora_baja"],
}, index=["roe_ttm", "npl15_total", "costo_riesgo_ttm"])
META.index.name = "metrica"

BANCO = pd.DataFrame({
    "cod_inst": ["C1", "C2"], "slug": ["uno", "dos"], "nombre_corto": ["Uno", "Dos"],
    "modelo": ["Grandes", "Digitales"],
})

C1 = [0.10, 0.11, 0.12, 0.11, 0.13, 0.14, 0.15, 0.20, 0.21, 0.22]
C2 = [0.30, 0.30, 0.29, 0.31, 0.31, 0.30, 0.33, 0.33, 0.32, 0.30]


def _cambio_al(hasta: str, quiebre: set[str] = frozenset()) -> dict[str, float]:
    """Cambio de roe_ttm de cada banco con el panel cortado en `hasta`."""
    n = GRILLA.index(hasta) + 1
    out = Q.calcular(_panel({"C1": C1[:n], "C2": C2[:n]}, "roe_ttm", GRILLA[:n]), META, BANCO, set(quiebre),
                     metricas=["roe_ttm"])
    assert (out["periodo"] == hasta).all()
    return dict(zip(out["cod_inst"], out["cambio"]))


def test_cambio_en_pp_y_vacio_al_tocar_2024T4():
    assert _cambio_al("202409")["C1"] == pytest.approx((0.14 - 0.13) * 100)
    assert all(pd.isna(v) for v in _cambio_al("202412").values())      # 2024-T3 → 2024-T4
    assert all(pd.isna(v) for v in _cambio_al("202503").values())      # 2024-T4 → 2025-T1
    assert _cambio_al("202506")["C1"] == pytest.approx((0.21 - 0.20) * 100)


def test_quiebre_2025_vacia_2025T2_solo_para_el_banco_con_quiebre():
    c = _cambio_al("202506", {"C2"})
    assert pd.isna(c["C2"])
    assert c["C1"] == pytest.approx((0.21 - 0.20) * 100)
    assert _cambio_al("202509", {"C2"})["C2"] == pytest.approx((0.30 - 0.32) * 100)


def test_calcular_z_sentido_y_rango_a_mano():
    out = Q.calcular(_panel({"C1": C1, "C2": C2}, "roe_ttm"), META, BANCO, set(), metricas=["roe_ttm"])
    # cambios a mano: quedan vacíos los de 2024-T3→2024-T4 y 2024-T4→2025-T1
    c = {}
    for cod, s in (("C1", C1), ("C2", C2)):
        c[cod] = [np.nan] + [(b - a) * 100 for a, b in zip(s, s[1:])]
        c[cod][GRILLA.index("202412")] = np.nan
        c[cod][GRILLA.index("202503")] = np.nan
    pool = np.array(c["C1"] + c["C2"], dtype=float)
    sd = pool[~np.isnan(pool)].std(ddof=1)
    fila = {r.cod_inst: r for r in out.itertuples()}
    assert fila["C1"].cambio == pytest.approx((0.22 - 0.21) * 100)
    assert fila["C2"].cambio == pytest.approx((0.30 - 0.32) * 100)
    assert fila["C1"].z == pytest.approx((0.22 - 0.21) * 100 / sd)
    assert fila["C2"].z == pytest.approx(-2.0 / sd)
    assert fila["C1"].sentido == "mejora" and fila["C2"].sentido == "deterioro"
    assert fila["C2"].rango == 1 and fila["C1"].rango == 2     # mayor |z| primero
    assert fila["C1"].unidad_cambio == "pp" and fila["C1"].periodo == "202509"


def test_sentido_sigue_el_signo_de_la_metrica():
    plano = [0.05] * len(GRILLA)
    panel = pd.concat([_panel({"C1": C1, "C2": plano}, "npl15_total")], ignore_index=True)
    out = Q.calcular(panel, META, BANCO, set(), metricas=["npl15_total"]).set_index("cod_inst")
    assert out.at["C1", "sentido"] == "deterioro"     # la mora sube y mejora_baja
    assert out.at["C2", "sentido"] == "neutro"        # sin cambio


def test_rango_deja_sin_rango_las_filas_sin_z():
    c2 = C2[:8] + [np.nan, C2[9]]          # sin valor en 202506: su cambio a 202509 queda vacío
    panel = _panel({"C1": C1, "C2": c2}, "npl15_total")
    out = Q.calcular(panel, META, BANCO, set(), metricas=["npl15_total"])
    sin = out[out["cod_inst"] == "C2"].iloc[0]
    assert pd.isna(sin["cambio"]) and pd.isna(sin["z"]) and pd.isna(sin["rango"]) and pd.isna(sin["sentido"])
    assert out[out["cod_inst"] == "C1"].iloc[0]["rango"] == 1


@pytest.fixture(scope="module")
def construido() -> pd.DataFrame:
    return Q.construir()


@pytest.mark.integracion
def test_real_cambio_coincide_con_d_tt_del_panel(construido, ultimo_periodo):
    """qcambio y bk_panel.d_tt salen de módulos distintos; fuera de las reglas de ruptura deben coincidir."""
    p = pd.read_parquet(BANKS / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "d_tt"])
    p = p[p["periodo"] == ultimo_periodo].assign(cod_inst=lambda d: d["cod_inst"].astype(str))
    comp = construido.merge(p, on=["cod_inst", "metrica"]).dropna(subset=["cambio", "d_tt"])
    assert len(comp) > 100
    assert np.allclose(comp["cambio"], comp["d_tt"], atol=1e-6)


@pytest.mark.integracion
def test_real_tres_filas_recalculadas_a_mano(construido, ultimo_periodo):
    out = construido
    antes_p = periodos.previo(ultimo_periodo)
    assert out["periodo"].unique().tolist() == [ultimo_periodo]
    assert out.duplicated(["cod_inst", "metrica"]).sum() == 0
    assert set(out["unidad_cambio"]) == {"pp"}
    assert set(out["sentido"].dropna()) <= {"mejora", "deterioro", "neutro"}
    p = pd.read_parquet(BANKS / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "valor"])
    p["cod_inst"] = p["cod_inst"].astype(str)
    for fila in out.dropna(subset=["cambio"]).sort_values("rango").head(3).itertuples():
        antes = p[(p.cod_inst == fila.cod_inst) & (p.metrica == fila.metrica) & (p.periodo == antes_p)]["valor"].iloc[0]
        ahora = p[(p.cod_inst == fila.cod_inst) & (p.metrica == fila.metrica) & (p.periodo == ultimo_periodo)]["valor"].iloc[0]
        assert fila.valor_antes == pytest.approx(antes)
        assert fila.valor_ahora == pytest.approx(ahora)
        assert fila.cambio == pytest.approx((ahora - antes) * 100)
