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
  d12, dventana, corte y las unidades de la tabla estándar. En crédito: saldo (R$ mil millones), y % de variación; en mora: nivel
  en % y cambios en pp; en ROE: % y pp con d1 = t/t, d3 vacío, d12 = a/a, dventana = 4T/4T.
- bk_portada_cuotas: vista, orden, banco, cuota (fracción), grupo, periodo. Diez mayores + «Resto».

REGLAS
------
- 3m/3m y 12m/12m: promedio de la ventana sobre el de la ventana anterior (saldos) o diferencia de
  promedios (tasas). m/m y a/a: punta contra punta.
- Real: saldo deflactado por el índice IPCA encadenado (SGS 433), base último mes.
- Contribución: (componente_t − componente_t−12) / total_t−12, en pp. Libre + direccionado = total
  (diferencia < 1 %); PF + PJ = total.
- Series SGS: saldos del crudo bcb_sgs/bancos_sistema (sgs.py); mora > 90 días de bk_sistema_m; CDI de
  sgs.cdi_12m (promedio de los 12 meses que terminan en el trimestre).
- Cuotas: último trimestre del panel IF.Data con informes de pasivo (r3) y cartera PF/PJ (r11, r13);
  activos y crédito total desde bk_panel (share_ativo, share_credito). Solo conglomerados del panel.
"""
from __future__ import annotations

import sys

import pandas as pd

import almacen as A
import bancos as B
import ifdata_texto as T_IF
import sgs as SG
import tabla_estandar as T

DESDE = "2016-01"

SALDOS = {"total": "credito_total", "libre": "credito_libre", "direccionado": "credito_direccionado",
          "pf": "credito_pf", "pj": "credito_pj"}           # componente → nombre en sgs.CODIGOS
NOMBRE_CREDITO = {"total": "Total", "libre": "Libre", "direccionado": "Direccionado", "pf": "Personas", "pj": "Empresas"}
# Mora > 90 días: (fila, serie_id de bk_sistema_m, en fracción).
MORA = [("Total", "mora90_total"), ("Libre", "mora90_libre"), ("Direccionado", "mora90_direccionado"),
        ("Personas", "mora90_pf"), ("Empresas", "mora90_pj"), ("Personas · libre", "mora90_pf_livre"),
        ("Empresas · libre", "mora90_pj_livre")]


def credito() -> tuple[pd.DataFrame, list[dict]]:
    sal = {k: SG.serie_mensual(SG.CODIGOS[n]) for k, n in SALDOS.items()}
    indice = SG.deflactor(SG.serie_mensual(SG.CODIGOS["ipca"]))
    filas, tabla = [], []
    for modo in ("nominal", "real"):
        ss = {k: (v if modo == "nominal" else v.div(indice.reindex(v.index))) for k, v in sal.items()}
        tot = ss["total"]
        for k, v in ss.items():
            aa = v / v.shift(12) - 1
            contrib = (v - v.shift(12)) / tot.shift(12).reindex(v.index) * 100
            df = pd.DataFrame({"fecha": T.fecha_fin(v.index),
                               "modo": modo, "componente": k, "aa": aa.to_numpy(), "contrib_pp": contrib.to_numpy()},
                              index=v.index)
            filas.append(df[df.index >= pd.Period(DESDE, "M")])
            var = T.variaciones_saldo(v)
            var["ultimo"] = sal[k].dropna().iloc[-1] / 1e3   # saldo nominal, R$ mil millones (SGS en R$ millones)
            u = sal[k].dropna()
            var["share"] = u.iloc[-1] / sal["total"].dropna().reindex(u.index).dropna().iloc[-1] if k != "total" else 1.0
            tabla.append(T.fila(var, bloque=f"credito_{modo}", orden=list(SALDOS).index(k), fila=NOMBRE_CREDITO[k],
                                unidad_ultimo="brl_mm", unidad_cambio="pct", trimestral=False,
                                destacar=k == "total"))
    return pd.concat(filas, ignore_index=True), tabla


def _serie_sistema(m: pd.DataFrame, serie_id: str) -> pd.Series:
    x = m[m["serie_id"] == serie_id]
    if x.empty:
        raise ValueError(f"bk_sistema_m no tiene {serie_id}")
    return pd.Series(x["valor"].to_numpy(), index=pd.PeriodIndex(x["fecha"], freq="M")).sort_index()


def mora() -> tuple[pd.DataFrame, list[dict]]:
    m = pd.read_parquet(A.GOLD / "bk_sistema_m.parquet", columns=["fecha", "serie_id", "valor"])
    tabla = []
    for i, (nombre, serie_id) in enumerate(MORA):
        s = _serie_sistema(m, serie_id)
        tabla.append(T.fila(T.variaciones_tasa(s, escala=100), bloque="mora", orden=i, fila=nombre,
                            unidad_ultimo="pct", unidad_cambio="pp", trimestral=False, destacar=nombre == "Total"))
    total = _serie_sistema(m, "mora90_total")
    t = pd.DataFrame({"fecha": T.fecha_fin(total.index),
                      "nivel": total.to_numpy(), "d_aa_pp": ((total - total.shift(12)) * 100).to_numpy()}, index=total.index)
    return t[t.index >= pd.Period(DESDE, "M")].reset_index(drop=True), tabla


def roe() -> tuple[pd.DataFrame, list[dict]]:
    g = pd.read_parquet(A.GOLD / "bk_grupo.parquet")
    r = g[(g.optica == B.OPTICA_PANEL) & (g.grupo == B.TODOS) & (g.metrica == "roe_ttm")][
        ["periodo", "fecha", "trimestre", "valor"]]
    r = r.dropna().sort_values("periodo").rename(columns={"valor": "roe"})
    r["cdi_4t"] = SG.cdi_12m().reindex(r["periodo"]).to_numpy()
    r["roe_cdi_pp"] = SG.menos_cdi(r.set_index("periodo")["roe"]).to_numpy() * 100
    r = r[r.periodo >= DESDE.replace("-", "")].reset_index(drop=True)
    tabla = []
    for i, (nombre, col, esc, uu) in enumerate([("ROE 12 meses", "roe", 100, "pct"),
                                                ("ROE − CDI", "roe_cdi_pp", 1, "pp")]):
        var = T.variaciones_trimestrales(r[col].to_numpy() * esc, r[col].iloc[-1], r.trimestre.iloc[-1])
        tabla.append(T.fila(var, bloque="roe", orden=i, fila=nombre, unidad_ultimo=uu,
                            unidad_cambio="pp", trimestral=True, destacar=False))
    return r, tabla


def cuotas() -> pd.DataFrame:
    banco = pd.read_parquet(A.GOLD / "bk_banco.parquet")[["cod_inst", "nombre_corto", "modelo"]]
    panel = pd.read_parquet(A.GOLD / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "valor"])
    bal = pd.read_parquet(A.GOLD / "bank_balances.parquet", columns=["cod_inst", "periodo", "depositos"])
    per = bal["periodo"].max()
    tot = pd.read_parquet(A.GOLD / "bk_cartera_totales.parquet")
    tot = tot[tot["periodo"] == per]

    # Vista, ahorro y plazo no son conceptos del balance curado: se leen del informe 3 (pasivo) del trimestre.
    p3 = A.leer_crudo_tabla(A.ruta_valores(per, 1, 3), ["CodInst", "NomeColuna", "Saldo"])
    p3["Saldo"] = T_IF.saldo(p3["Saldo"])
    p3["CodInst"] = p3["CodInst"].astype(str)   # texto con ceros a la izquierda (columna mixta)

    def col(pref):
        return p3[p3.NomeColuna.str.startswith(pref)].groupby("CodInst").Saldo.sum()

    def de_panel(metrica):
        return panel[(panel.metrica == metrica) & (panel.periodo == per)].set_index("cod_inst").valor

    vistas = {
        "Activos totales": de_panel("share_ativo"),
        "Crédito total": de_panel("share_credito"),
        "Crédito personas": tot[tot["tipo"] == "PF"].set_index("cod_inst")["publicado"],
        "Crédito empresas": tot[tot["tipo"] == "PJ"].set_index("cod_inst")["publicado"],
        "Depósitos totales": bal[bal["periodo"] == per].set_index("cod_inst")["depositos"],
        "Depósitos a la vista": col("Depósitos à Vista"),
        "Depósitos de ahorro": col("Depósitos de Poupança"),
        "Depósitos a plazo": col("Depósitos a Prazo"),
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


def comprobar(cred: pd.DataFrame, cuo: pd.DataFrame) -> None:
    ult = cred[cred.modo == "nominal"].dropna(subset=["contrib_pp"])
    u = ult[ult.fecha == ult.fecha.max()].set_index("componente")
    if {"pf", "pj"} <= set(u.index):
        dif = abs(u.loc["pf", "contrib_pp"] + u.loc["pj", "contrib_pp"] - u.loc["total", "aa"] * 100)
        if not dif < 0.05:
            raise ValueError(f"PF + PJ no suma el total a/a ({dif:.3f} pp)")
    for v, g in cuo.groupby("vista"):
        if not abs(g.cuota.sum() - 1) < 1e-6:
            raise ValueError(f"cuotas de {v} no suman 1")


def main(argv: list[str] | None = None) -> int:
    cred, t1 = credito()
    mor, t2 = mora()
    ro, t3 = roe()
    cuo = cuotas()
    tablas = pd.DataFrame(t1 + t2 + t3)
    comprobar(cred, cuo)
    for nombre, df in (("bk_portada_credito", cred), ("bk_portada_mora", mor), ("bk_portada_roe", ro),
                       ("bk_portada_tablas", tablas), ("bk_portada_cuotas", cuo)):
        A.publicar_gold(nombre, df, fuente="bcb_sgs", dataset="bancos_gold_portada",
                        desde=[f"crudo/{SG.FUENTE}", "crudo/bcb_ifdata/valores", "gold/bk_grupo.parquet",
                               "gold/bk_panel.parquet", "gold/bk_banco.parquet"], nota="Portada v3 del sitio de bancos")
        print(f"{nombre}: {len(df):,} filas")
    print(tablas[["bloque", "fila", "ultimo", "d1", "d3", "d12", "dventana", "corte"]].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
