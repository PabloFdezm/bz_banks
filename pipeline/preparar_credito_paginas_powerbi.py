"""Tablas de las hojas "Crédito: panorama" y "Crédito: calidad" del PBIP dual (prefijo ``cre_``), trimestral.

POR QUÉ EXISTE
--------------
Pablo vio la hoja 8 "Bancos" el 2026-10-13 y pidió otro concepto:
no comparar bancos, sino ver **de qué está hecho el crédito** del panel según dos cortes que se cruzan:

* **tipo de institución**: segmento S1–S4, propiedad, modelo de negocio, tradicional vs fintech; siempre grupos,
  nunca bancos sueltos;
* **tipo de crédito**: personas / empresas y sus modalidades (tarjeta, consignado, vehículos, capital de giro…).

Un botón decide qué dimensión se apila. El slicer de tipo tiene solo Total, Personas y Empresas (Pablo,
2026-10-20): apilado por tipo de crédito, "Total" muestra Personas contra Empresas (azul / naranjo) y cada uno
muestra sus modalidades. Del 2026-10-14 al 2026-10-20 "Total" apilaba las 16 modalidades y cada modalidad era un
nodo del slicer; se sacaron (no se elige un producto suelto). "Panorama" muestra nivel,
aportes al crecimiento, tabla y momentum;
"calidad", NPL / NIM / ROE y la tasa de los créditos nuevos contra el CDI.

Por qué los datos son estos y no otros
--------------------------------------
* **IF.data, no SGS.** Solo IF.data abre el crédito por banco (y así por grupo). Es trimestral: nada de m/m. Lo
  mensual del sistema (consignado privado, dirigido / no dirigido) va a la hoja 9, con el SGS.
* **Cartera activa en Brasil de los informes 11 (personas) y 13 (empresas), no la cuenta del balance.** Solo
  esos informes abren por modalidad, y para que el apilado sume hay que usar la misma fuente en el total. El
  "Total da Carteira" del BCB incluye las operaciones en el exterior (Itaú 2014-T2: R$ 124 mil millones solo en
  empresas); aquí un nodo vale la suma de sus modalidades, que es Brasil, y se valida que Σ modalidades +
  exterior = total publicado. No coincide con "Operações de crédito" del balance (hoja 8): la cartera incluye
  tarjetas y leasing, el balance incluye el exterior.
* **Antes de 2025 los informes de crédito van en el conglomerado financeiro**, con otros códigos que el panel
  (prudencial). El cadastro de cada trimestre dice qué unidades financeiras forman cada conglomerado prudencial
  (``CodConglomeradoFinanceiro`` / ``CodConglomeradoPrudencial``; ``"null"`` = la institución va sola). Validación:
  en la frontera 2024-T4 → 2025-T1 cada banco no puede saltar más que su propio balance.
* **NPL** (Pablo: E–H): hasta 2024, cartera E–H / AA–H del informe 8 (financeiro; AA–H es Brasil). Desde 2025
  la Res. 4.966 eliminó la escala AA–H: "Ativos problemáticos" / (total − exterior) del informe 16 (prudencial),
  lo más parecido. Quiebre
  marcado en la página. Por modalidad no hay ni uno ni otro: atraso de 15 días o más (informes 11 y 13).
* **NIM** = resultado de intermediación + provisiones (vienen restadas dentro), 4 trimestres / activo total
  promedio (t y t−4). **ROE** = lucro 4 trimestres / patrimonio promedio. Del panel (``datos/gold``).
* **Bancos con cambio de cobertura en 2025** (BNDES y varias fintechs: su cartera cambia en la frontera mucho más
  que su balance): su nivel salta y la página lo avisa, pero quedan fuera de las variaciones que cruzan 2025-T1.
  Los grandes (Itaú, BB, Bradesco, Caixa, Santander) cuadran con su balance a menos de 3 p.p.
* **2024-T4 se deja vacío en las carteras por modalidad**: el BCB lo sirve con un salto imposible (+20 % el panel,
  Itaú +67 %, y vuelve en 2025-T1). La frontera financeiro → prudencial se valida de 2024-T3 a 2025-T1.
* **Variaciones de grupo con los mismos bancos en los dos lados** (como la hoja 8): la entrada de un banco no es
  crecimiento. Los aportes suman exacto la variación del total. Nada anualizado.
* **Slicers planos** (columna ``etiqueta``, sangrada con espacios eme): en un slicer jerárquico, un clic en el
  padre ("Total", "Propiedad") elige todos sus hijos y las medidas, que piden un solo valor, quedan en blanco. Le
  pasó a Pablo en Desktop el 2026-10-14.
* **Medias de 2 y 4 trimestres** (Pablo, 2026-10-14: series más suaves; IF.data es trimestral, así que "3m" es el
  propio trimestre). Media 4T a/a = Σ de los 4 trimestres / Σ de los mismos 4 de un año antes − 1, armada por
  pares de trimestres con las reglas de la variación simple (mismos bancos, frontera 2025). 2024-T4 (vacío) saca
  su par de la media y se usa el resto; nunca se interpola. Los aportes también suman exacto la variación.
* **NPL por tipo de crédito** ("Ver por", hoja de calidad): el atraso de 15 días o más de los informes 11 y 13, y
  la línea de referencia es el mismo atraso sobre todas las modalidades del nodo. Nunca junto al E–H / ativos
  problemáticos del total: son definiciones distintas (2026-T2: 8,0 % E–H contra ~3,4 % de atraso ≥15 días).
  NIM y ROE no existen por producto: IF.data los publica solo por banco.
* **Contexto de tasas** (``cre_contexto``, trimestral), según la medida de la hoja de calidad: ROE − CDI (media de
  los 12 meses del ROE), NIM con el CDI de los mismos 12 meses, y para el NPL la tasa promedio de los créditos
  nuevos (SGS 20714) contra el CDI (SGS 4389), sistema completo. El spread oficial del BCB (20783) descuenta un
  costo de captación menor que el CDI porque incluye el fondeo del crédito dirigido; por eso dice "vs CDI".

Uso::

    python -X utf8 pipeline/preparar_credito_paginas_powerbi.py   # SGS ya al día (actualizar.py lo refresca al empezar)

La lectura de IF.data (informes 11, 13, 8 y 16) está en ``ifdata_credito.py``; los informes se bajan a mano
(``ifdata.py colectar``). Corre después de ``preparar_bancos_powerbi.py`` (usa ``datos/gold``).
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

import almacen as A
import bancos as B
import ifdata_credito as IC
import periodos as PER
import reglas_gold as RG
import sgs as SG
from bancos import OPTICAS, PANEL, TODOS
from ifdata_credito import cruza_frontera, leer_credito, leer_npl_total, \
    periodos_credito, rupturas_frontera


COLORES = ["#2A78D6", "#E8A33D", "#1BAF7A", "#9B59B6", "#E34948", "#0E9AA7", "#EB6834", "#7A7F87", "#C9B79C",
           "#B58ADB"]
COLOR_PANEL = "#1F2328"
# Personas en tonos fríos, empresas en cálidos, como Personas (azul) y Empresas (naranjo) bajo "Total".
COLORES_MODALIDAD = {
    "pf_tarjeta": "#2A78D6", "pf_consignado": "#0B3C7A", "pf_personal": "#6FA8EC", "pf_vehiculos": "#0E9AA7",
    "pf_hipotecario": "#1BAF7A", "pf_rural": "#7CC9A6", "pf_otros": "#A9B4C2",
    "pj_giro": "#E8A33D", "pj_giro_rotativo": "#F2C76E", "pj_inversion": "#EB6834", "pj_comex": "#E34948",
    "pj_recebibles": "#8C2D04", "pj_infra": "#C0612B", "pj_inmobiliario": "#C9B79C", "pj_rural": "#B8860B",
    "pj_otros": "#7A7F87",
}
COLORES_TIPO = {"PF": "#2A78D6", "PJ": "#EB6834"}
SANGRIA = " "                       # espacio eme: el slicer plano se lee como árbol
VARIACIONES = [("a/a", 1), ("t/t", 2), ("Media 2T a/a", 3), ("Media 4T a/a", 4)]
VARIACIONES_CAL = [("a/a", 1), ("t/t", 2)]
VER = [("Institución", 1), ("Tipo de crédito", 2)]
REFERENCIA_TIPO = "Todo el nodo (atraso ≥15 días)"
SERIES_TASAS = {"Tasa créditos nuevos": "#E34948", "CDI": "#2A78D6", "Brecha (tasa − CDI)": "#8A8984",
                "CDI (media 4T)": "#8A8984"}
VENTANAS = [("8 trimestres", 8, 1), ("12 trimestres", 12, 2), ("20 trimestres", 20, 3), ("Todo", 999, 4)]
APILAR = [("Institución", 1), ("Tipo de crédito", 2)]
MEDIDAS_PANORAMA = [("Crédito", 1), ("Depósitos", 2)]
MEDIDAS_CALIDAD = [("NPL", 1), ("NIM", 2), ("ROE", 3)]


def _ancho(largo: pd.DataFrame, periodos: list[str], cols: list[str]) -> pd.DataFrame:
    return largo.pivot_table(index="periodo", columns="cod_inst", values="valor", aggfunc="sum").reindex(
        index=periodos, columns=cols)


def apilado(hijos: dict[str, pd.DataFrame], k: int, excluir: pd.DataFrame | None = None,
            ventana: int = 1) -> dict[str, pd.DataFrame]:
    """Nivel, variación propia y aporte de cada hijo, y nivel y variación del padre (= Σ hijos).

    Cada matriz es trimestres × bancos (NaN = el banco no informa). Un banco entra a la variación del período t
    contra t−k solo si el padre tiene dato en los dos lados; así los aportes suman exacto la variación del padre.
    Con ``ventana`` > 1 (medias de 2 o 4 trimestres) se suman los pares (t−j, t−j−k), j < ventana, cada uno con
    esa misma regla; un par sin datos (2024-T4) sale de la media, pero se exigen al menos ventana − 1 pares y
    siempre el del propio trimestre t (en 2024-T4 no hay media).
    """
    matrices = list(hijos.values())
    informa = matrices[0].notna()
    for h in matrices[1:]:
        informa = informa | h.notna()
    padre = sum(h.fillna(0) for h in matrices).where(informa)
    ok = padre.notna() & padre.shift(k).notna()
    if excluir is not None:   # bancos con quiebre propio en la frontera 2025: fuera de esa comparación
        ok &= ~excluir
    pares = [ok.shift(j, fill_value=False) for j in range(ventana)]
    usados = sum(m.any(axis=1).astype(int) for m in pares)
    suficiente = (usados >= max(ventana - 1, 1)) & pares[0].any(axis=1)   # el trimestre t, siempre

    def suma(matriz: pd.DataFrame, desfase: int, mascaras: list[pd.DataFrame]) -> pd.Series:
        partes = pd.concat([matriz.shift(j + desfase).where(m).sum(axis=1, min_count=1)
                            for j, m in enumerate(mascaras)], axis=1)
        return partes.sum(axis=1, min_count=1).where(suficiente)

    base = suma(padre, k, pares)
    base = base.where(base != 0)   # base cero (el nodo no existía en t−k): sin variación ni aporte, nunca infinito
    salida = {"_padre_nivel": padre.sum(axis=1, min_count=1),
              "_padre_var": suma(padre, 0, pares) / base - 1,
              "_padre_n": informa.sum(axis=1)}
    for nombre, h in hijos.items():
        h0 = h.fillna(0).where(informa)
        hok = [m & (h0.shift(j).abs() + h0.shift(j + k).abs() > 0) for j, m in enumerate(pares)]
        salida[nombre] = pd.DataFrame({
            "nivel": h.sum(axis=1, min_count=1),
            # Base cero (el producto no existía un año antes en esos bancos): sin variación, nunca infinito.
            "var": (suma(h0, 0, hok) / suma(h0, k, hok).replace(0, np.nan) - 1),
            "aporte": suma(h0 - h0.shift(k), 0, pares) / base,
            "n": h.notna().sum(axis=1),
        })
    return salida


def solo(matriz: pd.DataFrame, cods: list[str]) -> pd.DataFrame:
    """La misma matriz (todas las columnas del panel) con NaN fuera de los bancos dados."""
    return matriz.where(np.broadcast_to(matriz.columns.isin(cods), matriz.shape))


def _tabla_trimestres(periodos: list[str]) -> pd.DataFrame:
    t = pd.DataFrame({"periodo": periodos})
    t["trimestre"] = PER.etiqueta_anio_trimestre(t["periodo"])
    t["orden_trim"] = t["periodo"].astype("int64")
    t["pos"] = np.arange(len(t) - 1, -1, -1, dtype="int64")
    return t


def selecciones(attrs: pd.DataFrame) -> list[dict]:
    """Filas del slicer de institución (bancos.membresia), con los grupos hijos de cada «Todos los grupos»."""
    grupos = B.membresia(attrs).to_dict("records")
    for g in grupos:
        g["hijos"] = ([] if g["columna"] is None or g["grupo"] != TODOS else
                      [(h["grupo"], h["bancos"]) for h in grupos
                       if h["optica_id"] == g["optica_id"] and h["grupo"] != TODOS])
    return grupos


def nodos_tipo(defs: dict) -> list[dict]:
    """Nodos del slicer de tipo de crédito: Total (hijos Personas y Empresas) y Personas y Empresas (hijos, sus
    modalidades). Las modalidades no son nodos: no se elige un producto suelto (Pablo, 2026-10-20)."""
    pf, pj = defs["tipos"]["PF"], defs["tipos"]["PJ"]
    nodos = [{"tipo_key": "total", "nivel": "Total", "nodo": "Total", "hojas": None, "sangria": 0,
              "hijos": [(d["etiqueta"], (t, None)) for t, d in (("PF", pf), ("PJ", pj))]}]
    for tipo, d in (("PF", pf), ("PJ", pj)):
        nodos.append({"tipo_key": tipo, "nivel": "Total", "nodo": d["etiqueta"], "hojas": (tipo, None), "sangria": 1,
                      "hijos": [(m["etiqueta"], (tipo, m["id"])) for m in d["modalidades"]]})
    for i, n in enumerate(nodos):
        n["orden_nodo"] = i
        n["etiqueta"], n["orden_etiqueta"] = SANGRIA * n["sangria"] + n["nodo"], i
    return nodos


def construir() -> dict[str, pd.DataFrame]:
    defs = IC.definiciones()
    inst = B.atributos()
    panel = inst["cod_inst"].tolist()
    periodos = periodos_credito()
    credito, totales = leer_credito(periodos, panel, defs)
    # Trimestres que el BCB sirve con un salto imposible (2024-T4): vacíos, nunca interpolados.
    anomalos = list(PER.ANOMALOS)
    credito_todo, credito = credito, credito[~credito["periodo"].isin(anomalos)]
    trim = _tabla_trimestres(periodos)

    def matriz(tipo: str | None, modalidad: str | None, medida: str = "saldo") -> pd.DataFrame:
        x = credito[credito["medida"] == medida]
        if tipo:
            x = x[x["tipo"] == tipo]
        if modalidad:
            x = x[x["modalidad"] == modalidad]
        return _ancho(x, periodos, panel)

    memo = {}

    def matriz_hoja(hoja, medida="saldo"):
        if (hoja, medida) not in memo:
            memo[hoja, medida] = matriz(None, None, medida) if hoja is None else matriz(hoja[0], hoja[1], medida)
        return memo[hoja, medida]

    sels, nodos = selecciones(inst), nodos_tipo(defs)
    hojas = {n["hojas"]: matriz_hoja(n["hojas"]) for n in nodos}
    hojas.update({h: matriz_hoja(h) for n in nodos for _, h in n["hijos"]})
    bal = pd.read_parquet(A.GOLD / "bank_balances.parquet")
    ruptura = rupturas_frontera(credito, bal, periodos, panel, anomalos)
    excluir = {k: pd.DataFrame(np.outer(cruza_frontera(periodos, k).to_numpy(), np.isin(panel, ruptura)),
                               index=periodos, columns=panel) for k in (1, 4)}
    depositos = bal.pivot(index="periodo", columns="cod_inst", values="depositos").reindex(index=periodos, columns=panel)

    filas = []
    for sel in sels:
        for nodo in nodos:
            nivel_nodo = hojas[nodo["hojas"]]
            combos = []
            # Apilar por institución: hijos = grupos de la óptica (o el grupo elegido, o el panel).
            hijos_inst = sel["hijos"] or [(sel["grupo"] if sel["grupo"] != TODOS else PANEL, sel["bancos"])]
            combos.append(("Institución", "Crédito", {g: solo(nivel_nodo, c) for g, c in hijos_inst}))
            # Apilar por tipo de crédito: hijos = hijos del nodo, dentro de los bancos de la selección.
            combos.append(("Tipo de crédito", "Crédito",
                           {nombre: solo(hojas[hoja], sel["bancos"]) for nombre, hoja in nodo["hijos"]}))
            # Depósitos: no se abren por tipo de crédito; mismos valores en cualquier nodo.
            combos.append(("Institución", "Depósitos", {g: solo(depositos, c) for g, c in hijos_inst}))
            combos.append(("Tipo de crédito", "Depósitos", {"Depósitos": solo(depositos, sel["bancos"])}))
            for apilar, medida, hijos in combos:
                fuera = excluir if medida == "Crédito" else {1: None, 4: None}   # depósitos: sin quiebre
                aa, tt = apilado(hijos, 4, fuera[4]), apilado(hijos, 1, fuera[1])
                aa2, aa4 = apilado(hijos, 4, fuera[4], 2), apilado(hijos, 4, fuera[4], 4)
                for nombre in hijos:
                    filas.append(pd.DataFrame({
                        "inst_key": sel["inst_key"], "tipo_key": nodo["tipo_key"], "apilar": apilar, "medida": medida,
                        "periodo": periodos, "serie": nombre,
                        "nivel": aa[nombre]["nivel"].values / 1e9, "n_bancos": aa[nombre]["n"].values.astype("int64"),
                        "aa": aa[nombre]["var"].values, "tt": tt[nombre]["var"].values,
                        "aporte_aa": aa[nombre]["aporte"].values, "aporte_tt": tt[nombre]["aporte"].values,
                        "aa2": aa2[nombre]["var"].values, "aa4": aa4[nombre]["var"].values,
                        "aporte_aa2": aa2[nombre]["aporte"].values, "aporte_aa4": aa4[nombre]["aporte"].values,
                        "total_nivel": aa["_padre_nivel"].values / 1e9,
                        "total_aa": aa["_padre_var"].values, "total_tt": tt["_padre_var"].values,
                        "total_aa2": aa2["_padre_var"].values, "total_aa4": aa4["_padre_var"].values,
                    }))
    pan = pd.concat(filas, ignore_index=True)
    # Fuera las filas vacías, salvo un hijo que hoy vale 0 pero aportó (si no, los aportes no suman el total).
    aportes = ["aporte_aa", "aporte_tt", "aporte_aa2", "aporte_aa4"]
    pan = pan[(pan["nivel"].notna() & (pan["nivel"] != 0)) | pan[aportes].fillna(0).ne(0).any(axis=1)].copy()
    pan["participacion"] = pan["nivel"] / pan["total_nivel"]
    pan = pan.sort_values(["inst_key", "tipo_key", "apilar", "medida", "serie", "periodo"])
    clave = ["inst_key", "tipo_key", "apilar", "medida", "serie"]
    previa = pan.groupby(clave)["periodo"].shift(4)
    part4 = pan.groupby(clave)["participacion"].shift(4)
    pan["d_participacion"] = np.where(previa == PER.previo_serie(pan["periodo"], 4), pan["participacion"] - part4, np.nan)
    pan = pan.merge(trim, on="periodo")

    npl_total = leer_npl_total(periodos, panel, defs)
    npl_total = npl_total[~npl_total["periodo"].isin(
        [p for p, a in defs.get("trimestres_anomalos", {}).items() if 8 in a["informes"] or 16 in a["informes"]])]
    res = pd.read_parquet(A.GOLD / "bank_resultados.parquet")
    flujos = {c: res.pivot(index="periodo", columns="cod_inst", values=c).reindex(index=periodos, columns=panel)
              for c in ("resultado_intermediacao_financeira", "provisoes_credito", "lucro_liquido")}
    stock = {c: bal.pivot(index="periodo", columns="cod_inst", values=c).reindex(index=periodos, columns=panel)
             for c in ("ativo_total", "patrimonio_liquido")}
    # NIM de esta página: margen antes de provisiones de 4 trimestres / activo medio (t y t−4). No es
    # margem_intermediacao_ttm (neto de provisiones, con transacciones de pago) ni el NIM trimestral de bk_sensibilidad.
    margen_antes_prov_4t = (flujos["resultado_intermediacao_financeira"]
                            - flujos["provisoes_credito"]).rolling(4, min_periods=4).sum()
    lucro4 = flujos["lucro_liquido"].rolling(4, min_periods=4).sum()
    activo_prom = (stock["ativo_total"] + stock["ativo_total"].shift(4)) / 2
    pl_prom = (stock["patrimonio_liquido"] + stock["patrimonio_liquido"].shift(4)) / 2
    npl_num = _ancho(npl_total.rename(columns={"num": "valor"}), periodos, panel)
    npl_den = _ancho(npl_total.rename(columns={"den": "valor"}), periodos, panel)

    def ratio(num: pd.DataFrame, den: pd.DataFrame, bancos_sel: list[str]) -> pd.Series:
        ok = num.notna() & den.notna() & (den > 0)
        ok &= ok.columns.to_series().isin(bancos_sel).values[None, :]
        return num.where(ok).sum(axis=1, min_count=1) / den.where(ok).sum(axis=1, min_count=1)

    filas = []
    for sel in sels:
        series = sel["hijos"] or [(sel["grupo"] if sel["grupo"] != TODOS else PANEL, sel["bancos"])]
        if all(n != PANEL for n, _ in series):
            series = series + [(PANEL, panel)]
        for nodo in nodos:
            if nodo["tipo_key"] == "total":
                num_npl, den_npl = npl_num, npl_den
            else:
                num_npl, den_npl = matriz_hoja(nodo["hojas"], "vencido"), matriz_hoja(nodo["hojas"])
            def fila(ver, medida, nombre, valor):
                filas.append(pd.DataFrame({"inst_key": sel["inst_key"], "tipo_key": nodo["tipo_key"], "ver": ver,
                                           "medida_cal": medida, "periodo": periodos, "serie": nombre,
                                           "valor": valor.values, "d_aa": (valor - valor.shift(4)).values,
                                           "d_tt": (valor - valor.shift(1)).values}))

            for nombre, cods in series:
                fila("Institución", "NPL", nombre, ratio(num_npl, den_npl, cods))
                fila("Institución", "NIM", nombre, ratio(margen_antes_prov_4t, activo_prom, cods))
                fila("Institución", "ROE", nombre, ratio(lucro4, pl_prom, cods))
            # Ver por tipo de crédito: solo NPL, siempre atraso ≥15 días (también la referencia del nodo).
            productos = list(nodo["hijos"])
            if len(productos) > 1:
                productos.append((REFERENCIA_TIPO, nodo["hojas"]))
            for nombre, hoja in productos:
                fila("Tipo de crédito", "NPL", nombre,
                     ratio(matriz_hoja(hoja, "vencido"), matriz_hoja(hoja), sel["bancos"]))
    cal = pd.concat(filas, ignore_index=True)
    # El NPL cambia de definición en 2025 (E–H → ativos problemáticos; perímetro de varios bancos): su cambio
    # a/a o t/t que cruza la frontera no se publica.
    for k, col in ((4, "d_aa"), (1, "d_tt")):
        cruza = cal["periodo"].map(cruza_frontera(periodos, k))
        cal.loc[cruza & (cal["medida_cal"] == "NPL"), col] = np.nan
    cal = cal.dropna(subset=["valor"]).merge(trim, on="periodo")
    cal["npl_def"] = np.where(cal["medida_cal"] != "NPL", "",
                              np.where((cal["tipo_key"] != "total") | (cal["ver"] != "Institución"),
                                       "Vencido ≥15 días",
                                       np.where(cal["periodo"] >= PER.QUIEBRE_2025, "Ativos problemáticos", "E–H")))

    # Contexto de tasas (abajo a la derecha de la hoja de calidad), trimestral.
    mensual = tasas_sgs()
    fin = pd.PeriodIndex([pd.Period(f"{p[:4]}-{p[4:]}", "M") for p in periodos])

    def media_meses(serie: pd.Series, meses: int) -> pd.Series:
        v = serie.rolling(meses, min_periods=meses).mean()
        return pd.Series(v.reindex(fin).to_numpy(), index=periodos)

    cdi4 = pd.Series(SG.cdi_12m().reindex(periodos).to_numpy(), index=periodos)
    cdi_trim = pd.Series(SG.cdi_trimestral().reindex(periodos).to_numpy(), index=periodos)
    filas = []
    for sel in sels:
        series = sel["hijos"] or [(sel["grupo"] if sel["grupo"] != TODOS else PANEL, sel["bancos"])]
        if all(n != PANEL for n, _ in series):
            series = series + [(PANEL, panel)]
        valores = {}
        for nombre, cods in series:
            valores[("ROE", nombre)] = SG.menos_cdi(ratio(lucro4, pl_prom, cods))
            valores[("NIM", nombre)] = ratio(margen_antes_prov_4t, activo_prom, cods)
        valores[("NIM", "CDI (media 4T)")] = cdi4
        for nombre in ("Tasa créditos nuevos", "CDI", "Brecha (tasa − CDI)"):
            valores[("NPL", nombre)] = (cdi_trim if nombre == "CDI" else media_meses(mensual[nombre], 3))
        for (medida, nombre), v in valores.items():
            filas.append(pd.DataFrame({"inst_key": sel["inst_key"], "medida_cal": medida, "periodo": periodos,
                                       "serie": nombre, "valor": v.values}))
    ctx = pd.concat(filas, ignore_index=True).dropna(subset=["valor"]).merge(trim, on="periodo")

    # Dimensiones del PBIP.
    dim_inst = pd.DataFrame([{k: s[k] for k in ("inst_key", "optica", "grupo", "orden_grupo", "orden_optica")}
                             for s in sels])
    dim_inst["orden_optica"] = dim_inst["orden_optica"].astype("int64")
    dim_inst["orden_grupo"] = dim_inst["orden_grupo"].astype("int64")
    # Slicer plano: la óptica ("Propiedad") es la fila "todos los grupos"; sus grupos van sangrados debajo.
    dim_inst["etiqueta"] = np.where(dim_inst["grupo"] == TODOS, dim_inst["optica"], SANGRIA + dim_inst["grupo"])
    dim_inst["orden_etiqueta"] = np.arange(len(dim_inst), dtype="int64")   # sels ya viene en orden de árbol
    dim_tipo = pd.DataFrame([{k: n[k] for k in ("tipo_key", "nivel", "nodo", "orden_nodo", "etiqueta",
                                                "orden_etiqueta")} for n in nodos])
    dim_tipo["orden_nivel"] = dim_tipo["nivel"].map({"Total": 1}).astype("int64")
    dim_tipo["orden_nodo"] = dim_tipo["orden_nodo"].astype("int64")
    nombres = list(dict.fromkeys([PANEL] + [g for _, _, _, gs in OPTICAS for _, g in gs]
                                 + [h for n in nodos for h, _ in n["hijos"]] + ["Depósitos", REFERENCIA_TIPO]
                                 + list(SERIES_TASAS)))
    dim_serie = pd.DataFrame({"serie": nombres, "orden_serie": np.arange(len(nombres), dtype="int64")})
    colores = {PANEL: COLOR_PANEL, "Depósitos": COLOR_PANEL, REFERENCIA_TIPO: COLOR_PANEL, **SERIES_TASAS}
    for _, _, _, gs in OPTICAS:
        for i, (_, g) in enumerate(gs):
            colores[g] = COLORES[i % len(COLORES)]
    for n in nodos:
        for h, hoja in n["hijos"]:
            colores.setdefault(h, COLORES_MODALIDAD.get(hoja[1]) or COLORES_TIPO.get(hoja[0], COLOR_PANEL))
    dim_serie["color"] = dim_serie["serie"].map(colores)

    tablas = {
        "cre_panorama": pan[["inst_key", "tipo_key", "apilar", "medida", "periodo", "trimestre", "orden_trim", "pos",
                             "serie", "nivel", "participacion", "d_participacion", "n_bancos", "aa", "tt", "aa2", "aa4",
                             "aporte_aa", "aporte_tt", "aporte_aa2", "aporte_aa4", "total_nivel", "total_aa",
                             "total_tt", "total_aa2", "total_aa4"]].reset_index(drop=True),
        "cre_calidad": cal[["inst_key", "tipo_key", "ver", "medida_cal", "periodo", "trimestre", "orden_trim", "pos",
                            "serie", "valor", "d_aa", "d_tt", "npl_def"]].reset_index(drop=True),
        "cre_contexto": ctx[["inst_key", "medida_cal", "periodo", "trimestre", "orden_trim", "pos", "serie",
                             "valor"]].reset_index(drop=True),
        "cre_institucion": dim_inst[["inst_key", "optica", "orden_optica", "grupo", "orden_grupo", "etiqueta",
                                     "orden_etiqueta"]],
        "cre_tipo": dim_tipo[["tipo_key", "nivel", "orden_nivel", "nodo", "orden_nodo", "etiqueta", "orden_etiqueta"]],
        "cre_serie": dim_serie,
        "cre_apilar": pd.DataFrame([{"apilar": a, "orden_apilar": np.int64(o)} for a, o in APILAR]),
        "cre_medida": pd.DataFrame([{"medida": m, "orden_medida": np.int64(o)} for m, o in MEDIDAS_PANORAMA]),
        "cre_medida_cal": pd.DataFrame([{"medida_cal": m, "orden_medida_cal": np.int64(o)} for m, o in MEDIDAS_CALIDAD]),
        "cre_variacion": pd.DataFrame([{"variacion": v, "orden_variacion": np.int64(o)} for v, o in VARIACIONES]),
        "cre_variacion_cal": pd.DataFrame([{"variacion_cal": v, "orden_variacion_cal": np.int64(o)}
                                           for v, o in VARIACIONES_CAL]),
        "cre_ver": pd.DataFrame([{"ver": v, "orden_ver": np.int64(o)} for v, o in VER]),
        "cre_ventana": pd.DataFrame([{"ventana": v, "trimestres": np.int64(n), "orden_ventana": np.int64(o)}
                                     for v, n, o in VENTANAS]),
    }
    for t in tablas.values():
        for c in t.columns:
            if t[c].dtype.kind == "f":
                t[c] = t[c].astype("float64")
            elif t[c].dtype.kind in "iu":
                t[c] = t[c].astype("int64")
    tablas["_credito"], tablas["_totales"], tablas["_npl"] = credito_todo, totales, npl_total
    tablas["_credito_limpio"], tablas["_anomalos"], tablas["_ruptura"] = credito, anomalos, ruptura
    tablas["_balance_credito"] = bal.pivot(index="periodo", columns="cod_inst",
                                           values="operacoes_credito").reindex(index=periodos, columns=panel)
    return tablas


def tasas_sgs() -> pd.DataFrame:
    """Tasa promedio de los créditos nuevos (SGS 20714, mensual) contra el CDI del mes (sgs.cdi_mensual), en unidad."""
    s = SG.serie(SG.CODIGOS["tasa_creditos_nuevos"])
    tasa = pd.Series(s.to_numpy() / 100, index=s.index.to_period("M")).groupby(level=0).mean()
    t = pd.DataFrame({"Tasa créditos nuevos": tasa, "CDI": SG.cdi_mensual()}).dropna()
    t["Brecha (tasa − CDI)"] = t["Tasa créditos nuevos"] - t["CDI"]
    return t.asfreq("M")       # meses × series; un mes faltante queda NaN y vacía la media que lo usa


def verificar(t: dict[str, pd.DataFrame]) -> list[str]:
    """Lanza ValueError si algo no cuadra; devuelve avisos (no bloqueantes) para imprimir."""
    avisos = []
    credito, totales, pan, cal = t["_credito"], t["_totales"], t["cre_panorama"], t["cre_calidad"]
    # 1. Σ modalidades (Brasil) + exterior = total publicado por el BCB, por banco, tipo y trimestre.
    suma = credito[credito["medida"] == "saldo"].groupby(["periodo", "cod_inst", "tipo"])["valor"].sum(min_count=1)
    comp = totales.set_index(["periodo", "cod_inst", "tipo"]).join(suma.rename("suma"))
    comp["suma"] = comp["suma"] + comp["exterior"].fillna(0)
    comp = comp[comp["publicado"].abs() > 1e6]
    desvio = (comp["suma"] / comp["publicado"] - 1).abs()
    if (desvio > RG.TOLERANCIA_TOTAL).any():
        raise ValueError(f"Σ modalidades no cuadra con el total del BCB:\n{comp[desvio > RG.TOLERANCIA_TOTAL].head(10)}")
    # 2. Frontera financeiro → prudencial: los bancos con cambio de cobertura (la falla dura está en
    # rupturas_frontera, al construir) se informan; quedan fuera de las variaciones que cruzan 2025-T1.
    if t["_ruptura"]:
        avisos.append(f"bancos con cambio de cobertura en 2025-T1 (fuera de las variaciones que cruzan la frontera): "
                      f"{t['_ruptura']}")
    total_banco = t["_credito_limpio"][t["_credito_limpio"]["medida"] == "saldo"].groupby(
        ["periodo", "cod_inst"])["valor"].sum(min_count=1).unstack()
    bal = t["_balance_credito"]
    previo = max(p for p in total_banco.index if p < PER.QUIEBRE_2025)
    # 2b. Renombre del rotativo de empresas (2021-09 → 2021-12): sin salto propio fuera de lo normal.
    rot = credito[(credito["medida"] == "saldo") & (credito["modalidad"] == "pj_giro_rotativo")]
    rot = rot.groupby("periodo")["valor"].sum()
    if {"202109", "202112"} <= set(rot.index):
        salto_rot = rot["202112"] / rot["202109"] - 1
        if abs(salto_rot) > 0.25:
            raise ValueError(f"el rotativo de empresas salta {salto_rot:+.1%} en el renombre de 2021-12")
        avisos.append(f"rotativo de empresas en el renombre de 2021-12: {salto_rot:+.1%} t/t")
    # 2c. El trimestre anómalo sigue siéndolo (si el BCB lo corrige, quitarlo de la definición).
    for p in t["_anomalos"]:
        sucio = credito[(credito["medida"] == "saldo") & (credito["periodo"].isin([p, previo]))]
        par = sucio.groupby("periodo")["valor"].sum()
        if p in par and previo in par and abs(par[p] / par[previo] - 1) < 0.10:
            avisos.append(f"{p} ya no parece anómalo ({par[p] / par[previo] - 1:+.1%} contra {previo}): revisar "
                          f"trimestres_anomalos en {IC.DEF_MODALIDADES}.json")
    # 3. Cartera activa contra el balance (informativo: la cartera incluye tarjetas y leasing).
    ult = total_banco.index.max()
    r = (total_banco.loc[ult] / bal.loc[ult]).dropna()
    fuera = r[(r < 0.9) | (r > 1.5)]
    if len(fuera):
        avisos.append(f"cartera activa / crédito del balance en {ult} fuera de 0,9–1,5: {fuera.round(2).to_dict()}")
    # 4. Apilados: los hijos suman el total y los aportes suman la variación del total.
    clave = ["inst_key", "tipo_key", "apilar", "medida", "periodo"]
    g = pan.groupby(clave).agg(nivel=("nivel", "sum"), total=("total_nivel", "first"))
    if not np.allclose(g["nivel"], g["total"], rtol=1e-9):
        raise ValueError("los hijos no suman el total en algún apilado")
    for sufijo in ("aa", "tt", "aa2", "aa4"):
        g = pan.groupby(clave).agg(aporte=(f"aporte_{sufijo}", lambda s: s.sum(min_count=1)),
                                   total=(f"total_{sufijo}", "first"))
        ok = g["total"].notna()
        if not np.allclose(g.loc[ok, "aporte"], g.loc[ok, "total"], atol=1e-9):
            malos = g[ok & ~np.isclose(g["aporte"], g["total"], atol=1e-9)]
            raise ValueError(f"los aportes {sufijo} no suman la variación del total:\n{malos.head(8)}")
    u4 = pan[(pan["pos"] == 0) & (pan["inst_key"] == B.CLAVE_PANEL) & (pan["tipo_key"] == "total")
             & (pan["medida"] == "Crédito")]
    if u4["total_aa4"].isna().any():
        raise ValueError("sin media 4T a/a en el último trimestre del panel")
    # 5. Mismo total por cualquier camino: panel × Total por institución = panel × Total por tipo de crédito.
    a = pan[(pan["inst_key"] == "propiedad|todos") & (pan["tipo_key"] == "total") & (pan["medida"] == "Crédito")]
    tot = a.groupby(["apilar", "periodo"])["total_nivel"].first().unstack(0)
    if not np.allclose(tot["Institución"], tot["Tipo de crédito"], rtol=1e-9):
        raise ValueError("el total del panel difiere según la dimensión apilada")
    # 6. Ratios dentro de rangos razonables (último trimestre, panel).
    u = cal[(cal["pos"] == 0) & (cal["serie"] == PANEL) & (cal["tipo_key"] == "total")
            & (cal["inst_key"] == B.CLAVE_PANEL)].set_index("medida_cal")["valor"]
    for medida, (lo, hi) in {"NPL": (0.005, 0.15), "NIM": (0.01, 0.10), "ROE": (0.03, 0.35)}.items():
        if not lo <= u.get(medida, np.nan) <= hi:
            raise ValueError(f"{medida} del panel fuera de [{lo}, {hi}]: {u.get(medida)}")
    # 7. sortBy del PBIP: cada etiqueta con un solo orden y viceversa.
    for nombre, pares in (("cre_institucion", [("optica", "orden_optica"), ("grupo", "orden_grupo"),
                                               ("etiqueta", "orden_etiqueta")]),
                          ("cre_tipo", [("nivel", "orden_nivel"), ("nodo", "orden_nodo"), ("etiqueta", "orden_etiqueta")]),
                          ("cre_serie", [("serie", "orden_serie")]),
                          ("cre_panorama", [("trimestre", "orden_trim")]),
                          ("cre_calidad", [("trimestre", "orden_trim")])):
        for x, y in pares:
            par = t[nombre][[x, y]].drop_duplicates()
            if par[x].duplicated().any() or par[y].duplicated().any():
                raise ValueError(f"{nombre}: {x} y {y} no son 1:1")
    # 8. Ver por tipo de crédito: solo NPL, y con una sola definición (atraso ≥15 días).
    vt = cal[cal["ver"] == "Tipo de crédito"]
    if set(vt["medida_cal"]) != {"NPL"} or set(vt["npl_def"]) != {"Vencido ≥15 días"}:
        raise ValueError("ver por tipo de crédito mezcla medidas o definiciones de NPL")
    faltan = set(pan["serie"]) | set(cal["serie"]) | set(t["cre_contexto"]["serie"])
    faltan -= set(t["cre_serie"]["serie"])
    if faltan or t["cre_serie"]["color"].isna().any():
        raise ValueError(f"series sin fila o sin color en cre_serie: {faltan}")
    return avisos


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args(argv)
    t = construir()
    avisos = verificar(t)
    for nombre, tabla in t.items():
        if nombre.startswith("_"):
            continue
        A.escribir_parquet(tabla, A.INTERMEDIO / f"{nombre}.parquet")
        print(f"{nombre}: {len(tabla):,} filas")
    # El sitio lee panorama, calidad y contexto tal cual, como bk_cre_*.
    for nombre in ("cre_panorama", "cre_calidad", "cre_contexto"):
        A.publicar_gold(f"bk_{nombre}", t[nombre], dataset="bancos_gold_credito", desde=[f"intermedio/{nombre}.parquet"])
    for aviso in avisos:
        print(f"  [aviso] {aviso}")
    pan = t["cre_panorama"]
    u = pan[(pan["pos"] == 0) & (pan["inst_key"] == "propiedad|todos") & (pan["tipo_key"] == "total")
            & (pan["apilar"] == "Institución") & (pan["medida"] == "Crédito")]
    print(f"Último trimestre: {u['trimestre'].iloc[0]}")
    print(u[["serie", "nivel", "participacion", "aa", "aporte_aa"]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
