# -*- coding: utf-8 -*-
"""Capital: informe 5 de IF.Data («Informações de Capital») → bk_capital y bk_capital_grupo.

Fuente: el crudo que deja ``ifdata.py colectar --escopo prudencial --informe 5`` en
datos/crudo/bcb_ifdata/valores/actual/valores_<AAAAMM>_1_r5.(csv|parquet). Este paso no baja nada: la colecta de
IF.Data es trimestral y a mano (ver spec/07). Si falta un trimestre, queda como hueco con su motivo.

Trampas (verificadas el 9-nov-2026 sobre 2015-03 a 2026-06; detalle en spec/08):
1. El informe 5 existe desde 2015-03. Los archivos de 2014 vienen vacíos (la API responde, sin filas).
2. Las letras de las columnas cambian por época («RWA (i) = (f)+(g)+(h)» hasta 2022-12, «(j) = (f)+(g)+(h)+(i)»
   desde 2023-03): se casa por el nombre sin la letra (definiciones/bcb_ifdata__capital.json).
3. En 2025-09 la API sirve cada fila tres veces (99.000 filas para 1.375 entidades). Se deduplica por
   entidad × campo y se exige que las copias tengan el mismo valor; si difieren, falla.
4. Desde 2023-03 el informe trae el «Adicional de Capital Principal» exigido en R$: el requerimiento de CP de
   cada banco sale de ahí (lo calcula el BCB). Antes de 2023-03 se reconstruye con
   definiciones/minimos_regulatorios.json; lo que la norma no respalda queda vacío.
5. Saldos con coma decimal y «null» literal (ifdata_texto.a_valor).

Salidas:
- datos/gold/bk_capital.parquet          banco × trimestre (columnas anchas)
- datos/gold/bk_capital_grupo.parquet    óptica × grupo × trimestre; índices = Σ capital / Σ RWA
- datos/derivado/bcb_ifdata/capital/huecos_capital.csv

Uso:  python -X utf8 pipeline/capital.py            (arma y publica)
      python -X utf8 pipeline/capital.py --resumen  (solo imprime cobertura y avisos, sin publicar)
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date

import numpy as np
import pandas as pd

import almacen as A
import bancos as B
import periodos as PER
from ifdata_texto import a_valor, normalizar

DEF_MAPA = "bcb_ifdata__capital"
DEF_MINIMOS = "minimos_regulatorios"
FUENTE = "bcb_ifdata"
DATASET = "capital"
ESCOPO = 1
INFORME = 5
COLUMNAS_CRUDO = ["CodInst", "Conta", "NomeColuna", "Saldo"]

TOL_INDICE = 5e-4      # 0,05 pp: índice del BCB contra el cociente propio
TOL_RWA = 2e-3         # 0,2 %: RWA total contra la suma de sus componentes

FUENTE_ACP_BCB = "BCB (informe 5, Adicional de Capital Principal)"
FUENTE_ACP_NORMA = "normas (definiciones/minimos_regulatorios.json)"

COLUMNAS_BANCO = [
    "cod_inst", "periodo", "fecha", "trimestre",
    "capital_principal", "capital_complementar", "nivel1", "nivel2", "pr",
    "rwa_credito", "rwa_mercado", "rwa_operacional", "rwa_sp", "rwa_total", "exposicion_total",
    "indice_cp", "indice_nivel1", "basilea", "razon_apalancamiento", "indice_inmovilizacion",
    "acp_requerido", "irrbb", "ativo_total", "densidad_rwa",
    "min_cp", "min_nivel1", "min_pr", "acp_pct", "fuente_acp",
    "requerimiento_cp", "requerimiento_nivel1", "requerimiento_pr",
    "holgura_cp_pp", "holgura_nivel1_pp", "holgura_basilea_pp", "exceso_cp", "holgura_crecimiento",
    "var_cp_4t", "lucro_ttm", "otros_var_cp_4t", "alerta",
]
SUMABLES = ["capital_principal", "nivel1", "pr", "rwa_credito", "rwa_mercado", "rwa_operacional", "rwa_total",
            "acp_brl"]


# ---------------------------------------------------------------- definiciones

_LETRA = re.compile(r"\s*\([a-z]\d?\)")   # «(k)», «(g4)»; no «(RWA)», que va en mayúsculas


def nombre_base(texto: str) -> str:
    """«Índice de Basileia \\n(n) = (e) / (j)» → «indice de basileia»: el nombre sin la letra de la época.

    Se corta en el salto de línea y también en la primera letra entre paréntesis, porque en 2023-03 y 2023-06 el
    BCB sirvió «Índice de Capital Principal (k) = (a) / (i)» sin el salto.
    """
    texto = str(texto).split("\n")[0]
    return normalizar(_LETRA.split(texto)[0]).strip()


def mapa_campos(defn: dict | None = None) -> dict[str, str]:
    """nombre base → campo de bk_capital. Falla si dos campos comparten nombre."""
    defn = A.leer_definicion(DEF_MAPA) if defn is None else defn
    out: dict[str, str] = {}
    for campo, spec in defn["campos"].items():
        clave = nombre_base(spec["nombre"])
        if clave in out:
            raise ValueError(f"{DEF_MAPA}.json: «{spec['nombre']}» mapea a {out[clave]} y a {campo}")
        out[clave] = campo
    return out


def _fecha(texto: str) -> date:
    return date.fromisoformat(texto)


def vigente(filas: list[dict], dia: date, clave: str = "valor"):
    """El valor de la fila cuya vigencia [desde, hasta] contiene ``dia``; None si ninguna o si es null."""
    for f in filas:
        desde = _fecha(f["desde"])
        hasta = _fecha(f["hasta"]) if f.get("hasta") else date.max
        if desde <= dia <= hasta:
            return f.get(clave)
    return None


def sistemico(minimos: dict, cod_inst: str, dia: date):
    """ACP Sistêmico del banco en ``dia``.

    - Si el cronograma lo fija en 0 para todos (antes de 2017), 0.
    - Si el banco está en ``bancos``, el valor publicado de ese año (con su fuente); None si ese año falta.
    - Si no está: 0 cuando ``lista_completa`` (verificado que nadie más supera el umbral), None si no.
    """
    s = minimos.get("sistemico") or {}
    if vigente(s.get("cronograma") or [], dia) == 0:
        return 0.0
    bancos = s.get("bancos") or {}
    if cod_inst not in bancos:
        return 0.0 if s.get("lista_completa") else None
    return vigente(bancos[cod_inst].get("valores") or [], dia)


# ---------------------------------------------------------------- lectura del crudo

def ruta_crudo(periodo: str):
    return A.ruta_valores(periodo, ESCOPO, INFORME)


def leer_informe(periodo: str, cods: set[str], campos: dict[str, str], defn: dict,
                 avisos: list[str]) -> pd.DataFrame:
    """Un trimestre del informe 5 en formato ancho (una fila por banco), solo los bancos de ``cods``."""
    ruta = ruta_crudo(periodo)
    if not A.existe_crudo(ruta):
        return pd.DataFrame(columns=["cod_inst"])
    crudo = A.leer_crudo_tabla(ruta, COLUMNAS_CRUDO)
    crudo = crudo[crudo["CodInst"].isin(cods)]
    if crudo.empty:
        return pd.DataFrame(columns=["cod_inst"])
    crudo = crudo.assign(campo=crudo["NomeColuna"].map(lambda s: campos.get(nombre_base(s))))
    ignoradas = {nombre_base(x) for x in defn.get("ignorar", [])}
    desconocidas = sorted(set(crudo.loc[crudo["campo"].isna(), "NomeColuna"].map(nombre_base)) - ignoradas)
    if desconocidas:
        avisos.append(f"{periodo}: columnas del informe 5 sin mapear (se ignoran): {desconocidas}")
    crudo = crudo.dropna(subset=["campo"])
    crudo = crudo.assign(valor=pd.to_numeric(crudo["Saldo"].map(a_valor), errors="coerce"))

    # Trampa 3: filas repetidas. Se aceptan solo si todas las copias dicen lo mismo.
    n_val = crudo.groupby(["CodInst", "campo"])["valor"].nunique(dropna=False)
    conflicto = n_val[n_val > 1]
    if len(conflicto):
        raise ValueError(f"{periodo}: el informe 5 trae valores distintos para la misma entidad y campo: "
                         f"{conflicto.index.tolist()[:5]}")
    repetidas = int(crudo.duplicated(["CodInst", "campo"]).sum())
    if repetidas:
        avisos.append(f"{periodo}: {repetidas} filas repetidas idénticas en el informe 5 (se deduplican)")
    crudo = crudo.drop_duplicates(["CodInst", "campo"])

    esperadas = {c: set(s.get("conta", [])) for c, s in defn["campos"].items()}
    raras = crudo[[c not in esperadas[k] for c, k in zip(crudo["Conta"], crudo["campo"])]]
    if len(raras):
        pares = sorted(set(zip(raras["campo"], raras["Conta"])))
        avisos.append(f"{periodo}: Conta distinta de la anotada en {DEF_MAPA}.json (se usa igual, casa por "
                      f"nombre): {pares}")

    ancho = crudo.pivot(index="CodInst", columns="campo", values="valor")
    ancho.columns.name = None
    return ancho.reset_index().rename(columns={"CodInst": "cod_inst"})


# ---------------------------------------------------------------- cálculo

def requerimientos(df: pd.DataFrame, minimos: dict) -> pd.DataFrame:
    """Mínimos, adicional de capital principal y holguras de cada banco × trimestre."""
    df = df.copy()
    dias = PER.fin_de_mes(df["periodo"]).dt.date
    m = minimos.get("minimos") or []
    df["min_cp"] = [vigente(m, d, "cp") for d in dias]
    df["min_nivel1"] = [vigente(m, d, "nivel1") for d in dias]
    df["min_pr"] = [vigente(m, d, "pr") for d in dias]

    acp, fuente = [], []
    for cod, dia, acp_brl, rwa in zip(df["cod_inst"], dias, df["acp_requerido"], df["rwa_total"]):
        if pd.notna(acp_brl) and pd.notna(rwa) and rwa > 0:
            acp.append(float(acp_brl) / float(rwa))
            fuente.append(FUENTE_ACP_BCB)
            continue
        partes = [vigente(minimos.get("conservacion") or [], dia),
                  vigente(minimos.get("contraciclico") or [], dia),
                  sistemico(minimos, cod, dia)]
        if any(p is None for p in partes):
            acp.append(np.nan)
            fuente.append("")
        else:
            acp.append(float(sum(partes)))
            fuente.append(FUENTE_ACP_NORMA)
    df["acp_pct"] = acp
    df["fuente_acp"] = fuente
    for col in ("min_cp", "min_nivel1", "min_pr"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["requerimiento_cp"] = df["min_cp"] + df["acp_pct"]
    df["requerimiento_nivel1"] = df["min_nivel1"] + df["acp_pct"]
    df["requerimiento_pr"] = df["min_pr"] + df["acp_pct"]
    df["acp_brl"] = df["acp_pct"] * df["rwa_total"]
    df["holgura_cp_pp"] = df["indice_cp"] - df["requerimiento_cp"]
    df["holgura_nivel1_pp"] = df["indice_nivel1"] - df["requerimiento_nivel1"]
    df["holgura_basilea_pp"] = df["basilea"] - df["requerimiento_pr"]
    df["exceso_cp"] = df["capital_principal"] - df["requerimiento_cp"] * df["rwa_total"]
    # Cuánto pueden crecer los RWA (y el activo, a densidad constante) con el CP de hoy: CP / (req × RWA) − 1.
    df["holgura_crecimiento"] = df["indice_cp"] / df["requerimiento_cp"] - 1
    return df


def con_panel(df: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """Densidad de RWA (RWA / activo total) y el puente del CP a 4 trimestres (lucro TTM y resto)."""
    p = panel[panel["metrica"].isin(["ativo_total", "lucro_liquido_ttm"])]
    p = p.pivot_table(index=["cod_inst", "periodo"], columns="metrica", values="valor", aggfunc="first")
    p.columns.name = None
    p = p.reset_index().rename(columns={"lucro_liquido_ttm": "lucro_ttm"})
    for c in ("ativo_total", "lucro_ttm"):
        if c not in p:
            p[c] = np.nan
    df = df.merge(p[["cod_inst", "periodo", "ativo_total", "lucro_ttm"]], on=["cod_inst", "periodo"], how="left")
    df["densidad_rwa"] = df["rwa_total"] / df["ativo_total"].where(df["ativo_total"] > 0)
    previo = df[["cod_inst", "periodo", "capital_principal"]].copy()
    previo["periodo"] = previo["periodo"].map(lambda x: PER.previo(x, -4))
    previo = previo.rename(columns={"capital_principal": "cp_t4"})
    df = df.merge(previo, on=["cod_inst", "periodo"], how="left")
    df["var_cp_4t"] = df["capital_principal"] - df["cp_t4"]
    # Residuo: dividendos e intereses sobre capital, ajustes prudenciales, OCI, emisiones. El informe 5 no los
    # separa; no se inventa la división.
    df["otros_var_cp_4t"] = df["var_cp_4t"] - df["lucro_ttm"]
    return df.drop(columns="cp_t4")


def verificar(df: pd.DataFrame, avisos: list[str]) -> None:
    """Coherencia interna del informe 5. Lo que no calza es aviso, no se corrige el dato del BCB."""
    rwa = df["rwa_total"].where(df["rwa_total"] > 0)
    for campo, indice in (("capital_principal", "indice_cp"), ("nivel1", "indice_nivel1"), ("pr", "basilea")):
        propio = df[campo] / rwa
        malas = df[(propio - df[indice]).abs() > TOL_INDICE]
        if len(malas):
            avisos.append(f"{indice}: {len(malas)} filas difieren más de {TOL_INDICE:.2%} del cociente "
                          f"{campo}/rwa_total (se publica el del BCB): "
                          f"{list(zip(malas['cod_inst'], malas['periodo']))[:5]}")
    orden = df[(df["basilea"] + 1e-9 < df["indice_nivel1"]) | (df["indice_nivel1"] + 1e-9 < df["indice_cp"])]
    if len(orden):
        avisos.append(f"{len(orden)} filas con basilea < nivel I o nivel I < CP: "
                      f"{list(zip(orden['cod_inst'], orden['periodo']))[:5]}")
    suma = df[["rwa_credito", "rwa_mercado", "rwa_operacional"]].sum(axis=1, min_count=3) + df["rwa_sp"].fillna(0)
    malas = df[((suma - df["rwa_total"]).abs() / rwa) > TOL_RWA]
    if len(malas):
        avisos.append(f"rwa_total ≠ crédito + mercado + operacional (+ sp) en {len(malas)} filas: "
                      f"{list(zip(malas['cod_inst'], malas['periodo']))[:5]}")


def alertas_repetidos(df: pd.DataFrame) -> pd.Series:
    """Texto de alerta para los trimestres cuyo CP, PR y RWA son idénticos al centavo a los de otro trimestre del
    mismo banco (Agibank 2015-06 a 2016-06, PagSeguro 4T25 = 2T25). Es lo que publica el BCB y no se corrige,
    pero un balance que no se movió nada en seis meses casi seguro es un dato repetido."""
    claves = ["capital_principal", "pr", "rwa_total"]
    alerta = pd.Series("", index=df.index, dtype=object)
    completo = df.dropna(subset=claves)
    firma = completo[claves].round(2).astype(str).agg("|".join, axis=1)
    for (cod, _), idx in completo.groupby([completo["cod_inst"], firma]).groups.items():
        if len(idx) > 1:
            periodos = sorted(df.loc[idx, "periodo"])
            for i in idx:
                otros = [p for p in periodos if p != df.at[i, "periodo"]]
                alerta.at[i] = (f"CP, PR y RWA idénticos a {', '.join(otros)}: posible dato repetido por el BCB "
                                f"(se publica tal cual)")
    return alerta


def agregar_grupos(df: pd.DataFrame, minimos_cp: pd.Series) -> pd.DataFrame:
    """Óptica × grupo × trimestre. Los índices son Σ capital / Σ RWA de los bancos con dato, nunca promedio de
    índices. El requerimiento del grupo se publica solo si todos sus bancos tienen ACP."""
    attrs = B.atributos().set_index("cod_inst").loc[[b["cod_inst"] for b in B.universo()]].reset_index()
    mb = B.pertenencia(attrs)[["cod_inst", "optica", "grupo", "orden_optica", "orden_grupo"]]
    base = df[df["capital_principal"].notna() & df["rwa_total"].gt(0)]
    j = mb.merge(base, on="cod_inst")
    claves = ["optica", "grupo", "orden_optica", "orden_grupo", "periodo"]
    g = j.groupby(claves).agg(**{c: (c, "sum") for c in SUMABLES if c != "acp_brl"},
                              n_bancos=("cod_inst", "nunique"),
                              n_con_acp=("acp_brl", "count"),
                              acp_brl=("acp_brl", "sum"))
    activo = j[j["ativo_total"].gt(0)].groupby(claves).agg(rwa_con_activo=("rwa_total", "sum"),
                                                           ativo_total=("ativo_total", "sum"))
    g = g.join(activo).reset_index()
    g["indice_cp"] = g["capital_principal"] / g["rwa_total"]
    g["indice_nivel1"] = g["nivel1"] / g["rwa_total"]
    g["basilea"] = g["pr"] / g["rwa_total"]
    g["densidad_rwa"] = g["rwa_con_activo"] / g["ativo_total"]
    completo = g["n_con_acp"].eq(g["n_bancos"])
    g["acp_pct"] = (g["acp_brl"] / g["rwa_total"]).where(completo)
    g["acp_brl"] = g["acp_brl"].where(completo)
    g["min_cp"] = g["periodo"].map(minimos_cp)
    g["requerimiento_cp"] = g["min_cp"] + g["acp_pct"]
    g["holgura_cp_pp"] = g["indice_cp"] - g["requerimiento_cp"]
    g["holgura_crecimiento"] = g["indice_cp"] / g["requerimiento_cp"] - 1
    g["fecha"] = PER.fin_de_mes(g["periodo"]).dt.date
    g["trimestre"] = g["periodo"].map(PER.etiqueta_trimestre)
    cols = ["optica", "grupo", "periodo", "fecha", "trimestre", "n_bancos", "capital_principal", "nivel1", "pr",
            "rwa_credito", "rwa_mercado", "rwa_operacional", "rwa_total", "ativo_total", "indice_cp",
            "indice_nivel1", "basilea", "densidad_rwa", "acp_brl", "acp_pct", "min_cp", "requerimiento_cp",
            "holgura_cp_pp", "holgura_crecimiento", "orden_optica", "orden_grupo"]
    return g[cols].sort_values(["orden_optica", "orden_grupo", "periodo"]).reset_index(drop=True)


# ---------------------------------------------------------------- armado

def construir(*, avisos: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """(bk_capital, bk_capital_grupo, huecos)."""
    avisos = [] if avisos is None else avisos
    defn = A.leer_definicion(DEF_MAPA)
    minimos = A.leer_definicion(DEF_MINIMOS)
    campos = mapa_campos(defn)
    universo = {b["cod_inst"]: b["nombre_corto"] for b in B.universo()}
    panel = pd.read_parquet(A.GOLD / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "valor"])
    presentes = panel[["cod_inst", "periodo"]].drop_duplicates()
    periodos = sorted(presentes["periodo"].unique())

    partes, huecos = [], []
    for p in periodos:
        t = leer_informe(p, set(universo), campos, defn, avisos)
        esperados = set(presentes.loc[presentes["periodo"] == p, "cod_inst"])
        vacio = t.empty
        for cod in sorted(esperados - set(t["cod_inst"])):
            motivo = ("SIN_INFORME_5" if not A.existe_crudo(ruta_crudo(p))
                      else "INFORME_5_VACIO" if vacio else "BANCO_AUSENTE_EN_INFORME_5")
            huecos.append({"cod_inst": cod, "nombre_corto": universo[cod], "periodo": p, "motivo": motivo})
        if not vacio:
            partes.append(t.assign(periodo=p))
    if not partes:
        raise ValueError("bk_capital salió vacío: ¿está el crudo del informe 5? (ifdata.py colectar --informe 5)")
    df = pd.concat(partes, ignore_index=True)
    for c in defn["campos"]:
        if c not in df:
            df[c] = np.nan
    sin_cp = df[df["capital_principal"].isna() | df["rwa_total"].isna()]
    for cod, p in zip(sin_cp["cod_inst"], sin_cp["periodo"]):
        huecos.append({"cod_inst": cod, "nombre_corto": universo[cod], "periodo": p,
                       "motivo": "SIN_CAPITAL_PRINCIPAL_O_RWA"})

    verificar(df, avisos)
    df["alerta"] = alertas_repetidos(df)
    if df["alerta"].ne("").any():
        rep = df[df["alerta"].ne("")]
        avisos.append(f"trimestres con CP, PR y RWA idénticos a otro del mismo banco: "
                      f"{sorted(zip(rep['cod_inst'], rep['periodo']))}")
    df = con_panel(df, panel)
    df = requerimientos(df, minimos)
    df["fecha"] = PER.fin_de_mes(df["periodo"]).dt.date
    df["trimestre"] = df["periodo"].map(PER.etiqueta_trimestre)
    minimos_cp = df.groupby("periodo")["min_cp"].first()
    grupo = agregar_grupos(df, minimos_cp)
    banco = df[COLUMNAS_BANCO].sort_values(["cod_inst", "periodo"]).reset_index(drop=True)
    return banco, grupo, pd.DataFrame(huecos, columns=["cod_inst", "nombre_corto", "periodo", "motivo"])


def resumen(banco: pd.DataFrame, huecos: pd.DataFrame, avisos: list[str]) -> None:
    print(f"[+] bk_capital: {len(banco):,} filas, {banco['cod_inst'].nunique()} bancos, "
          f"{banco['periodo'].min()}–{banco['periodo'].max()}")
    for fuente, n in banco["fuente_acp"].replace("", "(sin requerimiento)").value_counts().items():
        print(f"    requerimiento de CP desde {fuente}: {n} filas")
    if len(huecos):
        print(f"[i] {len(huecos)} huecos: " + ", ".join(f"{m} {n}" for m, n in huecos["motivo"].value_counts().items()))
    for a in avisos:
        print(f"[!] {a}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--resumen", action="store_true", help="no publica: imprime cobertura y avisos")
    args = ap.parse_args(argv)
    avisos: list[str] = []
    banco, grupo, huecos = construir(avisos=avisos)
    resumen(banco, huecos, avisos)
    if args.resumen:
        return 0
    desde = ["datos/crudo/bcb_ifdata/valores/actual", f"definiciones/{DEF_MAPA}.json",
             f"definiciones/{DEF_MINIMOS}.json", "datos/gold/bk_panel.parquet"]
    A.publicar_gold("bk_capital", banco, dataset=DATASET, desde=desde,
                    nota="Capital regulatorio por banco (IF.Data informe 5) con requerimiento y holguras")
    A.publicar_gold("bk_capital_grupo", grupo, dataset=DATASET, desde=desde,
                    nota="Capital por grupo: índices = Σ capital / Σ RWA")
    A.guardar_derivado(FUENTE, DATASET, "huecos_capital.csv", huecos.to_csv(index=False).encode("utf-8-sig"),
                       desde=desde, como=A.comando_actual(),
                       nota="banco × trimestre del panel sin dato de capital, con el motivo")
    print(f"[+] bk_capital_grupo: {len(grupo):,} filas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
