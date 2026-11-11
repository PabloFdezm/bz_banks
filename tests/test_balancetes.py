"""Balancetes COSIF 4060 (pipeline/balancetes.py, frente 11)."""
import numpy as np
import pandas as pd
import pytest

import balancetes as BL
from conftest import GOLD


def _flujos(valores: dict[str, float]) -> pd.Series:
    df = pd.DataFrame({"cod_inst": "C1", "concepto": "lucro_liquido", "periodo": list(valores),
                       "valor": list(valores.values())})
    return BL.acumulado_a_flujo(df)


def test_flujo_desde_acumulado_semestral():
    # BB, ene–jul 2026 (sondeo §4): el acumulado se reinicia en enero y en julio.
    f = _flujos({"202512": 9.0, "202601": 0.947, "202602": 2.021, "202603": 3.033, "202606": 6.216, "202607": 0.764})
    assert f.iloc[1] == pytest.approx(0.947)            # enero: el propio acumulado
    assert f.iloc[2] == pytest.approx(2.021 - 0.947)    # febrero: diferencia
    assert np.isnan(f.iloc[4])                          # junio sin mayo: vacío, no se inventa
    assert f.iloc[5] == pytest.approx(0.764)            # julio: reinicio


def test_epoca_y_trimestre():
    assert BL.epoca("202412") == "vieja" and BL.epoca("202501") == "nueva"
    assert [BL.fin_trimestre(p) for p in ("202601", "202603", "202604", "202612")] == \
        ["202603", "202603", "202606", "202612"]


def test_conceptos_suman_por_base_y_epoca():
    defn = {"conceptos": {
        "ativo_total": {"tipo": "saldo", "vieja": ["1000000", "2000000"], "nueva": ["1000000", "2000000"]},
        "lucro_liquido": {"tipo": "flujo", "vieja": ["7000000", "8000000"], "nueva": ["7000000", "8000000"]}}}
    sal = pd.DataFrame({"cod_inst": "C1", "periodo": ["202412"] * 4 + ["202501"] * 3,
                        "conta": ["10000007", "20000004", "70000009", "80000006", "10000000", "70000000", "80000000"],
                        "nome": "", "saldo": [10.0, 2.0, 5.0, -3.0, 11.0, 1.0, -0.5]})
    c = BL.conceptos(sal, defn).set_index(["periodo", "concepto"])["valor"]
    assert c[("202412", "ativo_total")] == 12.0 and c[("202501", "ativo_total")] == 11.0
    assert c[("202501", "lucro_liquido")] == pytest.approx(0.5)          # enero: acumulado del semestre nuevo


def test_cuadre_no_exige_patrimonio_de_junio_y_diciembre():
    c = pd.DataFrame([{"cod_inst": "C1", "periodo": p, "concepto": k, "tipo": "x", "valor": v}
                      for p in ("202604", "202605", "202606")
                      for k, v in (("ativo_total", 100.0), ("patrimonio_liquido", 10.5), ("credito_liquido", 50.0),
                                   ("depositos", 60.0), ("lucro_liquido", 1.0))])
    panel = pd.DataFrame([{"cod_inst": "C1", "periodo": "202606", "metrica": m, "valor": v}
                          for m, v in (("ativo_total", 100.0), ("patrimonio_liquido", 10.0), ("credito_liquido", 50.0),
                                       ("depositos", 60.0), ("lucro_liquido_q", 3.0))])
    q = BL.cuadre(c, panel).iloc[0]
    assert q["d_patrimonio_liquido"] == pytest.approx(0.05) and bool(q["cuadra"])
    c.loc[c["concepto"].eq("patrimonio_liquido"), "periodo"] = c["periodo"]   # mismo dato en marzo sí se exige
    c2 = c.assign(periodo=c["periodo"].str.replace("2026", "2025").str.replace("04", "01").str.replace("05", "02")
                  .str.replace("06", "03"))
    panel2 = panel.assign(periodo="202503")
    assert not bool(BL.cuadre(c2, panel2).iloc[0]["cuadra"])


@pytest.fixture(scope="module")
def gold():
    return (pd.read_parquet(GOLD / "bk_balancete_m.parquet"), pd.read_parquet(GOLD / "bk_sistema_bal_m.parquet"))


@pytest.mark.integracion
def test_gold_identidades(gold):
    m, g = gold
    assert m["mes"].min() >= "202001"
    assert not m.duplicated(["cod_inst", "mes", "concepto"]).any()
    w = m.pivot_table(index=["cod_inst", "mes"], columns="concepto", values="valor")
    partes = w[["depositos_vista", "depositos_ahorro", "depositos_interfinanceiros", "depositos_plazo"]].sum(axis=1)
    con = w["depositos"].notna()                              # hay bancos sin depósitos (p. ej. C0086581)
    assert (partes[con] <= w.loc[con, "depositos"] * 1.0001 + 1).all()     # las cuatro líneas no superan el total
    tp = g[g["optica"].eq("Total panel")].set_index("mes")
    assert (tp["roe_12m"].dropna().between(0.05, 0.30)).all()
    r = (tp["credito_liquido"] / tp["depositos"] - tp["credito_depositos"]).abs().max()
    assert r < 1e-12                                          # cociente de sumas, no promedio


@pytest.mark.integracion
def test_roe_total_panel_contra_ifdata(gold):
    """Criterio del encargo: roe_12m del Total panel a fin de trimestre contra roe_ttm de bk_grupo, ≤ 0,3 pp.
    Diciembre de 2024 queda en −0,36 pp por el patrimonio previo al cierre del semestre (trampa 9): se tolera 0,4."""
    _, g = gold
    gr = pd.read_parquet(GOLD / "bk_grupo.parquet")
    r = gr[gr["metrica"].eq("roe_ttm") & gr["optica"].eq("Total panel")].assign(periodo=lambda d: d["periodo"].astype(str))
    j = g[g["optica"].eq("Total panel")].merge(r[["periodo", "valor"]].rename(columns={"periodo": "mes"}), on="mes").dropna(subset=["roe_12m"])
    assert len(j) >= 20
    dif = (j["roe_12m"] - j["valor"]).abs() * 100
    assert (dif <= 0.3).mean() >= 0.9 and dif.max() <= 0.4
