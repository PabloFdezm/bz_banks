# -*- coding: utf-8 -*-
"""Hojas por producto de personas (frente 12): tarjeta, personal sin planilla, descuento por planilla y vehículos.

Lleva a gold las cifras que el canvas de rediseño calculaba con el borrador `extraer_producto.py`. Dos tablas largas,
genéricas por producto (columna ``producto``), en vez de una tabla por hoja.

TABLAS (datos/gold/)
--------------------
- bk_producto_pf_m (SGS, mensual): producto, sub, medida, fecha (último día del mes), valor.
  Clave: producto, sub, medida, fecha.
  * Niveles: ``saldo`` y ``concesiones`` (R$ millones; concesiones = flujo del mes), ``tasa`` y ``mora90``
    (fracción: el % del SGS / 100).
  * Descomposición de la tasa media (solo productos con submodalidades en ``DESCOMPONER``), con
    ``sub = "media"``: ``tasa_media`` (Σ w_i·r_i, w = peso de la submodalidad en las concesiones del mes),
    ``d_tasa_media`` (a/a, fracción), ``efecto_mezcla``; y por submodalidad ``peso_conc`` y ``efecto_tasa``.
    efecto_tasa_i = w̄_i·Δr_i; efecto_mezcla = Σ (r̄_i − r̄)·Δw_i, con promedios de t y t−12. Suman d_tasa_media.
  * Productos de referencia: ``personas`` (total personas: saldo, concesiones, tasa, mora) y ``referencia``
    (sub ``selic_meta``, medida ``tasa``: meta Selic, último dato del mes; sub ``salario_minimo``, medida ``nivel``:
    R$, último dato del mes y arrastrado a los meses sin cambio).
- bk_producto_pf_scr_m (SCR.data, mensual desde ene-18): producto, dimension, segmento, medida, fecha, valor.
  Clave: producto, dimension, segmento, medida, fecha.
  * Dimensiones: ``total`` (segmento «Total»), ``renta`` (7 tramos + «Sin renta / N.D.»), ``institucion``,
    ``ocupacion``, ``renta_institucion`` y ``renta_ocupacion`` (celdas «tramo · institución» y «tramo · ocupación») y ``tope_3sm`` («Hasta 3 SM» y
    «Más de 3 SM y sin dato»).
  * Medidas de nivel (todas las dimensiones): ``saldo``, ``mora90``, ``atraso15_90``, ``activo_problematico``
    (R$), ``ops`` (número de operaciones), ``cart_ops`` (R$ de las celdas con operaciones) y las razones
    ``tasa_mora``, ``tasa_atraso``, ``tasa_apr``, ``peso`` (saldo / saldo total del producto), ``saldo_aa`` y
    ``ticket`` (cart_ops / ops, R$) y ``ticket_real`` (R$ del último mes, IPCA).
  * Aportes (renta, institución, ocupación), en fracción (pp / 100), suman el total en cada mes:
    ``aporte_crec`` = (S_i,t − S_i,t−12) / S_total,t−12; para x en {mora, atraso}: ``aporte_x`` =
    w_i,t·m_i,t − w_i,t−12·m_i,t−12, ``efecto_tasa_x`` = w̄_i·Δm_i, ``efecto_mezcla_x`` = m̄_i·Δw_i.
  * Tres partes (dimensiones ``descomp_renta_primero`` y ``descomp_institucion_primero``, medidas ``mora`` y
    ``atraso``): segmentos ``efecto_tasa`` (en celdas renta × institución), ``mezcla_renta``,
    ``mezcla_institucion`` y ``variacion_total``. La mezcla del primer factor se mide sola; la del segundo es la
    mezcla de las celdas menos la del primero.
  * Meses de renta por operación (dimensión ``renta``, 7 tramos con renta): ``meses_renta_medio``,
    ``meses_renta_piso`` (renta en el piso del tramo: cota alta) y ``meses_renta_techo`` (cota baja) = ticket /
    (salario mínimo × múltiplo del tramo). «Hasta 1 SM» usa 0,75 / 0,5 / 1 y «Más de 20 SM» 20 en las tres.

REGLAS
------
- SGS: el personal no consignado TOTAL (20574, 20666, 20742, 21114) ya incluye la renegociación (20575, 20667,
  20743, 21115); el total de la hoja personal es personal + sobregiro y la renegociación es una parte, nunca un
  sumando (validado el 10-nov: 20580 = 20574 + 20579).
- Tarjeta: 22024 incluye el contado a tasa 0 y no se reconstruye con 22022/22023; la descomposición se hace contra la
  tasa media reconstruida (rotativo + cuotas ponderadas por concesiones), que no es 22024.
- Aportes: si un segmento no existe en t o en t−12, su tasa faltante toma la del otro período (todo su aporte cae en
  mezcla). Celdas sin saldo pesan 0.
- Agrupación de instituciones del canvas: Bancos, Cooperativas, Fintechs, Inst. de pago, Financieras y Otros. Difiere
  de definiciones/scr_productos.json (que manda Fintech a «Otras»): es la que Pablo aprobó en la hoja Tarjeta.
- Ocupación: asalariado privado incluye entidades sin fines de lucro; empresarios incluye MEI; el resto (incluido
  el valor «Outros» de la fuente) va a «Otros».
- Quiebres del SCR (no se suavizan): jul-25 reclasificación de renta; ago-26 ~R$ 15 mil millones de tarjeta pasan
  de «más de 20 SM» a «Indisponível».
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import almacen as A
import preparar_gold_bancos_scr_productos as SP
import sgs as SG
import tabla_estandar as T

DATASET = "bancos_gold_producto_pf"
DESDE_SCR = 2018

# --- SGS -----------------------------------------------------------------------------------------------------------
# producto → sub → medida → clave de sgs.CODIGOS (o tupla de claves que se suman).
PRODUCTOS_SGS: dict[str, dict[str, dict[str, str | tuple[str, ...]]]] = {
    "tarjeta": {
        "total": dict(saldo="credito_pf_tarjeta", concesiones="conc_pf_tarjeta_total",
                      tasa="tasa_pf_tarjeta_total", mora90="mora90_cartao_total"),
        "rotativo": dict(saldo="credito_pf_tarjeta_rotativo", concesiones="conc_pf_tarjeta_rotativo",
                         tasa="tasa_pf_tarjeta_rotativo", mora90="mora90_rotativo"),
        "cuotas": dict(saldo="credito_pf_tarjeta_parcelado", concesiones="conc_pf_tarjeta_parcelado",
                       tasa="tasa_pf_tarjeta_parcelado", mora90="mora90_parcelado"),
        "contado": dict(saldo="credito_pf_tarjeta_vista", concesiones="conc_pf_tarjeta_vista"),
    },
    "personal": {
        "total": dict(saldo=("credito_pf_personal", "credito_pf_cheque_especial"),
                      concesiones=("conc_pf_personal", "conc_pf_cheque_especial")),
        "personal": dict(saldo="credito_pf_personal", concesiones="conc_pf_personal",
                         tasa="tasa_pf_personal", mora90="mora90_personal"),
        "renegociacion": dict(saldo="credito_pf_personal_renegociacion",
                              concesiones="conc_pf_personal_renegociacion",
                              tasa="tasa_pf_personal_renegociacion", mora90="mora90_personal_renegociacion"),
        "sobregiro": dict(saldo="credito_pf_cheque_especial", concesiones="conc_pf_cheque_especial",
                          tasa="tasa_pf_cheque_especial", mora90="mora90_cheque_especial"),
    },
    "planilla": {
        "total": dict(saldo="credito_pf_consignado_total", concesiones="conc_pf_consignado_total",
                      tasa="tasa_pf_consignado_total", mora90="mora90_consignado_total"),
        "privados": dict(saldo="credito_pf_consignado_a", concesiones="conc_pf_consignado_privado",
                         tasa="tasa_pf_consignado_privado", mora90="mora90_consignado_privado"),
        "publico": dict(saldo="credito_pf_consignado_b", concesiones="conc_pf_consignado_publico",
                        tasa="tasa_pf_consignado_publico", mora90="mora90_consignado_publico"),
        "inss": dict(saldo="credito_pf_consignado_c", concesiones="conc_pf_consignado_inss",
                     tasa="tasa_pf_consignado_inss", mora90="mora90_consignado_inss"),
    },
    "vehiculos": {
        "total": dict(saldo="credito_pf_vehiculos", concesiones="conc_pf_vehiculos",
                      tasa="tasa_pf_vehiculos", mora90="mora90_vehiculos"),
    },
    "personas": {
        "total": dict(saldo="credito_pf", concesiones="concesiones_pf", tasa="tasa_pf_total", mora90="mora90_pf"),
    },
}
# Submodalidades de la descomposición de la tasa media (peso = concesiones del mes).
DESCOMPONER = {"tarjeta": ["rotativo", "cuotas"], "personal": ["personal", "sobregiro"],
               "planilla": ["privados", "publico", "inss"]}
EN_PORCENTAJE = {"tasa", "mora90"}

# --- SCR -----------------------------------------------------------------------------------------------------------
PRODUCTOS_SCR = {"tarjeta": "Tarjeta", "personal": "Personal no consignado", "planilla": "Consignado",
                 "vehiculos": "Vehículos"}
TRAMOS = {"Até 1 salário mínimo": "Hasta 1 SM", "Mais de 1 a 2 salários mínimos": "1–2 SM",
          "Mais de 2 a 3 salários mínimos": "2–3 SM", "Mais de 3 a 5 salários mínimos": "3–5 SM",
          "Mais de 5 a 10 salários mínimos": "5–10 SM", "Mais de 10 a 20 salários mínimos": "10–20 SM",
          "Acima de 20 salários mínimos": "Más de 20 SM"}
SIN_RENTA = "Sin renta / N.D."
ORDEN = {
    "renta": list(TRAMOS.values()) + [SIN_RENTA],
    "institucion": ["Bancos", "Cooperativas", "Fintechs", "Inst. de pago", "Financieras", "Otros"],
    "ocupacion": ["Asalariado privado", "Servidor público", "Jubilados", "Autónomos",
                  "Empresarios y microempresarios", "Otros"],
    "tope_3sm": ["Hasta 3 SM", "Más de 3 SM y sin dato"],
}
INSTITUCIONES = {"Banco": "Bancos", "Cooperativa": "Cooperativas", "Fintech": "Fintechs",
                 "Instituição de pagamento": "Inst. de pago", "Financeira": "Financieras"}
OCUPACIONES = {"Aposentado/pensionista": "Jubilados", "Empregado de empresa privada": "Asalariado privado",
               "Empregado de entidades sem fins lucrativos": "Asalariado privado",
               "Servidor ou empregado público": "Servidor público", "Autônomo": "Autónomos",
               "Empresário": "Empresarios y microempresarios", "MEI": "Empresarios y microempresarios"}
# múltiplo del salario mínimo por tramo: (punto medio, piso, techo)
MULTIPLO_SM = {"Hasta 1 SM": (0.75, 0.5, 1), "1–2 SM": (1.5, 1, 2), "2–3 SM": (2.5, 2, 3), "3–5 SM": (4, 3, 5),
               "5–10 SM": (7.5, 5, 10), "10–20 SM": (15, 10, 20), "Más de 20 SM": (20, 20, 20)}
MEDIDAS_SCR = ["carteira_ativa", "carteira_inadimplencia", "vencido_de_15_ate_90_dias", "ativo_problematico",
               "ops", "cart_ops"]
NOMBRE_NIVEL = {"carteira_ativa": "saldo", "carteira_inadimplencia": "mora90",
                "vencido_de_15_ate_90_dias": "atraso15_90", "ativo_problematico": "activo_problematico",
                "ops": "ops", "cart_ops": "cart_ops"}
NUMERADORES = {"mora": "carteira_inadimplencia", "atraso": "vencido_de_15_ate_90_dias"}


# ================================================== SGS ============================================================

def _serie(claves, leer) -> pd.Series:
    if isinstance(claves, tuple):
        partes = [leer(SG.CODIGOS[k]) for k in claves]
        return sum(partes[1:], partes[0])
    return leer(SG.CODIGOS[claves])


def descomponer_tasa(tasas: dict[str, pd.Series], conc: dict[str, pd.Series]) -> dict[tuple[str, str], pd.Series]:
    """Tasa media ponderada por concesiones y su variación a/a en efecto tasa (por sub) y efecto mezcla.

    Devuelve {(sub, medida): serie}. Identidad exacta: Σ efecto_tasa + efecto_mezcla = d_tasa_media.
    """
    subs = list(tasas)
    q = pd.concat([conc[s] for s in subs], axis=1, keys=subs)
    r = pd.concat([tasas[s] for s in subs], axis=1, keys=subs)
    w = q.div(q.sum(axis=1), axis=0)
    tm = (w * r).sum(axis=1, min_count=len(subs))
    w0, r0, tm0 = w.shift(12), r.shift(12), tm.shift(12)
    rbar = (tm + tm0) / 2
    efecto = (w + w0) / 2 * (r - r0)
    mezcla = ((r + r0) / 2).sub(rbar, axis=0).mul(w - w0).sum(axis=1, min_count=len(subs))
    out = {("media", "tasa_media"): tm, ("media", "d_tasa_media"): tm - tm0, ("media", "efecto_mezcla"): mezcla}
    for s in subs:
        out[(s, "peso_conc")] = w[s]
        out[(s, "efecto_tasa")] = efecto[s]
    return out


def construir_sgs(leer=SG.serie_mensual) -> pd.DataFrame:
    """bk_producto_pf_m. ``leer(codigo)`` devuelve la serie mensual (PeriodIndex) de un código SGS."""
    filas = []

    def agregar(producto, sub, medida, s):
        s = s.dropna()
        filas.append(pd.DataFrame({"producto": producto, "sub": sub, "medida": medida,
                                   "fecha": T.fecha_fin(s.index), "valor": s.to_numpy(dtype=float)}))

    for producto, subs in PRODUCTOS_SGS.items():
        for sub, medidas in subs.items():
            for medida, claves in medidas.items():
                s = _serie(claves, leer)
                agregar(producto, sub, medida, s / 100 if medida in EN_PORCENTAJE else s)
        if producto in DESCOMPONER:
            ss = DESCOMPONER[producto]
            tasas = {s: _serie(subs[s]["tasa"], leer) / 100 for s in ss}
            conc = {s: _serie(subs[s]["concesiones"], leer) for s in ss}
            for (sub, medida), serie in descomponer_tasa(tasas, conc).items():
                agregar(producto, sub, medida, serie)
    selic = SG.serie(SG.CODIGOS["selic_meta"])
    selic = selic.groupby(selic.index.to_period("M")).last() / 100
    agregar("referencia", "selic_meta", "tasa", selic)
    agregar("referencia", "salario_minimo", "nivel", salario_minimo_mensual())
    df = pd.concat(filas, ignore_index=True)
    # las referencias (Selic diaria, salario mínimo anunciado) no pasan del último mes de los productos
    fin = df.loc[df["producto"] != "referencia", "fecha"].max()
    return df[(df["producto"] != "referencia") | (df["fecha"] <= fin)].reset_index(drop=True)


# ================================================== SCR ============================================================

def preparar_cubo(cubo: pd.DataFrame) -> pd.DataFrame:
    """Cubo PF con las dimensiones del canvas (renta, institución, ocupación, tope 3 SM) y mes como Period."""
    c = cubo[cubo["cliente"] == "PF"].copy()
    c["mes"] = pd.to_datetime(c["fecha"]).dt.to_period("M")
    c["renta"] = c["porte"].map(TRAMOS).fillna(SIN_RENTA)
    c["institucion"] = c["segmento"].map(INSTITUCIONES).fillna("Otros")
    c["ocupacion"] = c["cnae_ocupacao"].map(OCUPACIONES).fillna("Otros")
    c["tope_3sm"] = np.where(c["porte"].isin(list(TRAMOS)[:3]), "Hasta 3 SM", "Más de 3 SM y sin dato")
    c["renta_institucion"] = c["renta"] + " · " + c["institucion"]
    c["renta_ocupacion"] = c["renta"] + " · " + c["ocupacion"]
    c["total"] = "Total"
    return c


def _celdas(c: pd.DataFrame, meses: pd.PeriodIndex, total: pd.DataFrame, dims: list[str], num: str):
    """Peso w y tasa m por celda; la tasa faltante de un período toma la del otro (celda nueva o que desaparece)."""
    g = c.groupby(["mes"] + dims)[MEDIDAS_SCR].sum()
    sx = g["carteira_ativa"].unstack(dims).reindex(meses).fillna(0)
    ix = g[num].unstack(dims).reindex(meses).fillna(0)
    w = sx.div(total["carteira_ativa"], axis=0)
    m = ix / sx.where(sx > 0)
    m0 = m.shift(12)
    m1, m0 = m.fillna(m0), m0.fillna(m)
    return w, m1.fillna(0), m0.fillna(0)


def _efectos(c, meses, total, dims, num):
    w, m1, m0 = _celdas(c, meses, total, dims, num)
    w0 = w.shift(12)
    return (w + w0) / 2 * (m1 - m0), (m1 + m0) / 2 * (w - w0)


def construir_producto_scr(c: pd.DataFrame, salario_minimo: pd.Series, deflactor: pd.Series) -> list[pd.DataFrame]:
    """Filas largas de un producto (``c`` ya filtrado al producto y preparado). Sin columna producto."""
    meses = pd.period_range(c["mes"].min(), c["mes"].max(), freq="M")
    total = c.groupby("mes")[MEDIDAS_SCR].sum().reindex(meses)
    filas = []

    def agregar(dimension, segmento, medida, s):
        s = s.replace([np.inf, -np.inf], np.nan).dropna()
        if len(s):
            filas.append(pd.DataFrame({"dimension": dimension, "segmento": segmento, "medida": medida,
                                       "fecha": T.fecha_fin(s.index), "valor": s.to_numpy(dtype=float)}))

    def niveles(dimension, segmento, g):
        for col, nombre in NOMBRE_NIVEL.items():
            agregar(dimension, segmento, nombre, g[col])
        sa = g["carteira_ativa"]
        agregar(dimension, segmento, "tasa_mora", g["carteira_inadimplencia"] / sa)
        agregar(dimension, segmento, "tasa_atraso", g["vencido_de_15_ate_90_dias"] / sa)
        agregar(dimension, segmento, "tasa_apr", g["ativo_problematico"] / sa)
        agregar(dimension, segmento, "peso", sa / total["carteira_ativa"])
        agregar(dimension, segmento, "saldo_aa", sa / sa.shift(12) - 1)
        tick = g["cart_ops"] / g["ops"].where(g["ops"] > 0)
        agregar(dimension, segmento, "ticket", tick)
        agregar(dimension, segmento, "ticket_real", tick / deflactor.reindex(meses))
        return tick

    niveles("total", "Total", total)
    for dimension in ("renta", "institucion", "ocupacion", "tope_3sm", "renta_institucion", "renta_ocupacion"):
        g = c.groupby(["mes", dimension])[MEDIDAS_SCR].sum()
        for segmento in sorted(set(g.index.get_level_values(1)), key=_orden(dimension)):
            tick = niveles(dimension, segmento, g.xs(segmento, level=1).reindex(meses))
            if dimension == "renta" and segmento in MULTIPLO_SM:
                sm = salario_minimo.reindex(meses)
                for j, nombre in enumerate(("meses_renta_medio", "meses_renta_piso", "meses_renta_techo")):
                    agregar(dimension, segmento, nombre, tick / (sm * MULTIPLO_SM[segmento][j]))

    # Aportes por segmento (suman el total).
    tot = total["carteira_ativa"]
    for dimension in ("renta", "institucion", "ocupacion"):
        sal = c.groupby(["mes", dimension])["carteira_ativa"].sum().unstack().reindex(meses).fillna(0)
        for segmento in sal.columns:
            agregar(dimension, segmento, "aporte_crec", (sal[segmento] - sal[segmento].shift(12)) / tot.shift(12))
        for nombre, num in NUMERADORES.items():
            w, m1, m0 = _celdas(c, meses, total, [dimension], num)
            w0 = w.shift(12)
            for segmento in w.columns:
                agregar(dimension, segmento, f"aporte_{nombre}", w[segmento] * m1[segmento] - w0[segmento] * m0[segmento])
                agregar(dimension, segmento, f"efecto_tasa_{nombre}",
                        (w[segmento] + w0[segmento]) / 2 * (m1[segmento] - m0[segmento]))
                agregar(dimension, segmento, f"efecto_mezcla_{nombre}",
                        (m1[segmento] + m0[segmento]) / 2 * (w[segmento] - w0[segmento]))

    # Tres partes: efecto tasa en celdas renta × institución, mezcla del primer factor y del segundo.
    for nombre, num in NUMERADORES.items():
        tasa, mez = _efectos(c, meses, total, ["renta", "institucion"], num)
        tt, mt = tasa.sum(axis=1), mez.sum(axis=1)
        nivel = total[num] / total["carteira_ativa"]
        var = nivel - nivel.shift(12)
        for primero, segundo, dimension in (("renta", "institucion", "descomp_renta_primero"),
                                            ("institucion", "renta", "descomp_institucion_primero")):
            _, mez1 = _efectos(c, meses, total, [primero], num)
            m1 = mez1.sum(axis=1)
            valido = var.notna()
            agregar(dimension, "efecto_tasa", nombre, tt.where(valido))
            agregar(dimension, f"mezcla_{primero}", nombre, m1.where(valido))
            agregar(dimension, f"mezcla_{segundo}", nombre, (mt - m1).where(valido))
            agregar(dimension, "variacion_total", nombre, var)
    return filas


def _orden(dimension):
    orden = ORDEN.get(dimension)
    return (lambda s: (orden.index(s) if s in orden else len(orden), s)) if orden else (lambda s: s)


def construir_scr(cubo: pd.DataFrame, salario_minimo: pd.Series, deflactor: pd.Series) -> pd.DataFrame:
    """bk_producto_pf_scr_m. ``salario_minimo`` y ``deflactor`` mensuales con PeriodIndex."""
    c = preparar_cubo(cubo)
    out = []
    for producto, nombre in PRODUCTOS_SCR.items():
        x = c[c["producto"] == nombre]
        if x.empty:
            raise ValueError(f"el cubo SCR no tiene el producto {nombre}")
        for df in construir_producto_scr(x, salario_minimo, deflactor):
            out.append(df.assign(producto=producto))
    df = pd.concat(out, ignore_index=True)
    return df[["producto", "dimension", "segmento", "medida", "fecha", "valor"]]


def salario_minimo_mensual() -> pd.Series:
    sm = SG.serie(SG.CODIGOS["salario_minimo"])
    return sm.groupby(sm.index.to_period("M")).last().asfreq("M").ffill()


def main(argv: list[str] | None = None) -> int:
    sgs_df = construir_sgs()
    defs, version = SP.definiciones()
    cubo = SP.cubo(defs, version, DESDE_SCR)
    deflactor = SG.deflactor(SG.serie_mensual(SG.CODIGOS["ipca"]))
    fin = pd.to_datetime(cubo["fecha"]).max().to_period("M")
    deflactor = deflactor / deflactor.get(fin, np.nan)        # R$ del último mes del SCR
    scr_df = construir_scr(cubo, salario_minimo_mensual(), deflactor)
    for nombre, df, fuente, desde in (
            ("bk_producto_pf_m", sgs_df, "bcb_sgs", [f"crudo/{SG.FUENTE}"]),
            ("bk_producto_pf_scr_m", scr_df, "bcb_scr", ["crudo/bcb_scr/scrdata", f"intermedio/scr_productos/{version}",
                                                         f"crudo/{SG.FUENTE}"])):
        A.publicar_gold(nombre, df, fuente=fuente, dataset=DATASET, desde=desde,
                        nota="Hojas por producto de personas (frente 12)")
        print(f"{nombre}: {len(df):,} filas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
