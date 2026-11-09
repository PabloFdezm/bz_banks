# -*- coding: utf-8 -*-
"""Fuente CVM (ITR y DFP) de los bancos cotizados: descarga, extracción filtrada y tabla gold ``bk_publicado``.

POR QUÉ EXISTE
--------------
El IF.Data del BCB llega con rezago: el trimestre cierra y los datos aparecen semanas después. Los bancos
cotizados, en cambio, publican su ITR (Informe Trimestral) en la CVM mucho antes. Esta fuente da el último
trimestre publicado con la base contable rotulada (IFRS o BR GAAP), que es lo que necesita la tarjeta
B8-06-0 «Último trimestre publicado (CVM)».

Es OTRA contabilidad, no un reemplazo del IF.Data: el ITR/DFP es el consolidado societario bajo
pronunciamientos del CPC (o IFRS, según el banco), mientras que el IF.Data es el conglomerado prudencial
bajo COSIF. Los dos números del mismo trimestre difieren —por las subsidiarias de seguros, por el método
de participación y por reglas de consolidación— y esa diferencia se mide y se informa
(``contrastar``), nunca se corrige.

CAPAS
-----
    datos/crudo/cvm/itr/<año>/itr_cia_aberta_<año>.zip      el ZIP íntegro de la CVM, sin tocar
    datos/crudo/cvm/dfp/<año>/dfp_cia_aberta_<año>.zip      idem, estados anuales
    datos/crudo/cvm/cadastro/actual/cad_cia_aberta.csv      registro de compañías abiertas
    datos/derivado/cvm/bancos/...                           solo las filas de los bancos del mapa (parquet)
    datos/gold/bk_publicado.parquet                         las líneas mínimas por banco y trimestre

El ZIP se vuelve a bajar cuando cambia de tamaño en el servidor: la CVM regenera el del año en curso casi
todas las semanas (entra el ITR nuevo, o una compañía reentrega y sube la VERSAO).

TRAMPAS DE LA FUENTE (todas verificadas sobre el dato; ver también definiciones/cvm__dfp_bancos.json)
------------------------------------------------------------------------------------------------------
1. Cada cuenta viene DOS veces por ``ORDEM_EXERC`` («ÚLTIMO» y «PENÚLTIMO», el ejercicio comparativo):
   sin filtrar se duplica todo y se mezclan dos años. Este módulo toma «ÚLTIMO» para el cierre del archivo
   y usa ``DT_FIM_EXERC`` para saber de qué periodo es cada cifra.
2. ``ESCALA_MOEDA`` vale «MIL»: los valores están en R$ mil. ``bk_publicado`` los publica en R$ (×1000).
   La escala se LEE de la columna, no se asume: la CVM también usa «UNIDADE».
3. En el ITR, la DRE trae el trimestre y el acumulado del año en la misma cuenta: se distinguen por
   ``DT_INI_EXERC`` (1 de enero = acumulado; inicio del trimestre = trimestre). La DFP solo trae el año.
4. Una compañía puede reentregar (``VERSAO``): se usa la mayor por compañía y documento.
5. ``CD_CONTA`` es jerárquico y el plan de cuentas lo arma cada compañía dentro del esqueleto de la CVM:
   la misma cuenta puede tener códigos distintos entre bancos. De ahí el mapa por banco de
   ``definiciones/cvm__bancos_lineas.json``.
6. Nubank, Inter, XP, Stone y PagSeguro NO entregan ITR/DFP: reportan en EE.UU. (20-F/6-K). Quedan fuera
   de alcance en la v1, con ``bk_publicado`` vacío para ellos.

Uso (desde la raíz del repo, con el .venv):

    python -X utf8 pipeline/cvm.py descargar              # ZIP ITR/DFP + registro, solo si cambiaron
    python -X utf8 pipeline/cvm.py extraer                # derivado filtrado a los bancos del mapa
    python -X utf8 pipeline/cvm.py gold                   # bk_publicado + huecos
    python -X utf8 pipeline/cvm.py contrastar             # contra IF.Data: activo, PL, depósitos, crédito y lucro
    python -X utf8 pipeline/cvm.py todo                   # extraer + gold + contrastar, sin tocar la red
    python -X utf8 pipeline/cvm.py todo --descargar       # idem, bajando antes lo que cambió (actualizar.py)
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import pandas as pd

import almacen as A
import bancos as B
import periodos as PER
import red

FUENTE = "cvm"
DS_ITR, DS_DFP, DS_CADASTRO = "itr", "dfp", "cadastro"
DS_DERIVADO = "bancos"          # datos/derivado/cvm/bancos/
DATASET_GOLD = "bancos_gold_cvm"

BASE = "https://dados.cvm.gov.br/dados/CIA_ABERTA"
URL_ZIP = {
    "itr": BASE + "/DOC/ITR/DADOS/itr_cia_aberta_{anio}.zip",
    "dfp": BASE + "/DOC/DFP/DADOS/dfp_cia_aberta_{anio}.zip",
}
URL_CADASTRO = BASE + "/CAD/DADOS/cad_cia_aberta.csv"
UA = {"User-Agent": "Mozilla/5.0 bz-banks-cvm/1.0"}
INTENTOS, PAUSA_S = 3, 20
CHUNK = 500_000

# Años que baja el paso «descargar» (ITR: trimestres; DFP: cierres de ejercicio, que dan el T4).
ANIOS_ITR = (2024, 2025, 2026)      # 2024 para que el ROE de 1T24 en adelante tenga PL de t−1
ANIOS_DFP = (2023, 2024, 2025, 2026)

# Qué estados del ZIP se leen. Los nombres internos son <doc>_cia_aberta_<estado>_con_<año>.csv
# («con» = consolidado; «ind» = solo la controladora, que no se usa: el panel es de conglomerados).
ESTADOS = ("BPA", "BPP", "DRE")

# Columnas de los archivos de estados financieros (la DFP no trae DT_INI_EXERC; el ITR sí).
COLUMNAS_ESTADOS = ["CNPJ_CIA", "DT_REFER", "VERSAO", "DENOM_CIA", "CD_CVM", "GRUPO_DFP", "MOEDA",
                    "ESCALA_MOEDA", "ORDEM_EXERC", "DT_FIM_EXERC", "DT_INI_EXERC", "CD_CONTA", "DS_CONTA",
                    "VL_CONTA", "ST_CONTA_FIXA"]
COLUMNAS_CADASTRO = ["CNPJ_CIA", "DENOM_SOCIAL", "CD_CVM", "SETOR_ATIV", "CATEG_REG", "SIT", "DT_REG",
                     "DT_INI_SIT", "SIT_EMISSOR", "TP_MERC"]


# ---------------------------------------------------------------- rutas


def ruta_zip(documento: str, anio: int) -> Path:
    """datos/crudo/cvm/<itr|dfp>/<año>/<doc>_cia_aberta_<año>.zip"""
    return A.ruta_cruda(FUENTE, documento, str(anio)) / f"{documento}_cia_aberta_{anio}.zip"


def ruta_cadastro() -> Path:
    return A.ruta_cruda(FUENTE, DS_CADASTRO) / "cad_cia_aberta.csv"


def url_zip(documento: str, anio: int) -> str:
    return URL_ZIP[documento].format(anio=anio)


# ---------------------------------------------------------------- descarga


def _tamano_servidor(url: str) -> tuple[int, str]:
    """(Content-Length, Last-Modified) del servidor, o (−1, '') si no los da."""
    import certificados  # noqa: F401  CA del proxy corporativo; antes de requests
    import requests

    r = requests.head(url, headers=UA, timeout=60)
    r.raise_for_status()
    return int(r.headers.get("Content-Length") or -1), r.headers.get("Last-Modified") or ""


def descargar_zip(documento: str, anio: int, *, forzar: bool = False) -> tuple[Path, str]:
    """Baja el ZIP del documento y año al crudo con su procedencia. Devuelve (ruta, qué pasó).

    Se vuelve a bajar si el tamaño que anuncia el servidor no coincide con el archivo local: la CVM
    regenera el ZIP del año en curso casi todas las semanas. ``forzar`` lo baja igual.
    """
    red.exigir_red(f"el ZIP {documento.upper()} {anio} de la CVM")
    import certificados  # noqa: F401  CA del proxy corporativo; antes de requests
    import requests

    url = url_zip(documento, anio)
    destino = ruta_zip(documento, anio)
    remoto, modificado = _tamano_servidor(url)

    if destino.exists() and not forzar:
        local = destino.stat().st_size
        if remoto in (local, -1):
            return destino, f"sin cambios ({local / 1e6:.1f} MB)"

    def validar(parcial: Path) -> None:
        with zipfile.ZipFile(parcial) as z:          # ZIP truncado o incompleto -> excepción
            if z.testzip() is not None:
                raise ValueError("el ZIP trae un archivo corrupto")

    print(f"[~] bajando {url} ({remoto / 1e6:.1f} MB)...", file=sys.stderr)
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        red.bajar_a_disco(lambda u, **kw: requests.get(u, headers=UA, **kw), url, destino, intentos=INTENTOS,
                          espera=lambda n, e: PAUSA_S * n, validar=validar)
    except Exception as e:
        raise RuntimeError(f"{destino.name}: falló {INTENTOS} veces ({e})") from e

    A.registrar_crudo(FUENTE, documento, destino, url, version=str(anio))
    _anotar_crudo(documento, str(anio), destino.name,
                  {"last_modified_servidor": modificado, "bytes_servidor": remoto})
    return destino, f"bajado ({destino.stat().st_size / 1e6:.1f} MB)"


def _anotar_crudo(dataset: str, version: str, nombre: str, extra: dict) -> None:
    """Agrega campos de proveniencia al manifiesto de un crudo ya registrado (Last-Modified del servidor)."""
    d = A.ruta_cruda(FUENTE, dataset, version)
    man = A.leer_manifiesto(d) or {"fuente": FUENTE, "dataset": dataset, "archivos": {}}
    man["archivos"].setdefault(nombre, {}).update(extra)
    A.escribir_manifiesto(d, man)


def descargar_cadastro(*, forzar: bool = False) -> tuple[Path, str]:
    """Baja el registro de compañías abiertas (CNPJ, razón social, sector, situación)."""
    red.exigir_red("el registro de compañías abiertas de la CVM")
    import certificados  # noqa: F401  CA del proxy corporativo; antes de requests
    import requests

    destino = ruta_cadastro()
    remoto, modificado = _tamano_servidor(URL_CADASTRO)
    if destino.exists() and not forzar and remoto in (destino.stat().st_size, -1):
        return destino, f"sin cambios ({destino.stat().st_size / 1e6:.2f} MB)"

    print(f"[~] bajando {URL_CADASTRO}...", file=sys.stderr)

    def una_vez() -> bytes:
        r = requests.get(URL_CADASTRO, headers=UA, timeout=(30, 300))
        r.raise_for_status()
        return r.content

    datos = red.reintentar(una_vez, INTENTOS, lambda n, e: PAUSA_S * n)
    A.guardar_crudo(FUENTE, DS_CADASTRO, destino.name, datos, URL_CADASTRO)
    _anotar_crudo(DS_CADASTRO, "actual", destino.name,
                  {"last_modified_servidor": modificado, "bytes_servidor": remoto})
    return destino, f"bajado ({len(datos) / 1e6:.2f} MB)"


def descargar(*, forzar: bool = False,
              anios_itr: tuple[int, ...] = ANIOS_ITR,
              anios_dfp: tuple[int, ...] = ANIOS_DFP) -> int:
    """El paso «descargar»: registro + ZIP ITR y DFP. Un 404 en un año no corta la corrida (el ZIP del año
    en curso puede no existir todavía); cualquier otro error sí."""
    fallos = 0
    for doc, anios in ((DS_CADASTRO, (None,)), (DS_ITR, anios_itr), (DS_DFP, anios_dfp)):
        for anio in anios:
            etiqueta = f"{doc.upper()}" + ("" if anio is None else f" {anio}")
            try:
                if doc == DS_CADASTRO:
                    ruta, que = descargar_cadastro(forzar=forzar)
                else:
                    ruta, que = descargar_zip(doc, anio, forzar=forzar)
                print(f"[+] {etiqueta}: {que}")
            except Exception as e:
                if "404" in str(e):
                    print(f"[!] {etiqueta}: el servidor no lo tiene ({e})")
                    continue
                fallos += 1
                print(f"[!] {etiqueta}: {e}", file=sys.stderr)
    return 1 if fallos else 0


# ---------------------------------------------------------------- quiénes son bancos


def raiz_cnpj(cnpj: object) -> str:
    """Los 8 primeros dígitos del CNPJ (la raíz), que es como el BCB identifica la institución."""
    digitos = "".join(ch for ch in str(cnpj) if ch.isdigit())
    return digitos[:8]


DEF_BANCOS = "cvm__bancos"
DEF_LINEAS = "cvm__bancos_lineas"


def cnpj_lider_panel() -> pd.DataFrame:
    """CNPJ líder de cada banco del panel, leído del cadastro crudo del IF.Data.

    El BCB publica ``CnpjInstituicaoLider`` por conglomerado prudencial: es el CNPJ de la institución que
    lidera el conglomerado y, para los bancos cotizados, coincide con el CNPJ con que la compañía se
    registra en la CVM (verificado el 9-nov-2026 contra ``cad_cia_aberta.csv``: las 16 compañías del panel
    que entregan ITR/DFP casan por raíz de CNPJ). Sirve para armar y auditar ``definiciones/cvm__bancos.json``,
    no para filtrar en caliente: el filtro de ``bk_publicado`` es el mapa, que está en git y se revisa a mano.
    """
    universo = {b["cod_inst"]: b["nombre_corto"] for b in B.universo()}
    filas: dict[str, dict] = {}
    for ruta in sorted(A.ruta_cruda("bcb_ifdata", "cadastro").glob("cadastro_*.parquet")):
        periodo = ruta.stem.replace("cadastro_", "")
        d = pd.read_parquet(ruta, columns=["CodInst", "CodConglomeradoPrudencial", "CnpjInstituicaoLider"])
        for cod, congl, cnpj in zip(d["CodInst"], d["CodConglomeradoPrudencial"], d["CnpjInstituicaoLider"]):
            clave = cod if cod in universo else (congl if congl in universo else None)
            c = str(cnpj).strip()
            if clave is None or not c.isdigit():
                continue
            actual = filas.get(clave)
            if actual is None or actual["periodo"] <= periodo:   # se queda con el trimestre más reciente
                filas[clave] = {"cod_inst": clave, "nombre_corto": universo[clave], "cnpj": c,
                                "raiz": raiz_cnpj(c), "periodo": periodo}
    out = pd.DataFrame(filas.values()).drop(columns=["periodo"])
    return out.sort_values("nombre_corto").reset_index(drop=True)


def registro_cvm() -> pd.DataFrame:
    """El registro de compañías abiertas de la CVM (crudo), con la raíz de CNPJ agregada."""
    ruta = ruta_cadastro()
    if not ruta.exists():
        raise FileNotFoundError(f"falta {ruta}: correr «python -X utf8 pipeline/cvm.py descargar»")
    cad = pd.read_csv(ruta, sep=";", dtype=str, keep_default_na=False, encoding="cp1252",
                      usecols=COLUMNAS_CADASTRO)
    cad["raiz"] = cad["CNPJ_CIA"].map(raiz_cnpj)
    return cad


def mapa_bancos() -> pd.DataFrame:
    """``definiciones/cvm__bancos.json`` → tabla con una fila por banco del panel.

    Columnas: cod_inst, nombre_corto, cnpj_raiz, cnpj_ifdata, cd_cvm, denominacion_cvm, tipo_estado
    (con|ind|""), usar_individual_si_falta (bool), base, entrega (bool), registro_cvm, nota.
    Falla si el mapa no cubre exactamente el universo del panel, si repite un CNPJ entre dos bancos o si
    trae tipos inválidos: el filtro de ``bk_publicado`` es este mapa, así que un mapa roto es un gold roto.
    """
    d = A.leer_definicion(DEF_BANCOS)
    df = pd.DataFrame(d["bancos"])
    for c in ("cnpj_raiz", "cnpj_ifdata", "cd_cvm", "denominacion_cvm", "tipo_estado", "base",
              "registro_cvm", "nota"):
        if c not in df:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)
    if "entrega" not in df:
        raise ValueError(f"{DEF_BANCOS}.json: falta el campo «entrega»")
    df["entrega"] = df["entrega"].astype(bool)
    df["usar_individual_si_falta"] = (df["usar_individual_si_falta"].astype(bool)
                                     if "usar_individual_si_falta" in df else False)
    universo = {b["cod_inst"] for b in B.universo()}
    fuera = sorted(set(df["cod_inst"]) - universo)
    if fuera:
        raise ValueError(f"{DEF_BANCOS}.json trae códigos fuera del universo del panel: {fuera}")
    faltan = sorted(universo - set(df["cod_inst"]))
    if faltan:
        raise ValueError(f"{DEF_BANCOS}.json: faltan bancos del panel: {faltan}")
    rep = df.loc[df["cnpj_raiz"] != "", "cnpj_raiz"]
    if rep.duplicated().any():
        raise ValueError(f"{DEF_BANCOS}.json: CNPJ repetido para dos bancos: "
                         f"{sorted(rep[rep.duplicated()].unique())}")
    malos = df.loc[df["entrega"] & df["cnpj_raiz"].eq(""), "cod_inst"].tolist()
    if malos:
        raise ValueError(f"{DEF_BANCOS}.json: bancos con entrega=true y sin cnpj_raiz: {malos}")
    tipos = df.loc[df["entrega"], "tipo_estado"]
    if not tipos.isin(["con", "ind"]).all():
        raise ValueError(f"{DEF_BANCOS}.json: tipo_estado fuera de con|ind: "
                         f"{sorted(set(tipos) - {'con', 'ind'})}")
    return df


# ---------------------------------------------------------------- lectura del ZIP


def nombre_interno(z: zipfile.ZipFile, documento: str, estado: str, anio: int, tipo: str = "con") -> str | None:
    """El CSV del estado dentro del ZIP: ``<doc>_cia_aberta_<estado>_<tipo>_<año>.csv``, o None si no está.

    ``tipo`` es «con» (consolidado) o «ind» (solo la controladora). Tres bancos del panel (ABC Brasil desde
    2024, Banco da Amazônia y Banco do Nordeste) no entregan estados consolidados: para ellos ``con`` devuelve
    None y el que llama decide si cae a «ind».
    """
    buscado = f"{documento}_cia_aberta_{estado}_{tipo}_{anio}.csv"
    nombres = {n.split("/")[-1] for n in z.namelist()}
    return buscado if buscado in nombres else None


def codificacion(z: zipfile.ZipFile, nombre: str) -> str:
    """Los CSV de la CVM son latin1 (cp1252 los lee igual); se comprueba UTF-8 estricto por si acaso."""
    with z.open(nombre) as f:
        muestra = f.read(65536)
    if muestra.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    try:
        muestra[:-4].decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "cp1252"


def leer_estado(z: zipfile.ZipFile, nombre: str, columnas: list[str], **opciones):
    """Itera por partes un CSV del ZIP, todo como texto (los números se convierten al usarlos)."""
    cod = codificacion(z, nombre)
    with z.open(nombre) as f:
        yield from pd.read_csv(f, sep=";", dtype=str, keep_default_na=False, encoding=cod,
                               chunksize=CHUNK, **opciones)


def columnas_estado(z: zipfile.ZipFile, nombre: str) -> list[str]:
    """El encabezado del CSV, para pedir solo las columnas que existen (la DFP no trae DT_INI_EXERC)."""
    with z.open(nombre) as f:
        return pd.read_csv(f, sep=";", nrows=0, encoding=codificacion(z, nombre)).columns.tolist()


# ---------------------------------------------------------------- extracción filtrada a bancos

# El derivado guarda las columnas de la fuente con nombre del repo, más la llave del panel. No se toca
# ningún valor: el filtrado es por compañía (CNPJ del mapa), nada más. ORDEM_EXERC, VERSAO y la escala se
# resuelven al armar bk_publicado, que es donde están las pruebas.
COLUMNAS_DERIVADO = ["cod_inst", "nombre_corto", "documento", "anio_zip", "estado", "tipo_estado", "cnpj",
                     "cd_cvm", "denominacion", "dt_refer", "versao", "ordem_exerc", "dt_ini_exerc",
                     "dt_fim_exerc", "grupo", "cd_conta", "ds_conta", "vl_conta", "escala", "moeda",
                     "st_conta_fixa"]
RENOMBRE = {"CNPJ_CIA": "cnpj", "CD_CVM": "cd_cvm", "DENOM_CIA": "denominacion", "DT_REFER": "dt_refer",
            "VERSAO": "versao", "ORDEM_EXERC": "ordem_exerc", "DT_INI_EXERC": "dt_ini_exerc",
            "DT_FIM_EXERC": "dt_fim_exerc", "GRUPO_DFP": "grupo", "CD_CONTA": "cd_conta",
            "DS_CONTA": "ds_conta", "VL_CONTA": "vl_conta", "ESCALA_MOEDA": "escala", "MOEDA": "moeda",
            "ST_CONTA_FIXA": "st_conta_fixa"}


def ruta_derivada(nombre: str) -> Path:
    return A.ruta_derivada(FUENTE, DS_DERIVADO) / nombre


def _leer_estado_filtrado(documento: str, anio: int, estado: str, tipo: str, por_raiz: dict[str, str],
                          nombres: dict[str, str]) -> pd.DataFrame:
    """Las filas consolidadas (o individuales) de un estado y año, solo de los bancos del mapa."""
    ruta_zip_ = ruta_zip(documento, anio)
    if not ruta_zip_.exists():
        raise FileNotFoundError(f"falta {ruta_zip_.name}: correr «python -X utf8 pipeline/cvm.py descargar»")
    with zipfile.ZipFile(ruta_zip_) as z:
        nombre = nombre_interno(z, documento, estado, anio, tipo)
        if nombre is None:
            return pd.DataFrame()
        disponibles = [c for c in COLUMNAS_ESTADOS if c in columnas_estado(z, nombre)]
        partes = []
        for parte in leer_estado(z, nombre, disponibles):
            parte = parte[parte["CNPJ_CIA"].map(raiz_cnpj).isin(por_raiz)].copy()
            if parte.empty:
                continue
            parte["raiz"] = parte["CNPJ_CIA"].map(raiz_cnpj)
            partes.append(parte)
    if not partes:
        return pd.DataFrame()
    df = pd.concat(partes, ignore_index=True)
    df = df.rename(columns=RENOMBRE)
    df["cod_inst"] = df["raiz"].map(por_raiz)
    df["nombre_corto"] = df["cod_inst"].map(nombres)
    df["documento"] = documento.upper()
    df["anio_zip"] = str(anio)
    df["estado"] = estado
    df["tipo_estado"] = tipo
    for c in ("dt_ini_exerc", "st_conta_fixa"):
        if c not in df:
            df[c] = ""          # la DFP de algunos años no trae DT_INI_EXERC; no es un dato faltante nuestro
    return df[COLUMNAS_DERIVADO]


def extraer_documento(documento: str, anio: int, mapa: pd.DataFrame | None = None) -> Path:
    """Filtra los estados (BPA, BPP, DRE) de un ZIP a los bancos del mapa y los guarda en el derivado.

    Cada banco se lee en su ``tipo_estado``, que es la base de su serie. Los que llevan
    ``usar_individual_si_falta`` se leen también en individual, y esas filas solo quedan donde no existe el
    consolidado de la misma referencia: Daycoval tiene así su 3T26 (que la CVM solo publicó individual)
    sin mezclar bases en el resto de la serie.
    """
    mapa = mapa_bancos() if mapa is None else mapa
    entrega = mapa[mapa["entrega"] & mapa["cnpj_raiz"].ne("")]
    nombres = dict(zip(entrega["cod_inst"], entrega["nombre_corto"]))
    por_tipo: dict[str, dict[str, str]] = {"con": {}, "ind": {}}
    respaldo: dict[str, str] = {}
    for _, f in entrega.iterrows():
        tipo = f["tipo_estado"] or "con"
        por_tipo[tipo][f["cnpj_raiz"]] = f["cod_inst"]
        if f["usar_individual_si_falta"] and tipo == "con":
            respaldo[f["cnpj_raiz"]] = f["cod_inst"]

    partes = []
    con_refs: set[tuple[str, str, str]] = set()      # (documento, dt_refer, cod_inst) que ya tienen consolidado
    for tipo in ("con", "ind"):
        for estado in ESTADOS:
            if not por_tipo[tipo]:
                continue
            df = _leer_estado_filtrado(documento, anio, estado, tipo, por_tipo[tipo], nombres)
            if df.empty:
                continue
            partes.append(df)
            if tipo == "con":
                con_refs |= set(zip(df["documento"], df["dt_refer"], df["cod_inst"]))
    for estado in ESTADOS:
        if not respaldo:
            continue
        ind = _leer_estado_filtrado(documento, anio, estado, "ind", respaldo, nombres)
        if ind.empty:
            continue
        ind = ind[[c not in con_refs for c in zip(ind["documento"], ind["dt_refer"], ind["cod_inst"])]]
        if len(ind):
            print(f"    [i] {documento.upper()} {anio} {estado}: sin consolidado, se usa el individual "
                  f"({sorted(set(ind['cod_inst'] + ' ' + ind['dt_refer']))})")
            partes.append(ind)
    out = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=COLUMNAS_DERIVADO)

    nombre = f"estados_{documento}_{anio}.parquet"
    desde = [str(ruta_zip(documento, anio).relative_to(A.RAIZ)), f"definiciones/{DEF_BANCOS}.json"]
    A.guardar_derivado(FUENTE, DS_DERIVADO, nombre, A.parquet_bytes(out), desde=desde,
                       como=A.comando_actual(),
                       nota=f"{documento.upper()} {anio} filtrado a los bancos de definiciones/{DEF_BANCOS}.json "
                            f"(CNPJ del mapa); columnas con nombre del repo, valores tal cual los sirvió la CVM")
    print(f"[+] {nombre}: {len(out):,} filas, {out['cod_inst'].nunique() if len(out) else 0} bancos")
    return ruta_derivada(nombre)


def entregas_documento(documento: str, anio: int, mapa: pd.DataFrame | None = None) -> pd.DataFrame:
    """El índice de entregas del ZIP (fecha de recepción y link al documento), filtrado al mapa."""
    mapa = mapa_bancos() if mapa is None else mapa
    entrega = mapa[mapa["entrega"]]
    por_raiz = dict(zip(entrega["cnpj_raiz"], entrega["cod_inst"]))
    ruta_zip_ = ruta_zip(documento, anio)
    with zipfile.ZipFile(ruta_zip_) as z:
        nombre = f"{documento}_cia_aberta_{anio}.csv"
        if nombre not in {n.split("/")[-1] for n in z.namelist()}:
            return pd.DataFrame()
        d = pd.read_csv(z.open(nombre), sep=";", dtype=str, keep_default_na=False, encoding="cp1252")
    d["cod_inst"] = d["CNPJ_CIA"].map(raiz_cnpj).map(por_raiz)
    d = d[d["cod_inst"].notna()].copy()
    d["documento"] = documento.upper()
    d["anio_zip"] = str(anio)
    return d.rename(columns=str.lower)[["cod_inst", "documento", "anio_zip", "cnpj_cia", "cd_cvm", "denom_cia",
                                       "dt_refer", "versao", "categ_doc", "id_doc", "dt_receb", "link_doc"]]


def extraer(*, anios_itr: tuple[int, ...] = ANIOS_ITR, anios_dfp: tuple[int, ...] = ANIOS_DFP) -> int:
    """El paso «extraer»: todos los ZIP bajados → un parquet derivado por documento y año, más las entregas."""
    mapa = mapa_bancos()
    entregas = []
    for doc, anios in ((DS_ITR, anios_itr), (DS_DFP, anios_dfp)):
        for anio in anios:
            if not ruta_zip(doc, anio).exists():
                print(f"[!] {doc.upper()} {anio}: no está bajado; se salta")
                continue
            extraer_documento(doc, anio, mapa)
            e = entregas_documento(doc, anio, mapa)
            if len(e):
                entregas.append(e)
    ent = pd.concat(entregas, ignore_index=True) if entregas else pd.DataFrame()
    A.guardar_derivado(FUENTE, DS_DERIVADO, "entregas.parquet", A.parquet_bytes(ent),
                       desde=[f"datos/crudo/{FUENTE}/{DS_ITR}", f"datos/crudo/{FUENTE}/{DS_DFP}"],
                       como=A.comando_actual(),
                       nota="índice de entregas de la CVM (DT_RECEB y LINK_DOC) filtrado a los bancos del mapa")
    print(f"[+] entregas.parquet: {len(ent):,} entregas")
    return 0


# ---------------------------------------------------------------- de la cuenta a la línea
#
# El plan de cuentas de la CVM es un esqueleto: hasta el nivel 3 las cuentas son fijas (ST_CONTA_FIXA='S',
# comparables entre compañías), pero el detalle lo arma cada banco ('N'). Encima, el esqueleto mismo cambió
# (los estados de 2025 en adelante usan la clasificación de instrumentos financieros del CPC 48) y cada banco
# migró en un momento distinto —Pine pasó del plan nuevo al viejo entre el DFP 2024 y el ITR 1T25, y Santander
# cambia el nivel de detalle entre entregas. Por eso una línea no se busca por un código fijo sino por una
# REGLA: código candidato + texto que debe contener la descripción. Si el código se corre pero la cuenta sigue
# siendo la misma, la regla la encuentra; si la cuenta cambia de significado, la descripción no coincide y la
# línea queda vacía en vez de publicar un número equivocado.

MESES_TRIMESTRE = ("03", "06", "09", "12")
INICIO_TRIMESTRE = {"03": "01-01", "06": "04-01", "09": "07-01", "12": "10-01"}


def normalizar(texto: object) -> str:
    """Descripción de cuenta comparable: minúsculas, sin acentos ni puntuación, espacios colapsados.

    «(-) Provisão para Perda Esperada» → «provisao para perda esperada». Así la misma regla sirve para
    «Atribuído a Sócios da Empresa Controladora» y «Atribuído aos Sócios da Empresa Controladora».
    """
    import re
    import unicodedata
    s = unicodedata.normalize("NFD", str(texto))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", s.lower()).split())


def periodo_de_referencia(dt_refer: str) -> str | None:
    """«2026-06-30» → «202606» (el formato de periodos.py). None si no es fin de trimestre."""
    from datetime import date
    try:
        anio, mes, dia = (int(x) for x in str(dt_refer)[:10].split("-"))
        d = date(anio, mes, dia)
    except (ValueError, TypeError):
        return None
    if f"{mes:02d}" not in MESES_TRIMESTRE:
        return None
    ultimo_dia = (pd.Timestamp(d) + pd.offsets.MonthEnd(0)).day
    return f"{anio}{mes:02d}" if dia == ultimo_dia else None


def inicios_esperados(dt_refer: str) -> tuple[str, str]:
    """(inicio del acumulado del año, inicio del trimestre) para un DT_REFER de fin de trimestre."""
    mes = str(dt_refer)[5:7]
    return f"{dt_refer[:4]}-01-01", f"{dt_refer[:4]}-{INICIO_TRIMESTRE[mes]}"


def definicion_lineas() -> dict:
    """definiciones/cvm__bancos_lineas.json."""
    return A.leer_definicion(DEF_LINEAS)


def especificaciones(cod_inst: str, defn: dict | None = None) -> dict[str, dict]:
    """Las líneas de un banco: la plantilla que le toca, con sus excepciones encima.

    Un override reemplaza la línea entera (no se mezcla con la plantilla): así lo que está en el JSON es
    exactamente lo que se va a buscar.
    """
    defn = definicion_lineas() if defn is None else defn
    bancos = defn["bancos"]
    if cod_inst not in bancos:
        raise ValueError(f"{DEF_LINEAS}.json: no hay líneas para {cod_inst}")
    entrada = bancos[cod_inst]
    plantilla = entrada.get("plantilla", "")
    base = dict(defn.get("plantillas", {}).get(plantilla, {})) if plantilla else {}
    if plantilla and not base:
        raise ValueError(f"{DEF_LINEAS}.json: {cod_inst} usa la plantilla inexistente «{plantilla}»")
    base.update(entrada.get("lineas", {}))
    meta = defn.get("lineas", {})
    for linea, spec in base.items():
        if linea not in meta:
            raise ValueError(f"{DEF_LINEAS}.json: {cod_inst} mapea la línea desconocida «{linea}»")
        spec.setdefault("estado", meta[linea].get("estado", ""))
        # Un 0 en una cuenta de saldo de un banco no es un dato: es «no lo divulgo» en el archivo estructurado
        # (Santander entrega la cartera en 0 en el DFP 2023 y 2025). Se decide por línea, no por banco.
        spec.setdefault("cero_es_vacio", bool(meta[linea].get("cero_es_vacio", False)))
    return base


def _buscar(cuentas: pd.DataFrame, regla: dict, estado: str, medida: str, dt_refer: str):
    """Una regla (código + texto + ventana) contra las cuentas de una entrega.

    Devuelve (valor_en_reales, fila, None) si casa exactamente una cuenta; (None, None, motivo) si no.
    Que case más de una cuenta es un error, no un empate: significa que la regla está mal escrita.
    """
    if regla.get("desde") and dt_refer < regla["desde"]:
        return None, None, "fuera de ventana"
    if regla.get("hasta") and dt_refer > regla["hasta"]:
        return None, None, "fuera de ventana"
    m = cuentas[(cuentas["estado"] == regla.get("estado", estado)) & (cuentas["medida"] == medida)]
    codigos = regla.get("cd") or []
    if codigos:
        m = m[m["cd_conta"].isin(codigos)]
    for patron in regla.get("ds") or []:
        m = m[m["ds_norm"].str.contains(normalizar(patron), regex=False, na=False)]
    for patron in regla.get("ds_no") or []:
        m = m[~m["ds_norm"].str.contains(normalizar(patron), regex=False, na=False)]
    if len(m) == 0:
        return None, None, "sin coincidencia"
    if len(m) > 1:
        # Pasa: BB llenó en el ITR 3T25 las cuentas del esqueleto nuevo (3.09.01/3.09.02) con 0 además de las
        # suyas (3.11.01/3.11.02). Si de las que casan solo una trae número, es la que vale; si todas vienen en
        # 0, el banco no divulgó; si hay dos con número, la regla está mal y no se adivina.
        no_nulas = m[m["valor"] != 0]
        if len(no_nulas) == 1:
            m = no_nulas
        elif no_nulas.empty:
            return None, None, f"las cuentas que casan vienen todas en 0: {sorted(m['cd_conta'])}"
        else:
            return None, None, f"ambigua: {sorted(m['cd_conta'])}"
    fila = m.iloc[0]
    return float(fila["valor"]), fila, None


def resolver(cuentas: pd.DataFrame, spec: dict, medida: str, dt_refer: str) -> dict:
    """Resuelve una línea en una entrega probando sus alternativas en orden; la primera que casa gana.

    Devuelve un dict con valor (None si ninguna casa), cd_conta, ds_conta, alternativa y problema.
    """
    estado = spec.get("estado", "")
    motivos = []
    for i, alt in enumerate(spec.get("alternativas", []), 1):
        total, cuentas_usadas, fallo = 0.0, [], None
        for signo, claves in ((1.0, alt.get("suma", [])), (-1.0, alt.get("resta", []))):
            for regla in claves:
                valor, fila, problema = _buscar(cuentas, regla, estado, medida, dt_refer)
                if problema:
                    fallo = problema
                    break
                total += signo * valor
                cuentas_usadas.append(fila)
            if fallo:
                break
        if fallo:
            motivos.append(f"alt{i}: {fallo}")
            continue
        if total == 0 and alt.get("cero_es_vacio", spec.get("cero_es_vacio")):
            motivos.append(f"alt{i}: la cuenta viene en 0, el banco no la divulga")
            continue            # sigue con la alternativa siguiente (p. ej. total menos no controladores)
        if spec.get("signo") == "positivo":
            total = abs(total)
        return {"valor": total,
                "cd_conta": " + ".join(c["cd_conta"] for c in cuentas_usadas),
                "ds_conta": " | ".join(c["ds_conta"] for c in cuentas_usadas),
                "alternativa": i, "problema": None}
    if motivos and all(m.endswith("fuera de ventana") for m in motivos):
        # La regla existe pero está acotada a otras fechas (un banco que cambió de criterio): no es un hueco,
        # es la definición diciendo que en este periodo no corresponde.
        return {"valor": None, "cd_conta": "", "ds_conta": "", "alternativa": 0, "problema": "FUERA_DE_VENTANA"}
    return {"valor": None, "cd_conta": "", "ds_conta": "", "alternativa": 0,
            "problema": "; ".join(motivos) or "sin alternativas"}


# ---------------------------------------------------------------- bk_publicado

# Columnas del gold. Las cuatro primeras son las que pide tareas/07_fuente_cvm.md; el resto existe para que
# una cifra se pueda auditar sin volver al ZIP: de qué documento viene, si es saldo o flujo, si el estado es
# consolidado o individual, qué cuenta la produjo y qué trampa tiene.
COLUMNAS_PUBLICADO = ["cod_inst", "periodo", "linea", "valor", "base", "fecha_entrega", "cd_cvm", "versao",
                      "documento", "medida", "consolidacion", "cd_conta", "ds_conta", "nota"]
CLAVE_PUBLICADO = ["cod_inst", "periodo", "linea", "medida"]
ESCALAS = {"MIL": 1_000.0, "UNIDADE": 1.0}
LINEA_ROE = "roe_anualizado"
LINEA_LUCRO_TRIM = "lucro_liquido_controlador"
LINEA_PL_CONTROLADOR = "patrimonio_liquido_controlador"


def numero_cvm(texto: str) -> float:
    """VL_CONTA a float. La CVM sirve «3202125000.0000000000» (punto decimal), pero si algún archivo viniera
    con formato brasileño (coma decimal) también se lee: manda el último separador que aparezca."""
    s = str(texto).strip()
    if not s:
        raise ValueError("VL_CONTA vacío")
    coma, punto = s.rfind(","), s.rfind(".")
    if coma > punto:
        s = s.replace(".", "").replace(",", ".")
    elif punto >= 0 and coma >= 0:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError as e:
        raise ValueError(f"VL_CONTA ilegible: {texto!r}") from e


def estados_preparados(mapa: pd.DataFrame | None = None) -> tuple[pd.DataFrame, list[str]]:
    """El derivado filtrado, listo para resolver líneas: una fila por cuenta con periodo, medida y valor en R$.

    Aquí se aplican las cuatro trampas de la fuente (ver el docstring del módulo): ORDEM_EXERC «ÚLTIMO»,
    la VERSAO mayor, la escala (MIL → ×1000) y trimestre contra acumulado por DT_INI_EXERC. Lo que no pasa
    esos filtros no se descarta en silencio: va a la lista de avisos que devuelve.
    """
    mapa = mapa_bancos() if mapa is None else mapa
    validos = set(mapa.loc[mapa["entrega"], "cod_inst"])
    rutas = sorted(A.ruta_derivada(FUENTE, DS_DERIVADO).glob("estados_*.parquet"))
    if not rutas:
        raise FileNotFoundError("no hay derivados de la CVM: correr «python -X utf8 pipeline/cvm.py extraer»")
    d = pd.concat([pd.read_parquet(p) for p in rutas], ignore_index=True)
    avisos: list[str] = []

    fuera = sorted(set(d["cod_inst"]) - validos)
    if fuera:
        raise ValueError(f"el derivado trae CNPJ fuera del mapa: {fuera}")     # nunca debe entrar a bk_publicado
    malas_monedas = sorted(set(d["moeda"]) - {"REAL"})
    if malas_monedas:
        raise ValueError(f"hay estados en otra moneda que REAL: {malas_monedas}")
    malas_escalas = sorted(set(d["escala"]) - set(ESCALAS))
    if malas_escalas:
        raise ValueError(f"ESCALA_MOEDA fuera de {sorted(ESCALAS)}: {malas_escalas}")

    d = d[d["ordem_exerc"] == "ÚLTIMO"].copy()          # trampa 1: el PENÚLTIMO es el ejercicio comparativo
    d["valor"] = [numero_cvm(v) * ESCALAS[e] for v, e in zip(d["vl_conta"], d["escala"])]   # trampa 2

    raro = d[d["dt_fim_exerc"] != d["dt_refer"]]
    if len(raro):
        avisos.append(f"{len(raro)} filas ÚLTIMO con DT_FIM_EXERC distinto de DT_REFER: descartadas")
        d = d[d["dt_fim_exerc"] == d["dt_refer"]]

    d["versao_n"] = pd.to_numeric(d["versao"], errors="coerce").fillna(0).astype(int)
    claves = ["cod_inst", "documento", "dt_refer", "estado"]
    n_versiones = d.groupby(claves)["versao_n"].nunique()
    if (n_versiones > 1).any():                          # trampa 4: reentregas
        avisos.append(f"{int((n_versiones > 1).sum())} entregas con más de una VERSAO en los estados: "
                      f"se usa la mayor")
    d = d[d["versao_n"] == d.groupby(claves)["versao_n"].transform("max")]

    d["periodo"] = d["dt_refer"].map(periodo_de_referencia)
    sin_periodo = d[d["periodo"].isna()]
    if len(sin_periodo):
        avisos.append(f"{len(sin_periodo)} filas con DT_REFER que no es fin de trimestre: descartadas")
        d = d[d["periodo"].notna()]

    # trampa 3: la DRE trae el trimestre y el acumulado del año en la misma cuenta
    d["medida"] = "saldo"
    dre = d["estado"] == "DRE"
    inicios = [inicios_esperados(r) for r in d["dt_refer"]]
    d.loc[dre, "medida"] = [
        "acumulado" if ini == a else ("trimestre" if ini == t else "")
        for ini, (a, t), es in zip(d["dt_ini_exerc"], inicios, dre) if es
    ]
    drea = d[dre]
    mala = drea[drea["medida"] == ""]
    if len(mala):
        detalle = (mala.groupby(["nombre_corto", "documento", "dt_refer", "dt_ini_exerc"]).size()
                   .reset_index(name="n"))
        for _, f in detalle.iterrows():
            avisos.append(f"{f['nombre_corto']} {f['documento']} {f['dt_refer']}: la DRE cubre "
                          f"{f['dt_ini_exerc']}→{f['dt_refer']} (no es el año ni el trimestre): "
                          f"{int(f['n'])} cuentas descartadas")
        d = d[~((d["estado"] == "DRE") & (d["medida"] == ""))]

    d["ds_norm"] = d["ds_conta"].map(normalizar)

    # En el 1T el acumulado del año Y el trimestre son el mismo número (los dos arrancan el 1 de enero), y la
    # CVM entrega una sola fila. Se duplica como «trimestre» para que el 1T no quede sin flujo trimestral (y sin
    # ROE anualizado) frente a los otros tres cortes.
    primer_trimestre = (d["estado"] == "DRE") & (d["medida"] == "acumulado") & (d["dt_refer"].str[5:7] == "03")
    if primer_trimestre.any():
        copia = d[primer_trimestre].copy()
        copia["medida"] = "trimestre"
        d = pd.concat([d, copia], ignore_index=True)

    columnas = ["cod_inst", "nombre_corto", "documento", "dt_refer", "periodo", "estado", "medida",
                "tipo_estado", "cd_cvm", "versao_n", "cd_conta", "ds_conta", "ds_norm", "valor", "escala"]
    return d[columnas].reset_index(drop=True), avisos


def entregas() -> pd.DataFrame:
    """Fecha de recepción de cada entrega (DT_RECEB) por banco, documento, referencia y versión."""
    p = A.ruta_derivada(FUENTE, DS_DERIVADO) / "entregas.parquet"
    if not p.exists():
        return pd.DataFrame(columns=["cod_inst", "documento", "dt_refer", "versao", "dt_receb"])
    d = pd.read_parquet(p)
    return d[["cod_inst", "documento", "dt_refer", "versao", "dt_receb"]]


def bk_publicado(mapa: pd.DataFrame | None = None, defn: dict | None = None, *,
                 avisos: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Arma ``bk_publicado`` y la tabla de huecos (líneas buscadas que no dieron número).

    Devuelve (publicado, huecos). Una línea sin valor NO se publica como NaN: va a huecos con el motivo, y el
    sitio la trata como «en preparación».
    """
    mapa = mapa_bancos() if mapa is None else mapa
    defn = definicion_lineas() if defn is None else defn
    cuentas, avisos_estados = estados_preparados(mapa)
    if avisos is not None:
        avisos.extend(avisos_estados)
    ent = entregas()
    base_por_cod = dict(zip(mapa["cod_inst"], mapa["base"]))
    meta = defn["lineas"]

    filas, huecos = [], []
    vacias: list[dict] = []
    for cod, grupo in cuentas.groupby("cod_inst", sort=False):
        specs = especificaciones(cod, defn)
        for (documento, dt_refer), entrega in grupo.groupby(["documento", "dt_refer"], sort=True):
            periodo = entrega["periodo"].iloc[0]
            versao = int(entrega["versao_n"].max())
            entrega = entrega[entrega["versao_n"] == versao]
            fila_ent = ent[(ent["cod_inst"] == cod) & (ent["documento"] == documento) &
                           (ent["dt_refer"] == dt_refer) &
                           (pd.to_numeric(ent["versao"], errors="coerce") == versao)]
            fecha_entrega = fila_ent["dt_receb"].iloc[0] if len(fila_ent) else ""
            comun = {"cod_inst": cod, "periodo": periodo, "documento": documento, "versao": versao,
                     "cd_cvm": entrega["cd_cvm"].iloc[0], "base": base_por_cod.get(cod, ""),
                     "consolidacion": entrega["tipo_estado"].iloc[0], "fecha_entrega": fecha_entrega}
            for linea, spec in specs.items():
                if spec.get("vacia"):
                    vacias.append({"cod_inst": cod, "linea": linea, "motivo": spec["vacia"]})
                    continue        # vacía a propósito: el motivo está en la definición, no es un hueco
                if meta[linea].get("medida") == "flujo":
                    medidas = ["trimestre", "acumulado"]
                else:
                    medidas = ["saldo"]
                estado = spec.get("estado", "")
                for medida in medidas:
                    if not ((entrega["estado"] == estado) & (entrega["medida"] == medida)).any():
                        continue        # la DFP no trae trimestre; no es un hueco, es el documento
                    r = resolver(entrega, spec, medida, dt_refer)
                    nota = spec.get("nota", "") or ""
                    if r["valor"] is None:
                        if r["problema"] != "FUERA_DE_VENTANA":
                            huecos.append({**comun, "linea": linea, "medida": medida,
                                           "motivo": r["problema"], "nota_linea": nota})
                        continue
                    filas.append({**comun, "linea": linea, "medida": medida, "valor": r["valor"],
                                  "cd_conta": r["cd_conta"], "ds_conta": r["ds_conta"],
                                  "nota": _unir_notas(nota, NOTA_PRIMER_TRIMESTRE
                                                      if (medida == "trimestre" and periodo[4:] == "03")
                                                      else "")})

    out = pd.DataFrame(filas)
    if out.empty:
        raise ValueError("bk_publicado salió vacío: revisar el mapa y las reglas")
    base = pd.concat([out, _cuarto_trimestre(out, meta)], ignore_index=True)
    out = pd.concat([base, _roe_anualizado(base, meta)], ignore_index=True)
    out = out[COLUMNAS_PUBLICADO]
    out["nota"] = out["nota"].fillna("")
    repetidas = out.duplicated(CLAVE_PUBLICADO).sum()
    if repetidas:
        dup = out[out.duplicated(CLAVE_PUBLICADO, keep=False)].sort_values(CLAVE_PUBLICADO)
        raise ValueError(f"bk_publicado: {repetidas} filas repiten la clave {CLAVE_PUBLICADO}:\n"
                         f"{dup[['cod_inst', 'periodo', 'linea', 'medida', 'documento', 'cd_conta']]}")
    orden = {k: i for i, k in enumerate(meta)}
    out = out.sort_values(["cod_inst", "periodo", "linea", "medida"],
                          key=lambda s: s.map(orden) if s.name == "linea" else s)
    h = pd.DataFrame(huecos)
    v = pd.DataFrame(vacias).drop_duplicates(["cod_inst", "linea"]) if vacias else pd.DataFrame()
    if len(v):
        print("[i] líneas vacías por diseño (el motivo está en "
              f"definiciones/{DEF_LINEAS}.json):")
        for _, f in v.iterrows():
            print(f"      {f['cod_inst']} · {f['linea']}: {f['motivo']}")
    return out.reset_index(drop=True), h.reset_index(drop=True)


def _unir_notas(*notas: object) -> str:
    return " ".join(str(n).strip() for n in notas if isinstance(n, str) and n.strip())


LINEAS_FLUJO = ("resultado_intermediacion", "lucro_liquido", "lucro_liquido_controlador")
NOTA_PRIMER_TRIMESTRE = ("1T: la CVM entrega una sola DRE porque el trimestre y el acumulado del "
                           "año arrancan el mismo 1 de enero; las dos medidas son la misma cifra.")


def _cuarto_trimestre(pub: pd.DataFrame, meta: dict) -> pd.DataFrame:
    """El 4T de cada banco: DFP anual − ITR acumulado a setiembre. Derivado, y la fila lo dice.

    La DFP solo trae el año completo; el cuarto trimestre no lo publica nadie en la CVM. Se resta el acumulado
    de nueve meses (ITR 3T) del anual (DFP), que es como se des-acumulan los resultados en el resto del repo
    (ver spec/08, «Resultados acumulados con reseteo en julio»). Si falta el ITR 3T de ese año, o si la DRE de
    la DFP no cubre el año entero (BRB entrega solo diciembre), no se deriva nada.
    """
    flujos = [l for l in LINEAS_FLUJO if l in set(pub["linea"])]
    acum = pub[(pub["medida"] == "acumulado") & (pub["linea"].isin(flujos))]
    anual = acum[acum["documento"] == "DFP"]
    nueve = acum[acum["periodo"].str[4:] == "09"]
    if anual.empty or nueve.empty:
        return pd.DataFrame(columns=COLUMNAS_PUBLICADO)
    indice = {(f["cod_inst"], f["periodo"], f["linea"]): f for _, f in nueve.iterrows()}
    filas = []
    for _, a in anual.iterrows():
        anterior = indice.get((a["cod_inst"], f"{a['periodo'][:4]}09", a["linea"]))
        if anterior is None:
            continue
        if anterior["consolidacion"] != a["consolidacion"]:
            continue            # no se restan bases distintas (consolidado contra individual)
        filas.append({**{c: a[c] for c in ("cod_inst", "periodo", "base", "fecha_entrega", "cd_cvm",
                                           "consolidacion")},
                      "linea": a["linea"], "medida": "trimestre", "valor": float(a["valor"]) - float(anterior["valor"]),
                      "documento": "DFP−ITR", "versao": a["versao"],
                      "cd_conta": f"{a['cd_conta']} − {anterior['cd_conta']} (3T{a['periodo'][2:4]})",
                      "ds_conta": "anual menos acumulado a setiembre",
                      "nota": _unir_notas(
                          a["nota"],
                          f"4T derivado: DFP {a['periodo'][:4]} (v{a['versao']}, {a['fecha_entrega']}) menos "
                          f"ITR 3T{a['periodo'][2:4]} acumulado (v{anterior['versao']}, "
                          f"{anterior['fecha_entrega']}). Si el banco reexpresó cifras entre las dos entregas, "
                          f"la resta lo arrastra.")})
    return pd.DataFrame(filas)


def _roe_anualizado(pub: pd.DataFrame, meta: dict) -> pd.DataFrame:
    """ROE anualizado = lucro atribuible del trimestre × 4 / PL promedio del trimestre del controlador.

    PL promedio = (PL_t + PL_t−1) / 2, la convención de los releases de los bancos (decisión de Pablo, 9-nov-2026),
    para que el número se pueda comparar con lo que publica cada banco. Es distinta del ROE TTM de IF.Data
    (``pl_medio_ttm`` = (PL_t + PL_t−4) / 2): no mezclar las dos en una serie. Sin PL de t−1 no hay promedio y la
    fila no se publica: no se aproxima con el PL del cierre.
    """
    lucro = pub[(pub["linea"] == LINEA_LUCRO_TRIM) & (pub["medida"] == "trimestre")]
    pl = pub[(pub["linea"] == LINEA_PL_CONTROLADOR) & (pub["medida"] == "saldo")]
    if lucro.empty or pl.empty:
        return pd.DataFrame(columns=COLUMNAS_PUBLICADO)
    pl_mapa = {(c, p): v for c, p, v in zip(pl["cod_inst"], pl["periodo"], pl["valor"])}
    filas = []
    for _, f in lucro.iterrows():
        anterior = PER.previo(f["periodo"], 1)
        pl_t, pl_t4 = pl_mapa.get((f["cod_inst"], f["periodo"])), pl_mapa.get((f["cod_inst"], anterior))
        if pl_t is None or pl_t4 is None:
            continue
        promedio = (pl_t + pl_t4) / 2
        if promedio == 0:
            continue
        filas.append({**{c: f[c] for c in ("cod_inst", "periodo", "documento", "versao", "cd_cvm", "base",
                                           "consolidacion", "fecha_entrega")},
                      "linea": LINEA_ROE, "medida": "trimestre", "valor": float(f["valor"]) * 4 / promedio,
                      "cd_conta": "", "ds_conta": "",
                      "nota": f"derivado: {meta[LINEA_ROE]['definicion']} PL promedio = ({pl_t:,.0f} + "
                              f"{pl_t4:,.0f}) / 2 de {f['periodo']} y {anterior}."})
    return pd.DataFrame(filas)


def gold(*, publicar: bool = True) -> int:
    """El paso «gold»: arma bk_publicado, guarda los huecos y publica la tabla."""
    mapa = mapa_bancos()
    defn = definicion_lineas()
    avisos: list[str] = []
    pub, huecos = bk_publicado(mapa, defn, avisos=avisos)

    for a in avisos:
        print(f"[!] {a}")
    if len(huecos):
        A.guardar_derivado(FUENTE, DS_DERIVADO, "huecos.csv",
                           huecos.to_csv(index=False).encode("utf-8-sig"),
                           desde=[f"datos/derivado/{FUENTE}/{DS_DERIVADO}", f"definiciones/{DEF_LINEAS}.json"],
                           como=A.comando_actual(),
                           nota="líneas buscadas que no dieron número, con el motivo: ninguna se inventa")
    if publicar:
        A.publicar_gold("bk_publicado", pub, fuente=FUENTE, dataset=DATASET_GOLD,
                        desde=[f"datos/derivado/{FUENTE}/{DS_DERIVADO}", f"definiciones/{DEF_BANCOS}.json",
                               f"definiciones/{DEF_LINEAS}.json"],
                        nota="Último trimestre publicado por los bancos cotizados (ITR/DFP de la CVM)")
    print(f"[+] bk_publicado: {len(pub):,} filas, {pub['cod_inst'].nunique()} bancos, "
          f"{pub['periodo'].nunique()} periodos ({pub['periodo'].min()}–{pub['periodo'].max()}), "
          f"{pub['linea'].nunique()} líneas; {len(huecos)} huecos")
    return 0


# ---------------------------------------------------------------- contraste contra IF.Data

# Dos contabilidades distintas del mismo trimestre: la CVM es el consolidado societario bajo CPC y el
# IF.Data es el conglomerado prudencial bajo COSIF. La diferencia es esperable (subsidiarias de seguros y
# previdência, método de participación, reglas de consolidación) y se INFORMA, nunca se corrige.
# Umbral de aviso: por encima de esto la diferencia necesita una explicación escrita.
UMBRAL_DIF_PCT = 0.15

# (línea de bk_publicado, métrica de bk_panel, si es la comparación principal). Conviene comparar más de una
# métrica del IF.Data contra la misma línea porque los perímetros no coinciden: la «Operações de Crédito» del
# plan de la CVM se parece al credito_total del COSIF (que suma arrendamento, outras concessões y contas a
# receber), no a su credito_bruto. Verificado sobre 2T26: Banco do Brasil da +1,1 % contra credito_total y
# −17,3 % contra credito_liquido; Santander +0,3 % y Pine +2,8 % contra credito_total.
PARES_CONTRASTE = [
    ("ativo_total", "ativo_total", True),
    ("patrimonio_liquido", "patrimonio_liquido", True),
    ("depositos", "depositos", True),
    ("credito_bruto", "credito_total", True),
    ("credito_bruto", "credito_bruto", False),
    ("credito_liquido", "credito_total", True),
    ("credito_liquido", "credito_liquido", False),
]
# Flujos: el trimestre de la CVM contra el trimestre del IF.Data. Se comparan las dos versiones del lucro
# (atribuible al controlador y total) porque el IF.Data no descuenta sistemáticamente los no controladores:
# en Banco do Brasil el atribuible difiere +39 % y el total solo +2 %.
PARES_FLUJO = [("lucro_liquido", "lucro_liquido_q", True),
               ("lucro_liquido_controlador", "lucro_liquido_q", False)]


def contrastar(*, periodo: str | None = None, guardar: bool = True) -> pd.DataFrame:
    """Compara bk_publicado (CVM) contra bk_panel (IF.Data) en los bancos y trimestres que están en los dos.

    No corrige nada: devuelve la diferencia en % ((IF.Data − CVM) / CVM) y marca las que pasan UMBRAL_DIF_PCT.
    """
    ruta_panel = A.GOLD / "bk_panel.parquet"
    if not ruta_panel.exists():
        raise FileNotFoundError("falta bk_panel.parquet: correr antes «actualizar.py --desde base»")
    pub = pd.read_parquet(A.GOLD / "bk_publicado.parquet")
    panel = pd.read_parquet(ruta_panel, columns=["cod_inst", "periodo", "metrica", "valor"])

    filas = []
    comparaciones = ([(a, b, "saldo", pr) for a, b, pr in PARES_CONTRASTE]
                     + [(a, b, "trimestre", pr) for a, b, pr in PARES_FLUJO])
    for linea_cvm, metrica, medida, principal in comparaciones:
        c = pub[(pub["linea"] == linea_cvm) & (pub["medida"] == medida)][["cod_inst", "periodo", "valor",
                                                                          "documento", "consolidacion"]]
        p = panel[panel["metrica"] == metrica][["cod_inst", "periodo", "valor"]]
        j = c.merge(p, on=["cod_inst", "periodo"], how="inner", suffixes=("_cvm", "_ifdata"))
        for _, f in j.iterrows():
            cvm, ifd = float(f["valor_cvm"]), float(f["valor_ifdata"])
            filas.append({
                "cod_inst": f["cod_inst"], "periodo": f["periodo"], "linea_cvm": linea_cvm,
                "metrica_ifdata": metrica, "documento": f["documento"], "consolidacion": f["consolidacion"],
                "cvm": cvm, "ifdata": ifd,
                "dif_pct": (ifd - cvm) / cvm if cvm else float("nan"),
                "supera_umbral": bool(abs((ifd - cvm) / cvm) > UMBRAL_DIF_PCT) if cvm else False,
                "principal": bool(principal),
            })
    out = pd.DataFrame(filas)
    if out.empty:
        print("[!] contraste: no hay bancos ni periodos comunes entre bk_publicado y bk_panel")
        return out
    banco = pd.DataFrame([{ "cod_inst": b["cod_inst"], "nombre_corto": b["nombre_corto"]} for b in B.universo()])
    out = out.merge(banco, on="cod_inst", how="left")
    if periodo:
        out = out[out["periodo"] == periodo]
    out = out.sort_values(["periodo", "nombre_corto", "linea_cvm", "metrica_ifdata",
                           "principal"]).reset_index(drop=True)

    if guardar:
        A.guardar_derivado(FUENTE, DS_DERIVADO, "contraste_ifdata.csv",
                           out.to_csv(index=False).encode("utf-8-sig"),
                           desde=["datos/gold/bk_publicado.parquet", "datos/gold/bk_panel.parquet"],
                           como=A.comando_actual(),
                           nota="CVM contra IF.Data, mismo banco y trimestre: la diferencia es de definición "
                                "(consolidado societario CPC contra conglomerado prudencial COSIF), no un error")
    return out


def informe_contraste(tabla: pd.DataFrame, periodo: str | None = None) -> None:
    """Imprime el contraste en R$ mil millones, con las diferencias que pasan el umbral marcadas."""
    if tabla.empty:
        print("(sin filas)")
        return
    t = tabla[tabla["periodo"] == periodo] if periodo else tabla
    for p, g in t.groupby("periodo"):
        print(f"\n--- {PER.etiqueta_trimestre(str(p))} ({p}) · CVM contra IF.Data, en R$ mil millones")
        for _, f in g.iterrows():
            marca = "  <<< supera el umbral" if f["supera_umbral"] else ""
            print(f"  {f['nombre_corto']:21} {f['linea_cvm']:22} → {f['metrica_ifdata']:16} "
                  f"CVM {f['cvm'] / 1e9:9.2f}  IF.Data {f['ifdata'] / 1e9:9.2f}  "
                  f"dif {f['dif_pct'] * 100:+6.1f} %  ({f['consolidacion']}){marca}")
    malas = t[t["supera_umbral"] & t["principal"]]
    otras = t[t["supera_umbral"] & ~t["principal"]]
    print(f"\n{len(malas)} de {int(t['principal'].sum())} comparaciones principales superan el "
          f"{UMBRAL_DIF_PCT:.0%} de diferencia (y {len(otras)} de las secundarias, que comparan perímetros "
          f"distintos a propósito).")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paso", nargs="?", default="todo",
                    choices=["descargar", "extraer", "gold", "contrastar", "todo"])
    ap.add_argument("--forzar", action="store_true", help="vuelve a bajar aunque el tamaño no haya cambiado")
    ap.add_argument("--descargar", action="store_true",
                    help="con «todo», baja antes los ZIP: así lo llama actualizar.py. Sin esta opción trabaja "
                         "con lo que ya está en datos/crudo/cvm/ y no toca la red")
    ap.add_argument("--periodo", default=None, help="para «contrastar»: solo este trimestre (AAAAMM)")
    args = ap.parse_args(argv)

    if args.paso == "descargar" or (args.paso == "todo" and args.descargar):
        if descargar(forzar=args.forzar):
            return 1
    if args.paso in ("extraer", "todo"):
        if extraer():
            return 1
    if args.paso in ("gold", "todo"):
        if gold():
            return 1
    if args.paso in ("contrastar", "todo"):
        tabla = contrastar()
        informe_contraste(tabla, args.periodo or (tabla["periodo"].max() if len(tabla) else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
