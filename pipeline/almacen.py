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
REPORTES = DATOS / "reportes"

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


def olvidar(fuente: str, dataset: str, nombre: str, capa: str = "crudo",
            version: str = "actual") -> bool:
    """Quita una entrada del manifiesto sin borrar el archivo. Devuelve si existía.

    Para cuando un archivo estaba clasificado en la capa equivocada: se registra en
    la capa correcta y se olvida en la otra. Nunca borra datos.
    """
    d = ruta_cruda(fuente, dataset, version) if capa == "crudo" else ruta_derivada(fuente, dataset)
    man = leer_manifiesto(d)
    if man is None or nombre not in man.get("archivos", {}):
        return False
    del man["archivos"][nombre]
    escribir_manifiesto(d, man)
    return True


def archivar_crudo(fuente: str, dataset: str, nombre: str, version: str) -> Path:
    """Saca un crudo de `actual/` a `<version>/` sin tocar sus bytes ni su procedencia.

    Para lotes que una descarga posterior dejó superados (el tramo `202601_202608` cuando ya
    está `202601_202609`): si quedan en `actual/`, quien lea `valores_*` ve cada período dos
    veces. No se borran porque `crudo/` no se edita; pasan a la versión de su descarga con la
    misma entrada de manifiesto (URL, sha256, momento de descarga).
    """
    origen_dir, destino_dir = ruta_cruda(fuente, dataset), ruta_cruda(fuente, dataset, version)
    man = leer_manifiesto(origen_dir) or {"archivos": {}}
    entrada = man["archivos"].get(nombre)
    if entrada is None:
        raise ValueError(f"{nombre} no está en el manifiesto de {origen_dir}")
    destino = destino_dir / nombre
    if destino.exists():
        raise FileExistsError(destino)
    destino_dir.mkdir(parents=True, exist_ok=True)
    (origen_dir / nombre).replace(destino)
    man_dest = leer_manifiesto(destino_dir) or {"fuente": fuente, "dataset": dataset, "archivos": {}}
    man_dest["archivos"][nombre] = entrada
    escribir_manifiesto(destino_dir, man_dest)
    olvidar(fuente, dataset, nombre)
    return destino


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


def comparar_derivado(fuente: str, dataset: str, salidas: dict[str, bytes]) -> dict[str, list[str]]:
    """Que cambiaria al publicar `salidas` en el dataset: nuevos, cambiados, iguales, sobrantes.

    `sobrantes` son los archivos que el manifiesto tiene y esta corrida ya no genera.
    Importa en los corpus que se suben a mano (gema/, notebooklm_*): guardar_derivado
    solo escribe, nunca borra, asi que un archivo que dejo de generarse se queda en la
    carpeta y se sube como si siguiera siendo del corpus. Es el mismo fantasma que dejo
    copiar codigo encima sin git.
    """
    previos = (leer_manifiesto(ruta_derivada(fuente, dataset)) or {}).get("archivos", {})
    cambio = {"nuevos": [], "cambiados": [], "iguales": [], "sobrantes": []}
    for nombre, datos in sorted(salidas.items()):
        if nombre not in previos:
            cambio["nuevos"].append(nombre)
        elif previos[nombre].get("sha256") != sha256(datos):
            cambio["cambiados"].append(nombre)
        else:
            cambio["iguales"].append(nombre)
    cambio["sobrantes"] = sorted(n for n in previos if n not in salidas)
    return cambio


def borrar_sobrantes(fuente: str, dataset: str, salidas: dict[str, bytes]) -> list[str]:
    """Saca del disco y del manifiesto lo que el dataset ya no genera. Devuelve los nombres."""
    d = ruta_derivada(fuente, dataset)
    sobrantes = comparar_derivado(fuente, dataset, salidas)["sobrantes"]
    for nombre in sobrantes:
        (d / nombre).unlink(missing_ok=True)
        olvidar(fuente, dataset, nombre, capa="derivado")
    return sobrantes


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
        if not p.exists():
            problemas.append(f"{d}/{nombre}: declarado en el manifiesto pero no existe")
            continue
        real = sha256(p.read_bytes())
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
