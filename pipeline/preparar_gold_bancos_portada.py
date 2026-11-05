# -*- coding: utf-8 -*-
"""Tablas de la Portada v3 del sitio de bancos (canvas «Bancos Brasil — propuesta visual», tablero 05).

POR QUÉ EXISTE
--------------
La Portada muestra cuatro bloques, cada uno con un gráfico y una tabla descriptiva de estructura fija
(m/m, 3m/3m, a/a, 12m/12m; en trimestrales t/t, a/a, 4T/4T). Por regla del sitio, el navegador no
calcula: todas las variaciones, contribuciones, deflactados y cuotas salen de aquí.

TABLAS (datos/gold/)
------------------
- bk_portada_credito: fecha, modo (nominal|real), componente (total, libre, direccionado, pf, pj),
  aa (fracción) y contrib_pp (contribución al a/a del total, en pp). Mensual desde 2016.
- bk_portada_mora: fecha, nivel (fracción) y d_aa_pp del total (SGS 21082). Mensual desde 2016.
- bk_portada_roe: periodo, fecha, trimestre, roe, cdi_4t, roe_cdi_pp (ROE del panel menos CDI promedio
  de 4 trimestres, en pp).
- bk_portada_tablas: bloque (credito_nominal, credito_real, mora, roe), orden, fila, ultimo, d1, d3,
  d12, dventana, unidad, corte. En crédito: saldo (R$ mil millones), y % de variación; en mora: nivel
  en % y cambios en pp; en ROE: % y pp con d1 = t/t, d3 vacío, d12 = a/a, dventana = 4T/4T.
- bk_portada_cuotas: vista, orden, banco, cuota (fracción), grupo, periodo. Diez mayores + «Resto».

REGLAS
------
- 3m/3m y 12m/12m: promedio de la ventana sobre el de la ventana anterior (saldos) o diferencia de
  promedios (tasas). m/m y a/a: punta contra punta.
- Real: saldo deflactado por el índice IPCA encadenado (SGS 433), base último mes.
- Contribución: (componente_t − componente_t−12) / total_t−12, en pp. Libre + direccionado = total
  (diferencia < 1 %); PF + PJ = total.
- Series SGS: se leen del crudo (cualquier dataset de bcb_sgs). Si falta, se bajan con el mismo
  mecanismo de preparar_gold_bancos_sistema; sin red, la fila queda vacía y se avisa.
- Cuotas: último trimestre del panel IF.Data con informes de pasivo (r3) y cartera PF/PJ (r11, r13);
  activos y crédito total desde bk_panel (share_ativo, share_credito). Solo conglomerados del panel.
"""
from __future__ import annotations

import glob
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import almacen as A
import preparar_gold_bancos_sistema as S

BASE = Path(__file__).resolve().parents[1]
BANKS = BASE / "datos" / "gold"
CRUDO_SGS = BASE / "datos" / "crudo" / "bcb_sgs"
CRUDO_IFDATA = BASE / "datos" / "crudo" / "bcb_ifdata" / "valores" / "actual"
COMANDO = "python -X utf8 preparar_gold_bancos_portada.py"
DESDE = "2016-01"

SALDOS = {"total": 20539, "libre": 20542, "direccionado": 20593, "pf": 20541, "pj": 20540}
NOMBRE_CREDITO = {"total": "Total", "libre": "Libre", "direccionado": "Direccionado", "pf": "Personas", "pj": "Empresas"}
# Mora > 90 días: (fila, código SGS). 21083 (PJ total), 21085 (libre total) y 21132 (direccionado total)
# se bajan si faltan; si el SGS no los sirve, la fila queda vacía.
MORA = [("Total", 21082), ("Libre", 21085), ("Direccionado", 21132), ("Personas", 21084), ("Empresas", 21083),
        ("Personas · libre", 21112), ("Empresas · libre", 21086)]
CDI = 4389
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def serie(codigo: int) -> pd.Series | None:
    """Serie mensual del crudo SGS (cualquier dataset); si falta, intenta bajarla."""
    rutas = sorted(glob.glob(str(CRUDO_SGS / "*" / "actual" / f"serie_{codigo}.json")))
    if rutas:
        d = pd.DataFrame(json.loads(Path(rutas[0]).read_text(encoding="utf-8")))
        col = "data" if "data" in d else "fecha"
        s = pd.Series(pd.to_numeric(d["valor"], errors="coerce").to_numpy(),
                      index=pd.to_datetime(d[col], format="%d/%m/%Y")).sort_index()
        s = s[~s.index.duplicated(keep="last")]
    else:
        try:
            s = S.sgs(codigo, False)
        except Exception as e:  # sin red o código inexistente: la fila queda vacía
            print(f"aviso: SGS {codigo} no disponible ({type(e).__name__}: {e})", file=sys.stderr)
            return None
    return S.mensual(s)


def mes(p: pd.Period) -> str:
    return f"{MESES[p.month - 1]}-{str(p.year)[2:]}"


def variaciones_saldo(x: pd.Series) -> dict:
    x = x.dropna()
    return {"ultimo": x.iloc[-1], "d1": x.iloc[-1] / x.iloc[-2] - 1,
            "d3": x.iloc[-3:].mean() / x.iloc[-6:-3].mean() - 1, "d12": x.iloc[-1] / x.iloc[-13] - 1,
            "dventana": x.iloc[-12:].mean() / x.iloc[-24:-12].mean() - 1, "corte": mes(x.index[-1])}


def variaciones_tasa(x: pd.Series) -> dict:
    x = x.dropna()
    return {"ultimo": x.iloc[-1], "d1": x.iloc[-1] - x.iloc[-2], "d3": x.iloc[-3:].mean() - x.iloc[-6:-3].mean(),
            "d12": x.iloc[-1] - x.iloc[-13], "dventana": x.iloc[-12:].mean() - x.iloc[-24:-12].mean(),
            "corte": mes(x.index[-1])}


def credito() -> tuple[pd.DataFrame, list[dict]]:
    sal = {k: serie(c) for k, c in SALDOS.items()}
    indice = S.deflactor(serie(433))
    filas, tabla = [], []
    for modo in ("nominal", "real"):
        ss = {k: (v if modo == "nominal" else v.div(indice.reindex(v.index))) for k, v in sal.items()}
        tot = ss["total"]
        for k, v in ss.items():
            aa = v / v.shift(12) - 1
            contrib = (v - v.shift(12)) / tot.shift(12).reindex(v.index) * 100
            df = pd.DataFrame({"fecha": v.index.to_timestamp(how="end").normalize().strftime("%Y-%m-%d"),
                               "modo": modo, "componente": k, "aa": aa.to_numpy(), "contrib_pp": contrib.to_numpy()},
                              index=v.index)
            filas.append(df[df.index >= pd.Period(DESDE, "M")])
            var = variaciones_saldo(v)
            var["ultimo"] = sal[k].dropna().iloc[-1] / 1e3   # saldo nominal, R$ mil millones (SGS en R$ millones)
            u = sal[k].dropna()
            var["share"] = u.iloc[-1] / sal["total"].dropna().reindex(u.index).dropna().iloc[-1] if k != "total" else 1.0
            tabla.append({"bloque": f"credito_{modo}", "orden": list(SALDOS).index(k), "fila": NOMBRE_CREDITO[k],
                          "unidad": "pct", **var})
    return pd.concat(filas, ignore_index=True), tabla


def mora() -> tuple[pd.DataFrame, list[dict]]:
    tabla, total = [], None
    for i, (nombre, cod) in enumerate(MORA):
        s = serie(cod)
        if s is None or s.dropna().empty:
            tabla.append({"bloque": "mora", "orden": i, "fila": nombre, "unidad": "pp", "ultimo": np.nan,
                          "d1": np.nan, "d3": np.nan, "d12": np.nan, "dventana": np.nan, "corte": None})
            continue
        s = s / 100  # SGS en %
        if cod == 21082:
            total = s
        v = variaciones_tasa(s)
        tabla.append({"bloque": "mora", "orden": i, "fila": nombre, "unidad": "pp",
                      **{k: (v[k] * 100 if k in ("d1", "d3", "d12", "dventana") else v[k]) for k in v}})
    t = pd.DataFrame({"fecha": total.index.to_timestamp(how="end").normalize().strftime("%Y-%m-%d"),
                      "nivel": total.to_numpy(), "d_aa_pp": ((total - total.shift(12)) * 100).to_numpy()}, index=total.index)
    return t[t.index >= pd.Period(DESDE, "M")].reset_index(drop=True), tabla


def roe() -> tuple[pd.DataFrame, list[dict]]:
    g = pd.read_parquet(BANKS / "bk_grupo.parquet")
    r = g[(g.optica == "Total panel") & (g.grupo == "Todos los grupos") & (g.metrica == "roe_ttm")][["periodo", "fecha", "trimestre", "valor"]]
    r = r.dropna().sort_values("periodo").rename(columns={"valor": "roe"})
    cdi = serie(CDI)
    if cdi is None:
        raise SystemExit("falta SGS 4389 (CDI)")
    q = cdi.groupby(cdi.index.asfreq("Q")).mean().rolling(4).mean() / 100
    r["cdi_4t"] = [q.get(pd.Period(f"{p[:4]}Q{int(p[4:]) // 3}", "Q"), np.nan) for p in r.periodo]
    r["roe_cdi_pp"] = (r.roe - r.cdi_4t) * 100
    r = r[r.periodo >= "201601"].reset_index(drop=True)
    tabla = []
    for i, (nombre, col, esc) in enumerate([("ROE 12 meses", "roe", 100), ("ROE − CDI", "roe_cdi_pp", 1)]):
        x = r[col].to_numpy() * (esc if col == "roe" else 1)
        tabla.append({"bloque": "roe", "orden": i, "fila": nombre, "unidad": "pp",
                      "ultimo": r[col].iloc[-1], "d1": x[-1] - x[-2], "d3": np.nan, "d12": x[-1] - x[-5],
                      "dventana": x[-4:].mean() - x[-8:-4].mean(), "corte": r.trimestre.iloc[-1]})
    return r, tabla


def cuotas() -> pd.DataFrame:
    banco = pd.read_parquet(BANKS / "bk_banco.parquet")[["cod_inst", "nombre_corto", "modelo"]]
    panel = pd.read_parquet(BANKS / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "valor"])
    per = max(p.name.split("_")[1] for p in A.glob_crudo(CRUDO_IFDATA, "valores_*_1_r3.csv"))   # CSV o parquet

    def informe(n):
        d = A.leer_crudo_tabla(CRUDO_IFDATA / f"valores_{per}_1_r{n}.csv", ["CodInst", "NomeColuna", "Saldo"])
        d["Saldo"] = pd.to_numeric(d.Saldo.astype(str).str.replace(",", "."), errors="coerce")
        d["CodInst"] = d.CodInst.astype(str)   # texto con ceros a la izquierda, como la lectura anterior (columna mixta)
        return d

    def col(d, pref):
        return d[d.NomeColuna.str.startswith(pref)].groupby("CodInst").Saldo.sum()

    p3, p11, p13 = informe(3), informe(11), informe(13)
    vistas = {
        "Activos totales": panel[(panel.metrica == "share_ativo") & (panel.periodo == per)].set_index("cod_inst").valor,
        "Crédito total": panel[(panel.metrica == "share_credito") & (panel.periodo == per)].set_index("cod_inst").valor,
        "Crédito personas": col(p11, "Total da Carteira de Pessoa Física"),
        "Crédito empresas": col(p13, "Total da Carteira de Pessoa Jurídica"),
        "Depósitos totales": col(p3, "Depósitos \n(a)"),
        "Depósitos a la vista": col(p3, "Depósitos à Vista"),
        "Depósitos de ahorro": col(p3, "Depósitos de Poupança"),
        "Depósitos a plazo": col(p3, "Depósitos a Prazo"),
    }
    nm = banco.set_index("cod_inst")
    out = []
    for j, (vista, x) in enumerate(vistas.items()):
        x = x[x.index.isin(nm.index)].astype(float)
        x = x[x > 0]
        s = (x / x.sum()).sort_values(ascending=False)
        for i, (c, v) in enumerate(s.head(10).items()):
            out.append({"vista": vista, "orden_vista": j, "orden": i, "banco": nm.nombre_corto[c], "cuota": v,
                        "grupo": nm.modelo[c], "periodo": per})
        if len(s) > 10:
            out.append({"vista": vista, "orden_vista": j, "orden": 10, "banco": f"Resto ({len(s) - 10})",
                        "cuota": s.iloc[10:].sum(), "grupo": "Resto", "periodo": per})
    return pd.DataFrame(out)


def guardar(nombre: str, df: pd.DataFrame) -> None:
    b = io.BytesIO()
    df.to_parquet(b, index=False)
    A.guardar_derivado("bcb_sgs", "bancos_gold_portada", f"{nombre}.parquet", b.getvalue(),
                       desde=["bcb_sgs/bancos_sistema", "bcb_ifdata/valores"], como=COMANDO,
                       nota="Portada v3 del sitio de bancos")
    A.escribir_atomico(BANKS / f"{nombre}.parquet", b.getvalue())
    print(f"{nombre}: {len(df):,} filas")


def main() -> int:
    cred, t1 = credito()
    mor, t2 = mora()
    ro, t3 = roe()
    cuo = cuotas()
    tablas = pd.DataFrame(t1 + t2 + t3)
    # comprobaciones
    ult = cred[cred.modo == "nominal"].dropna(subset=["contrib_pp"])
    f = ult.fecha.max()
    u = ult[ult.fecha == f].set_index("componente")
    if {"pf", "pj"} <= set(u.index):
        dif = abs(u.loc["pf", "contrib_pp"] + u.loc["pj", "contrib_pp"] - u.loc["total", "aa"] * 100)
        assert dif < 0.05, f"PF + PJ no suma el total a/a ({dif:.3f} pp)"
    for v, g in cuo.groupby("vista"):
        assert abs(g.cuota.sum() - 1) < 1e-6, f"cuotas de {v} no suman 1"
    guardar("bk_portada_credito", cred)
    guardar("bk_portada_mora", mor)
    guardar("bk_portada_roe", ro)
    guardar("bk_portada_tablas", tablas)
    guardar("bk_portada_cuotas", cuo)
    print(tablas[["bloque", "fila", "ultimo", "d1", "d3", "d12", "dventana", "corte"]].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
