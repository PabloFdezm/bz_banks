# -*- coding: utf-8 -*-
"""Pruebas del encargo 78a (gold post-MVP, rentabilidad y variaciones).

Cubre: valor_tt con muestra constante, 2024-T4 y quiebre 2025; credito_real_aa (banco y grupo);
gasto_total_ttm e ingreso_total_ttm (identidad con eficiencia_ttm sobre los datos reales); y brecha de
bk_roe_arbol. Las pruebas sobre datos reales se saltan si la tabla o el archivo no existe.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import preparar_gold_bancos as G  # noqa: E402

BANKS = RAIZ / "datos" / "gold"


def _fb(filas: list[dict], columnas: list[str]) -> pd.DataFrame:
    """Base de agregación con las columnas de nivel t, t−1 y t−4 que usa _agregar."""
    df = pd.DataFrame([{c: f.get(c, np.nan) for c in columnas} for f in filas])
    return df


def test_periodo_previo_cruza_el_ano():
    assert G._periodo_previo("202409") == "202406"
    assert G._periodo_previo("202503") == "202412"
    assert G._periodo_previo("202506", 4) == "202406"


def test_mascara_tt_2024t4_y_quiebre():
    periodo = pd.Series(["202409", "202412", "202503", "202506", "202503"])
    cod = pd.Series(["A", "A", "A", "A", "B"])
    ok = G._mascara_tt(periodo, cod, {"B"})
    # 202409: ok. 202412: t es 2024-T4. 202503 de A: cruza 2024-T4. 202506 de A: ok.
    # 202503 de B: quiebre 2025 en 2025-T1 (y cruza 2024-T4).
    assert ok.tolist() == [True, False, False, True, False]


def test_mascara_tt_quiebre_solo_en_2025t1():
    periodo = pd.Series(["202506", "202503"])
    cod = pd.Series(["B", "B"])
    ok = G._mascara_tt(periodo, cod, {"B"})
    # 202506 de B vs 202503: no cruza 2025-T1, debe quedar válido.
    assert ok.tolist() == [True, False]


def test_agregar_ratio_tt_muestra_constante():
    # roe_ttm de grupo: Σ lucro / Σ PL medio. Banco B no tiene t−1, así que sale de ambos lados.
    cols = ["inst_key", "periodo", "roe_ttm", "lucro_liquido_ttm", "lucro_liquido_ttm__1", "lucro_liquido_ttm__4",
            "pl_medio_ttm", "pl_medio_ttm__1", "pl_medio_ttm__4"]
    fb = _fb([
        {"inst_key": "g", "periodo": "202309", "roe_ttm": 0.10, "lucro_liquido_ttm": 10, "lucro_liquido_ttm__1": 8,
         "pl_medio_ttm": 100, "pl_medio_ttm__1": 100, "pl_medio_ttm__4": 90, "lucro_liquido_ttm__4": 7},
        {"inst_key": "g", "periodo": "202309", "roe_ttm": 0.10, "lucro_liquido_ttm": 5, "lucro_liquido_ttm__1": np.nan,
         "pl_medio_ttm": 50, "pl_medio_ttm__1": np.nan, "pl_medio_ttm__4": 40, "lucro_liquido_ttm__4": 4},
    ], cols)
    res = G._agregar(fb, "roe_ttm", "ratio", "ratio")
    fila = res.iloc[0]
    # valor_tt solo con el banco A: 10/100 − 8/100 = 2 pp.
    assert fila["valor_tt"] == pytest.approx(2.0)
    # el nivel sí usa a los dos bancos: (10+5)/(100+50) = 10 %.
    assert fila["valor"] == pytest.approx(0.10)


def test_agregar_monto_tt_respeta_ok_tt():
    cols = ["inst_key", "periodo", "gasto_total_ttm", "gasto_total_ttm__1", "gasto_total_ttm__4"]
    fb = _fb([
        {"inst_key": "g", "periodo": "202503", "gasto_total_ttm": 200, "gasto_total_ttm__1": 100, "gasto_total_ttm__4": 150},
        {"inst_key": "g", "periodo": "202506", "gasto_total_ttm": 300, "gasto_total_ttm__1": 200, "gasto_total_ttm__4": 250},
    ], cols)
    ok = pd.Series([False, True])  # 202503 con quiebre: fuera de la variación
    res = G._agregar(fb, "gasto_total_ttm", "monto", "brl", ok).set_index("periodo")
    assert np.isnan(res.loc["202503", "valor_tt"])
    assert res.loc["202506", "valor_tt"] == pytest.approx(300 / 200 - 1)
    assert res.loc["202503", "valor"] == pytest.approx(200)


def test_real_desde_nominal():
    assert G._real_desde_nominal(0.10, 0.05) == pytest.approx(1.10 / 1.05 - 1)
    assert np.isnan(G._real_desde_nominal(np.nan, 0.05))


def test_ipca_ausente_deja_vacia(tmp_path, monkeypatch):
    ruta = tmp_path / "bk_sistema_q.parquet"
    pd.DataFrame({"fecha": pd.to_datetime(["2024-12-31"]), "serie_id": ["atraso15_90_pf"],
                  "valor": [0.06]}).to_parquet(ruta)
    monkeypatch.setattr(G, "ENTRADA_SISTEMA_Q", ruta)
    assert G._ipca_12m_trimestral().empty


def test_ipca_trimestral_toma_fin_de_trimestre(tmp_path, monkeypatch):
    ruta = tmp_path / "bk_sistema_q.parquet"
    pd.DataFrame({"fecha": pd.to_datetime(["2024-12-31", "2025-03-31", "2025-03-31"]),
                  "serie_id": ["ipca_12m", "ipca_12m", "atraso15_90_pf"],
                  "valor": [0.045, 0.05, 0.06]}).to_parquet(ruta)
    monkeypatch.setattr(G, "ENTRADA_SISTEMA_Q", ruta)
    ipca = G._ipca_12m_trimestral()
    assert ipca.to_dict() == {"202412": pytest.approx(0.045), "202503": pytest.approx(0.05)}


def test_credito_real_grupo_y_variaciones():
    # Crecimiento nominal del grupo (credito_aa de la pieza) y IPCA 12 m por trimestre.
    pieza = pd.DataFrame({
        "inst_key": ["g", "g", "g", "g"],
        "periodo": ["202309", "202312", "202409", "202412"],
        "valor": [0.10, 0.11, 0.12, 0.13],
    })
    ipca = pd.Series({"202309": 0.05, "202312": 0.04, "202409": 0.045, "202412": 0.04})
    fb = _fb([
        {"inst_key": "g", "periodo": p, "credito_real_aa": 0.01} for p in ["202309", "202312", "202409", "202412"]
    ], ["inst_key", "periodo", "credito_real_aa"])
    out = G._agregar_real(fb, pieza, ipca).set_index("periodo")
    assert out.loc["202309", "valor"] == pytest.approx(1.10 / 1.05 - 1)
    assert out.loc["202409", "valor"] == pytest.approx(1.12 / 1.045 - 1)
    # a/a en pp: 202409 contra 202309 (ambos fuera de 2024-T4).
    assert out.loc["202409", "valor_aa"] == pytest.approx((1.12 / 1.045 - 1 - (1.10 / 1.05 - 1)) * 100)
    # 202412 es 2024-T4: variaciones vacías.
    assert np.isnan(out.loc["202412", "valor_tt"])
    assert np.isnan(out.loc["202412", "valor_aa"])


def test_gasto_ingreso_reproduce_eficiencia():
    ruta = BANKS.parent.parent / "datos" / "intermedio" / "metricas_bancos.parquet"
    if not ruta.exists():
        pytest.skip("metricas_bancos.parquet no existe")
    m = pd.read_parquet(ruta)
    cods = sorted(m["cod_inst"].astype(str).unique())
    w, _ = G._cargar_ancho(cods)
    ok = w["ingreso_total_ttm"].gt(0) & w["eficiencia_ttm"].notna()
    ratio = w.loc[ok, "gasto_total_ttm"] / w.loc[ok, "ingreso_total_ttm"]
    assert len(ratio) > 0
    assert (ratio - w.loc[ok, "eficiencia_ttm"]).abs().max() <= 1e-9
    # Lo que tiene eficiencia debe tener también numerador y denominador.
    assert not (w["eficiencia_ttm"].notna() & w["ingreso_total_ttm"].isna()).any()


def test_brecha_es_valor_menos_mediana():
    ruta = BANKS / "bk_roe_arbol.parquet"
    if not ruta.exists():
        pytest.skip("bk_roe_arbol.parquet no existe")
    t = pd.read_parquet(ruta)
    if "brecha" not in t.columns:
        pytest.skip("bk_roe_arbol todavía sin columna brecha (correr rentabilidad)")
    ok = t["valor"].notna() & t["mediana_grupo"].notna()
    assert (t.loc[ok, "brecha"] - (t.loc[ok, "valor"] - t.loc[ok, "mediana_grupo"])).abs().max() <= 1e-12
    assert t.loc[~ok, "brecha"].isna().all()
