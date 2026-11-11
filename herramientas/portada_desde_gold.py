# -*- coding: utf-8 -*-
"""Recarga los datos incrustados de las hojas de la Portada (diseno/canvas/Seccion01–03.dc.html) desde gold.

Las hojas de la Portada llevan sus datos dentro (``const D``, ``const T`` o ``const LARGO`` y ``const FALTA``); el
sitio no las lee de JSON (herramientas/construir_v2.py). Este script reemplaza esas líneas con las cifras de:
- Sección 01: bk_concesiones y bk_concesiones_tablas (bloque «12m»): a/a de las concesiones de 12 meses (``aa_<seg>``),
  índice de concesiones reales sobre actividad (``ci_<seg>``) y la tabla de la página (``LARGO``).
- Sección 04: bk_sistema_bal_m (balancetes, frente 11): ROE de 12 meses y depósitos a/a por grupo.
- Secciones 02 y 03: bk_portada_m y bk_portada_m_tablas (frente 9): tasa y spread (02), mora y atraso (03) por los
  nueve segmentos; ``T`` = [último, m/m, 3m/3m, a/a, 12m/12m, Z 10 años] en % y pp.
Lo que el SGS no publica (spread dirigido de personas) queda fuera de ``D`` y en ``NO_PUB`` de la hoja.
Las series de contexto (PIB, crédito real, impulso, referencias, productos y empresas) también salen de gold
(EXTRAS); antes quedaban congeladas en la hoja.

    Set-Location C:\\dev\\bz_banks; python -X utf8 herramientas/portada_desde_gold.py [--revisar]

Con --revisar solo informa qué cambiaría (no escribe).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

RAIZ = Path(__file__).resolve().parents[1]
CANVAS = RAIZ / "diseno" / "canvas"
GOLD = RAIZ / "datos" / "gold"
SEGMENTOS = ["tot", "pf", "pj", "li", "di", "pfli", "pfdi", "pjli", "pjdi"]
INICIO = "2014-01"


def meses(n: int) -> pd.PeriodIndex:
    return pd.period_range(INICIO, periods=n, freq="M")


def hasta_ultimo(*fechas: pd.Series) -> pd.PeriodIndex:
    """Calendario mensual desde INICIO hasta el último mes con dato en gold (antes se recortaba al largo que ya
    tenía la hoja, y la Portada no avanzaba con un mes nuevo)."""
    fin = max(pd.Period(pd.to_datetime(f).max(), "M") for f in fechas)
    return pd.period_range(INICIO, fin, freq="M")


def alargar(D: dict, n_viejo: int, n: int) -> None:
    """Las series mensuales de la hoja que este script no recarga (PIB, referencias, productos…) se completan con
    vacíos hasta el largo nuevo, para que sigan alineadas con el calendario. No se recorta nunca."""
    for k, v in D.items():
        if isinstance(v, dict):
            alargar(v, n_viejo, n)
        elif isinstance(v, list) and len(v) == n_viejo and n > n_viejo:
            D[k] = v + [None] * (n - n_viejo)


def lista(s: pd.Series, ix: pd.PeriodIndex, escala=1.0, dec=2) -> list:
    v = s.reindex(ix)
    return [None if pd.isna(x) or math.isinf(x) else round(float(x) * escala, dec) for x in v]


def serie(df: pd.DataFrame, col: str = "valor") -> pd.Series:
    return pd.Series(df[col].to_numpy(), index=pd.PeriodIndex(pd.to_datetime(df["fecha"]), freq="M"))


def linea(texto: str, nombre: str) -> tuple[int, int]:
    """Posición (inicio, fin) de la línea «const <nombre> = …;» de la hoja (una sola línea)."""
    m = re.search(rf"^(\s*)const {nombre} = .*;$", texto, re.M)
    if not m:
        raise ValueError(f"la hoja no tiene «const {nombre} = …;» en una línea")
    return m.start(), m.end()


def leer_const(texto: str, nombre: str):
    i, j = linea(texto, nombre)
    cuerpo = texto[i:j].split("=", 1)[1].strip().rstrip(";")
    return json.loads(cuerpo)


def poner_const(texto: str, nombre: str, valor, js: str | None = None) -> str:
    i, j = linea(texto, nombre)
    sangria = re.match(r"\s*", texto[i:j]).group(0)
    cuerpo = js if js is not None else json.dumps(valor, ensure_ascii=False, separators=(",", ":"))
    return texto[:i] + f"{sangria}const {nombre} = {cuerpo};" + texto[j:]


def num_es(x: float, dec: int = 1) -> str:
    s = f"{abs(x):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if x < 0 else "") + s


def pct_signo(x: float) -> str:
    return ("+" if x > 0 else "−" if x < 0 else "") + num_es(abs(x) * 100) + " %"


# ---------------------------------------------------------------- sección 01

def seccion01(texto: str) -> str:
    D = leer_const(texto, "D")
    c = pd.read_parquet(GOLD / "bk_concesiones.parquet")
    n_viejo = len(D["aa_tot"])
    ix = hasta_ultimo(c["fecha"])
    alargar(D, n_viejo, len(ix))
    for seg in SEGMENTOS:
        x = c[c["segmento"] == seg]
        D[f"aa_{seg}"] = lista(serie(x, "conc_12m_aa"), ix, 100)
        D[f"ci_{seg}"] = lista(serie(x, "indice"), ix, 1)
    t = pd.read_parquet(GOLD / "bk_concesiones_tablas.parquet")
    t = t[t["bloque"] == "12m"].sort_values("orden")
    largo = {}
    for seg, (_, r) in zip(SEGMENTOS, t.iterrows()):
        largo[seg] = [num_es(r["ultimo"]), num_es(r["share"] * 100) + " %", pct_signo(r["d1"]), pct_signo(r["d3"]),
                      pct_signo(r["d12"]), pct_signo(r["dventana"])]
    texto = poner_const(texto, "D", D)
    texto = poner_const(texto, "LARGO", largo)
    texto = poner_const(texto, "RES", resumen(t))
    return poner_const(texto, "FALTA", [])


def pp_signo(x: float) -> str:
    return ("+" if x > 0 else "−" if x < 0 else "") + num_es(abs(x), 2) + " pp"


def resumen(conc12) -> list[dict]:
    """Franja de entrada de la Portada: cinco cifras con su cambio a/a y su corte, cada una con enlace a su par."""
    tot = conc12.iloc[0]
    tab = pd.read_parquet(GOLD / "bk_portada_m_tablas.parquet").set_index(["indicador", "segmento"])
    out = [{"nombre": "Concesiones de crédito, 12 meses", "valor": num_es(tot["ultimo"]), "unidad": "R$ mil mill.",
            "cambio": "a/a " + pct_signo(tot["d12"]), "corte": tot["corte"], "href": "#seccion-1"}]
    for ind, nombre, href in (("tasa", "Tasa media de las operaciones", "#seccion-2"),
                              ("spread", "Spread de las operaciones", "#seccion-2"),
                              ("mora90", "Mora > 90 días", "#seccion-3"),
                              ("atraso15_90", "Atraso de 15 a 90 días", "#seccion-3")):
        r = tab.loc[(ind, "tot")]
        unidad = " pp" if ind == "spread" else " %"
        out.append({"nombre": nombre, "valor": num_es(r["ultimo"] * 100, 2) + unidad, "unidad": "",
                    "cambio": "Δ a/a " + pp_signo(r["d12"]), "corte": r["corte"], "href": href})
    return out


# ---------------------------------------------------------------- secciones 02 y 03

def fila_t(r) -> list:
    return [round(r["ultimo"] * 100, 2), round(r["d1"], 2), round(r["d3"], 2), round(r["d12"], 2),
            round(r["dventana"], 2), None if pd.isna(r["z120"]) else round(r["z120"], 2)]


def seccion_m(texto: str, mapa: dict[str, str]) -> tuple[str, dict[str, list[str]]]:
    """``mapa``: clave de D (mo, at) → indicador de bk_portada_m. Devuelve el texto y los segmentos no publicados."""
    D, T = leer_const(texto, "D"), leer_const(texto, "T")
    clave0 = next(iter(mapa))
    largo = pd.read_parquet(GOLD / "bk_portada_m.parquet")
    n_viejo = len(next(iter(D[clave0].values())))
    ix = hasta_ultimo(largo.loc[largo["indicador"].isin(list(mapa.values())), "fecha"])
    alargar(D, n_viejo, len(ix))
    tab = pd.read_parquet(GOLD / "bk_portada_m_tablas.parquet").set_index(["indicador", "segmento"])
    no_pub = {}
    for clave, indicador in mapa.items():
        D[clave] = {}
        for seg in SEGMENTOS:
            x = largo[(largo["indicador"] == indicador) & (largo["segmento"] == seg)]
            if x.empty:
                no_pub.setdefault(clave, []).append(seg)
                T.pop(f"{clave}_{seg}", None)
                continue
            D[clave][seg] = lista(serie(x), ix, 100)
            T[f"{clave}_{seg}"] = fila_t(tab.loc[(indicador, seg)])
    texto = poner_const(texto, "D", D)
    texto = poner_const(texto, "T", T)
    return texto, no_pub


# ---------------------------------------------------------------- series de contexto (antes congeladas en sep-26)

# Hoja → clave de D (con «.» para las anidadas) → (tabla gold, serie, escala). Verificadas el 11-nov-2026 contra lo que
# tenía la hoja: diferencia 0 (≤ 0,005 por redondeo) en todos los meses.
EXTRAS = {
    "Seccion01": {
        "pib_tot": ("pm", ("credito_pib", "tot"), 100), "pib_pf": ("pm", ("credito_pib", "pf"), 100),
        "pib_pj": ("pm", ("credito_pib", "pj"), 100), "pib_li": ("pm", ("credito_pib", "li"), 100),
        "pib_di": ("pm", ("credito_pib", "di"), 100),
        "credito_total_real_aa": ("sm", "credito_total_real_aa", 100),
        "credito_total_real_aa_pf": ("sm", "credito_total_real_aa_pf", 100),
        "credito_total_real_aa_pj": ("sm", "credito_total_real_aa_pj", 100),
        "impulso_credito_pp": ("sm", "impulso_credito_pp", 1),
    },
    "Seccion02": {
        "ref.sel": ("pm", ("selic_meta", "tot"), 100), "ref.icc": ("pm", ("icc", "tot"), 100),
        "ref.gap": ("pm", ("tasa_menos_icc", "tot"), 100), "ref.npl": ("pm", ("mora90", "li"), 100),
        "ref.cdi": ("pm", ("cdi", "tot"), 100),
    },
    "Seccion03": {
        "pr.tar": ("sm", "mora90_cartao_total", 100), "pr.con": ("sm", "mora90_consignado_total", 100),
        "pr.per": ("sm", "mora90_personal", 100), "pr.veh": ("sm", "mora90_vehiculos", 100),
        "pr.inm": ("sm", "mora90_inmobiliario_total", 100), "em.mpme": ("sm", "mora90_mpme", 100),
        "em.gr": ("sm", "mora90_grande", 100),
    },
}
# Filas de tabla (T) que salen de esas series: [último, m/m, 3m/3m, a/a, 12m/12m, Z 10 años] en % y pp.
T_EXTRAS = {"Seccion03": {"pr_tar": "pr.tar", "pr_con": "pr.con", "pr_per": "pr.per", "pr_veh": "pr.veh",
                          "pr_inm": "pr.inm", "em_mpme": "em.mpme", "em_gr": "em.gr"}}
INICIO_CICLO = "2005Q1"


def _gold_series() -> dict[str, pd.Series]:
    """Todas las series candidatas, en fracción o en su unidad, con índice mensual."""
    out = {}
    sm = pd.read_parquet(GOLD / "bk_sistema_m.parquet")
    for k, g in sm.groupby("serie_id"):
        out[("sm", k)] = serie(g)
    pm = pd.read_parquet(GOLD / "bk_portada_m.parquet")
    for (i, s), g in pm.groupby(["indicador", "segmento"]):
        out[("pm", (i, s))] = serie(g)
    return out


def _poner(D: dict, clave: str, valor) -> None:
    if "." in clave:
        a, b = clave.split(".")
        D.setdefault(a, {})[b] = valor
    else:
        D[clave] = valor


def _leer(D: dict, clave: str):
    a, _, b = clave.partition(".")
    return D[a][b] if b else D[a]


def extras(hoja: str, texto: str) -> str:
    """Recarga las series de contexto de la hoja desde gold (y sus filas de T y, en la 01, el ciclo trimestral)."""
    if hoja not in EXTRAS:
        return texto
    D = leer_const(texto, "D")
    clave0 = "aa_tot" if hoja == "Seccion01" else "mo.tot"
    ix = meses(len(_leer(D, clave0)))
    g = _gold_series()
    for clave, (tabla, nombre, escala) in EXTRAS[hoja].items():
        s = g.get((tabla, nombre))
        if s is None:
            raise ValueError(f"{hoja}: no está en gold {tabla}:{nombre}")
        _poner(D, clave, lista(s, ix, escala))
    if hoja == "Seccion01":
        cs = pd.read_parquet(GOLD / "bk_cred_series.parquet")
        q = {}
        for nombre in ("cpib_nivel", "cpib_tendencia"):
            x = cs[cs["serie"] == nombre]
            q[nombre] = pd.Series(x["valor"].to_numpy(dtype=float),
                                  index=pd.PeriodIndex(pd.to_datetime(x["fecha"]), freq="Q")).loc[INICIO_CICLO:]
        iq = q["cpib_nivel"].index
        D["cpib_nivel"] = [round(float(v), 2) for v in q["cpib_nivel"]]
        D["cpib_tend"] = [None if pd.isna(v) else round(float(v), 2) for v in q["cpib_tendencia"].reindex(iq)]
        D["cpib_tri"] = [f"{p.quarter}T{str(p.year)[2:]}" for p in iq]
    texto = poner_const(texto, "D", D)
    if hoja in T_EXTRAS:
        import preparar_gold_bancos_portada_m as PM
        import tabla_estandar as TE
        T = leer_const(texto, "T")
        for fila, clave in T_EXTRAS[hoja].items():
            tabla, nombre, _ = EXTRAS[hoja][clave]
            s = g[(tabla, nombre)].dropna()
            v = TE.variaciones_tasa(s, escala=100)
            T[fila] = [round(v["ultimo"] * 100, 2), round(v["d1"], 2), round(v["d3"], 2), round(v["d12"], 2),
                       round(v["dventana"], 2), None if pd.isna(z := PM.zscore(s)) else round(z, 2)]
        texto = poner_const(texto, "T", T)
    return texto


# ---------------------------------------------------------------- sección 04 (balancetes, frente 11)

GRUPOS_S04 = {("Total panel", "Todos los grupos"): "tot",
              ("Propiedad", "Público"): "pub", ("Propiedad", "Privado nacional"): "pnac",
              ("Propiedad", "Privado extranjero"): "pext",
              ("Modelo de negocio", "Grandes"): "gra", ("Modelo de negocio", "Medianos y nicho"): "med",
              ("Modelo de negocio", "Digitales"): "dig", ("Modelo de negocio", "Pagos"): "pag",
              ("Modelo de negocio", "Desarrollo"): "des",
              ("Segmento regulatorio", "S1"): "s1", ("Segmento regulatorio", "S2"): "s2",
              ("Segmento regulatorio", "S3"): "s3", ("Segmento regulatorio", "S4"): "s4",
              ("Tradicional vs Fintech", "Tradicionales"): "trad", ("Tradicional vs Fintech", "Fintechs"): "fint"}
INICIO_S04 = "2020-01"


def seccion04(texto: str) -> str:
    """ROE de 12 meses (mo) y depósitos a/a (at) por grupo, y patrimonio/activo y crédito/depósitos del Total panel
    (ref), desde bk_sistema_bal_m. T = [último, m/m, 3m/3m, a/a, 12m/12m, Z]: Z vacío (la serie empieza en 2020)."""
    import tabla_estandar as TE
    g = pd.read_parquet(GOLD / "bk_sistema_bal_m.parquet")
    ix = pd.period_range(INICIO_S04, pd.Period(g["mes"].max(), "M"), freq="M")
    D = {"mo": {}, "at": {}, "ref": {}}
    T = {}
    for (opt, grp), k in GRUPOS_S04.items():
        x = g[(g["optica"] == opt) & (g["grupo"] == grp)]
        s_idx = pd.PeriodIndex(pd.to_datetime(x["mes"], format="%Y%m"), freq="M")
        for clave, col in (("mo", "roe_12m"), ("at", "depositos_aa")):
            s = pd.Series(x[col].to_numpy(dtype=float), index=s_idx)
            D[clave][k] = lista(s, ix, 100)
            v = TE.variaciones_tasa(s.dropna(), escala=100, minimo=25)
            if pd.notna(v.get("ultimo")):
                T[f"{clave}_{k}"] = [round(v["ultimo"] * 100, 2), round(v["d1"], 2), round(v["d3"], 2),
                                     round(v["d12"], 2), round(v["dventana"], 2), None]
        if k == "tot":
            D["ref"]["pla"] = lista(pd.Series(x["patrimonio_activo"].to_numpy(dtype=float), index=s_idx), ix, 100)
            D["ref"]["cd"] = lista(pd.Series(x["credito_depositos"].to_numpy(dtype=float), index=s_idx), ix, 100)
    texto = poner_const(texto, "D", D)
    texto = poner_const(texto, "T", T)
    return texto


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--revisar", action="store_true", help="informa sin escribir")
    a = ap.parse_args(argv)
    for hoja, f in (("Seccion01", None), ("Seccion02", {"mo": "tasa", "at": "spread"}),
                    ("Seccion03", {"mo": "mora90", "at": "atraso15_90"}), ("Seccion04", "bal")):
        p = CANVAS / f"{hoja}.dc.html"
        if not p.exists():
            continue
        antes = p.read_text(encoding="utf-8")
        if f == "bal":
            nuevo, no_pub = seccion04(antes), {}
        elif f is None:
            nuevo, no_pub = seccion01(antes), {}
        else:
            nuevo, no_pub = seccion_m(antes, f)
            pares = {"mo": "va", "at": "vb"}
            nuevo = poner_const(nuevo, "FALTA", {pares[k]: [] for k in f},
                                js="{ " + ", ".join(f"{pares[k]}: []" for k in f) + " }")
            nuevo = poner_const(nuevo, "NO_PUB", {pares[k]: v for k, v in no_pub.items()})
        nuevo = extras(hoja, nuevo)
        print(f"{hoja}: {'cambia' if nuevo != antes else 'sin cambios'}"
              + (f"; no publicados: {no_pub}" if no_pub else ""))
        if not a.revisar and nuevo != antes:
            p.write_text(nuevo, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
