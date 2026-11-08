"""Arquitectura de datos: capas, procedencia y rutas.

EL PROBLEMA QUE RESUELVE
------------------------
Antes de esto había 45 CSV sueltos en la raíz, mezclados con el código, sin forma de
responder tres preguntas básicas:

  - ¿de dónde salió este archivo?
  - ¿cuándo se bajó?
  - ¿es lo que la fuente sirvió, o algo que nosotros derivamos?

La tercera es la que más duele. `cvm_dfp_bancos_2024.csv` parecía un dato de la CVM y en
realidad era el resultado de un filtro nuestro — un filtro que estuvo mal y metió 72% de
empresas que no son bancos. Como el ZIP original nunca se guardó, no se podía ni auditar
qué había hecho el filtro ni re-derivar sin volver a descargar.

LAS DOS CAPAS
-------------
    datos/crudo/<fuente>/<dataset>/<version>/    exactamente lo que sirvió la fuente
    datos/derivado/<fuente>/<dataset>/           lo que produce nuestro código

La regla que decide: **crudo es lo que la fuente sirvió, ANTES de cualquier filtro
nuestro.** Si nuestro código lo tocó, es derivado. Un CSV filtrado por bancos es derivado
aunque venga de la CVM.

`crudo/` no se edita nunca. Si un parser falla, se arregla el parser.

PROCEDENCIA
-----------
Cada archivo crudo lleva al lado un `_manifiesto.json` con URL, sha256, tamaño y momento
de descarga. Eso es lo que permite decir "este número salió de esta URL, este día, y el
archivo sigue siendo el mismo".

Los derivados llevan su propio manifiesto que además nombra los crudos de los que salieron,
para poder rehacer la cadena.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
CRUDO = DATOS / "crudo"
DERIVADO = DATOS / "derivado"
INTERMEDIO = DATOS / "intermedio"
GOLD = DATOS / "gold"
DEFINICIONES = RAIZ / "definiciones"

MANIFIESTO = "_manifiesto.json"


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def sha256_archivo(p: Path) -> str:
    """sha256 leyendo por bloques, para archivos que no conviene cargar enteros."""
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def ruta_cruda(fuente: str, dataset: str, version: str = "actual") -> Path:
    """datos/crudo/<fuente>/<dataset>/<version>/"""
    return CRUDO / fuente / dataset / version


def ruta_derivada(fuente: str, dataset: str) -> Path:
    """datos/derivado/<fuente>/<dataset>/"""
    return DERIVADO / fuente / dataset


def escribir_atomico(destino: Path, datos: bytes) -> None:
    """Escribe por archivo temporal y renombra, para que no quede a medias."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=destino.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fo:
            fo.write(datos)
        os.replace(tmp, destino)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def guardar_crudo(
    fuente: str, dataset: str, nombre: str, datos: bytes, url: str, version: str = "actual",
) -> Path:
    """Guarda bytes tal cual llegaron, con su manifiesto de procedencia."""
    d = ruta_cruda(fuente, dataset, version)
    destino = d / nombre
    escribir_atomico(destino, datos)

    man = leer_manifiesto(d) or {"fuente": fuente, "dataset": dataset, "archivos": {}}
    man["archivos"][nombre] = {
        "url": url,
        "sha256": sha256(datos),
        "bytes": len(datos),
        "descargado_en": _ahora(),
    }
    escribir_manifiesto(d, man)
    return destino


def registrar_crudo(fuente: str, dataset: str, ruta: Path, url: str,
                    version: str = "actual", *,
                    descargado_en: str | None = None,
                    nota: str | None = None) -> Path:
    """Anota en el manifiesto un archivo crudo YA escrito en su sitio.

    `guardar_crudo` recibe los bytes; eso no sirve cuando la descarga se streamea
    a disco porque el archivo pesa decenas de MB (IFDATA sirve trimestres de 40 MB).
    Aquí el archivo ya está donde va y solo falta su procedencia.

    Exige que `ruta` esté dentro de ruta_cruda(fuente, dataset, version): si el
    llamador se equivoca de carpeta, el manifiesto quedaría describiendo un archivo
    que no está ahí, que es peor que no tener manifiesto.

    `descargado_en` se pasa solo al registrar algo bajado antes (una migración);
    omitirlo significa "se está bajando ahora". Poner la hora del registro en un
    archivo viejo convierte el manifiesto en una afirmación falsa.
    """
    ruta = Path(ruta)
    d = ruta_cruda(fuente, dataset, version)
    if ruta.parent.resolve() != d.resolve():
        raise ValueError(f"{ruta} no está en {d}")
    if not ruta.exists():
        raise FileNotFoundError(ruta)

    man = leer_manifiesto(d) or {"fuente": fuente, "dataset": dataset, "archivos": {}}
    entrada = {
        "url": url,
        "sha256": sha256_archivo(ruta),
        "bytes": ruta.stat().st_size,
        "descargado_en": descargado_en or _ahora(),
    }
    if nota:
        entrada["nota"] = nota
    man["archivos"][ruta.name] = entrada
    escribir_manifiesto(d, man)
    return ruta


def guardar_derivado(
    fuente: str, dataset: str, nombre: str, datos: bytes, *, desde: list[str], como: str,
    nota: str | None = None,
) -> Path:
    """Guarda un derivado nombrando de qué crudos salió y con qué comando.

    `desde` son rutas relativas a datos/, `como` es el comando que lo produjo. Sin eso un
    derivado es indistinguible de un dato de la fuente, que es exactamente el error que
    hizo pasar un filtro roto por dato oficial de la CVM.
    """
    d = ruta_derivada(fuente, dataset)
    destino = d / nombre
    escribir_atomico(destino, datos)

    man = leer_manifiesto(d) or {"fuente": fuente, "dataset": dataset, "archivos": {}}
    entrada = {
        "derivado_de": desde,
        "producido_por": como,
        "sha256": sha256(datos),
        "bytes": len(datos),
        "generado_en": _ahora(),
    }
    if nota:
        entrada["nota"] = nota
    man["archivos"][nombre] = entrada
    escribir_manifiesto(d, man)
    return destino


def leer_manifiesto(d: Path) -> dict | None:
    p = d / MANIFIESTO
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def escribir_manifiesto(d: Path, man: dict) -> None:
    escribir_atomico(d / MANIFIESTO, json.dumps(man, indent=2, ensure_ascii=False).encode())


def verificar(d: Path) -> list[str]:
    """Comprueba que cada archivo del manifiesto exista y su sha256 coincida.

    Devuelve la lista de problemas; vacía significa que la capa está íntegra.
    """
    man = leer_manifiesto(d)
    if man is None:
        return [f"{d}: sin manifiesto"]
    problemas = []
    for nombre, meta in man.get("archivos", {}).items():
        p = d / nombre
        pq = meta.get("parquet")
        if not p.exists() and pq and (d / pq["archivo"]).exists():
            if sha256_archivo(d / pq["archivo"]) != pq.get("sha256"):
                problemas.append(f"{d}/{pq['archivo']}: sha256 no coincide (el parquet cambió)")
            continue
        if not p.exists():
            problemas.append(f"{d}/{nombre}: declarado en el manifiesto pero no existe")
            continue
        real = sha256_archivo(p)
        if real != meta.get("sha256"):
            problemas.append(f"{d}/{nombre}: sha256 no coincide (el archivo cambió)")
    return problemas


def verificar_todo() -> list[str]:
    """Verifica cada directorio con manifiesto bajo datos/."""
    problemas = []
    for base in (CRUDO, DERIVADO):
        if not base.exists():
            continue
        for d in sorted(p.parent for p in base.rglob(MANIFIESTO)):
            problemas += verificar(d)
    return problemas


def inventario() -> list[dict]:
    """Una fila por archivo, con su capa y procedencia. Para reportes y auditoría."""
    filas = []
    for capa, base in (("crudo", CRUDO), ("derivado", DERIVADO)):
        if not base.exists():
            continue
        for mp in sorted(base.rglob(MANIFIESTO)):
            man = json.loads(mp.read_text(encoding="utf-8"))
            for nombre, meta in man.get("archivos", {}).items():
                filas.append({
                    "capa": capa,
                    "fuente": man.get("fuente", ""),
                    "dataset": man.get("dataset", ""),
                    "archivo": nombre,
                    "ruta": str((mp.parent / nombre).relative_to(RAIZ)),
                    "bytes": meta.get("bytes", 0),
                    "origen": meta.get("url") or " + ".join(meta.get("derivado_de", [])),
                    "cuando": meta.get("descargado_en") or meta.get("generado_en", ""),
                })
    return filas


# Crudo tabular en parquet. Los CSV de IF.Data pesan ~80 veces más que el mismo contenido en parquet. El parquet guarda
# TODAS las columnas como texto, tal cual venían en el CSV (sin inferir tipos, "" se conserva):
# es una recodificación sin pérdida, así que sigue siendo capa cruda. El manifiesto conserva la
# URL y el sha256 del CSV original y agrega los del parquet (clave "parquet").

def ruta_parquet(ruta_csv: Path) -> Path:
    return Path(ruta_csv).with_suffix(".parquet")


def existe_crudo(ruta_csv: Path) -> bool:
    """True si el crudo está como CSV o ya convertido a parquet."""
    return Path(ruta_csv).exists() or ruta_parquet(ruta_csv).exists()


def leer_crudo_tabla(ruta_csv: Path, columnas: list[str] | None = None):
    """Lee un crudo tabular como texto: del parquet si existe, si no del CSV.

    Devuelve lo mismo que ``pd.read_csv(ruta, dtype=str, keep_default_na=False, usecols=columnas)``.
    """
    import pandas as pd
    pq = ruta_parquet(ruta_csv)
    if pq.exists():
        return pd.read_parquet(pq, columns=columnas)
    return pd.read_csv(ruta_csv, dtype=str, keep_default_na=False, usecols=columnas)


def csv_a_parquet(fuente: str, dataset: str, ruta_csv: Path, *, borrar_csv: bool = False,
                  version: str = "actual", **opciones_csv) -> Path:
    """Convierte un CSV crudo a parquet (todo texto, zstd), comprueba que no se perdió nada y
    lo anota en el manifiesto. Con ``borrar_csv`` elimina el CSV después de comprobar."""
    import io
    import pandas as pd
    ruta_csv = Path(ruta_csv)
    d = ruta_cruda(fuente, dataset, version)
    if ruta_csv.parent.resolve() != d.resolve():
        raise ValueError(f"{ruta_csv} no está en {d}")
    df = pd.read_csv(ruta_csv, dtype=str, keep_default_na=False, **opciones_csv)
    buf = io.BytesIO()
    df.to_parquet(buf, index=False, compression="zstd")
    datos = buf.getvalue()
    vuelta = pd.read_parquet(io.BytesIO(datos))
    if not (vuelta.shape == df.shape and list(vuelta.columns) == list(df.columns) and vuelta.equals(df)):
        raise ValueError(f"{ruta_csv.name}: el parquet no reproduce el CSV")
    destino = ruta_parquet(ruta_csv)
    escribir_atomico(destino, datos)
    man = leer_manifiesto(d) or {"fuente": fuente, "dataset": dataset, "archivos": {}}
    entrada = man["archivos"].setdefault(ruta_csv.name, {
        "sha256": sha256_archivo(ruta_csv), "bytes": ruta_csv.stat().st_size, "descargado_en": None,
        "nota": "CSV registrado al convertirlo a parquet"})
    entrada["parquet"] = {
        "archivo": destino.name, "sha256": sha256(datos), "bytes": len(datos), "filas": len(df),
        "convertido_en": _ahora(),
        "nota": "mismo contenido que el CSV: todas las columnas como texto, sin inferir tipos",
    }
    escribir_manifiesto(d, man)
    if borrar_csv:
        ruta_csv.unlink()
    return destino


def glob_crudo(carpeta: Path, patron_csv: str) -> list[Path]:
    """Como ``carpeta.glob(patron_csv)``, pero cuenta también los que ya están en parquet.
    Devuelve siempre la ruta con extensión .csv (el nombre lógico del crudo)."""
    carpeta = Path(carpeta)
    nombres = {p.name for p in carpeta.glob(patron_csv)}
    nombres |= {p.with_suffix(".csv").name for p in carpeta.glob(patron_csv[:-4] + ".parquet")} if patron_csv.endswith(".csv") else set()
    return [carpeta / n for n in sorted(nombres)]


MIN_BYTES_CRUDO = 200


def crudo_con_datos(ruta_csv: Path) -> bool:
    """True si el crudo trae filas. En CSV se usa el tamaño (una respuesta vacía de OLinda es solo la
    cabecera, menos de MIN_BYTES_CRUDO); en parquet, el número de filas de sus metadatos."""
    ruta_csv = Path(ruta_csv)
    pq = ruta_parquet(ruta_csv)
    if pq.exists():
        import pyarrow.parquet as papq
        return papq.ParquetFile(pq).metadata.num_rows > 0
    return ruta_csv.exists() and ruta_csv.stat().st_size > MIN_BYTES_CRUDO


# IF.Data: nombres de los crudos de OLinda (siempre con extensión .csv, aunque estén en parquet).

def ruta_valores(periodo: str, escopo: int | str, informe: int | str | None = None) -> Path:
    """datos/crudo/bcb_ifdata/valores/actual/valores_<periodo>_<escopo>[_r<informe>].csv"""
    sufijo = "" if informe is None else f"_r{informe}"
    return ruta_cruda("bcb_ifdata", "valores") / f"valores_{periodo}_{escopo}{sufijo}.csv"


def ruta_cadastro(periodo: str) -> Path:
    return ruta_cruda("bcb_ifdata", "cadastro") / f"cadastro_{periodo}.csv"


def leer_definicion(nombre: str) -> dict:
    """definiciones/<nombre>.json"""
    return json.loads((DEFINICIONES / f"{nombre}.json").read_text(encoding="utf-8"))


# Capa gold e intermedia.

def parquet_bytes(df) -> bytes:
    import io
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    return buf.getvalue()


def escribir_parquet(df, destino: Path) -> bytes:
    """Escribe ``df`` como parquet de forma atómica y devuelve los bytes escritos."""
    datos = parquet_bytes(df)
    escribir_atomico(Path(destino), datos)
    return datos


def contrato_gold() -> dict[str, dict]:
    """Columnas mínimas y clave única de cada tabla gold (definiciones/contrato_gold.json)."""
    return leer_definicion("contrato_gold")["tablas"]


def validar_contrato(nombre: str, df) -> None:
    """Falla si la tabla no está en el contrato, si le falta una columna o si repite la clave."""
    contrato = contrato_gold().get(nombre)
    if contrato is None:
        raise ValueError(f"{nombre}: no está en definiciones/contrato_gold.json")
    faltan = [c for c in contrato["columnas"] if c not in df.columns]
    if faltan:
        raise ValueError(f"{nombre}: faltan columnas del contrato gold: {faltan}")
    repetidas = int(df.duplicated(contrato["clave"]).sum())
    if repetidas:
        raise ValueError(f"{nombre}: {repetidas} filas repiten la clave {contrato['clave']}")


def comando_actual() -> str:
    """El comando que corre ahora (script y argumentos), para la procedencia de lo que escribe."""
    import sys
    return " ".join(["python -X utf8", Path(sys.argv[0]).name, *sys.argv[1:]])


def publicar_gold(nombre: str, df, *, dataset: str, desde: list[str],
                  fuente: str = "bcb_ifdata", nota: str | None = None) -> bytes:
    """Publica ``datos/gold/<nombre>.parquet`` con su procedencia en ``datos/derivado/<fuente>/<dataset>/``.

    Antes de escribir valida la tabla contra el contrato gold. El manifiesto del derivado nombra el comando
    que la produjo (comando_actual()); ``bk_manifiesto`` lo lee de ahí. Devuelve los bytes escritos.
    """
    validar_contrato(nombre, df)
    archivo = f"{nombre}.parquet"
    datos = parquet_bytes(df)
    guardar_derivado(fuente, dataset, archivo, datos, desde=desde, como=comando_actual(), nota=nota)
    escribir_atomico(GOLD / archivo, datos)
    return datos


def productores_gold() -> dict[str, str]:
    """Archivo gold → comando que lo publicó, según los manifiestos de datos/derivado/."""
    out = {}
    if DERIVADO.exists():
        for mp in sorted(DERIVADO.rglob(MANIFIESTO)):
            man = json.loads(mp.read_text(encoding="utf-8"))
            for nombre, meta in man.get("archivos", {}).items():
                if nombre.startswith("bk_") and meta.get("producido_por"):
                    out[nombre] = meta["producido_por"]
    return out


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        problemas = verificar_todo()
        if problemas:
            print(f"{len(problemas)} problemas de integridad:")
            for p in problemas:
                print(f"  {p}")
            sys.exit(1)
        print("integridad OK")
    else:
        filas = inventario()
        total = sum(f["bytes"] for f in filas)
        print(f"{len(filas)} archivos, {total / 1e6:.0f} MB")
        for f in filas:
            print(f"  [{f['capa']:8}] {f['bytes'] / 1e6:8.1f} MB  {f['ruta']}")
