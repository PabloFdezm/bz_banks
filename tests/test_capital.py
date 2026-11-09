# -*- coding: utf-8 -*-
"""Pruebas de la fuente de capital (informe 5 de IF.Data) y de bk_capital / bk_capital_grupo.

Las unitarias son sintéticas y sin red: reproducen las trampas reales del informe 5 (letras que cambian por
época, el nombre sin salto de línea de 2023-03, filas triplicadas de 2025-09, coma decimal y «null»). Las
marcadas `integracion` leen datos/ y se omiten si no está.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

import almacen as A
import capital as C
from conftest import GOLD

DEFN = {"campos": {
    "capital_principal": {"nombre": "Capital Principal para Comparação com RWA", "conta": ["79645"]},
    "pr": {"nombre": "Patrimônio de Referência para Comparação com o RWA", "conta": ["79649"]},
    "rwa_total": {"nombre": "Ativos Ponderados pelo Risco (RWA)", "conta": ["79665"]},
    "indice_cp": {"nombre": "Índice de Capital Principal", "conta": ["79659"]},
}, "ignorar": ["RWAcam"]}

MINIMOS = {
    "minimos": [{"desde": "2019-01-01", "hasta": "", "cp": 0.045, "nivel1": 0.06, "pr": 0.08}],
    "conservacion": [{"desde": "2020-04-01", "hasta": "2021-03-31", "valor": 0.0125},
                     {"desde": "2022-04-01", "hasta": "", "valor": 0.025}],
    "contraciclico": [{"desde": "2016-01-01", "hasta": "", "valor": 0.0}],
    "sistemico": {"cronograma": [{"desde": "2019-01-01", "hasta": "", "valor": 0.01}],
                  "bancos": {"C0000001": {"desde": "2017-01-01"}}, "lista_completa": True},
}


@pytest.mark.parametrize("texto", [
    "Índice de Capital Principal \n(l) = (a) / (j)",      # desde 2023-12
    "Índice de Capital Principal \n(k) = (a) / (i)",      # hasta 2022-12
    "Índice de Capital Principal (k) = (a) / (i)",        # 2023-03 y 2023-06: sin salto de línea
])
def test_nombre_base_ignora_la_letra_de_la_epoca(texto):
    assert C.nombre_base(texto) == "indice de capital principal"


def test_nombre_base_no_corta_el_rwa_en_mayusculas():
    assert C.nombre_base("Ativos Ponderados pelo Risco (RWA) \n(j) = (f) + (g) + (h) + (i)") == \
        "ativos ponderados pelo risco (rwa)"
    assert C.nombre_base("RWA para Risco de Mercado \n(g) = (g1) + (g2)") == "rwa para risco de mercado"


def test_mapa_campos_rechaza_nombres_repetidos():
    defn = {"campos": {"a": {"nombre": "Capital Nível II \n(d)"}, "b": {"nombre": "Capital Nível II"}}}
    with pytest.raises(ValueError):
        C.mapa_campos(defn)


def _crudo(monkeypatch, filas):
    df = pd.DataFrame(filas, columns=C.COLUMNAS_CRUDO)
    monkeypatch.setattr(A, "existe_crudo", lambda ruta: True)
    monkeypatch.setattr(A, "leer_crudo_tabla", lambda ruta, columnas=None: df)


def test_leer_informe_deduplica_copias_identicas_y_lee_coma_decimal(monkeypatch):
    fila = ["C0000001", "79659", "Índice de Capital Principal \n(l) = (a) / (j)", "0,123087092655114"]
    _crudo(monkeypatch, [fila, fila, fila,
                         ["C0000001", "79645", "Capital Principal para Comparação com RWA \n(a)", "194741701271,11"],
                         ["C0000001", "1", "RWAcam \n(g1)", "1,0"],
                         ["C0000002", "79645", "Capital Principal para Comparação com RWA \n(a)", "null"]])
    avisos: list[str] = []
    t = C.leer_informe("202509", {"C0000001", "C0000002"}, C.mapa_campos(DEFN), DEFN, avisos).set_index("cod_inst")
    assert t.loc["C0000001", "indice_cp"] == pytest.approx(0.123087092655114)
    assert t.loc["C0000001", "capital_principal"] == pytest.approx(194741701271.11)
    assert pd.isna(t.loc["C0000002", "capital_principal"])           # «null» no es 0
    assert any("repetidas" in a for a in avisos)
    assert not any("sin mapear" in a for a in avisos)                # RWAcam está en «ignorar»


def test_leer_informe_falla_si_las_copias_difieren(monkeypatch):
    _crudo(monkeypatch, [["C0000001", "79659", "Índice de Capital Principal \n(l)", "0,12"],
                         ["C0000001", "79659", "Índice de Capital Principal \n(l)", "0,13"]])
    with pytest.raises(ValueError):
        C.leer_informe("202509", {"C0000001"}, C.mapa_campos(DEFN), DEFN, [])


def test_vigencia_por_fecha():
    cons = MINIMOS["conservacion"]
    assert C.vigente(cons, date(2020, 6, 30)) == 0.0125
    assert C.vigente(cons, date(2021, 6, 30)) is None           # tramo sin fila: no se inventa
    assert C.vigente(cons, date(2026, 6, 30)) == 0.025


def test_sistemico_por_banco():
    assert C.sistemico(MINIMOS, "C0000001", date(2026, 6, 30)) == 0.01
    assert C.sistemico(MINIMOS, "C0000009", date(2026, 6, 30)) == 0.0     # lista completa: no está → 0
    incompleta = {**MINIMOS, "sistemico": {**MINIMOS["sistemico"], "lista_completa": False}}
    assert C.sistemico(incompleta, "C0000009", date(2026, 6, 30)) is None


def _bancos(**kw) -> pd.DataFrame:
    base = {"cod_inst": ["C0000001", "C0000002"], "periodo": ["202606", "202012"],
            "capital_principal": [12.0, 10.0], "rwa_total": [100.0, 100.0], "acp_requerido": [3.5, np.nan],
            "indice_cp": [0.12, 0.10], "indice_nivel1": [0.13, 0.11], "basilea": [0.15, 0.13]}
    base.update(kw)
    return pd.DataFrame(base)


def test_requerimiento_usa_el_acp_del_bcb_y_si_no_la_norma():
    r = C.requerimientos(_bancos(), MINIMOS).set_index("cod_inst")
    assert r.loc["C0000001", "fuente_acp"] == C.FUENTE_ACP_BCB
    assert r.loc["C0000001", "requerimiento_cp"] == pytest.approx(0.045 + 0.035)
    assert r.loc["C0000001", "holgura_cp_pp"] == pytest.approx(0.12 - 0.08)
    assert r.loc["C0000001", "holgura_crecimiento"] == pytest.approx(0.12 / 0.08 - 1)
    # 2020-12: conservación 1,25 % + contracíclico 0 + no sistémico (lista completa)
    assert r.loc["C0000002", "fuente_acp"] == C.FUENTE_ACP_NORMA
    assert r.loc["C0000002", "requerimiento_cp"] == pytest.approx(0.045 + 0.0125)


def test_requerimiento_vacio_si_la_norma_no_cubre_la_fecha():
    r = C.requerimientos(_bancos(periodo=["202606", "202106"]), MINIMOS).set_index("cod_inst")
    assert pd.isna(r.loc["C0000002", "requerimiento_cp"]) and r.loc["C0000002", "fuente_acp"] == ""


# ---------------------------------------------------------------- integración

@pytest.fixture(scope="module")
def capital():
    return pd.read_parquet(GOLD / "bk_capital.parquet")


@pytest.mark.integracion
def test_bk_capital_cubre_el_panel(capital):
    panel = pd.read_parquet(GOLD / "bk_panel.parquet", columns=["cod_inst", "periodo"]).drop_duplicates()
    panel = panel[panel["periodo"] >= "201503"]
    faltan = panel.merge(capital[["cod_inst", "periodo"]], how="left", indicator=True)
    assert faltan["_merge"].eq("both").all(), faltan[faltan["_merge"] != "both"].head()


@pytest.mark.integracion
def test_basilea_mayor_o_igual_nivel1_mayor_o_igual_cp(capital):
    c = capital.dropna(subset=["basilea", "indice_nivel1", "indice_cp"])
    assert (c["basilea"] + 1e-9 >= c["indice_nivel1"]).all()
    assert (c["indice_nivel1"] + 1e-9 >= c["indice_cp"]).all()


@pytest.mark.integracion
def test_rwa_total_es_la_suma_de_sus_componentes(capital):
    c = capital.dropna(subset=["rwa_credito", "rwa_mercado", "rwa_operacional", "rwa_total"])
    c = c[c["rwa_total"] > 0]
    suma = c["rwa_credito"] + c["rwa_mercado"] + c["rwa_operacional"] + c["rwa_sp"].fillna(0)
    assert ((suma - c["rwa_total"]).abs() / c["rwa_total"]).max() < C.TOL_RWA


@pytest.mark.integracion
def test_indice_de_grupo_es_suma_de_capital_sobre_suma_de_rwa(capital):
    g = pd.read_parquet(GOLD / "bk_capital_grupo.parquet")
    total = g[(g["optica"] == "Total panel") & (g["grupo"] == "Todos los grupos")].set_index("periodo")
    c = capital[capital["capital_principal"].notna() & capital["rwa_total"].gt(0)]
    propio = c.groupby("periodo")["capital_principal"].sum() / c.groupby("periodo")["rwa_total"].sum()
    comunes = total.index.intersection(propio.index)
    assert len(comunes) > 40
    assert np.allclose(total.loc[comunes, "indice_cp"], propio.loc[comunes], rtol=1e-12)


@pytest.mark.integracion
def test_requerimiento_desde_2023_sale_del_bcb(capital):
    c = capital[(capital["periodo"] >= "202303") & capital["acp_requerido"].notna() & capital["rwa_total"].gt(0)]
    assert len(c) > 300
    assert c["fuente_acp"].eq(C.FUENTE_ACP_BCB).all()
    # El adicional exigido va de 0 a 5 % del RWA: 2,5 % de conservación + hasta 1 % sistémico en los bancos, y
    # otros niveles en los conglomerados de pago (Neon y PagSeguro 5 %, Nubank, Stone y Mercado Pago 1,25 %).
    pct = c["acp_requerido"] / c["rwa_total"]
    assert pct.between(0, 0.05 + 1e-9).all(), c.loc[~pct.between(0, 0.05 + 1e-9), ["cod_inst", "periodo"]]


def test_alerta_de_trimestres_repetidos():
    df = pd.DataFrame({"cod_inst": ["A", "A", "A", "B"], "periodo": ["202506", "202509", "202512", "202506"],
                       "capital_principal": [1.0, 2.0, 1.0, 1.0], "pr": [3.0, 3.0, 3.0, 3.0],
                       "rwa_total": [10.0, 10.0, 10.0, 10.0]})
    a = C.alertas_repetidos(df)
    assert "202512" in a[0] and "202506" in a[2] and a[1] == "" and a[3] == ""


def test_sistemico_cero_para_todos_cuando_la_norma_lo_fija():
    m = {**MINIMOS, "sistemico": {"cronograma": [{"desde": "2015-01-01", "hasta": "2016-12-31", "valor": 0.0},
                                                 {"desde": "2017-01-01", "hasta": "", "valor": None}],
                                  "bancos": {}, "lista_completa": False}}
    assert C.sistemico(m, "C0000009", date(2016, 6, 30)) == 0.0
    assert C.sistemico(m, "C0000009", date(2018, 6, 30)) is None


def test_minimos_reales_tienen_norma_y_url():
    m = A.leer_definicion(C.DEF_MINIMOS)
    for clave in ("minimos", "conservacion", "contraciclico"):
        assert m[clave] and all(f["norma"] and f["url"].startswith("https://") for f in m[clave])
    # PR 11 % en 2015 y 8 % desde 2019; conservación COVID 1,25 % en 2020-T2
    assert C.vigente(m["minimos"], date(2015, 6, 30), "pr") == 0.11
    assert C.vigente(m["minimos"], date(2026, 6, 30), "pr") == 0.08
    assert C.vigente(m["conservacion"], date(2020, 6, 30)) == 0.0125


@pytest.mark.integracion
def test_contraste_2t26_contra_pilar3(capital):
    """KM1 / notas de capital de 2T26 (fuentes en tareas/borradores/capital_informe.md). Tolerancia 0,1 pp."""
    publicados = {"C0080099": (0.123, 0.140, 0.154), "C0080329": (0.1127, 0.1327, 0.1391),
                  "C0080075": (0.113, 0.128, 0.155), "C0080185": (0.1117, 0.1222, 0.1534),
                  "C0080336": (0.1159, 0.1260, 0.1604)}
    c = capital[capital["periodo"] == "202606"].set_index("cod_inst")
    for cod, (cp, n1, bas) in publicados.items():
        f = c.loc[cod]
        assert abs(f["indice_cp"] - cp) <= 0.001 and abs(f["indice_nivel1"] - n1) <= 0.001 \
            and abs(f["basilea"] - bas) <= 0.001, cod
