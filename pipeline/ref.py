# -*- coding: utf-8 -*-
"""REF del BCB: Anexo Estatístico (xlsx) de cada edición → bk_ref (edición × gráfico × serie × punto).

Fuente: https://www.bcb.gov.br/publicacoes/ref. Cada edición semestral del Relatório de Estabilidade Financeira
publica un xlsx con una hoja por gráfico o tabla («Graf 1.2.2.16», «Tab 1.2.4.1»). Es público, a diferencia del
PDF guardado en referencias/: el xlsx se baja a datos/crudo/bcb_ref/anexo/<edicion>/ con su manifiesto.

Trampas (verificadas el 9-nov-2026 sobre las ediciones 202304 a 202610):
1. El mes de publicación varía (may-26 en vez de abr-26): las ediciones se listan en definiciones/bcb_ref.json y
   «descargar» sondea los meses candidatos del semestre siguiente para avisar de una nueva.
2. Cada hoja tiene su forma: título, «Fonte», notas, una fila de unidad («%», «R$ bilhões»), uno o dos niveles de
   encabezado (el superior en celdas combinadas que openpyxl lee como vacías a la derecha) y después los datos.
3. Las fechas vienen como datetime, como «2020-12», o como «Jun\\n2023» seguido de «Jul», «Ago»… sin año.
4. Hay hojas sin eje temporal (distribuciones, tablas por categoría, escenarios de estrés): se guardan con
   ``categoria`` en vez de ``fecha_ref``.
5. Algunas columnas vienen vacías a propósito (el contrafactual de 1.2.2.21 solo existe en la proyección):
   no se rellena nada; una celda vacía no genera fila.

Uso:  python -X utf8 pipeline/ref.py descargar   (baja las ediciones que falten y sondea la siguiente)
      python -X utf8 pipeline/ref.py gold        (lee todas las ediciones bajadas → bk_ref)
      python -X utf8 pipeline/ref.py --descargar (las dos cosas; así lo llama actualizar.py, que quita
                                                   --descargar cuando corre sin red)
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

import pandas as pd

import almacen as A
import red

FUENTE = "bcb_ref"
DATASET_CRUDO = "anexo"
DATASET_GOLD = "ref"
DEF = "bcb_ref"
UA = {"User-Agent": "Mozilla/5.0 (bz_banks; datos públicos del BCB)"}
INTENTOS = 3

COLUMNAS = ["edicion", "hoja", "grafico", "titulo", "unidad", "tipo", "serie", "orden", "fecha_ref", "categoria",
            "valor"]
# «fecha_ref» es texto («2026-06», o «2027» en series anuales) y no fecha: el anexo trae proyecciones y escenarios
# posteriores a hoy (brecha de crédito, estrés a 2029), que la regla general de fechas del verificador rechazaría.
CLAVE = ["edicion", "hoja", "serie", "orden"]
HOJAS_SIN_DATOS = {"Folha de rosto", "Capa", "Índice"}

MESES = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10,
         "nov": 11, "dez": 12,
         # algunas hojas (1.2.1.3, 1.4.1) vienen con los meses en inglés
         "feb": 2, "apr": 4, "may": 5, "aug": 8, "sep": 9, "oct": 10, "dec": 12}
_UNIDAD = re.compile(r"^(%|r\$|us\$|p\.?\s?p\.?|pontos|n[ºo°]|número|numero|meses|dias|anos|índice|indice|"
                     r"bilh|milh|mil\b|em\s)", re.I)


# ---------------------------------------------------------------- definiciones y rutas

def definicion() -> dict:
    return A.leer_definicion(DEF)


def url_anexo(edicion: str) -> str:
    return definicion()["url"].format(edicion=edicion)


def ruta_anexo(edicion: str) -> Path:
    return A.ruta_cruda(FUENTE, DATASET_CRUDO, edicion) / f"RELESTAB{edicion}-refAnexoEstatistico.xlsx"


def ediciones_bajadas() -> list[str]:
    base = A.ruta_cruda(FUENTE, DATASET_CRUDO, "x").parent
    if not base.exists():
        return []
    return sorted(d.name for d in base.iterdir() if d.is_dir() and ruta_anexo(d.name).exists())


def candidatas_siguientes(ultima: str, meses: dict) -> list[str]:
    """Meses candidatos del semestre que sigue a ``ultima`` (AAAAMM)."""
    anio, mes = int(ultima[:4]), int(ultima[4:])
    if mes <= 6:
        return [f"{anio}{m}" for m in meses["segundo_semestre"]]
    return [f"{anio + 1}{m}" for m in meses["primer_semestre"]]


# ---------------------------------------------------------------- descarga

def _validar_xlsx(parcial: Path) -> None:
    import zipfile
    with zipfile.ZipFile(parcial) as z:          # un 404 del BCB vuelve como HTML de 6 kB: no es un ZIP
        if "xl/workbook.xml" not in z.namelist():
            raise ValueError("no es un xlsx")


def bajar_edicion(edicion: str, *, forzar: bool = False) -> str:
    """Baja el anexo de una edición si falta. Devuelve qué pasó."""
    import certificados  # noqa: F401  CA del proxy corporativo; antes de requests
    import requests

    destino = ruta_anexo(edicion)
    if destino.exists() and not forzar:
        return "ya estaba"
    url = url_anexo(edicion)
    destino.parent.mkdir(parents=True, exist_ok=True)
    red.bajar_a_disco(lambda u, **kw: requests.get(u, headers=UA, **kw), url, destino, intentos=INTENTOS,
                      espera=lambda n, e: 5 * n, validar=_validar_xlsx)
    A.registrar_crudo(FUENTE, DATASET_CRUDO, destino, url, version=edicion)
    return f"bajado ({destino.stat().st_size / 1e6:.1f} MB)"


def existe_en_servidor(edicion: str) -> bool:
    import certificados  # noqa: F401
    import requests
    r = requests.head(url_anexo(edicion), headers=UA, timeout=60, allow_redirects=True)
    return r.status_code == 200


def descargar(*, forzar: bool = False) -> int:
    red.exigir_red("el Anexo Estatístico del REF")
    d = definicion()
    for ed in d["ediciones"]:
        print(f"[+] REF {ed}: {bajar_edicion(ed, forzar=forzar)}")
    nuevas = [c for c in candidatas_siguientes(d["ediciones"][-1], d["meses_candidatos"]) if existe_en_servidor(c)]
    if nuevas:
        print(f"[!] hay una edición nueva del REF en el servidor: {nuevas}. Agregarla a definiciones/{DEF}.json "
              f"(«ediciones») y volver a correr.")
    return 0


# ---------------------------------------------------------------- lectura de una hoja

def limpiar(texto) -> str:
    if isinstance(texto, (datetime, date)):          # encabezados con fecha («2025-12-01 00:00:00» → «2025-12»)
        return f"{texto.year}-{texto.month:02d}"
    s = unicodedata.normalize("NFC", str(texto)).replace("\xa0", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", s).strip()


def grafico_de_hoja(hoja: str) -> str:
    """«Graf 1.2.2.16» → «1.2.2.16»; «Tab 1.2.4.1» → «T1.2.4.1»; «Grafs 1.2.5.1 a 1.2.5.5» → «1.2.5.1-1.2.5.5»."""
    h = limpiar(hoja)
    numeros = re.findall(r"\d+(?:\.\d+)+(?:\.[a-z])?", h)
    if not numeros:
        return h
    ident = "-".join(numeros)
    return f"T{ident}" if h.lower().startswith("tab") else ident


def _es_numero(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v


class _Fechas:
    """Convierte la primera columna en «AAAA-MM» (o «AAAA»), con el año de contexto para «Jul», «Ago»…"""

    def __init__(self):
        self.anio: int | None = None
        self.mes: int | None = None

    def leer(self, v) -> str | None:
        if isinstance(v, (datetime, date)):
            return self._fijar(v.year, v.month)
        if isinstance(v, int) and not isinstance(v, bool):
            if 190001 <= v <= 210012 and 1 <= v % 100 <= 12:
                return self._fijar(v // 100, v % 100)
            if 1900 <= v <= 2100:
                self.anio, self.mes = v, 12
                return f"{v}"
            return None
        if not isinstance(v, str):
            return None
        s = limpiar(v).lower()
        m = re.fullmatch(r"(\d{4})-(\d{2})(?:-\d{2})?", s)
        if m:
            return self._fijar(int(m[1]), int(m[2]))
        m = re.fullmatch(r"([a-zç]{3})[a-zç]*\.?\s*[/ -]?\s*(\d{2}|\d{4})", s)
        if m and m[1] in MESES:
            anio = int(m[2]) + (2000 if len(m[2]) == 2 else 0)
            return self._fijar(anio, MESES[m[1]])
        m = re.fullmatch(r"([a-zç]{3})[a-zç]*\.?", s)
        if m and m[1] in MESES and self.anio is not None:
            mes = MESES[m[1]]
            anio = self.anio + (1 if self.mes is not None and mes <= self.mes else 0)
            return self._fijar(anio, mes)
        m = re.fullmatch(r"(\d{4})", s)
        if m:
            self.anio, self.mes = int(m[1]), 12
            return m[1]
        return None

    def _fijar(self, anio: int, mes: int) -> str:
        self.anio, self.mes = anio, mes
        return f"{anio}-{mes:02d}"


def _es_fecha_suelta(v) -> bool:
    """¿La celda parece una fecha por sí sola (sin contexto)?"""
    return _Fechas().leer(v) is not None


def _es_unidad(fila: list) -> str | None:
    vals = [c for c in fila if c is not None and str(c).strip()]
    if len(vals) == 1 and isinstance(vals[0], str) and _UNIDAD.match(limpiar(vals[0])):
        return limpiar(vals[0])
    return None


def leer_hoja(filas: list[tuple], hoja: str, edicion: str, avisos: list[str]) -> pd.DataFrame:
    """Una hoja del anexo en formato largo. Ver las trampas 2 a 5 del encabezado."""
    filas = [list(f) for f in filas]
    ancho = max((len(f) for f in filas), default=0)
    filas = [f + [None] * (ancho - len(f)) for f in filas]
    titulo, i_titulo = "", -1
    for i, f in enumerate(filas[:10]):
        c = next((x for x in f if isinstance(x, str) and x.strip()), None)
        if c and re.match(r"^(gr[áa]ficos?|tabela)\b", limpiar(c), re.I):
            titulo, i_titulo = limpiar(c), i
            break

    # primera fila de datos: col 0 con fecha y algún número a la derecha; si no hay ninguna, hoja por categorías
    def con_numeros(f):
        return any(_es_numero(x) for x in f[1:])

    inicio, tipo = None, "serie"
    for i in range(i_titulo + 1, len(filas)):
        if _es_fecha_suelta(filas[i][0]) and con_numeros(filas[i]):
            inicio = i
            break
    if inicio is None:
        tipo = "categorias"
        for i in range(i_titulo + 1, len(filas)):
            c0 = filas[i][0]
            rotulo = (isinstance(c0, str) and c0.strip()) or _es_numero(c0)   # tramos de CRI, n.º de entidad
            if rotulo and con_numeros(filas[i]) and not _es_unidad(filas[i]):
                inicio = i
                break
    if inicio is None:
        avisos.append(f"{edicion} {hoja}: sin datos numéricos reconocibles")
        return pd.DataFrame(columns=COLUMNAS)

    unidad, encabezados = "", []
    for f in filas[i_titulo + 1:inicio]:
        texto = next((limpiar(x) for x in f if x is not None and str(x).strip()), "")
        if not texto:
            continue
        u = _es_unidad(f)
        if u:
            unidad = unidad or u
            continue
        if re.match(r"^(fonte|\*|obs[.:]|notas?[.:]|\(\d+\)\s)", texto, re.I):   # no «Observada»
            continue
        encabezados.append(f)

    # columnas con datos y su nombre: niveles superiores arrastrados a la derecha (celdas combinadas)
    datos_cols = [j for j in range(1, ancho) if any(_es_numero(filas[i][j]) for i in range(inicio, len(filas)))]
    nombres: dict[int, str] = {}
    arrastre = [None] * len(encabezados)
    for j in range(1, ancho):
        niveles = [e[j] for e in encabezados]
        if j not in datos_cols and all(v is None for v in niveles):
            arrastre = [None] * len(encabezados)        # columna separadora: corta el arrastre
            continue
        partes = []
        for k, v in enumerate(niveles):
            ultimo = k == len(niveles) - 1
            if v is not None and str(v).strip():
                if not ultimo:
                    arrastre[k] = limpiar(v)
                partes.append(limpiar(v))
            elif not ultimo and arrastre[k]:
                partes.append(arrastre[k])
        if j in datos_cols:
            nombres[j] = " | ".join(partes) or f"col{j}"
    vistos: dict[str, int] = {}
    for j in sorted(nombres):
        n = nombres[j]
        vistos[n] = vistos.get(n, 0) + 1
        if vistos[n] > 1:
            nombres[j] = f"{n} ({vistos[n]})"

    salida, fechas, grafico = [], _Fechas(), grafico_de_hoja(hoja)
    for i in range(inicio, len(filas)):
        f = filas[i]
        if not con_numeros(f):
            continue
        if tipo == "serie":
            fecha, categoria = fechas.leer(f[0]), ""
            if fecha is None:
                if f[0] is not None and str(f[0]).strip():
                    avisos.append(f"{edicion} {hoja}: fila {i + 1} con «{limpiar(f[0])}» en la columna de fechas "
                                  f"(se omite)")
                continue
        else:
            c0 = f[0]
            if _es_numero(c0):
                categoria = f"{c0:g}"
            else:
                categoria = limpiar(c0) if c0 is not None else ""
            fecha = None
        for j, nombre in nombres.items():
            v = f[j]
            if _es_numero(v):
                salida.append({"edicion": edicion, "hoja": hoja, "grafico": grafico, "titulo": titulo,
                               "unidad": unidad, "tipo": tipo, "serie": nombre, "orden": i + 1, "fecha_ref": fecha,
                               "categoria": categoria, "valor": float(v)})
    return pd.DataFrame(salida, columns=COLUMNAS)


def leer_edicion(edicion: str, avisos: list[str]) -> pd.DataFrame:
    import openpyxl
    wb = openpyxl.load_workbook(ruta_anexo(edicion), read_only=True, data_only=True)
    try:
        partes = [leer_hoja(list(wb[h].iter_rows(values_only=True)), h, edicion, avisos)
                  for h in wb.sheetnames if h not in HOJAS_SIN_DATOS]
    finally:
        wb.close()
    partes = [p for p in partes if len(p)]
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=COLUMNAS)


# ---------------------------------------------------------------- gold y controles

def controlar_usados(df: pd.DataFrame, avisos: list[str]) -> list[str]:
    """Los gráficos usados existen en la última edición con sus series. Devuelve los errores."""
    errores = []
    ultima = df["edicion"].max()
    u = df[df["edicion"] == ultima]
    for graf, series in definicion()["usados"]["graficos"].items():
        g = u[u["grafico"] == graf]
        if g.empty:
            errores.append(f"{ultima}: falta el gráfico {graf}")
            continue
        faltan = sorted(set(series) - set(g["serie"]))
        if faltan:
            errores.append(f"{ultima} {graf}: faltan las series {faltan} (hay {sorted(g['serie'].unique())})")
        if (g["tipo"] == "serie").all():
            for s, gs in g.groupby("serie"):
                f = gs["fecha_ref"].tolist()
                if f != sorted(f) or len(set(f)) != len(f):
                    avisos.append(f"{ultima} {graf} «{s}»: fechas fuera de orden o repetidas")
    return errores


def construir(*, avisos: list[str] | None = None) -> pd.DataFrame:
    avisos = [] if avisos is None else avisos
    eds = ediciones_bajadas()
    if not eds:
        raise ValueError("no hay anexos del REF en datos/crudo/bcb_ref/: correr «ref.py descargar»")
    df = pd.concat([leer_edicion(e, avisos) for e in eds], ignore_index=True)
    rep = int(df.duplicated(CLAVE).sum())
    if rep:
        raise ValueError(f"bk_ref: {rep} filas repiten la clave {CLAVE}")
    return df


def gold(*, publicar: bool = True) -> int:
    avisos: list[str] = []
    df = construir(avisos=avisos)
    errores = controlar_usados(df, avisos)
    for a in avisos:
        print(f"[i] {a}")
    print(f"[+] bk_ref: {len(df):,} filas, {df['edicion'].nunique()} ediciones, "
          f"{df.groupby('edicion')['hoja'].nunique().to_dict()} hojas con datos")
    if errores:
        for e in errores:
            print(f"[!] {e}", file=sys.stderr)
        return 1
    if publicar:
        A.publicar_gold("bk_ref", df, fuente=FUENTE, dataset=DATASET_GOLD,
                        desde=[f"datos/crudo/{FUENTE}/{DATASET_CRUDO}", f"definiciones/{DEF}.json"],
                        nota="Anexo Estatístico del REF (BCB), todas las ediciones bajadas, en formato largo")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paso", nargs="?", default="todo", choices=["descargar", "gold", "todo"])
    ap.add_argument("--forzar", action="store_true", help="vuelve a bajar las ediciones ya bajadas")
    ap.add_argument("--descargar", action="store_true",
                    help="con «todo», baja antes las ediciones que falten; sin esta opción no toca la red")
    ap.add_argument("--resumen", action="store_true", help="con «gold», no publica")
    args = ap.parse_args(argv)
    if args.paso == "descargar" or (args.paso == "todo" and args.descargar):
        if descargar(forzar=args.forzar):
            return 1
    if args.paso in ("gold", "todo"):
        return gold(publicar=not args.resumen)
    return 0


if __name__ == "__main__":
    sys.exit(main())
