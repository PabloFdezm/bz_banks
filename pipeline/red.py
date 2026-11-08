"""Reintentos y descargas a disco: la única política de reintento del pipeline (bcb_api, ifdata, scr_zip)."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Callable


SIN_RED = "BZ_SIN_RED"   # variable de entorno que pone actualizar.py --sin-red para sus pasos


def exigir_red(que: str) -> None:
    """Falla si la corrida es sin red: un dato que falta no se baja en silencio."""
    if os.environ.get(SIN_RED):
        raise RuntimeError(f"corrida sin red ({SIN_RED}): no se baja {que}")


def reintentar(fn: Callable, intentos: int, espera: Callable[[int, Exception], float], *,
               reintentables: tuple[type[Exception], ...] = (Exception,)):
    """Llama ``fn()`` hasta ``intentos`` veces. Tras el fallo n-ésimo (si es reintentable) espera ``espera(n, error)``
    segundos. Un error no reintentable, o el último, se propaga."""
    for intento in range(1, intentos + 1):
        try:
            return fn()
        except reintentables as e:
            if intento == intentos:
                raise
            segundos = espera(intento, e)
            print(f"  [!] intento {intento}/{intentos} falló ({e}); reintento en {segundos:g} s", file=sys.stderr)
            time.sleep(segundos)


def bajar_a_disco(get: Callable, url: str, destino: Path, *, intentos: int = 3,
                  espera: Callable[[int, Exception], float] = lambda n, e: 0,
                  reintentables: tuple[type[Exception], ...] = (Exception,),
                  validar: Callable[[Path], None] | None = None, pausa_previa: float = 0) -> Path:
    """Descarga ``url`` en streaming a ``destino`` vía un ``.part`` que solo se renombra si la descarga (y
    ``validar``, si se pasa) termina bien; si no, el ``.part`` se borra. ``get`` es ``requests.get`` o el ``get``
    de una sesión."""
    destino = Path(destino)
    parcial = destino.with_name(destino.name + ".part")

    def una_vez():
        time.sleep(pausa_previa)
        try:
            with get(url, stream=True, timeout=(30, 300)) as r:
                r.raise_for_status()
                with open(parcial, "wb") as f:
                    for bloque in r.iter_content(1 << 20):
                        if bloque:
                            f.write(bloque)
            if validar:
                validar(parcial)
            parcial.replace(destino)
        except BaseException:
            parcial.unlink(missing_ok=True)
            raise
        return destino

    return reintentar(una_vez, intentos, espera, reintentables=reintentables)
