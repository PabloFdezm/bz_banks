"""Cartera de crédito por banco y modalidad desde IF.Data (informes 11 personas y 13 empresas) y NPL total.

Lo leen preparar_credito_paginas_powerbi.py (tablas cre_* por grupo) y preparar_gold_bancos_cartera.py
(bk_cartera por banco), para que no haya dos lecturas del mismo crudo que puedan divergir.

Por qué los datos son estos:
* **Cartera activa en Brasil de los informes 11 y 13, no la cuenta del balance.** Solo esos informes abren
  por modalidad. El "Total da Carteira" del BCB incluye las operaciones en el exterior (Itaú 2014-T2:
  R$ 124 mil millones solo en empresas); aquí se valida que Σ modalidades + exterior = total publicado.
* **Antes de 2025 los informes de crédito van en el conglomerado financeiro**, con otros códigos que el panel
  (prudencial). El cadastro de cada trimestre dice qué unidades financeiras forman cada conglomerado
  prudencial (``CodConglomeradoFinanceiro`` / ``CodConglomeradoPrudencial``; ``"null"`` = la institución va sola).
* **NPL total** (E–H): hasta 2024, cartera E–H / AA–H del informe 8 (financeiro). Desde 2025 la Res. 4.966
  eliminó la escala AA–H: "Ativos problemáticos" / (total − exterior) del informe 16 (prudencial).
* **Bancos con cambio de cobertura en 2025** (BNDES y varias fintechs): su cartera cambia en la frontera
  mucho más que su balance (``rupturas_frontera``).
"""
from __future__ import annotations

import re

import pandas as pd

import almacen as A
import ifdata_texto as T
import periodos as PER

DEF_MODALIDADES = "bcb_ifdata__credito_modalidades"
TOLERANCIA_FRONTERA = 0.10            # salto propio en 2025-T1 menos el del balance, por banco
PESO_BANCO_GRANDE = 0.10              # un banco con más de esta cuota que no cuadra en la frontera es un error


def definiciones() -> dict:
    return A.leer_definicion(DEF_MODALIDADES)


def escopo(periodo: str) -> str:
    """Escopo en que vienen los informes de crédito: financeiro (2) hasta 2024, prudencial (1) desde 2025."""
    return "1" if periodo >= PER.QUIEBRE_2025 else "2"


def periodos_credito() -> list[str]:
    """Trimestres con los informes 11 y 13 en el escopo que corresponde; falla si hay huecos."""
    hay = {}
    for ruta in A.glob_crudo(A.ruta_cruda("bcb_ifdata", "valores"), "valores_*_r1[13].csv"):
        m = re.fullmatch(r"valores_(\d{6})_([12])_r(1[13])\.csv", ruta.name)
        if m and m.group(2) == escopo(m.group(1)) and A.crudo_con_datos(ruta):
            hay.setdefault(m.group(1), set()).add(m.group(3))
    periodos = sorted(p for p, inf in hay.items() if inf == {"11", "13"})
    if not periodos:
        raise FileNotFoundError("No hay informes 11/13 de IF.data: correr ifdata.py colectar")
    esperado = [f"{p.year}{p.month:02d}" for p in
                pd.period_range(pd.Period(periodos[0], "M"), pd.Period(periodos[-1], "M"), freq="3M").to_timestamp()]
    faltan = sorted(set(esperado) - set(periodos))
    if faltan:
        raise FileNotFoundError(f"Faltan informes 11/13 de IF.data para {faltan}: ifdata.py colectar")
    return periodos


def unidades(periodo: str, panel: list[str]) -> dict[str, str]:
    """Unidad que publica IF.data en ese trimestre → banco del panel (prudencial)."""
    if escopo(periodo) == "1":
        return {c: c for c in panel}
    cad = A.leer_crudo_tabla(A.ruta_cadastro(periodo),
                             ["CodInst", "CodConglomeradoFinanceiro", "CodConglomeradoPrudencial"])
    cad = cad[cad["CodConglomeradoPrudencial"].isin(panel) & (cad["CodInst"] != cad["CodConglomeradoPrudencial"])]
    unidad = cad["CodConglomeradoFinanceiro"].where(~cad["CodConglomeradoFinanceiro"].isin(["null", ""]),
                                                    cad["CodInst"])
    mapa = dict(zip(unidad, cad["CodConglomeradoPrudencial"]))
    if len(set(unidad)) != len(mapa) or (pd.Series(list(zip(unidad, cad["CodConglomeradoPrudencial"])))
                                         .drop_duplicates().map(lambda t: t[0]).duplicated().any()):
        raise ValueError(f"{periodo}: una unidad financeira cae en dos conglomerados prudenciales")
    return mapa


def leer_informe(periodo: str, informe: int, esc: str, mapa: dict[str, str]) -> pd.DataFrame:
    """Filas del informe para las unidades del panel, con el banco prudencial y el saldo numérico."""
    ruta = A.ruta_valores(periodo, esc, informe)
    if not A.existe_crudo(ruta):
        raise FileNotFoundError(f"Falta el crudo {ruta.name}: ifdata.py colectar")
    df = A.leer_crudo_tabla(ruta, ["CodInst", "AnoMes", "Grupo", "Conta", "NomeColuna", "Saldo"])
    if len(df) and not (df["AnoMes"] == periodo).all():
        raise ValueError(f"{ruta.name} trae otro AnoMes")
    # El BCB sirvió 2025-09 con cada fila tres veces: fuera los duplicados exactos; una clave repetida con
    # valores distintos en un banco del panel no se resuelve sola.
    df = df[df["CodInst"].isin(mapa)].drop_duplicates()
    repetidas = df.duplicated(["CodInst", "Grupo", "Conta", "NomeColuna"], keep=False)
    if repetidas.any():
        raise ValueError(f"{ruta.name}: claves repetidas con valores distintos:\n{df[repetidas].head(6)}")
    df = df.copy()
    df["cod_inst"] = df["CodInst"].map(mapa)
    df["valor"] = T.saldo(df["Saldo"])
    return df[["cod_inst", "Grupo", "NomeColuna", "valor"]]


def leer_credito(periodos: list[str], panel: list[str], defs: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Saldo y vencido ≥15 días por banco × modalidad × trimestre (R$), y los totales publicados para validar."""
    filas, totales = [], []
    for periodo in periodos:
        mapa, esc = unidades(periodo, panel), escopo(periodo)
        for tipo, d in defs["tipos"].items():
            df = leer_informe(periodo, d["informe"], esc, mapa)
            # Una modalidad puede tener varios nombres en el tiempo (el BCB renombró el rotativo en 2021-12).
            por_grupo = {g: m["id"] for m in d["modalidades"]
                         for g in ([m["grupo_bcb"]] if isinstance(m["grupo_bcb"], str) else m["grupo_bcb"])}
            sobra = set(df["Grupo"]) - set(por_grupo) - {"null", ""}
            if sobra:
                raise ValueError(f"{periodo} informe {d['informe']}: modalidades nuevas {sobra}; agregarlas a "
                                 f"{DEF_MODALIDADES}.json")
            mod = df[df["Grupo"].isin(por_grupo)]
            for columna, nombre in ((defs["columna_saldo_modalidad"], "saldo"),
                                    (defs["columna_vencido_modalidad"], "vencido")):
                x = mod[mod["NomeColuna"] == columna]
                x = x.groupby(["cod_inst", "Grupo"], as_index=False)["valor"].sum(min_count=1)
                filas.append(x.assign(periodo=periodo, tipo=tipo, modalidad=x["Grupo"].map(por_grupo),
                                      medida=nombre)[["periodo", "cod_inst", "tipo", "modalidad", "medida", "valor"]])
            sin_grupo = df[df["Grupo"].isin(["null", ""])]
            tot = pd.DataFrame({
                "publicado": sin_grupo[sin_grupo["NomeColuna"] == d["total_reportado"]].groupby("cod_inst")["valor"].sum(min_count=1),
                "exterior": sin_grupo[sin_grupo["NomeColuna"] == d["total_exterior"]].groupby("cod_inst")["valor"].sum(min_count=1),
            }).reset_index()
            totales.append(tot.assign(periodo=periodo, tipo=tipo))
    return pd.concat(filas, ignore_index=True), pd.concat(totales, ignore_index=True)


def leer_npl_total(periodos: list[str], panel: list[str], defs: dict) -> pd.DataFrame:
    """Numerador y denominador del NPL total por banco y trimestre (E–H / AA–H; desde 2025, ativos problemáticos)."""
    filas = []
    for periodo in periodos:
        regla = defs["npl"]["desde_2025" if escopo(periodo) == "1" else "hasta_2024"]
        df = leer_informe(periodo, regla["informe"], escopo(periodo), unidades(periodo, panel))
        df = df[df["Grupo"].isin(["null", ""])]
        num = df[df["NomeColuna"].isin(regla["numerador"])].groupby("cod_inst")["valor"].sum(min_count=1)
        den = df[df["NomeColuna"].isin(regla["denominador"])].groupby("cod_inst")["valor"].sum(min_count=1)
        resta = df[df["NomeColuna"].isin(regla.get("denominador_resta", []))].groupby("cod_inst")["valor"].sum()
        den = den.sub(resta.reindex(den.index).fillna(0))
        filas.append(pd.DataFrame({"num": num, "den": den}).reset_index().assign(periodo=periodo))
    return pd.concat(filas, ignore_index=True)


def cruza_frontera(periodos: list[str], k: int) -> pd.Series:
    """True en t si t está en la era prudencial y t−k en la financeira (por posición en ``periodos``)."""
    idx = pd.Index(periodos)
    previo = pd.Series(periodos).shift(k)
    return pd.Series((idx >= PER.QUIEBRE_2025) & (previo < PER.QUIEBRE_2025).to_numpy(), index=periodos)


def rupturas_frontera(credito: pd.DataFrame, bal: pd.DataFrame, periodos: list[str], panel: list[str],
                      anomalos: list[str]) -> list[str]:
    """Bancos cuya cartera cambia en la frontera 2025 más de lo que explica su balance (cambio de cobertura del BCB).

    Se compara el último trimestre financeiro válido con el primero prudencial. Un banco grande que no cuadra
    no es un cambio de cobertura sino un error del cruce de conglomerados: falla.
    """
    validos = [p for p in periodos if p < PER.QUIEBRE_2025 and p not in anomalos]
    if not validos or PER.QUIEBRE_2025 not in periodos:
        return []
    previo = validos[-1]
    cart = credito[credito["medida"] == "saldo"].groupby(["periodo", "cod_inst"])["valor"].sum(min_count=1).unstack()
    bal_c = bal.pivot(index="periodo", columns="cod_inst", values="operacoes_credito")
    salto = cart.loc[PER.QUIEBRE_2025] / cart.loc[previo] - 1
    salto_bal = bal_c.loc[PER.QUIEBRE_2025] / bal_c.loc[previo] - 1
    exceso = (salto - salto_bal.reindex(salto.index)).abs()
    malos = exceso[exceso > TOLERANCIA_FRONTERA].index.tolist()
    peso = cart.loc[PER.QUIEBRE_2025] / cart.loc[PER.QUIEBRE_2025].sum()
    grandes = [b for b in malos if peso.get(b, 0) > PESO_BANCO_GRANDE]
    if grandes:
        raise ValueError(f"Bancos grandes que no cuadran con su balance en la frontera 2025 (¿cruce de conglomerados?): "
                         f"{pd.DataFrame({'cartera': salto, 'balance': salto_bal}).loc[grandes]}")
    return sorted(b for b in malos if b in panel)
