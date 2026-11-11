"""Portada mensual, secciones 02 y 03 (pipeline/preparar_gold_bancos_portada_m.py, frente 9)."""
import numpy as np
import pandas as pd
import pytest

import preparar_gold_bancos_portada_m as P
from conftest import GOLD


def test_zscore_y_caja():
    x = pd.Series(np.arange(130, dtype=float), index=pd.period_range("2010-01", periods=130, freq="M"))
    w = x.iloc[-120:]
    assert P.zscore(x) == pytest.approx((w.iloc[-1] - w.mean()) / w.std(ddof=1))
    assert np.isnan(P.zscore(x.iloc[:100]))
    c = P.caja(x, "2019-01")
    assert c["minimo"] == x.loc[pd.Period("2019-01", "M")] and c["maximo"] == x.iloc[-1]


def test_spread_dirigido_personas_no_se_publica():
    assert "pfdi" not in P.CLAVES["spread"]
    assert all(set(P.CLAVES[i]) == set(P.SEGMENTOS) for i in ("tasa", "icc", "mora90", "atraso15_90"))


@pytest.fixture(scope="module")
def tablas():
    return pd.read_parquet(GOLD / "bk_portada_m_tablas.parquet").set_index(["indicador", "segmento"])


@pytest.mark.integracion
@pytest.mark.parametrize("indicador,segmento,ultimo,d12,z", [
    ("mora90", "tot", 4.98, 0.89, 2.60), ("mora90", "pfdi", 3.41, None, None), ("mora90", "pjdi", 2.06, None, None),
    ("atraso15_90", "pf", 6.45, None, None), ("atraso15_90", "tot", 4.86, None, None),
    ("tasa", "tot", 32.36, 0.89, None), ("icc", "tot", 24.28, None, None), ("tasa_menos_icc", "tot", 8.08, None, None),
    ("spread", "li", 35.52, 3.42, 1.16)])
def test_contraste_con_el_canvas(tablas, indicador, segmento, ultimo, d12, z):
    """Cifras del canvas aprobado (tareas/09, tabla de contraste) a sep-26."""
    r = tablas.loc[(indicador, segmento)]
    if r["corte"] != "sep-26":
        pytest.skip(f"el gold ya avanzó a {r['corte']}")
    assert round(r["ultimo"] * 100, 2) == ultimo
    if d12 is not None:
        assert round(r["d12"], 2) == d12
    if z is not None:
        assert round(r["z120"], 2) == z


@pytest.mark.integracion
def test_mora_dirigida_oficial_calza_con_la_derivacion_por_saldos():
    """La mora dirigida por cliente (21145, 21133) es la que el canvas despejaba con los saldos: < 0,03 pp desde 2015.
    Saldo libre de personas = libre total (20542) − libre de empresas (20543)."""
    import sgs as SG
    m = lambda k: SG.serie_mensual(SG.CODIGOS[k])
    libre = {"pj": m("credito_pj_libre"), "pf": m("credito_libre") - m("credito_pj_libre")}
    for cli in ("pf", "pj"):
        st, sl = m(f"credito_{cli}"), libre[cli]
        mora_libre = m("mora90_pf_livre" if cli == "pf" else "mora90_pj_livre")
        deriv = (m(f"mora90_{cli}") * st - mora_libre * sl) / (st - sl)
        d = (deriv - m(f"mora90_{cli}_direccionado")).dropna().loc["2015-01":]
        assert len(d) > 100
        assert d.abs().max() < 0.03, (cli, d.abs().idxmax(), d.abs().max())
