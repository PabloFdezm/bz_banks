# -*- coding: utf-8 -*-
"""Tablas de la página Crédito v3 (canvas «Bancos Brasil — propuesta visual», tablero 06).

Cuatro láminas, cada una con gráfico (izquierda) y tabla descriptiva estándar (derecha):
  01 por tipo de crédito, 02 contribución al crecimiento del último mes, 03 concesiones contra stock,
  04 crédito/PIB con tendencia HP unilateral y brecha.

TABLAS (datos/gold/)
- bk_cred_tablas: bloque, orden, fila, grupo, ultimo, d1, d3, d12, dventana, corte, unidad_ultimo,
  unidad_cambio, trimestral. Misma estructura que bk_portada_tablas, así la página usa una sola tabla.
- bk_cred_series: serie, fecha, valor (largo). Series: conc12_aa, stock_aa (fracción), cpib_nivel,
  cpib_tendencia (%), cpib_brecha (pp).

REGLAS
- Modalidades: códigos SGS identificados cuadrando montos (consignado = 20576 + 20577 + 20578; libres PF
  ≈ suma de modalidades). «Otros» = total − modalidades listadas, para que la contribución sume el total.
- Contribución (pp): cambio del saldo de la modalidad sobre el saldo total del período base, en las mismas
  cuatro ventanas que la tabla estándar; suma el crecimiento del total en cada ventana.
- Concesiones: flujo mensual; 12m/12m compara sumas de doce meses; conc12_aa = suma 12m a/a.
- HP unilateral sobre el promedio trimestral de SGS 20622, λ = 400.000 (convención del BIS), con
  al menos 20 trimestres de historia; el punto t usa solo datos hasta t.
"""
from __future__ import annotations

import io
import sys

import numpy as np
import pandas as pd

import almacen as A
from preparar_gold_bancos_portada import BANKS, serie, mes, variaciones_saldo

COMANDO = "python -X utf8 preparar_gold_bancos_pag_credito.py"
TOTAL = 20539
MODALIDADES = [  # (fila, grupo, códigos)
    ("Tarjeta", "Personas", [20590]),
    ("Consignado", "Personas", [20576, 20577, 20578]),
    ("Personal no consignado", "Personas", [20574]),
    ("Vehículos", "Personas", [20581]),
    ("Inmobiliario (personas)", "Personas", [20612]),
    ("Rural (personas)", "Personas", [20609]),
    ("Empresas libre", "Empresas", [20543]),
    ("BNDES (empresas)", "Empresas", [20604]),
    ("Rural (empresas)", "Empresas", [20597]),
    ("Inmobiliario (empresas)", "Empresas", [20600]),
]
CONCESIONES = [("Concesiones libres", 20631), ("Concesiones personas", 20633), ("Concesiones empresas", 20632)]


def suma(codigos):
    partes = [serie(c) for c in codigos]
    if any(p is None for p in partes):
        return None
    x = partes[0]
    for p in partes[1:]:
        x = x.add(p, fill_value=np.nan)
    return x.dropna()


def fila(bloque, orden, nombre, grupo, var, uu, uc, trimestral=False):
    return {"bloque": bloque, "orden": orden, "fila": nombre, "grupo": grupo, "unidad_ultimo": uu,
            "unidad_cambio": uc, "trimestral": trimestral, **var}


def hp(y, lam):
    n = len(y)
    D = np.zeros((n - 2, n))
    for i in range(n - 2):
        D[i, i:i + 3] = [1, -2, 1]
    return np.linalg.solve(np.eye(n) + lam * D.T @ D, y)


def main() -> int:
    tot = serie(TOTAL).dropna()
    tablas, series = [], []
    mods = {}
    for i, (n, g, cs) in enumerate(MODALIDADES):
        x = suma(cs)
        if x is None:
            continue
        mods[n] = x
        var = variaciones_saldo(x)
        var["ultimo"] = x.iloc[-1] / 1e3
        var["share"] = x.iloc[-1] / tot[x.index[-1]]
        tablas.append(fila("tipos", i, n, g, var, "brl_mm", "pct"))
        a = (x / x.shift(12) - 1).dropna()
        series += [{"serie": f"aa|{n}", "fecha": p.to_timestamp(how="end").strftime("%Y-%m-%d"), "valor": v} for p, v in a.items()]
    # Total siempre presente (tabla y gráfico)
    var = variaciones_saldo(tot)
    var["ultimo"] = tot.iloc[-1] / 1e3
    var["share"] = 1.0
    tablas.append(fila("tipos", 99, "Total", "Total", var, "brl_mm", "pct"))
    a = (tot / tot.shift(12) - 1).dropna()
    series += [{"serie": "aa|Total", "fecha": p.to_timestamp(how="end").strftime("%Y-%m-%d"), "valor": v} for p, v in a.items()]
    # contribución en el último mes común a todas las modalidades
    m = min(x.index[-1] for x in mods.values())
    otros = tot - sum(x.reindex(tot.index) for x in mods.values())
    for i, (n, x) in enumerate(list(mods.items()) + [("Otros", otros), ("Total", tot)]):
        T = tot
        d1 = (x[m] - x[m - 1]) / T[m - 1] * 100
        d3 = (x[m - 2:m].mean() - x[m - 5:m - 3].mean()) / T[m - 5:m - 3].mean() * 100
        d12 = (x[m] - x[m - 12]) / T[m - 12] * 100
        dv = (x[m - 11:m].mean() - x[m - 23:m - 12].mean()) / T[m - 23:m - 12].mean() * 100
        grupo = next((g for nn, g, _ in MODALIDADES if nn == n), "Otros" if n == "Otros" else "Total")
        # Último = saldo de la modalidad (R$ mil millones); los cambios son contribuciones en pp
        tablas.append(fila("contrib", i, n, grupo, {"ultimo": x[m] / 1e3, "share": x[m] / T[m], "d1": d1, "d3": d3, "d12": d12, "dventana": dv,
                                                    "corte": mes(m)}, "brl_mm", "pp"))
    # concesiones contra stock
    for i, (n, c) in enumerate(CONCESIONES):
        x = serie(c)
        if x is None:
            continue
        x = x.dropna()
        var = {"ultimo": x.iloc[-1] / 1e3, "d1": x.iloc[-1] / x.iloc[-2] - 1,
               "d3": x.iloc[-3:].mean() / x.iloc[-6:-3].mean() - 1, "d12": x.iloc[-1] / x.iloc[-13] - 1,
               "dventana": x.iloc[-12:].sum() / x.iloc[-24:-12].sum() - 1, "corte": mes(x.index[-1])}
        tablas.append(fila("conc", i, n, "Concesiones", var, "brl_mm", "pct"))
        if c == 20631:
            f12 = x.rolling(12).sum()
            a = (f12 / f12.shift(12) - 1).dropna()
            series += [{"serie": "conc12_aa", "fecha": p.to_timestamp(how="end").strftime("%Y-%m-%d"), "valor": v} for p, v in a.items()]
    var = variaciones_saldo(tot)
    var["ultimo"] = tot.iloc[-1] / 1e3
    tablas.append(fila("conc", 9, "Saldo total", "Stock", var, "brl_mm", "pct"))
    a = (tot / tot.shift(12) - 1).dropna()
    series += [{"serie": "stock_aa", "fecha": p.to_timestamp(how="end").strftime("%Y-%m-%d"), "valor": v} for p, v in a.items()]
    # crédito/PIB, HP unilateral trimestral
    cp = serie(20622).dropna()
    q = cp.groupby(cp.index.asfreq("Q")).mean()
    tend = pd.Series(np.nan, index=q.index)
    for i in range(20, len(q)):
        tend.iloc[i] = hp(q.values[:i + 1], 400000)[-1]
    brecha = q - tend
    etiqueta = lambda p: f"{p.quarter}T{str(p.year)[2:]}"
    for nombre, s in (("cpib_nivel", q), ("cpib_tendencia", tend), ("cpib_brecha", brecha)):
        series += [{"serie": nombre, "fecha": p.to_timestamp(how="end").strftime("%Y-%m-%d"), "valor": v} for p, v in s.dropna().items()]
    for i, (n, s, uu) in enumerate((("Crédito/PIB", q, "pct_nivel"), ("Tendencia HP", tend, "pct_nivel"), ("Brecha", brecha, "pp"))):
        s = s.dropna()
        tablas.append(fila("ciclo", i, n, "Ciclo", {"ultimo": s.iloc[-1], "d1": s.iloc[-1] - s.iloc[-2], "d3": np.nan,
                                                    "d12": s.iloc[-1] - s.iloc[-5], "dventana": s.iloc[-4:].mean() - s.iloc[-8:-4].mean(),
                                                    "corte": etiqueta(s.index[-1])}, uu, "pp", True))
    t = pd.DataFrame(tablas)
    sr = pd.DataFrame(series)
    # comprobación: las contribuciones suman el crecimiento del total en cada ventana
    c = t[t.bloque == "contrib"].set_index("fila")
    for col in ("d1", "d3", "d12", "dventana"):
        dif = abs(c.drop("Total")[col].sum() - c.loc["Total", col])
        assert dif < 1e-6, f"contribuciones no suman el total en {col}: {dif}"
    for nombre, df in (("bk_cred_tablas", t), ("bk_cred_series", sr)):
        b = io.BytesIO()
        df.to_parquet(b, index=False)
        A.guardar_derivado("bcb_sgs", "bancos_gold_pag_credito", f"{nombre}.parquet", b.getvalue(),
                           desde=["bcb_sgs"], como=COMANDO, nota="Página Crédito v3")
        A.escribir_atomico(BANKS / f"{nombre}.parquet", b.getvalue())
        print(f"{nombre}: {len(df):,} filas")
    print(t[["bloque", "fila", "ultimo", "d1", "d3", "d12", "dventana", "corte"]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
