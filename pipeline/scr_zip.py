"""ZIP anuales del SCR.data (``datos/crudo/bcb_scr/scrdata/actual/scrdata_<año>.zip``): descarga y lectura.

- La descarga va streameada a disco y se registra con ``almacen.registrar_crudo`` (los ZIP pesan cientos de MB).
- Los CSV del SCR.data son UTF-8 con BOM, no cp1252 como el resto de los archivos del gobierno brasileño
  (verificado byte a byte en 2012 y 2024); se prueba UTF-8 estricto y se cae a cp1252 solo si falla.
- Valores con coma decimal y sin separador de miles.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

import almacen as A
import red

CRUDO = A.ruta_cruda("bcb_scr", "scrdata")
URL = "https://www.bcb.gov.br/pda/desig/scrdata_{}.zip"
UA = {"User-Agent": "Mozilla/5.0 extraer-fuentes/1.0"}
CHUNK = 500_000
INTENTOS, PAUSA_S = 3, 30


def ruta(anio: int) -> Path:
    return CRUDO / f"scrdata_{anio}.zip"


def descargar(anio: int, *, no_menos_meses: bool = False) -> Path:
    """Baja el ZIP del año al crudo. Reintenta INTENTOS veces con PAUSA_S de pausa y después falla.

    Con ``no_menos_meses``, rechaza un ZIP que traiga menos meses que el que ya está (el BCB reescribe
    el del año en curso cada mes).
    """
    red.exigir_red(f"el ZIP del SCR.data {anio}")
    import certificados  # noqa: F401  CA del proxy corporativo; antes de requests
    import requests

    CRUDO.mkdir(parents=True, exist_ok=True)
    destino = ruta(anio)
    url = URL.format(anio)

    def validar(parcial: Path) -> None:
        nuevos = zipfile.ZipFile(parcial).namelist()      # ZIP truncado -> excepción
        if no_menos_meses and destino.exists() and len(nuevos) < len(zipfile.ZipFile(destino).namelist()):
            raise ValueError(f"el ZIP nuevo trae menos meses ({len(nuevos)}) que el actual")

    print(f"[~] bajando {url}...")
    try:
        red.bajar_a_disco(lambda u, **kw: requests.get(u, headers=UA, **kw), url, destino, intentos=INTENTOS,
                          espera=lambda n, e: PAUSA_S, validar=validar)
    except Exception as e:                                   # red, HTTP o ZIP roto, tres veces
        raise RuntimeError(f"{destino.name}: falló {INTENTOS} veces ({e})") from e
    A.registrar_crudo("bcb_scr", "scrdata", destino, url)
    print(f"[+] {destino.name}: {destino.stat().st_size / 1e6:.0f} MB")
    return destino


def codificacion(z: zipfile.ZipFile, nombre: str) -> str:
    """UTF-8 (con BOM) si la muestra decodifica estricta; cp1252 si no.

    La muestra se corta 4 bytes antes del final: una secuencia multibyte partida justo en el borde del
    buffer hace fallar el decode estricto aunque el archivo entero sea UTF-8 válido (pasó con scrdata_201412).
    """
    with z.open(nombre) as f:
        muestra = f.read(65536)
    if muestra.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    try:
        muestra[:-4].decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "cp1252"


def leer_csv(z: zipfile.ZipFile, nombre: str, columnas: list[str], **opciones):
    """Itera por partes (``CHUNK`` filas) un CSV del ZIP, todo como texto."""
    cod = codificacion(z, nombre)
    with z.open(nombre) as f:
        yield from pd.read_csv(f, sep=";", dtype=str, usecols=columnas, encoding=cod, chunksize=CHUNK, **opciones)


def numero(col: pd.Series) -> pd.Series:
    """Coma decimal a punto. ``errors="raise"``: un valor ilegible rompe la corrida, no queda en 0."""
    return pd.to_numeric(col.str.replace(",", ".", regex=False), errors="raise")
