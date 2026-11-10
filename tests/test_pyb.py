# -*- coding: utf-8 -*-
"""Hoja «P&L y balance por banco» (pipeline/preparar_gold_bancos_pyb.py, frente 15).

Las unitarias usan hechos sintéticos. Las marcadas `integracion` leen datos/gold (bk_pyb, bk_pyb_grupo, bank_hechos,
bk_panel).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import preparar_gold_bancos_pyb as P
from conftest import GOLD

TOL_RS = 1_000          # R$ 1 mil
TOL = 1e-9

# --- unitarias -----------------------------------------------------------------------------------------------------


def test_etiqueta_y_orden_de_trimestres():
    assert P.etiqueta("202606") == "2T26"
    assert P.etiqueta("201503") == "1T15"
    n = P.n_trimestre(pd.Series(["201412", "201503", "201506"]))
    assert list(np.diff(n)) == [1, 1]
    assert P.periodo_de_n(pd.Index(n)) == ["201412", "201503", "201506"]


def _ancho(periodos, valores, cod="X"):
    idx = pd.MultiIndex.from_tuples([(cod, p) for p in periodos], names=["cod_inst", "periodo"])
    return pd.DataFrame({"v": valores}, index=idx)


def test_12m_suma_cuatro_trimestres_consecutivos():
    a = _ancho(["202403", "202406", "202409", "202412", "202503"], [1.0, 2, 3, 4, 5])
    t = P.suma_12m(a)["v"]
    assert t.isna().tolist() == [True, True, True, False, False]
    assert t.iloc[3] == 10 and t.iloc[4] == 14


def test_12m_vacio_si_falta_un_trimestre():
    # falta 202409: por posición se sumarían 202403..202503; por calendario no hay 4 consecutivos hasta 202606
    a = _ancho(["202403", "202406", "202412", "202503", "202506", "202509"], [1.0, 2, 4, 5, 6, 7])
    t = P.suma_12m(a)["v"]
    assert t.isna().tolist() == [True, True, True, True, True, False]
    assert t.iloc[-1] == 4 + 5 + 6 + 7


def test_12m_no_depende_del_orden_de_las_filas():
    a = _ancho(["202412", "202403", "202409", "202406"], [4.0, 1, 3, 2])
    assert P.suma_12m(a).loc[("X", "202412"), "v"] == 10


def test_var_aa_usa_el_mismo_trimestre_del_anio_anterior():
    a = _ancho(["202403", "202406", "202409", "202412", "202503", "202509", "202512", "202603"],
               [100.0, 1, 1, 1, 110, 1, 1, 121])
    r = P.var_aa(a)["v"]
    assert r.loc[("X", "202503")] == pytest.approx(0.10)
    assert r.loc[("X", "202603")] == pytest.approx(0.10)
    assert r.loc[("X", "202509")] == pytest.approx(0.0)              # contra 202409, no contra la 4.ª fila previa


DEFN = {"fondeo": ["dep"], "lineas": [
    {"linea": "cred", "seccion": "pyl", "tipo": "cuentas", "epocas": {
        "nueva": {"informe": 4, "cuentas": [{"cuenta": "rendas de credito", "signo": 1},
                                            {"cuenta": "rendas de outras", "signo": 1}]},
        "vieja": {"informe": 4, "cuentas": [{"cuenta": "rendas de credito", "signo": 1}]}}},
    {"linea": "pag", "seccion": "pyl", "tipo": "cuentas", "epocas": {
        "nueva": {"informe": 4, "cuentas": [{"cuenta": "transacoes", "signo": 1}]},
        "vieja": {"informe": 4, "cuentas": []}}},
    {"linea": "otros", "seccion": "pyl", "tipo": "residual", "total": "rif", "resta": ["cred", "pag"]},
    {"linea": "rif", "seccion": "pyl", "tipo": "total", "epocas": {
        "nueva": {"informe": 4, "cuentas": [{"cuenta": "rif", "signo": 1}]},
        "vieja": {"informe": 4, "cuentas": [{"cuenta": "rif", "signo": 1}]}}},
    {"linea": "neg", "seccion": "pyl", "tipo": "subtotal", "suma": [{"linea": "rif", "signo": 1},
                                                                    {"linea": "cred", "signo": -1}]},
    {"linea": "dep", "seccion": "pasivo", "tipo": "cuentas", "epocas": {
        "nueva": {"informe": 3, "cuentas": [{"cuenta": "instrumentos derivativos", "signo": 1}]},
        "vieja": {"informe": 3, "cuentas": [{"cuenta": "instrumentos derivativos", "signo": 1}]}}},
    {"linea": "deriv", "seccion": "activo", "tipo": "cuentas", "epocas": {
        "nueva": {"informe": 2, "cuentas": [{"cuenta": "instrumentos derivativos", "signo": 1}]},
        "vieja": {"informe": 2, "cuentas": [{"cuenta": "instrumentos derivativos", "signo": 1}]}}},
    {"linea": "credb", "seccion": "activo", "tipo": "panel", "metrica": "credito_bruto", "signo": 1},
]}


def _hechos():
    f = []

    def h(per, era, inf, cuenta, v):
        f.append(dict(cod_inst="X", periodo=per, num_informe=inf, era=era, cuenta_base=cuenta, valor=v))

    # vieja: «rendas de outras» existe en la fila pero la época manda: no se suma
    h("202412", "vieja", 4, "rendas de credito", 10.0)
    h("202412", "vieja", 4, "rendas de outras", 99.0)
    h("202412", "vieja", 4, "transacoes", 50.0)
    h("202412", "vieja", 4, "rif", 30.0)
    h("202503", "nueva", 4, "rendas de credito", 10.0)
    h("202503", "nueva", 4, "rendas de outras", 5.0)
    h("202503", "nueva", 4, "transacoes", 7.0)
    h("202503", "nueva", 4, "rif", 30.0)
    for per, era in (("202412", "vieja"), ("202503", "nueva")):
        h(per, era, 2, "instrumentos derivativos", 1.0)
        h(per, era, 3, "instrumentos derivativos", 2.0)
    return pd.DataFrame(f)


def _panel():
    return pd.DataFrame({"cod_inst": "X", "periodo": ["202412", "202503"], "metrica": "credito_bruto",
                         "valor": [100.0, 110.0], "modelo": "M"})


def test_lineas_por_epoca_e_informe():
    L = P.calcular_lineas(_hechos(), _panel(), DEFN)
    v, n = L.loc[("X", "202412")], L.loc[("X", "202503")]
    assert v["cred"] == 10 and n["cred"] == 15                # la época decide, no la existencia de la cuenta
    assert v["pag"] == 0 and n["pag"] == 7                    # lista vacía en la época vieja = 0
    assert v["otros"] == 20 and n["otros"] == 8               # residual hasta el total
    assert v["cred"] + v["pag"] + v["otros"] == v["rif"]
    assert n["neg"] == 15
    assert v["deriv"] == 1 and v["dep"] == 2                  # mismo nombre en informes 2 y 3
    assert n["credb"] == 110


def test_total_faltante_queda_vacio():
    h = _hechos()
    h = h[~((h["periodo"] == "202503") & (h["cuenta_base"] == "rif"))]
    L = P.calcular_lineas(h, _panel(), DEFN)
    assert np.isnan(L.loc[("X", "202503"), "rif"]) and np.isnan(L.loc[("X", "202503"), "otros"])


def test_cuenta_repetida_en_un_informe_falla():
    h = _hechos()
    h = pd.concat([h, h.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="repetidas"):
        P.calcular_lineas(h, _panel(), DEFN)


# --- integración ---------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pyb():
    return pd.read_parquet(GOLD / "bk_pyb.parquet")


@pytest.fixture(scope="module")
def grupo():
    return pd.read_parquet(GOLD / "bk_pyb_grupo.parquet")


@pytest.fixture(scope="module")
def panel():
    return pd.read_parquet(GOLD / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "valor", "modelo"])


@pytest.fixture(scope="module")
def hechos():
    return pd.read_parquet(GOLD / "bank_hechos.parquet",
                           columns=["cod_inst", "periodo", "num_informe", "era", "cuenta_base", "valor"])


def _ancho_medida(pyb, medida):
    x = pyb[pyb["medida"] == medida]
    return x.pivot_table(index=["cod_inst", "periodo"], columns="linea", values="valor", aggfunc="first")


def _publicado(hechos, informe, cuentas_por_era):
    h = hechos[hechos["num_informe"] == informe]
    partes = [h[(h["era"] == e) & (h["cuenta_base"] == c)] for e, c in cuentas_por_era.items()]
    return pd.concat(partes).set_index(["cod_inst", "periodo"])["valor"]


def _lineas(seccion):
    return [l["linea"] for l in P.definiciones()["lineas"] if l["seccion"] == seccion]


@pytest.mark.integracion
def test_cuentas_del_mapa_existen_en_bank_hechos(hechos):
    existe = set(zip(hechos["num_informe"], hechos["era"], hechos["cuenta_base"]))
    faltan = [(l["linea"], e, ep["informe"], c["cuenta"]) for l in P.definiciones()["lineas"]
              for e, ep in l.get("epocas", {}).items() for c in ep["cuentas"]
              if (ep["informe"], e, c["cuenta"]) not in existe]
    assert not faltan, faltan


@pytest.mark.integracion
def test_pyl_suma_los_subtotales_publicados(pyb, hechos):
    q = _ancho_medida(pyb, "rs_trim")
    rif = _publicado(hechos, 4, {"cosif_2025": "resultado de intermediacao financeira",
                                 "cosif_pre2025": "resultado de intermediacao financeira"})
    antes = _publicado(hechos, 4, {"cosif_2025": "resultado antes da tributacao e participacoes",
                                   "cosif_pre2025": "resultado antes da tributacao, lucro e participacao"})
    lucro = _publicado(hechos, 4, {"cosif_2025": "lucro liquido", "cosif_pre2025": "lucro liquido"})
    s_rif = q[["cred", "tes", "capt", "oif", "prov"]].sum(axis=1)
    s_antes = s_rif + q[["serv", "pag", "pers", "adm", "trib", "part", "oop"]].sum(axis=1)
    s_lucro = s_antes + q[["imp", "plr", "obl"]].sum(axis=1)
    for s, pub in ((s_rif, rif), (s_antes, antes), (s_lucro, lucro)):
        pub = pub.dropna()
        assert set(q.index) == set(pub.index)          # sin informe 4 publicado no hay filas (nunca ceros)
        assert (s - pub.reindex(s.index)).abs().max() < TOL_RS
    assert ((q["mfb"] - (q["rif"] - q["prov"])).abs() < TOL_RS).all()


@pytest.mark.integracion
def test_balance_suma_activo_y_pasivo_total(pyb, hechos):
    b = _ancho_medida(pyb, "rs")
    activo = _publicado(hechos, 2, {"cosif_2025": "ativo total", "cosif_pre2025": "ativo total"})
    pasivo = _publicado(hechos, 3, {"cosif_2025": "passivo total", "cosif_pre2025": "passivo total"})
    a = [x for x in _lineas("activo") if x != "activo"]
    p = [x for x in _lineas("pasivo") if x != "pasivo"]
    b = b[b["activo"].notna()]
    for s, pub in ((b[a].sum(axis=1), activo), (b[p].sum(axis=1), pasivo)):
        pub = pub.dropna()
        assert set(b.index) == set(pub.index)
        assert (s - pub.reindex(s.index)).abs().max() < TOL_RS


@pytest.mark.integracion
def test_12m_son_cuatro_trimestres_consecutivos_o_vacio(pyb):
    q = _ancho_medida(pyb, "rs_trim")
    t = _ancho_medida(pyb, "rs_12m").reindex(q.index)
    n = P.n_trimestre(pd.Series(q.index.get_level_values(1))).to_numpy()
    clave = {(c, k): i for i, (c, k) in enumerate(zip(q.index.get_level_values(0), n))}
    vals = q.to_numpy()
    for i, (c, k) in enumerate(zip(q.index.get_level_values(0), n)):
        prev = [clave.get((c, k - j)) for j in range(4)]
        if any(x is None for x in prev):
            assert t.iloc[i].isna().all(), q.index[i]
        else:
            esperado = vals[prev].sum(axis=0)
            assert np.allclose(t.iloc[i].to_numpy(), esperado, atol=TOL_RS, equal_nan=True), q.index[i]


@pytest.mark.integracion
def test_contraste_con_bk_panel(pyb, panel):
    t = _ancho_medida(pyb, "rs_12m")
    for linea, metrica in (("lucro", "lucro_liquido_ttm"), ("antes", "antes_tributacao_ttm"),
                           ("prov", "provisoes_credito_ttm"), ("rif", "resultado_intermediacao_financeira_ttm")):
        b = panel[panel["metrica"] == metrica].set_index(["cod_inst", "periodo"])["valor"]
        j = pd.concat([t[linea], b], axis=1, keys=["pyb", "panel"]).dropna()
        assert len(j) > 1000
        assert (j["pyb"] - j["panel"]).abs().max() < TOL_RS, linea
    it = t.loc[("C0080099", "202606")] / 1e6
    assert it["lucro"] == pytest.approx(48_759, abs=1)
    assert it["antes"] == pytest.approx(64_607, abs=1)
    assert it["prov"] == pytest.approx(-35_449, abs=1)
    assert it["rif"] == pytest.approx(58_597, abs=1)


@pytest.mark.integracion
def test_mediana_del_grupo_recalculada(pyb, grupo, panel):
    mod = P.modelos(panel.assign(periodo=panel["periodo"].astype(str)))
    for medida in ("pct_activo_medio_12m", "pct_activo"):
        x = pyb[pyb["medida"] == medida].assign(grupo=lambda d: d["cod_inst"].map(mod))
        med = x.groupby(["grupo", "periodo", "linea"])["valor"].median()
        g = grupo[(grupo["medida"] == medida) & (grupo["grupo"] != P.PANEL)].set_index(
            ["grupo", "periodo", "linea"])["valor"]
        j = pd.concat([med, g], axis=1, keys=["a", "b"])
        assert j.notna().all().all()
        assert (j["a"] - j["b"]).abs().max() < TOL


@pytest.mark.integracion
def test_panel_es_razon_de_sumas(pyb, grupo, panel):
    am = panel[panel["metrica"] == "ativo_medio_ttm"].set_index(["cod_inst", "periodo"])["valor"].rename("den")
    t = pyb[pyb["medida"] == "rs_12m"].join(am, on=["cod_inst", "periodo"]).dropna(subset=["valor", "den"])
    s = t.groupby(["periodo", "linea"])[["valor", "den"]].sum()
    esperado = s["valor"] / s["den"]
    g = grupo[(grupo["grupo"] == P.PANEL) & (grupo["medida"] == "pct_activo_medio_12m")].set_index(
        ["periodo", "linea"])["valor"]
    j = pd.concat([esperado, g], axis=1, keys=["a", "b"]).dropna()
    assert len(j) == len(g)
    assert (j["a"] - j["b"]).abs().max() < TOL
    # el panel no es el promedio de las razones
    r = pyb[(pyb["medida"] == "pct_activo_medio_12m") & (pyb["linea"] == "lucro") & (pyb["periodo"] == "202606")]
    assert abs(r["valor"].mean() - g.loc[("202606", "lucro")]) > 1e-4
    # balance: Σ rs / Σ activo
    b = pyb[pyb["medida"] == "rs"]
    act = b[b["linea"] == "activo"].set_index(["cod_inst", "periodo"])["valor"].rename("den")
    s = b.join(act, on=["cod_inst", "periodo"]).dropna(subset=["valor", "den"]).groupby(["periodo", "linea"])[
        ["valor", "den"]].sum()
    g = grupo[(grupo["grupo"] == P.PANEL) & (grupo["medida"] == "pct_activo")].set_index(["periodo", "linea"])["valor"]
    assert ((s["valor"] / s["den"]).reindex(g.index) - g).abs().max() < TOL


@pytest.mark.integracion
def test_signos_de_gastos(pyb):
    # Gastos negativos. Hay trimestres sueltos con gasto positivo (reversiones al desacumular el semestre:
    # BTG 4T16, Original 4T24, PagSeguro 4T19...; ver tareas/borradores/pyb_verificaciones.md, punto 6): se toleran
    # mientras sean menos del 1 %.
    q = pyb[pyb["medida"] == "rs_trim"]
    for linea in ("pers", "adm", "trib", "capt"):
        v = q.loc[q["linea"] == linea, "valor"]
        assert (v > TOL_RS).mean() < 0.01, linea
