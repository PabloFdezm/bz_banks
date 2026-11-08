"""Universo de bancos del panel y sus ópticas de grupo: el único lugar que los lee de definiciones/.

El universo (cod_inst, nombre_corto, categoría, modelo de negocio) está en
``definiciones/bcb_ifdata__bancos_balances.json``; los atributos del sitio (slug, ticker, ficha) en
``definiciones/bancos__dashboard.json``. Las dos listas repiten cod_inst y nombre_corto para que se puedan
editar a mano; ``universo()`` falla si dejan de coincidir.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import almacen as A

DEF_BALANCES = "bcb_ifdata__bancos_balances"
DEF_DASHBOARD = "bancos__dashboard"

# Fintech = modelo de negocio Digitales o Pagos (Pablo, 2026-10-13).
MODELOS_FINTECH = ("Digitales", "Pagos")
PROPIEDAD = {"1": "Público", "2": "Privado nacional", "3": "Privado extranjero"}

TODOS = "Todos los grupos"
PANEL = "Panel"
# (id, etiqueta, columna de miembros, grupos [(código, etiqueta)])
OPTICAS = [
    ("panel", "Total panel", None, []),
    ("segmento", "Segmento regulatorio", "segmento",
     [("S1", "S1"), ("S2", "S2"), ("S3", "S3"), ("S4", "S4"), ("", "Sin segmento")]),
    ("propiedad", "Propiedad", "propiedad", list(PROPIEDAD.items())),
    ("modelo", "Modelo de negocio", "modelo",
     [("Grandes", "Grandes"), ("Medianos y nicho", "Medianos y nicho"), ("Digitales", "Digitales"),
      ("Pagos", "Pagos"), ("Desarrollo", "Desarrollo")]),
    ("fintech", "Tradicional vs Fintech", "fintech", [("Tradicional", "Tradicionales"), ("Fintech", "Fintechs")]),
]
ETIQUETA_OPTICA = {oid: etiqueta for oid, etiqueta, _, _ in OPTICAS}
SLUG_OPTICA = {etiqueta: oid for oid, etiqueta in ETIQUETA_OPTICA.items()}
OPTICA_PANEL = ETIQUETA_OPTICA["panel"]
OPTICA_MODELO = ETIQUETA_OPTICA["modelo"]
CLAVE_PANEL = "panel|todos"   # inst_key de «Todos los grupos» de la óptica Total panel (ver membresia)


def universo() -> list[dict]:
    """Los bancos del panel, en el orden de la definición, con los atributos de las dos definiciones."""
    balances = A.leer_definicion(DEF_BALANCES)["bancos"]
    dashboard = {b["cod_inst"]: b for b in A.leer_definicion(DEF_DASHBOARD)["bancos"]}
    if not balances:
        raise ValueError("La definición de bancos está vacía")
    if {b["cod_inst"] for b in balances} != set(dashboard):
        raise ValueError(f"{DEF_BALANCES}.json y {DEF_DASHBOARD}.json no tienen los mismos bancos")
    distintos = [b["cod_inst"] for b in balances if b["nombre_corto"] != dashboard[b["cod_inst"]]["nombre_corto"]]
    if distintos:
        raise ValueError(f"nombre_corto distinto entre {DEF_BALANCES}.json y {DEF_DASHBOARD}.json: {distintos}")
    return balances


def modelo_por_banco() -> dict[str, str]:
    return {b["cod_inst"]: b["modelo_negocio"] for b in universo()}


def fintech(modelo: pd.Series) -> pd.Series:
    """La regla fintech: modelo Digitales o Pagos."""
    return pd.Series(np.where(modelo.isin(MODELOS_FINTECH), "Fintech", "Tradicional"), index=modelo.index)


def atributos(inst: pd.DataFrame | None = None) -> pd.DataFrame:
    """Columnas de pertenencia de cada banco (códigos, no etiquetas): segmento (sr; "" sin segmento),
    propiedad (tc), modelo y fintech. Por defecto desde datos/gold/bank_instituciones.parquet."""
    if inst is None:
        inst = pd.read_parquet(A.GOLD / "bank_instituciones.parquet")
    out = pd.DataFrame({"cod_inst": inst["cod_inst"].astype(str).to_numpy(),
                        "segmento": inst["sr"].fillna("").astype(str).str.strip().to_numpy(),
                        "propiedad": inst["tc"].astype(str).str.strip().to_numpy()})
    out["modelo"] = out["cod_inst"].map(modelo_por_banco())
    out["fintech"] = fintech(out["modelo"])
    return out


def membresia(attrs: pd.DataFrame) -> pd.DataFrame:
    """Los grupos de cada óptica con sus bancos: la única regla de pertenencia.

    Una fila por grupo, en orden de árbol (óptica; «Todos los grupos» y después cada grupo): inst_key, optica_id,
    optica, codigo, grupo, orden_optica, orden_grupo, columna y bancos (lista, en el orden de ``attrs``).
    Falla si un banco queda sin grupo o un grupo sin bancos.
    """
    filas, orden = [], 1
    for orden_optica, (oid, etiqueta, columna, grupos) in enumerate(OPTICAS, 1):
        if columna and (set(attrs[columna]) - {c for c, _ in grupos} or attrs[columna].isna().any()):
            raise ValueError(f"óptica {columna}: hay bancos sin grupo")
        filas.append({"inst_key": f"{oid}|todos", "optica_id": oid, "optica": etiqueta, "codigo": "todos",
                      "grupo": TODOS, "orden_optica": orden_optica, "orden_grupo": 0, "columna": columna,
                      "bancos": attrs["cod_inst"].tolist()})
        for codigo, grupo in grupos:
            cods = attrs.loc[attrs[columna] == codigo, "cod_inst"].tolist()
            filas.append({"inst_key": f"{oid}|{codigo or 'sin'}", "optica_id": oid, "optica": etiqueta,
                          "codigo": codigo, "grupo": grupo, "orden_optica": orden_optica, "orden_grupo": orden,
                          "columna": columna, "bancos": cods})
            orden += 1
    return pd.DataFrame(filas)


def pertenencia(attrs: pd.DataFrame) -> pd.DataFrame:
    """Una fila por grupo × banco (los grupos de membresia() explotados); falla si un grupo queda vacío."""
    grupos = membresia(attrs)
    vacios = grupos.loc[grupos["bancos"].str.len() == 0, "inst_key"].tolist()
    if vacios:
        raise ValueError(f"grupos sin bancos: {vacios}")
    return grupos.explode("bancos").rename(columns={"bancos": "cod_inst"}).reset_index(drop=True)


def con_quiebre_2025() -> set[str]:
    """Bancos con cambio de cobertura en la frontera 2025 (quiebre_2025 en datos/gold/bk_cartera.parquet)."""
    ruta = A.GOLD / "bk_cartera.parquet"
    if not ruta.exists():
        raise FileNotFoundError("falta bk_cartera.parquet: correr antes «actualizar.py --desde cartera» (preparar_gold_bancos_cartera.py)")
    c = pd.read_parquet(ruta, columns=["cod_inst", "quiebre_2025"]).drop_duplicates("cod_inst")
    return set(c.loc[c["quiebre_2025"].fillna(False).astype(bool), "cod_inst"].astype(str))
