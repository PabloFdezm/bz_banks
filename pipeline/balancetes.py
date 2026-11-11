# -*- coding: utf-8 -*-
"""Balancetes COSIF del BCB, documento 4060 (conglomerado prudencial), mensual → bk_balancete_m y bk_sistema_bal_m.

Fuente: https://www4.bcb.gov.br/fis/cosif/cont/balan/individualizados/AAAAMM/4060/AAAAMM-4060-<CNPJ8>.ZIP, un archivo
por líder de conglomerado y mes (sondeo aprobado el 9-nov-2026: tareas/borradores/balancetes_sondeo.md). Es la única
fuente mensual con balance y resultado por banco; el IF.Data (bk_panel) es trimestral.

Trampas (verificadas el 11-nov-2026):
1. El archivo va por el CNPJ8 del **líder** del conglomerado (cadastro de IF.Data, ``CnpjInstituicaoLider``), no por
   el código C. Para Itaú el líder es la holding (60872504). Dentro del archivo, ``COD_CONGL`` es nuestro
   ``cod_inst``: se exige que coincida; si no, el archivo no se usa.
2. Latin-1, separador «;», coma decimal y tres líneas de título antes de la cabecera (``#DATA_BASE;…``).
3. Las cuentas de resultado (7 y 8) acumulan por semestre y se reinician en enero y julio; junio y diciembre NO
   cierran el resultado en el 4060. Flujo del mes = acumulado − acumulado del mes anterior, salvo ene y jul.
4. El 4060 trae el resultado abierto: el patrimonio de cierre es 6 + 7 + 8 (sin 7 y 8 queda bajo).
5. El plan de cuentas cambia en ene-25 (Res. CMN 4.966): antes ~160 cuentas de nivel 1–3; después ~750, con
   desglose de nivel 4. Las cuentas se casan por concepto (definiciones/bcb_balancetes__cuentas.json), por época.
7. Algunos conglomerados de un solo miembro no tienen 4060 (Banco da Amazônia): se usa el 4010 del líder, que trae
   las mismas cuentas sin COD_CONGL; el cuadre contra IF.Data lo valida. BRB no publica balancetes (ni 4060 ni 4010)
   desde jul-25: queda como hueco.
8. Hay archivos con todas las filas repetidas (Cielo IP, 202507): se deduplican si las copias son idénticas.
9. El patrimonio de junio y diciembre del 4060 es anterior al cierre del semestre (sin destinar dividendos ni
   JCP): queda 1–6 % sobre IF.Data. El cuadre no lo exige en esos meses (ver informe).
6. Los meses se publican por trimestre (Comunicado 44.132/2025), y al 11-nov-2026 la carpeta de 2026-04 en adelante
   no existe (404): la serie llega hasta donde el BCB publicó. Un 404 se anota como faltante, no es error.

Uso:  python -X utf8 pipeline/balancetes.py colectar [--desde AAAAMM] [--hasta AAAAMM]   (baja lo que falte)
      python -X utf8 pipeline/balancetes.py gold [--descargar]                           (arma y publica; así lo
                                                                                          llama actualizar.py)
      python -X utf8 pipeline/balancetes.py --resumen                                    (cobertura y cuadres)
"""
from __future__ import annotations

import argparse
import io
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

import almacen as A
import bancos as B
import periodos as PER
import red

FUENTE = "bcb_balancetes"
DATASET = "4060"
DOC = "4060"
DOC_UNICO = "4010"   # conglomerados de un solo miembro (trampa 7)
URL = "https://www4.bcb.gov.br/fis/cosif/cont/balan/individualizados/{m}/{doc}/{m}-{doc}-{cnpj}.ZIP"
UA = {"User-Agent": "Mozilla/5.0 (bz_banks; datos públicos del BCB)"}
DESDE = "201801"
HILOS = 6
INTENTOS = 3


# ---------------------------------------------------------------- meses y líderes

def meses(desde: str, hasta: str) -> list[str]:
    return [p.strftime("%Y%m") for p in pd.period_range(pd.Period(desde, "M"), pd.Period(hasta, "M"), freq="M")]


def cadastro_para(mes: str, disponibles: list[str]) -> str:
    """El cadastro de IF.Data (trimestral) que rige el mes: el del trimestre del mes o, si falta, el más cercano
    anterior; si no hay anterior, el primero."""
    fin_q = pd.Period(mes, "M").asfreq("Q").asfreq("M", "end").strftime("%Y%m")
    previos = [d for d in disponibles if d <= fin_q]
    return previos[-1] if previos else disponibles[0]


def _cadastro(mes: str) -> pd.DataFrame:
    carpeta = A.ruta_cruda("bcb_ifdata", "cadastro")
    disp = sorted(p.stem.split("_")[1] for p in carpeta.glob("cadastro_*.parquet"))
    return pd.read_parquet(carpeta / f"cadastro_{cadastro_para(mes, disp)}.parquet",
                           columns=["CodInst", "CnpjInstituicaoLider", "CodConglomeradoPrudencial"])


def lideres(mes: str, cods: list[str]) -> dict[str, str]:
    """cod_inst → CNPJ8 del líder del conglomerado, según el cadastro que rige el mes."""
    m = _cadastro(mes).drop_duplicates("CodInst").set_index("CodInst")["CnpjInstituicaoLider"]
    return {c: str(m[c]).zfill(8) for c in cods if c in m.index and str(m[c]).strip() not in ("", "nan", "None")}


def miembro_unico(mes: str, cods: list[str]) -> set[str]:
    """Conglomerados de un solo miembro individual (p. ej. Banco da Amazônia): el BCB no publica su 4060 y el 4010
    del líder ES el conglomerado. Para ellos se usa el 4010 (trampa 7)."""
    cad = _cadastro(mes)
    ind = cad[~cad["CodInst"].astype(str).str.startswith("C")]
    n = ind.groupby("CodConglomeradoPrudencial")["CodInst"].nunique()
    return {c for c in cods if n.get(c, 0) == 1}


# ---------------------------------------------------------------- colecta

def nombre_zip(mes: str, cnpj: str, doc: str = "4060") -> str:
    return f"{mes}-{doc}-{cnpj}.ZIP"


def _validar_zip(p: Path) -> None:
    with zipfile.ZipFile(p) as z:
        if not any(n.upper().endswith(".CSV") for n in z.namelist()):
            raise ValueError(f"{p.name}: el ZIP no trae CSV")


def colectar(desde: str, hasta: str) -> pd.DataFrame:
    """Baja los 4060 que faltan en disco. Devuelve una fila por banco × mes con el estado (bajado, ya estaba, 404)."""
    import certificados  # noqa: F401  CA del proxy corporativo; antes de requests
    import requests
    red.exigir_red("balancetes 4060")
    d = A.ruta_cruda(FUENTE, DATASET)
    d.mkdir(parents=True, exist_ok=True)
    cods = [b["cod_inst"] for b in B.universo()]
    sesion = requests.Session()
    sesion.headers.update(UA)

    def una(mes: str, cod: str, cnpj: str, unico: bool) -> dict:
        fila = {"periodo": mes, "cod_inst": cod, "cnpj_lider": cnpj}
        for doc in ((DOC, DOC_UNICO) if unico else (DOC,)):
            destino = d / nombre_zip(mes, cnpj, doc)
            if destino.exists():
                return {**fila, "archivo": destino.name, "estado": "ya estaba"}
            url = URL.format(m=mes, doc=doc, cnpj=cnpj)
            try:
                red.bajar_a_disco(sesion.get, url, destino, intentos=INTENTOS, espera=lambda n, e: 5 * n,
                                  reintentables=(requests.ConnectionError, requests.Timeout), validar=_validar_zip)
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    continue
                raise
            return {**fila, "archivo": destino.name, "estado": "bajado", "url": url}
        return {**fila, "estado": "404"}

    estados = []
    for mes in meses(desde, hasta):
        lid, uni = lideres(mes, cods), miembro_unico(mes, cods)
        with ThreadPoolExecutor(HILOS) as ex:
            res = list(ex.map(lambda c: una(mes, c, lid[c], c in uni), [c for c in cods if c in lid]))
        estados += res + [{"periodo": mes, "cod_inst": c, "estado": "sin líder en el cadastro"} for c in cods
                          if c not in lid]
        nuevos = [r for r in res if r["estado"] == "bajado"]
        if nuevos:   # manifiesto: una escritura por mes, no por archivo
            man = A.leer_manifiesto(d) or {"fuente": FUENTE, "dataset": DATASET, "archivos": {}}
            for r in nuevos:
                p = d / r["archivo"]
                man["archivos"][p.name] = {"url": r["url"], "sha256": A.sha256_archivo(p), "bytes": p.stat().st_size,
                                           "descargado_en": A._ahora()}
            A.escribir_manifiesto(d, man)
        n = pd.Series([r["estado"] for r in res]).value_counts().to_dict()
        print(f"  {mes}: {n}")
    return pd.DataFrame(estados)


# ---------------------------------------------------------------- lectura

def leer_zip(p: Path) -> pd.DataFrame:
    """Un 4060 → filas con periodo, cod_congl, conta (8 dígitos), nome y saldo (float)."""
    with zipfile.ZipFile(p) as z:
        nombre = next(n for n in z.namelist() if n.upper().endswith(".CSV"))
        texto = z.read(nombre).decode("latin-1")
    lineas = texto.splitlines()
    k = next(i for i, l in enumerate(lineas) if l.startswith("#DATA_BASE"))
    df = pd.read_csv(io.StringIO("\n".join(lineas[k:])), sep=";", dtype=str, keep_default_na=False)
    df.columns = [c.lstrip("#") for c in df.columns]
    doc = p.name.split("-")[1]
    if set(df["DOCUMENTO"]) != {doc}:
        raise ValueError(f"{p.name}: documento {set(df['DOCUMENTO'])}")
    return pd.DataFrame({"periodo": df["DATA_BASE"].str.strip(), "cod_congl": df["COD_CONGL"].str.strip(),
                         "conta": df["CONTA"].str.strip(), "nome": df["NOME_CONTA"].str.strip(),
                         "saldo": pd.to_numeric(df["SALDO"].str.replace(",", ".", regex=False), errors="raise")})


def saldos() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Todos los 4060 en disco → (saldos largos con cod_inst, descartes). Un archivo cuyo COD_CONGL no es un banco
    del panel, o que trae otro mes, se descarta con su motivo."""
    d = A.ruta_cruda(FUENTE, DATASET)
    cods = {b["cod_inst"] for b in B.universo()}
    partes, descartes = [], []
    cods_l = sorted(cods)
    for p in sorted(d.glob("*.ZIP")):
        mes, doc, cnpj = p.stem.split("-")
        df = leer_zip(p)
        if doc == DOC_UNICO:   # 4010 de un conglomerado de un solo miembro: el banco sale del cadastro del mes
            dueno = [c for c, v in lideres(mes, cods_l).items() if v == cnpj and c in miembro_unico(mes, cods_l)]
            if len(dueno) != 1:
                descartes.append({"archivo": p.name, "periodo": mes, "motivo": "4010 sin conglomerado de un miembro"})
                continue
            df["cod_congl"] = dueno[0]
        congl = set(df["cod_congl"])
        if len(congl) != 1 or not congl <= cods:
            descartes.append({"archivo": p.name, "periodo": mes, "motivo": f"COD_CONGL {sorted(congl)} fuera del panel"})
            continue
        if set(df["periodo"]) != {mes}:
            descartes.append({"archivo": p.name, "periodo": mes, "motivo": f"DATA_BASE {sorted(set(df['periodo']))}"})
            continue
        partes.append(df.rename(columns={"cod_congl": "cod_inst"}))
    out = pd.concat(partes, ignore_index=True)
    # Algunos archivos traen cada fila dos veces (Cielo IP, jul-25): se quitan las copias idénticas; si una cuenta
    # repite con otro saldo, falla (trampa 8).
    out = out.drop_duplicates()
    dup = out.duplicated(["cod_inst", "periodo", "conta"], keep=False)
    if dup.any():
        raise ValueError(f"cuentas repetidas: {out[dup].head()}")
    return out, pd.DataFrame(descartes, columns=["archivo", "periodo", "motivo"])


# ---------------------------------------------------------------- conceptos

DEF_CUENTAS = "bcb_balancetes__cuentas"
QUIEBRE = "202501"     # primer mes del plan nuevo en el 4060 (no es el 202503 de IF.Data)


def epoca(periodo: str) -> str:
    return "nueva" if periodo >= QUIEBRE else "vieja"


def acumulado_a_flujo(df: pd.DataFrame) -> pd.Series:
    """``df`` con cod_inst, concepto, periodo (AAAAMM) y valor = resultado acumulado del semestre → flujo del mes.
    Enero y julio: el propio acumulado. Otro mes: acumulado − el del mes anterior; vacío si falta el mes anterior."""
    per = pd.PeriodIndex(pd.to_datetime(df["periodo"], format="%Y%m"), freq="M")
    clave = df["cod_inst"] + "|" + df["concepto"]
    previo = pd.Series(df["valor"].to_numpy(), index=pd.MultiIndex.from_arrays([clave, per]))
    ant = previo.reindex(pd.MultiIndex.from_arrays([clave, per - 1])).to_numpy()
    reinicio = per.month.isin([1, 7])
    return pd.Series(df["valor"].where(reinicio, df["valor"] - ant).to_numpy(), index=df.index)


def conceptos(sal: pd.DataFrame, defn: dict | None = None) -> pd.DataFrame:
    """Saldos largos → cod_inst × periodo × concepto, con valor (saldo de fin de mes o flujo del mes) y tipo."""
    defn = defn or A.leer_definicion(DEF_CUENTAS)
    s = sal.assign(base=sal["conta"].str[:7], epoca=sal["periodo"].map(epoca))
    filas = []
    for nombre, c in defn["conceptos"].items():
        for ep in ("vieja", "nueva"):
            x = s[(s["epoca"] == ep) & s["base"].isin(c[ep])]
            g = x.groupby(["cod_inst", "periodo"])["saldo"].sum().rename("valor").reset_index()
            # Un mes sin ninguna de las cuentas queda vacío para los saldos; para los flujos es cero (no hubo).
            filas.append(g.assign(concepto=nombre, tipo=c["tipo"]))
    out = pd.concat(filas, ignore_index=True)
    meses_banco = s[["cod_inst", "periodo"]].drop_duplicates()
    fl = out[out["tipo"] == "flujo"]
    fl = (meses_banco.merge(pd.DataFrame({"concepto": fl["concepto"].unique()}), how="cross")
          .merge(fl, on=["cod_inst", "periodo", "concepto"], how="left").assign(tipo="flujo"))
    fl["valor"] = fl["valor"].fillna(0.0)
    fl["valor"] = acumulado_a_flujo(fl)
    return pd.concat([out[out["tipo"] == "saldo"], fl], ignore_index=True)[
        ["cod_inst", "periodo", "concepto", "tipo", "valor"]].sort_values(["cod_inst", "concepto", "periodo"]).reset_index(drop=True)


# ---------------------------------------------------------------- cuadre y gold

TOL_SALDO = 0.005      # 0,5 %: activo, patrimonio, crédito y depósitos de fin de trimestre contra IF.Data
TOL_LUCRO = 0.01       # 1 %: suma de los tres lucros mensuales contra el lucro del trimestre de IF.Data
SALDOS_CUADRE = ["ativo_total", "patrimonio_liquido", "credito_liquido", "depositos"]
COLUMNAS_M = ["cod_inst", "periodo", "fecha", "concepto", "tipo", "valor", "cuadra_ifdata"]
COLUMNAS_G = ["optica", "grupo", "periodo", "fecha", "n_bancos", "lucro_12m", "pl_medio_12m", "roe_12m", "ativo_total",
              "patrimonio_liquido", "credito_liquido", "depositos", "depositos_aa", "credito_depositos",
              "patrimonio_activo", "orden_optica", "orden_grupo"]


def fin_trimestre(periodo: str) -> str:
    """AAAAMM → AAAAMM del último mes de su trimestre."""
    return periodo[:4] + f"{(int(periodo[4:]) + 2) // 3 * 3:02d}"


def ancho(c: pd.DataFrame) -> pd.DataFrame:
    return c.pivot_table(index=["cod_inst", "periodo"], columns="concepto", values="valor").reset_index()


def cuadre(c: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """Banco × trimestre: diferencias relativas contra bk_panel y si cuadra. El patrimonio de junio y diciembre no
    se exige (trampa 9). Un trimestre sin sus tres meses no cuadra (el lucro no se puede comparar)."""
    w = ancho(c)
    w["q"] = w["periodo"].map(fin_trimestre)
    fin = w[w["periodo"] == w["q"]]
    luc = w.groupby(["cod_inst", "q"]).agg(n_meses=("periodo", "size"), lucro=("lucro_liquido", "sum")).reset_index()
    pv = panel[panel["metrica"].isin(SALDOS_CUADRE + ["lucro_liquido_q"])].pivot_table(
        index=["cod_inst", "periodo"], columns="metrica", values="valor").reset_index()
    pv["q"] = pv["periodo"].astype(str)
    j = (fin.merge(pv.drop(columns="periodo"), on=["cod_inst", "q"], suffixes=("", "_if"))
         .merge(luc, on=["cod_inst", "q"]).reset_index(drop=True))
    out = j[["cod_inst", "q", "n_meses"]].rename(columns={"q": "trimestre_fin"}).copy()
    malo = pd.Series(False, index=j.index)
    motivo = pd.Series("", index=j.index)
    for s in SALDOS_CUADRE:
        out[f"d_{s}"] = j[s] / j[f"{s}_if"] - 1
        exige = ~(j["q"].str[4:].isin(["06", "12"]) & (s == "patrimonio_liquido"))
        m = exige & out[f"d_{s}"].abs().gt(TOL_SALDO)
        motivo = motivo.where(~m, motivo + s + " " + out[f"d_{s}"].mul(100).round(2).astype(str) + " %; ")
        malo |= m
    out["d_lucro"] = (j["lucro"] / j["lucro_liquido_q"] - 1).where(j["n_meses"].eq(3))
    m = out["d_lucro"].abs().gt(TOL_LUCRO) | j["n_meses"].lt(3)
    motivo = motivo.where(~m, motivo + "lucro del trimestre " + out["d_lucro"].mul(100).round(2).astype(str) + " %; ")
    out["cuadra"] = ~(malo | m)
    out["motivo"] = motivo.str.strip()
    return out


def bk_balancete_m(c: pd.DataFrame, cq: pd.DataFrame, defn: dict) -> pd.DataFrame:
    """Los conceptos que se publican, desde el primer mes que cuadra con IF.Data, con la marca del cuadre de su
    trimestre (vacía si IF.Data todavía no tiene ese trimestre)."""
    pub = [k for k, v in defn["conceptos"].items() if v.get("publica")]
    m = c[c["concepto"].isin(pub) & c["periodo"].ge(defn["publicable_desde"])].copy()
    m["trimestre_fin"] = m["periodo"].map(fin_trimestre)
    m = m.merge(cq[["cod_inst", "trimestre_fin", "cuadra"]], on=["cod_inst", "trimestre_fin"], how="left")
    m["cuadra_ifdata"] = m["cuadra"].astype("boolean")
    m["fecha"] = PER.fin_de_mes(m["periodo"]).dt.date
    return m[COLUMNAS_M].sort_values(["cod_inst", "concepto", "periodo"]).reset_index(drop=True)


def por_banco(m: pd.DataFrame) -> pd.DataFrame:
    """Banco × mes con los meses que cuadran (o sin trimestre de IF.Data para comparar): saldos, lucro de 12 meses
    (exige los 12) y saldos de t−12 (PL medio = (t + t−12) / 2, como pl_medio_ttm de IF.Data)."""
    ok = m[m["cuadra_ifdata"].fillna(True).astype(bool)]
    w = ok.pivot_table(index=["cod_inst", "periodo"], columns="concepto", values="valor")
    partes = []
    for cod, x in w.groupby(level=0):
        x = x.droplevel(0)
        x.index = pd.PeriodIndex(pd.to_datetime(x.index, format="%Y%m"), freq="M")
        x = x.reindex(pd.period_range(x.index.min(), x.index.max(), freq="M"))
        x["lucro_12m"] = x["lucro_liquido"].rolling(12, min_periods=12).sum()
        x["pl_t12"] = x["patrimonio_liquido"].shift(12)
        x["dep_t12"] = x["depositos"].shift(12)
        x = x[x["ativo_total"].notna()]
        x.insert(0, "periodo", x.index.strftime("%Y%m"))
        x.insert(0, "cod_inst", cod)
        partes.append(x.reset_index(drop=True))
    return pd.concat(partes, ignore_index=True)


def _suma(s: pd.Series):
    return s.sum(min_count=1)


def bk_sistema_bal_m(m: pd.DataFrame) -> pd.DataFrame:
    """Óptica × grupo × mes como Σ numerador / Σ denominador sobre los bancos con dato (nunca promedio de ratios).
    El ROE suma solo bancos con lucro de 12 meses y PL de t y t−12; el a/a de depósitos, bancos con t y t−12."""
    b = por_banco(m)
    attrs = B.atributos().set_index("cod_inst").loc[[x["cod_inst"] for x in B.universo()]].reset_index()
    mb = B.pertenencia(attrs)[["cod_inst", "optica", "grupo", "orden_optica", "orden_grupo"]]
    j = mb.merge(b, on="cod_inst")
    roe_ok = j["lucro_12m"].notna() & j["patrimonio_liquido"].notna() & j["pl_t12"].notna()
    dep_ok = j["depositos"].notna() & j["dep_t12"].gt(0)
    j = j.assign(l12=j["lucro_12m"].where(roe_ok), plm=((j["patrimonio_liquido"] + j["pl_t12"]) / 2).where(roe_ok),
                 dep_a=j["depositos"].where(dep_ok), dep_b=j["dep_t12"].where(dep_ok))
    claves = ["optica", "grupo", "orden_optica", "orden_grupo", "periodo"]
    g = j.groupby(claves).agg(n_bancos=("cod_inst", "nunique"), lucro_12m=("l12", _suma), pl_medio_12m=("plm", _suma),
                              ativo_total=("ativo_total", _suma), patrimonio_liquido=("patrimonio_liquido", _suma),
                              credito_liquido=("credito_liquido", _suma), depositos=("depositos", _suma),
                              dep_a=("dep_a", _suma), dep_b=("dep_b", _suma)).reset_index()
    g["roe_12m"] = g["lucro_12m"] / g["pl_medio_12m"]
    g["depositos_aa"] = g["dep_a"] / g["dep_b"] - 1
    g["credito_depositos"] = g["credito_liquido"] / g["depositos"]
    g["patrimonio_activo"] = g["patrimonio_liquido"] / g["ativo_total"]
    g["fecha"] = PER.fin_de_mes(g["periodo"]).dt.date
    return g[COLUMNAS_G].sort_values(["orden_optica", "orden_grupo", "periodo"]).reset_index(drop=True)


def construir() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    defn = A.leer_definicion(DEF_CUENTAS)
    sal, descartes = saldos()
    if len(descartes):
        print(f"  [!] {len(descartes)} archivos descartados:\n{descartes.to_string()}", file=sys.stderr)
    c = conceptos(sal, defn)
    panel = pd.read_parquet(A.GOLD / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "valor"])
    cq = cuadre(c, panel)
    m = bk_balancete_m(c, cq, defn)
    g = bk_sistema_bal_m(m)
    huecos = cq[~cq["cuadra"] & cq["trimestre_fin"].ge(defn["publicable_desde"])].reset_index(drop=True)
    # En gold «periodo» es trimestral (AAAAMM de fin de trimestre; verificar_gold): estas tablas son mensuales.
    return m.rename(columns={"periodo": "mes"}), g.rename(columns={"periodo": "mes"}), cq, huecos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("accion", nargs="?", choices=["colectar", "gold"], default="gold")
    ap.add_argument("--desde", default=DESDE)
    ap.add_argument("--hasta", default=pd.Timestamp.today().strftime("%Y%m"))
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--descargar", action="store_true", help="con gold: baja antes los meses que falten")
    a = ap.parse_args(argv)
    if a.accion == "colectar":
        est = colectar(a.desde, a.hasta)
        print(est["estado"].value_counts().to_string())
        return 0
    if a.descargar:
        colectar(a.desde, a.hasta)
    m, g, cq, huecos = construir()
    desde_pub = A.leer_definicion(DEF_CUENTAS)["publicable_desde"]
    print(f"bk_balancete_m: {len(m):,} filas, {m['cod_inst'].nunique()} bancos, {m['mes'].min()}–{m['mes'].max()}")
    print(f"cuadre desde {desde_pub}: {int(cq.loc[cq['trimestre_fin'].ge(desde_pub), 'cuadra'].sum())} de "
          f"{int(cq['trimestre_fin'].ge(desde_pub).sum())} banco-trimestres; huecos: {len(huecos)}")
    if a.resumen:
        print(huecos[["cod_inst", "trimestre_fin", "motivo"]].to_string())
        return 0
    desde = [f"crudo/{FUENTE}/{DATASET}", "gold/bk_panel.parquet"]
    A.publicar_gold("bk_balancete_m", m, fuente=FUENTE, dataset="gold", desde=desde,
                    nota="Balancetes 4060 por concepto (frente 11)")
    A.publicar_gold("bk_sistema_bal_m", g, fuente=FUENTE, dataset="gold", desde=desde,
                    nota="Balancetes 4060 por grupo (frente 11)")
    for nombre, df, nota in (("huecos_balancetes.csv", huecos, "banco-trimestres que no cuadran con IF.Data"),
                             ("cuadre_balancetes.csv", cq, "cuadre de cada banco-trimestre contra bk_panel")):
        A.guardar_derivado(FUENTE, "gold", nombre, df.to_csv(index=False).encode("utf-8"), desde=desde,
                           como=A.comando_actual(), nota=nota)
    print(f"bk_sistema_bal_m: {len(g):,} filas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
