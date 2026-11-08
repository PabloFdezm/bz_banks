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

import sys

import numpy as np
import pandas as pd

import almacen as A
import periodos as PER
import sgs as SG
import tabla_estandar as T

TOTAL = "credito_total"
MODALIDADES = [  # (fila, grupo, series de sgs.CODIGOS que se suman)
    ("Tarjeta", "Personas", ["credito_pf_tarjeta"]),
    ("Consignado", "Personas", ["credito_pf_consignado_a", "credito_pf_consignado_b", "credito_pf_consignado_c"]),
    ("Personal no consignado", "Personas", ["credito_pf_personal"]),
    ("Vehículos", "Personas", ["credito_pf_vehiculos"]),
    ("Inmobiliario (personas)", "Personas", ["credito_pf_inmobiliario"]),
    ("Rural (personas)", "Personas", ["credito_pf_rural"]),
    ("Empresas libre", "Empresas", ["credito_pj_libre"]),
    ("BNDES (empresas)", "Empresas", ["credito_pj_bndes"]),
    ("Rural (empresas)", "Empresas", ["credito_pj_rural"]),
    ("Inmobiliario (empresas)", "Empresas", ["credito_pj_inmobiliario"]),
]
# Concesiones totales (libres + direccionadas); 20631 = 20632 + 20633.
CONCESIONES = [("Concesiones totales", "concesiones_total"), ("Concesiones personas", "concesiones_pf"),
               ("Concesiones empresas", "concesiones_pj")]
CONCESIONES_GRAFICO = "concesiones_total"   # la serie del gráfico concesiones contra stock


def _serie(nombre: str) -> pd.Series:
    return SG.serie_mensual(SG.CODIGOS[nombre])


def suma(codigos):
    partes = [_serie(c) for c in codigos]
    x = partes[0]
    for p in partes[1:]:
        x = x.add(p, fill_value=np.nan)
    return x.dropna()


def fila(bloque, orden, nombre, grupo, var, uu, uc, trimestral=False):
    return T.fila(var, bloque=bloque, orden=orden, fila=nombre, grupo=grupo, unidad_ultimo=uu,
                  unidad_cambio=uc, trimestral=trimestral)


def hp(y, lam):
    n = len(y)
    D = np.zeros((n - 2, n))
    for i in range(n - 2):
        D[i, i:i + 3] = [1, -2, 1]
    return np.linalg.solve(np.eye(n) + lam * D.T @ D, y)


def main(argv: list[str] | None = None) -> int:
    tot = _serie(TOTAL).dropna()
    tablas, series = [], []
    mods = {}
    for i, (n, g, cs) in enumerate(MODALIDADES):
        x = suma(cs)
        mods[n] = x
        var = T.variaciones_saldo(x)
        var["ultimo"] = x.iloc[-1] / 1e3
        var["share"] = x.iloc[-1] / tot[x.index[-1]]
        tablas.append(fila("tipos", i, n, g, var, "brl_mm", "pct"))
        series += T.series_largas(x / x.shift(12) - 1, f"aa|{n}")
    var = T.variaciones_saldo(tot)
    var["ultimo"] = tot.iloc[-1] / 1e3
    var["share"] = 1.0
    tablas.append(fila("tipos", 99, "Total", "Total", var, "brl_mm", "pct"))
    series += T.series_largas(tot / tot.shift(12) - 1, "aa|Total")
    # Contribución en el último mes común a todas las modalidades.
    m = min(x.index[-1] for x in mods.values())
    otros = tot - sum(x.reindex(tot.index) for x in mods.values())
    for i, (n, x) in enumerate(list(mods.items()) + [("Otros", otros), ("Total", tot)]):
        d1 = (x[m] - x[m - 1]) / tot[m - 1] * 100
        d3 = (x[m - 2:m].mean() - x[m - 5:m - 3].mean()) / tot[m - 5:m - 3].mean() * 100
        d12 = (x[m] - x[m - 12]) / tot[m - 12] * 100
        dv = (x[m - 11:m].mean() - x[m - 23:m - 12].mean()) / tot[m - 23:m - 12].mean() * 100
        grupo = next((g for nn, g, _ in MODALIDADES if nn == n), "Otros" if n == "Otros" else "Total")
        # Último = saldo de la modalidad (R$ mil millones); los cambios son contribuciones en pp.
        tablas.append(fila("contrib", i, n, grupo, {"ultimo": x[m] / 1e3, "share": x[m] / tot[m], "d1": d1, "d3": d3, "d12": d12, "dventana": dv,
                                                    "corte": PER.mes_corto(m)}, "brl_mm", "pp"))
    for i, (n, c) in enumerate(CONCESIONES):
        x = _serie(c).dropna()
        var = T.variaciones_saldo(x, flujo=True)
        var["ultimo"] = x.iloc[-1] / 1e3
        tablas.append(fila("conc", i, n, "Concesiones", var, "brl_mm", "pct"))
        if c == CONCESIONES_GRAFICO:
            f12 = x.rolling(12).sum()
            series += T.series_largas(f12 / f12.shift(12) - 1, "conc12_aa")
    var = T.variaciones_saldo(tot)
    var["ultimo"] = tot.iloc[-1] / 1e3
    tablas.append(fila("conc", 9, "Saldo total", "Stock", var, "brl_mm", "pct"))
    series += T.series_largas(tot / tot.shift(12) - 1, "stock_aa")
    # Crédito/PIB, HP unilateral trimestral.
    cp = _serie("credito_pib").dropna()
    q = cp.groupby(cp.index.asfreq("Q")).mean()
    tend = pd.Series(np.nan, index=q.index)
    for i in range(20, len(q)):
        tend.iloc[i] = hp(q.values[:i + 1], 400000)[-1]   # unilateral: el punto t solo ve datos hasta t
    brecha = q - tend
    for nombre, s in (("cpib_nivel", q), ("cpib_tendencia", tend), ("cpib_brecha", brecha)):
        series += T.series_largas(s, nombre)
    for i, (n, s, uu) in enumerate((("Crédito/PIB", q, "pct_nivel"), ("Tendencia HP", tend, "pct_nivel"), ("Brecha", brecha, "pp"))):
        s = s.dropna()
        p = s.index[-1]
        var = T.variaciones_trimestrales(s.to_numpy(), s.iloc[-1], PER.etiqueta_trimestre(f"{p.year}{p.quarter * 3:02d}"))
        tablas.append(fila("ciclo", i, n, "Ciclo", var, uu, "pp", True))
    t = pd.DataFrame(tablas)
    sr = pd.DataFrame(series)
    c = t[t.bloque == "contrib"].set_index("fila")
    for col in ("d1", "d3", "d12", "dventana"):
        dif = abs(c.drop("Total")[col].sum() - c.loc["Total", col])
        if not dif < 1e-6:
            raise ValueError(f"las contribuciones no suman el total en {col}: {dif}")
    for nombre, df in (("bk_cred_tablas", t), ("bk_cred_series", sr)):
        A.publicar_gold(nombre, df, fuente="bcb_sgs", dataset="bancos_gold_pag_credito", desde=[f"crudo/{SG.FUENTE}"], nota="Página Crédito v3")
        print(f"{nombre}: {len(df):,} filas")
    print(t[["bloque", "fila", "ultimo", "d1", "d3", "d12", "dventana", "corte"]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
