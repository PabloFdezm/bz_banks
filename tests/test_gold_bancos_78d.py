# -*- coding: utf-8 -*-
"""Tests de preparar_gold_bancos_qcambio.py (encargo 78d).

Cada regla tiene un caso sintético pequeño. Las pruebas sobre datos reales se saltan si
datos/gold/bk_panel.parquet no existe.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import preparar_gold_bancos_qcambio as Q  # noqa: E402

BANKS = RAIZ / "datos" / "gold"
GRILLA = ["202306", "202309", "202312", "202403", "202406", "202409", "202412", "202503", "202506", "202509"]


def _wide(valores: dict[str, list[float]], grilla=GRILLA) -> pd.DataFrame:
    return pd.DataFrame(valores, index=grilla)


def _panel(valores: dict[str, list[float]], metrica: str, grilla=GRILLA) -> pd.DataFrame:
    filas = []
    for cod, serie in valores.items():
        for p, v in zip(grilla, serie):
            filas.append({"cod_inst": cod, "periodo": p, "fecha": p, "trimestre": Q._trimestre(p),
                          "metrica": metrica, "valor": v})
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


# --- reglas de cambio --------------------------------------------------------

def test_cambio_en_pp_y_vacio_al_tocar_2024T4():
    c = Q._cambios(_wide({"C1": C1}), set())
    assert c.loc["202312", "C1"] == pytest.approx((0.12 - 0.11) * 100)
    assert c.loc["202409", "C1"] == pytest.approx((0.14 - 0.13) * 100)
    assert c.loc["202412"].isna().all()      # 2024-T3 → 2024-T4
    assert c.loc["202503"].isna().all()      # 2024-T4 → 2025-T1
    assert c.loc["202506", "C1"] == pytest.approx((0.21 - 0.20) * 100)


def test_quiebre_2025_vacia_2025T1_y_el_siguiente_solo_para_quiebre():
    c = Q._cambios(_wide({"C1": C1, "C2": C2}), {"C2"})
    assert pd.isna(c.loc["202506", "C2"])     # 2025-T1 → 2025-T2 de un banco con quiebre
    assert pd.notna(c.loc["202506", "C1"])    # el banco sin quiebre no se toca
    assert pd.notna(c.loc["202509", "C2"])    # a partir de 2025-T2 el banco vuelve a tener cambio


def test_cambio_coincide_con_d_tt_fuera_de_reglas():
    # d_tt de bk_panel = (valor − valor_t1) × 100 en pp; donde ninguna regla aplica deben coincidir.
    c = Q._cambios(_wide({"C1": C1, "C2": C2}), set())
    d = pd.DataFrame({"C1": [np.nan] + [(b - a) * 100 for a, b in zip(C1, C1[1:])],
                      "C2": [np.nan] + [(b - a) * 100 for a, b in zip(C2, C2[1:])]}, index=GRILLA)
    ok = c.notna() & d.notna()
    mascara = ok.to_numpy()
    assert mascara.sum() > 10
    assert np.allclose(c.to_numpy()[mascara], d.to_numpy()[mascara], atol=1e-9)


# --- desvío, z, sentido, rango ----------------------------------------------

def test_desvio_muestral_pooled_sobre_cambios_no_vacios():
    c = Q._cambios(_wide({"C1": C1, "C2": C2}), set())
    v = c.loc[GRILLA].to_numpy().ravel()
    v = v[~np.isnan(v)]
    assert Q._desvio(c, GRILLA) == pytest.approx(v.std(ddof=1))


def test_desvio_respeta_la_ventana():
    c = Q._cambios(_wide({"C1": C1, "C2": C2}), set())
    ventana = GRILLA[-4:]
    v = c.loc[ventana].to_numpy().ravel()
    v = v[~np.isnan(v)]
    assert Q._desvio(c, ventana) == pytest.approx(v.std(ddof=1))


def test_calcular_z_sentido_y_rango_a_mano():
    panel = pd.concat([_panel({"C1": C1, "C2": C2}, "roe_ttm")], ignore_index=True)
    out = Q.calcular(panel, META, BANCO, set(), metricas=["roe_ttm"])
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


def test_sentido_segun_signo():
    assert Q._sentido(-1.0, "mejora_baja") == "mejora"
    assert Q._sentido(1.0, "mejora_sube") == "mejora"
    assert Q._sentido(1.0, "mejora_baja") == "deterioro"
    assert Q._sentido(0.5, "neutro") == "neutro"
    assert Q._sentido(0.0, "mejora_sube") == "neutro"
    assert Q._sentido(np.nan, "mejora_sube") is None


def test_rango_deja_sin_rango_las_filas_sin_z():
    c2 = C2[:8] + [np.nan, C2[9]]          # sin valor en 202506: su cambio a 202509 queda vacío
    panel = _panel({"C1": C1, "C2": c2}, "npl15_total")
    out = Q.calcular(panel, META, BANCO, set(), metricas=["npl15_total"])
    sin = out[out["cod_inst"] == "C2"].iloc[0]
    assert pd.isna(sin["cambio"]) and pd.isna(sin["z"]) and pd.isna(sin["rango"]) and sin["sentido"] is None
    assert out[out["cod_inst"] == "C1"].iloc[0]["rango"] == 1


# --- datos reales (se saltan si no hay bk_panel) --------------------------------

requiere_real = pytest.mark.skipif(not (BANKS / "bk_panel.parquet").exists(), reason="sin bk_panel")


@requiere_real
def test_real_cambio_coincide_con_d_tt_donde_no_aplica_regla():
    p = pd.read_parquet(BANKS / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "valor", "d_tt"])
    p = p[p["metrica"] == "roe_ttm"].copy()
    p["cod_inst"] = p["cod_inst"].astype(str)
    grilla = sorted(p["periodo"].unique())
    wide = p.set_index(["periodo", "cod_inst"])["valor"].unstack("cod_inst").reindex(grilla)
    c = Q._cambios(wide, set()).stack(dropna=False)
    d = p.set_index(["periodo", "cod_inst"])["d_tt"]
    d.index = d.index.set_levels(d.index.levels[1].astype(str), level=1)
    comp = pd.concat([c.rename("c"), d.rename("d")], axis=1).dropna()
    comp = comp[~comp.index.get_level_values(0).isin(["202412", "202503"])]
    assert len(comp) > 1000
    assert np.allclose(comp["c"], comp["d"], atol=1e-6)


@requiere_real
def test_real_tres_filas_recalculadas_a_mano():
    out = Q.construir()
    assert out["periodo"].unique().tolist() == ["202606"]
    assert out.duplicated(["cod_inst", "metrica"]).sum() == 0
    assert set(out["unidad_cambio"]) == {"pp"}
    assert set(out["sentido"].dropna()) <= {"mejora", "deterioro", "neutro"}
    p = pd.read_parquet(BANKS / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "valor"])
    p["cod_inst"] = p["cod_inst"].astype(str)
    for fila in out.dropna(subset=["cambio"]).sort_values("rango").head(3).itertuples():
        antes = p[(p.cod_inst == fila.cod_inst) & (p.metrica == fila.metrica) & (p.periodo == "202603")]["valor"].iloc[0]
        ahora = p[(p.cod_inst == fila.cod_inst) & (p.metrica == fila.metrica) & (p.periodo == "202606")]["valor"].iloc[0]
        assert fila.valor_antes == pytest.approx(antes)
        assert fila.valor_ahora == pytest.approx(ahora)
        assert fila.cambio == pytest.approx((ahora - antes) * 100)
