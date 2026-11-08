#!/usr/bin/env python3
"""Prepara balances y resultados trimestrales de bancos brasileños para Power BI.

POR QUÉ EXISTE
--------------
IF.data publica informes planos por trimestre, escopo y cuenta. Tres cosas impiden
usar esos CSV directamente en un panel:

1. el informe 4 (Demonstração de Resultado) viene acumulado según la Lei 4.595, con
   reset en julio: marzo y septiembre son acumulados de enero-marzo y julio-septiembre,
   mientras junio y diciembre son acumulados de enero-junio y julio-diciembre;
2. los códigos de cuenta cambian en la frontera COSIF 2025-03, así que la serie
   continua no puede armarse por código;
3. la capa cruda completa trae todas las instituciones del escopo prudencial, y el
   panel usa un universo aprobado por Pablo.

Este módulo lee únicamente el crudo ya descargado por `ifdata.py colectar`, no sale a
la red, filtra el universo declarado en `definiciones/bcb_ifdata__bancos_balances.json`,
des-acumula los flujos, conserva intactos los stocks y escribe parquets atómicos en
`datos/gold/`.

Receta:

    python pipeline/ifdata.py colectar --desde 201403 --hasta 202606 --escopo prudencial \
        --informe 2 --informe 3 --informe 4
    python pipeline/preparar_bancos_powerbi.py
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import pandas as pd

import almacen as A
import bancos as B
import ifdata_texto as IF
import periodos as PER

VALORES = A.ruta_cruda("bcb_ifdata", "valores")

INFORMES = (2, 3, 4)
ESCOPO = "prudencial"

COLUMNAS_VALORES = [
    "TipoInstituicao",
    "CodInst",
    "AnoMes",
    "NomeRelatorio",
    "NumeroRelatorio",
    "Grupo",
    "Conta",
    "NomeColuna",
    "DescricaoColuna",
    "Saldo",
]

COLUMNAS_CADASTRO = [
    "CodInst",
    "NomeInstituicao",
    "Tcb",
    "Td",
    "Tc",
    "Sr",
    "SegmentoTb",
    "Atividade",
    "Situacao",
    "CodConglomeradoPrudencial",
]

CONCEPTOS_BALANCE = [
    "ativo_total",
    "operacoes_credito",
    "operacoes_credito_liquidas",
    "depositos",
    "captacoes",
    "passivo_total",
    "patrimonio_liquido",
]

CONCEPTOS_RESULTADO = [
    "resultado_intermediacao_financeira",
    "outras_receitas_despesas",
    "resultado_antes_tributacao_participacoes",
    "imposto_renda_contribuicao_social",
    "participacoes_lucro",
    "lucro_liquido",
    "despesas_pessoal",
    "despesas_administrativas",
    "despesas_tributarias",
    # Líneas para que el puente del resultado cierre.
    "provisoes_credito",
    "resultado_transacoes_pagamento",
    "resultado_nao_operacional",
    "rendas_tarifas_bancarias",
    "rendas_prestacao_servicos",
]

CLAVE_HECHO = ["periodo", "cod_inst", "num_informe", "cuenta_id"]
CLAVE_ENTIDAD = ["periodo", "cod_inst"]

COLUMNAS_HECHOS = [
    "periodo",
    "fecha",
    "anio",
    "trimestre",
    "escopo",
    "cod_inst",
    "institucion_bcb",
    "nombre_corto",
    "categoria",
    "num_informe",
    "informe",
    "era",
    "cod_cuenta",
    "cuenta",
    "cuenta_base",
    "grupo",
    "grupo_norm",
    "composicion",
    "cuenta_id",
    "concepto_era",
    "concepto",
    "tipo_valor",
    "es_acumulado",
    "valor_publicado",
    "valor",
]


def slug(texto: str, maximo: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (texto or "").casefold()).strip("_")
    return s[:maximo].strip("_") or "sin_nombre"


def sin_formula(texto: str) -> str:
    return IF.limpiar(texto).split("=", 1)[0].strip()


def cuenta_original_norm(texto: str) -> str:
    return re.sub(r"\s+", " ", IF.normalizar(sin_formula(texto)))


def cuenta_base(texto: str) -> str:
    base = re.sub(r"\([^)]*\)", " ", IF.normalizar(sin_formula(texto)))
    return re.sub(r"\s+", " ", base).strip()


def cargar_definiciones() -> dict:
    defs = A.leer_definicion(B.DEF_BALANCES)
    bancos = {b["cod_inst"]: b for b in B.universo()}
    lookup = {}
    tipos = {}
    for concepto, meta in defs.get("conceptos", {}).items():
        tipos[concepto] = meta["tipo_valor"]
        numero = int(meta["num_informe"])
        for regla in meta["cuentas_base"]:
            # Una regla es el nombre de la cuenta, o un objeto que además fija la era y/o el grupo: hace falta
            # cuando el mismo nombre significa otra cosa en cada era ("operacoes de credito" es bruto en el
            # COSIF viejo y neto en el 2025) o se repite en varios grupos ("valor contabil bruto").
            if isinstance(regla, str):
                regla = {"cuenta_base": regla}
            clave = (numero, regla["cuenta_base"], regla.get("era"), regla.get("grupo_norm"))
            if clave in lookup:
                raise ValueError(f"Concepto duplicado para {clave}: {lookup[clave]} y {concepto}")
            lookup[clave] = concepto
    defs["_bancos"] = bancos
    defs["_lookup_conceptos"] = lookup
    defs["_tipos_concepto"] = tipos
    return defs


def periodos_disponibles() -> list[str]:
    conjuntos = []
    for informe in INFORMES:
        encontrados = set()
        for ruta in A.glob_crudo(VALORES, f"valores_*_1_r{informe}.csv"):
            m = re.fullmatch(r"valores_(\d{6})_1_r\d+\.csv", ruta.name)
            if m and A.crudo_con_datos(ruta):
                encontrados.add(m.group(1))
        conjuntos.append(encontrados)
    if not conjuntos or not all(conjuntos):
        raise FileNotFoundError("Faltan crudos de informes 2/3/4; correr primero ifdata.py colectar")
    return sorted(set.intersection(*conjuntos))


def leer_cadastro(periodo: str, codes: set[str]) -> pd.DataFrame:
    ruta = A.ruta_cadastro(periodo)
    columnas = ["cod_inst", "institucion_bcb", "tcb", "td", "tc", "sr", "segmento", "actividad", "situacion"]
    if not A.existe_crudo(ruta):
        return pd.DataFrame(columns=columnas)
    todo = A.leer_crudo_tabla(ruta, COLUMNAS_CADASTRO)
    df = todo[todo["CodInst"].isin(codes)].copy()
    # Algunos conglomerados (Daycoval, XP desde 2025-T4) traen Sr nulo en su propia fila, pero sus
    # instituciones sí lo traen: se toma el valor más frecuente entre ellas.
    sr_grupo = (todo.assign(Sr=todo["Sr"].map(IF.nulo))
                .query("Sr != '' and CodConglomeradoPrudencial.isin(@codes)", engine="python")
                .groupby("CodConglomeradoPrudencial")["Sr"]
                .agg(lambda x: x.value_counts().sort_index().idxmax()))
    propio = df["Sr"].map(IF.nulo)
    df["Sr"] = propio.mask(propio == "", df["CodInst"].map(sr_grupo)).fillna("")
    df = df.rename(columns={
        "CodInst": "cod_inst",
        "NomeInstituicao": "institucion_bcb",
        "Tcb": "tcb",
        "Td": "td",
        "Tc": "tc",
        "Sr": "sr",
        "SegmentoTb": "segmento",
        "Atividade": "actividad",
        "Situacao": "situacion",
    })
    df["institucion_bcb"] = df["institucion_bcb"].map(IF.limpiar)
    for columna in ["tcb", "td", "tc", "sr", "segmento", "actividad", "situacion"]:
        df[columna] = df[columna].map(IF.nulo)
    return df[columnas]


def nombres_por_periodo(periodos: list[str], codes: set[str]) -> dict[str, dict[str, str]]:
    mapas = {}
    for periodo in periodos:
        df = leer_cadastro(periodo, codes)
        mapas[periodo] = dict(zip(df["cod_inst"], df["institucion_bcb"]))
    return mapas


def leer_valores(periodo: str, informe: int, codes: set[str]) -> pd.DataFrame:
    ruta = A.ruta_valores(periodo, 1, informe)
    if not A.existe_crudo(ruta):
        raise FileNotFoundError(f"Falta el crudo {ruta.name}")
    todo = A.leer_crudo_tabla(ruta, COLUMNAS_VALORES)
    df = todo[todo["CodInst"].isin(codes)]
    if not len(df):
        return pd.DataFrame()
    return df.reset_index(drop=True).drop_duplicates()


def transformar_valores(df: pd.DataFrame, periodo: str, informe: int,
                        nombres: dict[str, str], bancos: dict[str, dict]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    if not df["AnoMes"].isin([periodo]).all():
        raise ValueError(f"El crudo de {periodo} informe {informe} trae otro AnoMes")
    if not df["TipoInstituicao"].isin(["1"]).all():
        raise ValueError(f"El crudo de {periodo} informe {informe} trae otro TipoInstituicao")
    out = df.rename(columns={
        "CodInst": "cod_inst",
        "NomeRelatorio": "informe",
        "NumeroRelatorio": "num_informe",
        "Grupo": "grupo",
        "Conta": "cod_cuenta",
        "NomeColuna": "cuenta",
        "DescricaoColuna": "composicion",
        "Saldo": "saldo_crudo",
    }).copy()
    out["periodo"] = periodo
    out["escopo"] = ESCOPO
    out["num_informe"] = out["num_informe"].map(IF.nulo).astype(int)
    if not out["num_informe"].eq(informe).all():
        raise ValueError(f"El crudo de {periodo} informe {informe} trae otro NumeroRelatorio")
    out["informe"] = out["informe"].map(IF.limpiar)
    out["grupo"] = out["grupo"].map(IF.nulo)
    out["cod_cuenta"] = out["cod_cuenta"].map(IF.nulo)
    out["cuenta"] = out["cuenta"].map(IF.limpiar)
    out["composicion"] = out["composicion"].map(IF.nulo)
    out["valor_publicado"] = IF.saldo(out["saldo_crudo"])
    out["institucion_bcb"] = out["cod_inst"].map(nombres).fillna("")
    out["nombre_corto"] = out["cod_inst"].map(lambda c: bancos[c]["nombre_corto"])
    out["categoria"] = out["cod_inst"].map(lambda c: bancos[c]["categoria"])
    out["grupo_norm"] = out["grupo"].map(cuenta_original_norm)
    out["cuenta_original_norm"] = out["cuenta"].map(cuenta_original_norm)
    out["cuenta_base"] = out["cuenta"].map(cuenta_base)
    out["era"] = out["periodo"].map(lambda p: "cosif_2025" if p >= PER.QUIEBRE_2025 else "cosif_pre2025")
    out["anio"] = out["periodo"].str[:4].astype("int64")
    out["trimestre"] = (out["periodo"].str[4:].astype("int64") // 3).astype("int64")
    out["fecha"] = PER.fin_de_mes(out["periodo"])
    out["cuenta_id"] = [
        f"r{num}_{hashlib.sha1(f'{num}|{cod}|{norm}|{grp}'.encode('utf-8')).hexdigest()[:12]}"
        for num, cod, norm, grp in zip(out["num_informe"], out["cod_cuenta"],
                                       out["cuenta_original_norm"], out["grupo_norm"])
    ]
    return out.drop(columns=["TipoInstituicao", "AnoMes", "saldo_crudo", "cuenta_original_norm"])


def construir_hechos(periodos: list[str], defs: dict) -> pd.DataFrame:
    bancos = defs["_bancos"]
    codes = set(bancos)
    nombres = nombres_por_periodo(periodos, codes)
    partes = []
    for periodo in periodos:
        for informe in INFORMES:
            crudo = leer_valores(periodo, informe, codes)
            tabla = transformar_valores(crudo, periodo, informe, nombres[periodo], bancos)
            if len(tabla):
                partes.append(tabla)
    if not partes:
        raise ValueError("No hay filas de los bancos seleccionados en el crudo")
    hechos = pd.concat(partes, ignore_index=True)
    return completar_conceptos_y_valores(hechos, defs)


def completar_conceptos_y_valores(hechos: pd.DataFrame, defs: dict) -> pd.DataFrame:
    lookup = defs["_lookup_conceptos"]
    tipos_concepto = defs["_tipos_concepto"]
    excepciones = defs.get("excepciones_stock", {})

    ambiguas = (
        hechos.groupby(["num_informe", "era", "cuenta_base"])["cod_cuenta"]
        .nunique()
        .rename("n")
        .reset_index()
    )
    claves_ambiguas = set(map(tuple, ambiguas.loc[ambiguas["n"] > 1, ["num_informe", "era", "cuenta_base"]].values))

    hechos["concepto_era"] = [
        f"r{num}_{slug(base)}" + (f"_{slug(grupo)}" if (num, era, base) in claves_ambiguas else "")
        for num, era, base, grupo in zip(hechos["num_informe"], hechos["era"],
                                         hechos["cuenta_base"], hechos["grupo_norm"])
    ]
    def concepto_de(num: int, era: str, base: str, grupo: str) -> str | None:
        """La regla más específica gana: era y grupo, solo era, solo grupo, solo el nombre."""
        for clave in ((num, base, era, grupo), (num, base, era, None), (num, base, None, grupo), (num, base, None, None)):
            if clave in lookup:
                return lookup[clave]
        return None

    hechos["concepto"] = [
        concepto_de(num, era, base, grupo)
        for num, era, base, grupo in zip(hechos["num_informe"], hechos["era"], hechos["cuenta_base"],
                                         hechos["grupo_norm"])
    ]

    def tipo_de_fila(num: int, base: str, concepto: str | None) -> str:
        if concepto and concepto in tipos_concepto:
            return tipos_concepto[concepto]
        if num in (2, 3):
            return "stock"
        if base in excepciones.get(str(num), []):
            return "stock"
        return "flujo"

    hechos["tipo_valor"] = [
        tipo_de_fila(num, base, concepto)
        for num, base, concepto in zip(hechos["num_informe"], hechos["cuenta_base"], hechos["concepto"])
    ]
    hechos["es_acumulado"] = hechos["num_informe"].eq(4) & hechos["tipo_valor"].eq("flujo")
    return desacumular(hechos)[COLUMNAS_HECHOS]


def desacumular(hechos: pd.DataFrame) -> pd.DataFrame:
    hechos = hechos.copy()
    hechos["valor"] = hechos["valor_publicado"]
    flujos = hechos["tipo_valor"].eq("flujo")
    if not flujos.any():
        return hechos

    sub = hechos.loc[flujos]
    if sub.duplicated(["cod_inst", "cuenta_id", "anio", "trimestre"]).any():
        raise ValueError("Hay claves duplicadas antes de des-acumular")
    piv = sub.pivot_table(index=["cod_inst", "cuenta_id", "anio"], columns="trimestre",
                          values="valor_publicado", aggfunc="first")
    for t in range(1, 5):
        if t not in piv.columns:
            piv[t] = float("nan")
    puro = pd.DataFrame(index=piv.index)
    puro["T1"] = piv[1]
    puro["T2"] = piv[2] - piv[1]
    puro["T3"] = piv[3]
    puro["T4"] = piv[4] - piv[3]
    puro = puro.reset_index().melt(
        id_vars=["cod_inst", "cuenta_id", "anio"],
        var_name="trimestre",
        value_name="valor_puro",
    )
    puro["trimestre"] = puro["trimestre"].str[1:].astype("int64")

    hechos = hechos.merge(puro, on=["cod_inst", "cuenta_id", "anio", "trimestre"], how="left")
    hechos["valor"] = hechos["valor_puro"].where(hechos["tipo_valor"].eq("flujo"), hechos["valor"])
    return hechos.drop(columns=["valor_puro"])


def construir_cuentas(hechos: pd.DataFrame) -> pd.DataFrame:
    estables = [
        "num_informe", "informe", "era", "cod_cuenta", "cuenta", "cuenta_base",
        "grupo", "grupo_norm", "concepto_era", "concepto", "tipo_valor",
    ]
    for columna in estables:
        variantes = hechos.groupby("cuenta_id")[columna].nunique(dropna=False)
        if (variantes > 1).any():
            malas = variantes[variantes > 1].index[:5].tolist()
            raise ValueError(f"cuenta_id con {columna} inestable: {malas}")
    ordenado = hechos.sort_values(["cuenta_id", "periodo"])
    cuentas = ordenado.groupby("cuenta_id").agg(
        num_informe=("num_informe", "first"),
        informe=("informe", "first"),
        era=("era", "first"),
        cod_cuenta=("cod_cuenta", "first"),
        cuenta=("cuenta", "first"),
        cuenta_base=("cuenta_base", "first"),
        grupo=("grupo", "first"),
        grupo_norm=("grupo_norm", "first"),
        composicion=("composicion", "last"),
        composicion_primera=("composicion", "first"),
        n_composiciones=("composicion", "nunique"),
        concepto_era=("concepto_era", "first"),
        concepto=("concepto", "first"),
        tipo_valor=("tipo_valor", "first"),
        primer_periodo=("periodo", "min"),
        ultimo_periodo=("periodo", "max"),
        n_bancos=("cod_inst", "nunique"),
    ).reset_index()
    return cuentas.sort_values(["num_informe", "era", "concepto_era", "cuenta_id"])


def construir_instituciones(hechos: pd.DataFrame, defs: dict) -> pd.DataFrame:
    bancos = defs["_bancos"]
    ultimo_periodo = hechos["periodo"].max()
    ordenado = hechos.sort_values("periodo")
    cobertura = ordenado.groupby("cod_inst").agg(
        institucion_bcb_ultima=("institucion_bcb", "last"),
        primer_periodo=("periodo", "min"),
        ultimo_periodo=("periodo", "max"),
        n_filas=("valor", "size"),
    ).reset_index()
    cadastro = leer_cadastro(ultimo_periodo, set(bancos))
    attrs = cadastro[["cod_inst", "tcb", "td", "tc", "sr", "segmento", "actividad", "situacion"]]
    tabla = cobertura.merge(attrs, on="cod_inst", how="left")
    tabla["nombre_corto"] = tabla["cod_inst"].map(lambda c: bancos[c]["nombre_corto"])
    tabla["categoria"] = tabla["cod_inst"].map(lambda c: bancos[c]["categoria"])
    tabla["nota"] = tabla["cod_inst"].map(lambda c: bancos[c].get("nota"))
    faltan = sorted(set(bancos) - set(tabla["cod_inst"]))
    if faltan:
        raise ValueError(f"Bancos definidos sin datos en el crudo: {faltan}")
    columnas = [
        "cod_inst", "nombre_corto", "categoria", "institucion_bcb_ultima",
        "tcb", "td", "tc", "sr", "segmento", "actividad", "situacion",
        "primer_periodo", "ultimo_periodo", "n_filas", "nota",
    ]
    return tabla[columnas].sort_values(["categoria", "nombre_corto"]).reset_index(drop=True)


def construir_periodos(hechos: pd.DataFrame) -> pd.DataFrame:
    periodos = hechos[["periodo", "fecha", "anio", "trimestre"]].drop_duplicates().sort_values("periodo")
    periodos = periodos.copy()
    periodos["anio_trimestre"] = PER.etiqueta_anio_trimestre(periodos["periodo"])
    periodos["orden_anio_trimestre"] = periodos["anio"] * 4 + periodos["trimestre"]
    return periodos.reset_index(drop=True)


def pivote_conceptos(hechos: pd.DataFrame, conceptos: list[str]) -> pd.DataFrame:
    claves = (
        hechos[["periodo", "fecha", "cod_inst", "nombre_corto", "categoria"]]
        .drop_duplicates()
        .set_index(["periodo", "cod_inst"])
        .sort_index()
    )
    sub = hechos[hechos["concepto"].isin(conceptos)]
    if sub.duplicated(["periodo", "cod_inst", "concepto"]).any():
        duplicadas = sub[sub.duplicated(["periodo", "cod_inst", "concepto"], keep=False)]
        raise ValueError(f"Conceptos curados duplicados:\n{duplicadas.head(20)}")
    tabla = sub.pivot_table(index=["periodo", "cod_inst"], columns="concepto",
                            values="valor", aggfunc="first")
    tabla = claves.join(tabla)
    for concepto in conceptos:
        if concepto not in tabla.columns:
            tabla[concepto] = pd.NA
    tabla = tabla.reset_index()[["periodo", "fecha", "cod_inst", "nombre_corto", "categoria"] + conceptos]
    return tabla.sort_values(["periodo", "nombre_corto"]).reset_index(drop=True)


def validar(salidas: dict[str, pd.DataFrame]) -> None:
    hechos = salidas["bank_hechos"]
    cuentas = salidas["bank_cuentas"]
    instituciones = salidas["bank_instituciones"]
    periodos = salidas["bank_periodos"]
    balances = salidas["bank_balances"]
    resultados = salidas["bank_resultados"]

    if hechos.duplicated(CLAVE_HECHO).any():
        raise ValueError(f"bank_hechos tiene claves duplicadas: {CLAVE_HECHO}")
    if cuentas.duplicated("cuenta_id").any():
        raise ValueError("bank_cuentas tiene cuenta_id duplicado")
    if instituciones.duplicated("cod_inst").any():
        raise ValueError("bank_instituciones tiene cod_inst duplicado")
    if periodos.duplicated("periodo").any():
        raise ValueError("bank_periodos tiene periodo duplicado")
    for nombre, tabla in (("bank_balances", balances), ("bank_resultados", resultados)):
        if tabla.duplicated(CLAVE_ENTIDAD).any():
            raise ValueError(f"{nombre} tiene claves duplicadas")

    ultimo = hechos["periodo"].max()
    bancos_ultimo = set(hechos.loc[hechos["periodo"] == ultimo, "cod_inst"])
    faltan = sorted(set(instituciones["cod_inst"]) - bancos_ultimo)
    if faltan:
        raise ValueError(f"Bancos sin datos en el último periodo {ultimo}: {faltan}")

    malos_stock = hechos[
        hechos["tipo_valor"].eq("stock") & hechos["valor_publicado"].isna() & hechos["valor"].notna()
    ]
    if len(malos_stock):
        raise ValueError("Hay stocks faltantes convertidos en valor")
    malos_flujos = hechos[
        hechos["tipo_valor"].eq("flujo") & hechos["valor_publicado"].isna() & hechos["valor"].notna()
    ]
    if len(malos_flujos):
        raise ValueError("Hay flujos faltantes convertidos en valor")

    comp = balances.dropna(subset=["ativo_total", "passivo_total"])
    if comp.empty:
        raise ValueError("No hay pares Ativo Total / Passivo Total para validar el balance")
    diff = (comp["ativo_total"] - comp["passivo_total"]).abs()
    rel = (diff / comp["ativo_total"].abs().replace(0, float("nan"))).fillna(0.0)
    if (diff > 1.0).any() or (rel > 1e-8).any():
        peores = comp.assign(diff=diff, rel=rel).nlargest(5, "diff")
        raise ValueError(f"Identidad de balance fallida:\n{peores}")

    memo_r4 = hechos[hechos["concepto"] == "ativo_total_memo_dr"][["periodo", "cod_inst", "valor_publicado"]]
    memo_r2 = hechos[hechos["concepto"] == "ativo_total"][["periodo", "cod_inst", "valor_publicado"]]
    if not memo_r4.empty:
        comp_memo = memo_r4.merge(memo_r2, on=["periodo", "cod_inst"], suffixes=("_r4", "_r2"))
        diff_memo = (comp_memo["valor_publicado_r4"] - comp_memo["valor_publicado_r2"]).abs()
        if (diff_memo > 1e-6).any():
            raise ValueError("El memo Ativo Total del informe 4 no coincide con el informe 2")

    # Puente del resultado: antes de tributos = intermediación + otras + transacciones de pago (solo
    # COSIF 2025) + no operacional (solo COSIF viejo). Si no cierra, falta o sobra una línea del crosswalk.
    puente = resultados.dropna(subset=["resultado_antes_tributacao_participacoes", "resultado_intermediacao_financeira",
                                       "outras_receitas_despesas"])
    suma = (puente["resultado_intermediacao_financeira"] + puente["outras_receitas_despesas"]
            + puente["resultado_transacoes_pagamento"].fillna(0) + puente["resultado_nao_operacional"].fillna(0))
    desvio = (puente["resultado_antes_tributacao_participacoes"] - suma).abs()
    if (desvio > 1.0).any():
        raise ValueError(f"El puente del resultado no cierra:\n{puente.assign(desvio=desvio).nlargest(5, 'desvio')}")

    # Continuidad del crédito bruto en la frontera COSIF 2025: el 2026-10-09 se descubrió que el crosswalk unía bruto
    # (viejo) con neto (nuevo) y el panel caía −4,4 % falso en 2025-T1. Con los mismos bancos en los dos trimestres.
    antes, despues = PER.previo(PER.QUIEBRE_2025), PER.QUIEBRE_2025
    if {antes, despues} <= set(balances["periodo"]):
        par = balances[balances["periodo"].isin([antes, despues])].pivot(
            index="cod_inst", columns="periodo", values="operacoes_credito").dropna()
        salto = par[despues].sum() / par[antes].sum() - 1
        if abs(salto) > 0.06:
            raise ValueError(f"Salto del crédito bruto en la frontera 2025-T1: {salto:+.1%}; revisar el crosswalk")

    flujos = hechos[hechos["tipo_valor"].eq("flujo")]
    if not flujos.empty:
        piv_valor = flujos.pivot_table(index=["cod_inst", "cuenta_id", "anio"], columns="trimestre",
                                       values="valor", aggfunc="first")
        piv_pub = flujos.pivot_table(index=["cod_inst", "cuenta_id", "anio"], columns="trimestre",
                                     values="valor_publicado", aggfunc="first")
        for t in range(1, 5):
            if t not in piv_valor.columns:
                piv_valor[t] = float("nan")
            if t not in piv_pub.columns:
                piv_pub[t] = float("nan")
        h1 = (piv_valor[1] + piv_valor[2] - piv_pub[2]).abs()
        h2 = (piv_valor[3] + piv_valor[4] - piv_pub[4]).abs()
        if (h1.dropna() > 1e-4).any() or (h2.dropna() > 1e-4).any():
            raise ValueError("La des-acumulación no reproduce los acumulados de junio y diciembre")


def construir_salidas(defs: dict, periodos: list[str]) -> dict[str, pd.DataFrame]:
    hechos = construir_hechos(periodos, defs)
    salidas = {
        "bank_hechos": hechos,
        "bank_cuentas": construir_cuentas(hechos),
        "bank_instituciones": construir_instituciones(hechos, defs),
        "bank_periodos": construir_periodos(hechos),
        "bank_balances": pivote_conceptos(hechos, CONCEPTOS_BALANCE),
        "bank_resultados": pivote_conceptos(hechos, CONCEPTOS_RESULTADO),
    }
    validar(salidas)
    return salidas


def exportar_salidas(salidas: dict[str, pd.DataFrame], destino: Path = A.GOLD) -> list[Path]:
    """Escribe las salidas ya validadas por construir_salidas."""
    rutas = []
    for nombre, tabla in salidas.items():
        ruta = Path(destino) / f"{nombre}.parquet"
        A.escribir_parquet(tabla, ruta)
        rutas.append(ruta)
    return rutas


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description="Prepara el panel de bancos brasileños desde el crudo de IF.data.").parse_args(argv)
    defs = cargar_definiciones()
    salidas = construir_salidas(defs, periodos_disponibles())
    rutas = exportar_salidas(salidas)
    for ruta in rutas:
        tabla = salidas[ruta.stem]
        print(f"{ruta.name}: {len(tabla):,} filas")
    hechos = salidas["bank_hechos"]
    balances = salidas["bank_balances"]
    ultimo = hechos["periodo"].max()
    sin_activo = balances.loc[
        balances["periodo"].eq(ultimo) & balances["ativo_total"].isna(), "nombre_corto"
    ].tolist()
    print(f"Periodos: {hechos['periodo'].min()}-{hechos['periodo'].max()}")
    print(f"Bancos: {hechos['cod_inst'].nunique()}")
    print(f"Cuentas: {hechos['cuenta_id'].nunique()}")
    if sin_activo:
        print(f"Aviso: sin Ativo Total publicado en {ultimo}: {', '.join(sorted(sin_activo))}")
    print("Validaciones: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
