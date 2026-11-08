"""Actualiza los datos del sitio de bancos de punta a punta, en orden de dependencias (lo llama actualizar.bat).

Cada paso corre en su propio proceso (``python -X utf8 pipeline/<módulo>.py <argumentos>``, cuyo ``main`` devuelve
0 o 1): así la memoria de un paso no se acumula en el siguiente. Si un paso falla, la corrida se corta y no se
exporta nada. IF.Data no se baja aquí (es trimestral y a mano: ``ifdata.py colectar``).

    python -X utf8 pipeline/actualizar.py              # completo: baja SGS y el SCR del año, ..., verifica, exporta
    python -X utf8 pipeline/actualizar.py --sin-red    # sin descargas: un dato que falta hace fallar el paso
    python -X utf8 pipeline/actualizar.py --desde portada
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

import almacen as A
import red

# (nombre, módulo, argumentos, necesita red). Cada paso lee lo que dejaron los anteriores.
PASOS = [
    ("sgs", "sgs", [], True),                                         # todas las series del catálogo
    ("focus", "focus", [], True),                                     # Focus IPCA 12m (API Olinda)
    ("balances", "preparar_bancos_powerbi", [], False),               # bank_* desde IF.Data
    ("metricas", "preparar_metricas_bancos", [], False),              # intermedio/metricas_bancos
    ("credito", "preparar_credito_paginas_powerbi", [], False),       # cre_* y bk_cre_*
    ("sistema", "preparar_gold_bancos_sistema", [], False),           # bk_sistema_m/q
    ("cartera", "preparar_gold_bancos_cartera", [], False),           # usa bk_sistema_q
    ("base", "preparar_gold_bancos", ["base"], False),                # usa bk_cartera, bk_sistema_q
    ("rentabilidad", "preparar_gold_bancos", ["rentabilidad"], False),
    ("exposicion", "preparar_gold_bancos_exposicion", [], False),
    ("qcambio", "preparar_gold_bancos_qcambio", [], False),           # usa bk_panel, bk_metrica, bk_banco
    ("portada", "preparar_gold_bancos_portada", [], False),           # usa bk_grupo, bk_sistema_m
    ("pag_credito", "preparar_gold_bancos_pag_credito", [], False),
    ("scr_productos", "preparar_gold_bancos_scr_productos", ["--descargar"], True),
    ("scr", "preparar_gold_bancos_scr", [], False),                   # con caché por ZIP
    ("manifiesto", "manifiesto_gold", [], False),                     # después de todos los bk_*
    ("verificacion", None, [], False),                                # pytest + verificar_gold --gold
    ("exportar", "exportar_web_bancos", [], False),
]
NOMBRES = [p[0] for p in PASOS]


def verificar() -> int:
    """Las pruebas y el verificador de la capa gold, antes de exportar."""
    for cmd in ([sys.executable, "-m", "pytest", "-q"],
                [sys.executable, "-X", "utf8", "herramientas/verificar_gold.py", "--gold"]):
        if subprocess.run(cmd, cwd=A.RAIZ).returncode:
            print(f"[!] falló: {' '.join(cmd[1:])}", file=sys.stderr)
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sin-red", action="store_true", help="no baja nada: salta los pasos sgs y focus; un dato que falte hace fallar el paso")
    ap.add_argument("--sin-verificacion", action="store_true", help="salta pytest y verificar_gold (comparaciones)")
    ap.add_argument("--desde", choices=NOMBRES, default=NOMBRES[0], help="empieza en este paso")
    ap.add_argument("--hasta", choices=NOMBRES, default=NOMBRES[-1], help="termina en este paso")
    args = ap.parse_args(argv)

    pasos = PASOS[NOMBRES.index(args.desde):NOMBRES.index(args.hasta) + 1]
    entorno = {**os.environ, red.SIN_RED: "1"} if args.sin_red else None   # los pasos fallan antes que bajar
    for i, (nombre, modulo, argumentos, usa_red) in enumerate(pasos, 1):
        if nombre == "verificacion" and args.sin_verificacion:
            continue
        if args.sin_red and usa_red:
            if nombre in ("sgs", "focus"):
                continue
            argumentos = [a for a in argumentos if a != "--descargar"]
        print(f"\n[{i}/{len(pasos)}] {nombre}", flush=True)
        inicio = time.time()
        codigo = verificar() if modulo is None else subprocess.run(
            [sys.executable, "-X", "utf8", str(A.RAIZ / "pipeline" / f"{modulo}.py"), *argumentos], cwd=A.RAIZ,
            env=entorno).returncode
        if codigo:
            print(f"\nERROR: falló el paso «{nombre}»; no se sigue.", file=sys.stderr)
            return 1
        print(f"    ({time.time() - inicio:.0f} s)")
    print("\nDatos al día.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
