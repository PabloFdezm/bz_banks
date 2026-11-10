# -*- coding: utf-8 -*-
"""Hojas de empresas «MPME» y «Grandes» (frente 13).

Lleva a gold las cifras que el canvas de rediseño calculaba con el borrador `extraer_empresas.py`. Mismas fórmulas
que las hojas por producto de personas (`preparar_gold_bancos_producto_pf.py`, frente 12), de donde se importan los
cálculos de celdas y efectos.

TABLAS (datos/gold/)
--------------------
- bk_empresas_m (SGS, mensual): segmento, sub, medida, fecha (último día del mes), valor.
  Clave: segmento, sub, medida, fecha.
  * Segmentos: ``empresas`` (sub ``total``, ``libres``, ``direccionados``), ``mpme`` y ``grandes`` (sub ``total``),
    ``modalidad`` (sub = modalidad PJ del SGS: capital de giro, descuento de duplicatas, comercio exterior, BNDES…)
    y ``referencia`` (sub ``selic``, medida ``tasa``: Selic efectiva del mes anualizada, SGS 4189).
  * Niveles: ``saldo`` y ``concesiones`` (R$ millones; concesiones = flujo del mes); ``tasa``, ``mora90``,
    ``atraso15_90``, ``spread``, ``icc``, ``riesgo_eh`` y ``riesgo_4966`` (fracción: el % del SGS / 100).
  * Derivadas: ``saldo_aa`` (fracción) en todo lo que tiene saldo; ``peso`` de mpme y grandes en (mpme + grandes)
    (suman 1) y de cada modalidad en el saldo de empresas total (no suman 1: faltan modalidades chicas).
  * Descomposición de la tasa media de las modalidades libres con tasa (sub ``media`` y por modalidad, misma función
    que el frente 12): ``tasa_media``, ``d_tasa_media``, ``efecto_mezcla``, ``peso_saldo``, ``efecto_tasa``.
    Pondera por SALDO, no por concesiones: con concesiones el cheque especial (357 % a.a., concesiones del mes
    ≈ saldo) lleva la media a 52,8 % contra 24,4 % de la 20718 (sep-26); con saldo queda a ~2 pp. No es la 20718
    (faltan «outros créditos livres», sin tasa publicada).
- bk_empresas_scr_m (SCR.data, mensual desde ene-18): hoja, dimension, segmento, medida, fecha, valor.
  Clave: hoja, dimension, segmento, medida, fecha. Hojas: ``mpme`` (micro + pequeña + mediana) y ``grandes``.
  * Dimensiones: ``total`` («Total»), ``porte`` (solo mpme), ``sector`` (10 secciones CNAE + «Otros sectores»),
    ``institucion`` y la celda de la descomposición (``porte_sector`` en mpme, ``sector_institucion`` en grandes).
  * Medidas de nivel: ``saldo``, ``mora90``, ``atraso15_90``, ``activo_problematico`` (R$), ``ops``, ``cart_ops``;
    razones ``tasa_mora``, ``tasa_atraso``, ``tasa_apr``, ``peso``, ``saldo_aa``, ``ops_aa``, ``ticket``
    (cart_ops / ops, R$) y ``ticket_real`` (R$ del último mes, IPCA).
  * Aportes por dimensión (fracción; suman el total cada mes): ``aporte_crec``, ``aporte_mora``/``aporte_atraso``,
    ``efecto_tasa_x``, ``efecto_mezcla_x`` (fórmulas en preparar_gold_bancos_producto_pf.py).
  * Tres partes (dimensiones ``descomp_<a>_primero`` y ``descomp_<b>_primero``, medidas ``mora`` y ``atraso``):
    ``efecto_tasa`` (en celdas a × b), ``mezcla_<a>``, ``mezcla_<b>`` y ``variacion_total``. MPME: a = porte,
    b = sector. Grandes: a = sector, b = institución.

REGLAS
------
- 27706/27707 (riesgo E–H por porte) están DESACTIVADAS y terminan en dic-24; desde ene-25 el SGS publica el % de
  mayor riesgo de la Res. CMN 4.966 (29581–29583). No empalman: son definiciones distintas.
- 27701 + 27702 no es exactamente 20540 (diferencia de hasta R$ 37 mil millones): el peso de cada porte se mide sobre
  la suma de los dos, no sobre el total de empresas.
- SCR: el porte «Indisponível» queda fuera de las dos hojas (R$ 124 mil millones en sep-26). Instituciones como el
  canvas: Bancos, Desarrollo y fomento, Cooperativas, Financieras, Fintechs, Inst. de pago y Otros.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import almacen as A
import preparar_gold_bancos_producto_pf as PF
import preparar_gold_bancos_scr_productos as SP
import sgs as SG
import tabla_estandar as T

DATASET = "bancos_gold_empresas"
DESDE_SCR = 2018

# --- SGS -----------------------------------------------------------------------------------------------------------
_MOD = ("giro", "duplicatas", "antecipacao_cartao", "conta_garantida", "cheque_especial", "tarjeta", "acc", "export",
        "import", "repasse_externo", "bienes", "otros_libres", "direccionado", "bndes_inversion", "bndes", "rural",
        "inmobiliario", "programas_mpme")


def _modalidades() -> dict[str, dict[str, str]]:
    """sub → medida → clave de sgs.CODIGOS, con lo que exista para cada modalidad."""
    out = {}
    for m in _MOD:
        d = {medida: f"{pref}_pj_{m}" for medida, pref in
             (("saldo", "credito"), ("concesiones", "conc"), ("tasa", "tasa"), ("mora90", "mora90"))
             if f"{pref}_pj_{m}" in SG.CODIGOS}
        out[m] = d
    return out


SEGMENTOS_SGS: dict[str, dict[str, dict[str, str]]] = {
    "empresas": {
        "total": dict(saldo="credito_pj", concesiones="concesiones_pj", tasa="tasa_pj_total", mora90="mora90_pj",
                      atraso15_90="atraso15_90_pj", spread="spread_pj", icc="icc_pj", riesgo_4966="riesgo_4966_pj"),
        "libres": dict(saldo="credito_pj_libre", concesiones="concesiones_pj_libre", tasa="tasa_pj_libre",
                       mora90="mora90_pj_livre"),
    },
    "mpme": {"total": dict(saldo="credito_mpme", mora90="mora90_mpme", riesgo_eh="riesgo_eh_mpme",
                           riesgo_4966="riesgo_4966_mpme")},
    "grandes": {"total": dict(saldo="credito_grande", mora90="mora90_grande", riesgo_eh="riesgo_eh_grande",
                              riesgo_4966="riesgo_4966_grande")},
    "modalidad": _modalidades(),
}
# direccionados totales (saldo, concesiones, tasa, mora) como sub de empresas
SEGMENTOS_SGS["empresas"]["direccionados"] = SEGMENTOS_SGS["modalidad"].pop("direccionado")
# el saldo del BNDES, rural e inmobiliario PJ ya estaba en CODIGOS con otro nombre
for _m, _k in (("bndes", "credito_pj_bndes"), ("rural", "credito_pj_rural"), ("inmobiliario", "credito_pj_inmobiliario")):
    SEGMENTOS_SGS["modalidad"][_m] = {"saldo": _k, **SEGMENTOS_SGS["modalidad"][_m]}
# modalidades libres con tasa que entran en la descomposición de la tasa media
DESCOMPONER = [m for m in ("giro", "duplicatas", "antecipacao_cartao", "conta_garantida", "cheque_especial",
                           "tarjeta", "acc", "export", "import", "repasse_externo", "bienes")]
EN_PORCENTAJE = {"tasa", "mora90", "atraso15_90", "spread", "icc", "riesgo_eh", "riesgo_4966"}

# --- SCR -----------------------------------------------------------------------------------------------------------
PORTES = {"Micro": "Micro", "Pequeno": "Pequeña", "Médio": "Mediana", "Grande": "Grande"}
SIN_PORTE = "Sin dato"
SECTORES = {"Comércio; reparação de veículos automotores e motocicletas": "Comercio",
            "Indústrias de transformação": "Industria",
            "Atividades financeiras, de seguros e serviços relacionados": "Servicios financieros",
            "Transporte, armazenagem e correio": "Transporte y logística",
            "Administração pública, defesa e seguridade social": "Administración pública",
            "Eletricidade e gás": "Electricidad y gas", "Construção": "Construcción",
            "Atividades administrativas e serviços complementares": "Servicios administrativos",
            "Indústrias extrativas": "Extractivas",
            "Agricultura, pecuária, produção florestal, pesca e aquicultura": "Agropecuario"}
OTROS_SECTORES = "Otros sectores"
INSTITUCIONES = {"Banco": "Bancos", "Cooperativa": "Cooperativas", "Fintech": "Fintechs",
                 "Instituição de pagamento": "Inst. de pago", "Financeira": "Financieras",
                 "Desenvolvimento/Fomento": "Desarrollo y fomento"}
ORDEN = {
    "porte": ["Micro", "Pequeña", "Mediana", "Grande"],
    "sector": list(SECTORES.values()) + [OTROS_SECTORES],
    "institucion": ["Bancos", "Desarrollo y fomento", "Cooperativas", "Financieras", "Fintechs", "Inst. de pago",
                    "Otros"],
}
# hoja → (portes, dimensiones con aportes, celda de la descomposición en tres partes (a, b))
HOJAS = {
    "mpme": (["Micro", "Pequeña", "Mediana"], ["porte", "sector", "institucion"], ("porte", "sector")),
    "grandes": (["Grande"], ["sector", "institucion"], ("sector", "institucion")),
}
MEDIDAS_SCR = PF.MEDIDAS_SCR


# ================================================== SGS ============================================================

def construir_sgs(leer=SG.serie_mensual) -> pd.DataFrame:
    """bk_empresas_m. ``leer(codigo)`` devuelve la serie mensual (PeriodIndex) de un código SGS."""
    filas = []

    def agregar(segmento, sub, medida, s):
        s = s.replace([np.inf, -np.inf], np.nan).dropna()
        if len(s):
            filas.append(pd.DataFrame({"segmento": segmento, "sub": sub, "medida": medida,
                                       "fecha": T.fecha_fin(s.index), "valor": s.to_numpy(dtype=float)}))

    saldos = {}
    for segmento, subs in SEGMENTOS_SGS.items():
        for sub, medidas in subs.items():
            for medida, clave in medidas.items():
                s = leer(SG.CODIGOS[clave])
                agregar(segmento, sub, medida, s / 100 if medida in EN_PORCENTAJE else s)
                if medida == "saldo":
                    s = s.reindex(pd.period_range(s.index.min(), s.index.max(), freq="M"))
                    saldos[(segmento, sub)] = s
                    agregar(segmento, sub, "saldo_aa", s / s.shift(12) - 1)
    # pesos: mpme y grandes sobre su suma (suman 1); modalidades sobre empresas total
    suma = saldos[("mpme", "total")] + saldos[("grandes", "total")]
    for seg in ("mpme", "grandes"):
        agregar(seg, "total", "peso", saldos[(seg, "total")] / suma)
    tot = saldos[("empresas", "total")]
    for sub in SEGMENTOS_SGS["modalidad"]:
        if ("modalidad", sub) in saldos:
            agregar("modalidad", sub, "peso", saldos[("modalidad", sub)] / tot)
    # descomposición de la tasa media de las modalidades libres (reutiliza la del frente 12)
    mods = SEGMENTOS_SGS["modalidad"]
    tasas = {m: leer(SG.CODIGOS[mods[m]["tasa"]]) / 100 for m in DESCOMPONER}
    saldo = {m: leer(SG.CODIGOS[mods[m]["saldo"]]) for m in DESCOMPONER}
    for (sub, medida), serie in PF.descomponer_tasa(tasas, saldo).items():
        agregar("modalidad", sub, "peso_saldo" if medida == "peso_conc" else medida, serie)
    agregar("referencia", "selic", "tasa", leer(SG.CODIGOS["selic_efectiva_mes"]) / 100)
    df = pd.concat(filas, ignore_index=True)
    fin = df.loc[df["segmento"] != "referencia", "fecha"].max()
    return df[(df["segmento"] != "referencia") | (df["fecha"] <= fin)].reset_index(drop=True)


# ================================================== SCR ============================================================

def preparar_cubo(cubo: pd.DataFrame) -> pd.DataFrame:
    """Cubo PJ con porte, sector e institución del canvas y mes como Period."""
    c = cubo[cubo["cliente"] == "PJ"].copy()
    c["mes"] = pd.to_datetime(c["fecha"]).dt.to_period("M")
    c["porte"] = c["porte"].map(PORTES).fillna(SIN_PORTE)
    c["sector"] = c["cnae_ocupacao"].map(SECTORES).fillna(OTROS_SECTORES)
    c["institucion"] = c["segmento"].map(INSTITUCIONES).fillna("Otros")
    c["total"] = "Total"
    return c


def _orden(dimension):
    orden = ORDEN.get(dimension)
    return (lambda s: (orden.index(s) if s in orden else len(orden), s)) if orden else (lambda s: s)


def construir_hoja_scr(c: pd.DataFrame, dims: list[str], celda: tuple[str, str],
                       deflactor: pd.Series) -> list[pd.DataFrame]:
    """Filas largas de una hoja (``c`` ya filtrado a sus portes). Sin columna hoja."""
    a, b = celda
    c = c.assign(**{f"{a}_{b}": c[a] + " · " + c[b]})
    meses = pd.period_range(c["mes"].min(), c["mes"].max(), freq="M")
    total = c.groupby("mes")[MEDIDAS_SCR].sum().reindex(meses)
    filas = []

    def agregar(dimension, segmento, medida, s):
        s = s.replace([np.inf, -np.inf], np.nan).dropna()
        if len(s):
            filas.append(pd.DataFrame({"dimension": dimension, "segmento": segmento, "medida": medida,
                                       "fecha": T.fecha_fin(s.index), "valor": s.to_numpy(dtype=float)}))

    def niveles(dimension, segmento, g):
        for col, nombre in PF.NOMBRE_NIVEL.items():
            agregar(dimension, segmento, nombre, g[col])
        sa = g["carteira_ativa"]
        agregar(dimension, segmento, "tasa_mora", g["carteira_inadimplencia"] / sa)
        agregar(dimension, segmento, "tasa_atraso", g["vencido_de_15_ate_90_dias"] / sa)
        agregar(dimension, segmento, "tasa_apr", g["ativo_problematico"] / sa)
        agregar(dimension, segmento, "peso", sa / total["carteira_ativa"])
        agregar(dimension, segmento, "saldo_aa", sa / sa.shift(12) - 1)
        agregar(dimension, segmento, "ops_aa", g["ops"] / g["ops"].shift(12) - 1)
        tick = g["cart_ops"] / g["ops"].where(g["ops"] > 0)
        agregar(dimension, segmento, "ticket", tick)
        agregar(dimension, segmento, "ticket_real", tick / deflactor.reindex(meses))

    niveles("total", "Total", total)
    for dimension in dims + [f"{a}_{b}"]:
        g = c.groupby(["mes", dimension])[MEDIDAS_SCR].sum()
        for segmento in sorted(set(g.index.get_level_values(1)), key=_orden(dimension)):
            niveles(dimension, segmento, g.xs(segmento, level=1).reindex(meses))

    # aportes por segmento (suman el total)
    tot = total["carteira_ativa"]
    for dimension in dims:
        sal = c.groupby(["mes", dimension])["carteira_ativa"].sum().unstack().reindex(meses).fillna(0)
        for segmento in sal.columns:
            agregar(dimension, segmento, "aporte_crec", (sal[segmento] - sal[segmento].shift(12)) / tot.shift(12))
        for nombre, num in PF.NUMERADORES.items():
            w, m1, m0 = PF._celdas(c, meses, total, [dimension], num)
            w0 = w.shift(12)
            for s in w.columns:
                agregar(dimension, s, f"aporte_{nombre}", w[s] * m1[s] - w0[s] * m0[s])
                agregar(dimension, s, f"efecto_tasa_{nombre}", (w[s] + w0[s]) / 2 * (m1[s] - m0[s]))
                agregar(dimension, s, f"efecto_mezcla_{nombre}", (m1[s] + m0[s]) / 2 * (w[s] - w0[s]))

    # tres partes, con los dos órdenes
    for nombre, num in PF.NUMERADORES.items():
        tasa, mez = PF._efectos(c, meses, total, [a, b], num)
        tt, mt = tasa.sum(axis=1), mez.sum(axis=1)
        nivel = total[num] / total["carteira_ativa"]
        var = nivel - nivel.shift(12)
        valido = var.notna()
        for primero, segundo in ((a, b), (b, a)):
            _, mez1 = PF._efectos(c, meses, total, [primero], num)
            m1 = mez1.sum(axis=1)
            dimension = f"descomp_{primero}_primero"
            agregar(dimension, "efecto_tasa", nombre, tt.where(valido))
            agregar(dimension, f"mezcla_{primero}", nombre, m1.where(valido))
            agregar(dimension, f"mezcla_{segundo}", nombre, (mt - m1).where(valido))
            agregar(dimension, "variacion_total", nombre, var)
    return filas


def construir_scr(cubo: pd.DataFrame, deflactor: pd.Series) -> pd.DataFrame:
    """bk_empresas_scr_m. ``deflactor`` mensual con PeriodIndex (1 en el último mes del SCR)."""
    c = preparar_cubo(cubo)
    out = []
    for hoja, (portes, dims, celda) in HOJAS.items():
        x = c[c["porte"].isin(portes)]
        if x.empty:
            raise ValueError(f"el cubo SCR no tiene empresas de porte {portes}")
        for df in construir_hoja_scr(x, dims, celda, deflactor):
            out.append(df.assign(hoja=hoja))
    df = pd.concat(out, ignore_index=True)
    return df[["hoja", "dimension", "segmento", "medida", "fecha", "valor"]]


def main(argv: list[str] | None = None) -> int:
    sgs_df = construir_sgs()
    defs, version = SP.definiciones()
    cubo = SP.cubo(defs, version, DESDE_SCR)
    deflactor = SG.deflactor(SG.serie_mensual(SG.CODIGOS["ipca"]))
    fin = pd.to_datetime(cubo["fecha"]).max().to_period("M")
    deflactor = deflactor / deflactor.get(fin, np.nan)        # R$ del último mes del SCR
    scr_df = construir_scr(cubo, deflactor)
    for nombre, df, fuente, desde in (
            ("bk_empresas_m", sgs_df, "bcb_sgs", [f"crudo/{SG.FUENTE}"]),
            ("bk_empresas_scr_m", scr_df, "bcb_scr", ["crudo/bcb_scr/scrdata", f"intermedio/scr_productos/{version}",
                                                      f"crudo/{SG.FUENTE}"])):
        A.publicar_gold(nombre, df, fuente=fuente, dataset=DATASET, desde=desde,
                        nota="Hojas de empresas MPME y Grandes (frente 13)")
        print(f"{nombre}: {len(df):,} filas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
