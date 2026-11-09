"""Exporta la capa gold de bancos (datos/gold/bk_*.parquet) al JSON del sitio «Bancos Brasil».

Por qué existe: el sitio es estático y sin build, y toda su cifra vive en
`sitio/data/<tabla>.json` con el formato del spec macro §7.1
(`{tabla, columnas, filas}`); Power BI lee los mismos parquet (spec bancos §11). Este
script es el único puente entre ambas capas: aquí no se calcula nada, solo se serializa.

Qué produce en `sitio/data/` (se regenera entero en cada corrida):
- `<tabla>.json` para cada `datos/gold/bk_*.parquet`, salvo `bk_cartera_totales`, que es
  auxiliar del verificador (decisión 59) y está fuera del contrato del sitio.
- `banco/<slug>/<tabla>.json` para `bk_panel`, `bk_cartera` y `bk_roe_arbol`: las filas de
  ese banco, para que la ficha cargue solo lo suyo (spec bancos §7). En `bk_roe_arbol` la
  columna es `entidad`, que también trae grupos agregados («Modelo de negocio|Grandes»…):
  esas filas no son de ningún banco y quedan solo en la tabla completa.
- `metrica/<metrica>/bk_panel.json` y `optica/<slug>/bk_grupo.json`: los dos megatablones
  (17 y 9 MB) partidos por métrica y por óptica (encargo 75), para que las páginas de
  sistema carguen solo el trozo que muestran. Van descritas en el manifiesto con las
  claves `metricas` y `opticas` (filas y bytes).
- `_manifiesto.json` siempre, aunque no haya tablas: el sitio detecta desde ahí qué tablas
  existen (decisión 65b). Por tabla: filas, columnas, rango de fechas, sha256 del parquet
  de origen y bytes del JSON.

Licencias (spec web bancos §9, criterio 17): antes de escribir nada, falla si alguna
columna contiene `px_`, `pbv`, `pe_`, `bbg`, `bloomberg`, `consenso` o `target`.

Uso (desde la raíz del repo, Windows con `-X utf8`):
    python -X utf8 pipeline/exportar_web_bancos.py
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
import shutil
import sys
from pathlib import Path

import pandas as pd

import almacen as A
import bancos as B
import reglas_gold as RG

ORIGEN = A.GOLD
SALIDA = A.RAIZ / "sitio" / "data"

# Auxiliar del verificador (decisión 59): no es parte del contrato del sitio.
# bk_ref: todas las ediciones del Anexo del REF pesan ~81 MB en JSON; cuando una página lo use, se exportan solo
# los gráficos que use (frente 4, 9-nov-2026).
EXCLUIDAS = {"bk_cartera_totales", "bk_ref"}
# Columna que identifica al banco en cada tabla que se parte por banco.
PARTIBLES = {"bk_panel": "cod_inst", "bk_cartera": "cod_inst", "bk_roe_arbol": "entidad"}
# Slug de cada óptica de bk_grupo para nombrar su partición (encargo 75). Si aparece una óptica nueva sin
# slug, se rompe antes de escribir: partir la tabla a medias deja el manifiesto diciendo que la partición es
# la tabla completa.
OPTICAS = B.SLUG_OPTICA


def _valor(v):
    """Convierte un valor del parquet a JSON: fechas ISO, vacíos null, floats sin NaN/Inf."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, (pd.Timestamp, dt.datetime, dt.date)):
        return pd.Timestamp(v).strftime("%Y-%m-%d")
    if isinstance(v, float):
        return None if math.isnan(v) or math.isinf(v) else round(v, 6)
    if hasattr(v, "item"):
        return _valor(v.item())
    return v


def _rango(d: pd.DataFrame) -> list | None:
    """[columna, mínimo, máximo] de la primera columna de fecha que exista (reglas_gold.rango); None si no hay."""
    r = RG.rango(d)
    return None if r is None else [r[0], str(_valor(r[1])), str(_valor(r[2]))]


def _escribir_tabla(ruta: Path, tabla: str, d: pd.DataFrame) -> int:
    """Escribe `ruta` con el formato del spec macro §7.1 y devuelve sus bytes."""
    contenido = {
        "tabla": tabla,
        "columnas": [str(c) for c in d.columns],
        "filas": [[_valor(v) for v in fila] for fila in d.itertuples(index=False, name=None)],
    }
    ruta.write_text(json.dumps(contenido, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return ruta.stat().st_size


def main(argv: list[str] | None = None) -> int:
    parquets = sorted(p for p in ORIGEN.glob("bk_*.parquet") if p.stem not in EXCLUIDAS)
    tablas = {p.stem: pd.read_parquet(p) for p in parquets}

    # Licencias antes de tocar data/: si una sola columna delata dato con licencia, no se
    # escribe nada (criterio 17: mejor no exportar que exportar de más).
    infracciones = sorted(
        (t, c) for t, d in tablas.items() for c in map(str, d.columns)
        if any(marca in c.lower() for marca in RG.LICENCIAS)
    )
    if infracciones:
        for t, c in infracciones:
            print(f"LICENCIA: {t}.{c} contiene una marca de dato con licencia", file=sys.stderr)
        return 1

    # El slug viene de bk_banco y arma una ruta: validar que sea un slug de verdad.
    slugs: dict[str, str] = {}
    if "bk_banco" in tablas:
        for cod, slug in zip(tablas["bk_banco"]["cod_inst"], tablas["bk_banco"]["slug"]):
            if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9-]+", slug):
                raise ValueError(f"bk_banco: slug inválido para {cod}: {slug!r}")
            slugs[cod] = slug
    elif any(t in tablas for t in PARTIBLES):
        print("AVISO: falta bk_banco; no se puede partir por banco", file=sys.stderr)
    # Métricas y ópticas arman rutas de partición, igual que el slug: se validan antes de borrar nada.
    if "bk_panel" in tablas:
        malas = [m for m in tablas["bk_panel"]["metrica"].unique()
                 if not isinstance(m, str) or not re.fullmatch(r"[a-z0-9_]+", m)]
        if malas:
            raise ValueError(f"bk_panel: métricas inválidas para partición: {malas!r}")
    if "bk_grupo" in tablas:
        sin_slug = sorted(set(tablas["bk_grupo"]["optica"]) - set(OPTICAS))
        if sin_slug:
            raise ValueError(f"bk_grupo: ópticas sin slug asignado: {sin_slug!r}")

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir(parents=True, exist_ok=True)

    manifiesto: dict = {"generado": dt.datetime.now().isoformat(timespec="seconds"),
                        "tablas": {}, "bancos": {}, "metricas": {}, "opticas": {}}
    for nombre, d in tablas.items():
        sha256 = A.sha256_archivo(ORIGEN / f"{nombre}.parquet")
        bytes_json = _escribir_tabla(SALIDA / f"{nombre}.json", nombre, d)
        manifiesto["tablas"][nombre] = {
            "filas": len(d), "columnas": [str(c) for c in d.columns],
            "rango": _rango(d), "sha256": sha256, "bytes": bytes_json,
        }
        print(f"{nombre}: {len(d)} filas · {bytes_json / 1e6:.2f} MB")

    for nombre, col_banco in PARTIBLES.items():
        if nombre not in tablas:
            continue
        for cod, g in tablas[nombre].groupby(col_banco, sort=True):
            if cod not in slugs:  # entidades agregadas del árbol del ROE: no son de un banco
                continue
            ruta = SALIDA / "banco" / slugs[cod]
            ruta.mkdir(parents=True, exist_ok=True)
            bytes_json = _escribir_tabla(ruta / f"{nombre}.json", nombre, g)
            manifiesto["bancos"].setdefault(slugs[cod], {})[nombre] = {
                "filas": len(g), "columnas": [str(c) for c in g.columns],
                "rango": _rango(g),
                "sha256": manifiesto["tablas"][nombre]["sha256"], "bytes": bytes_json,
            }

    # Particiones por métrica y por óptica (encargo 75).
    if "bk_panel" in tablas:
        for metrica, g in tablas["bk_panel"].groupby("metrica", sort=True):
            ruta = SALIDA / "metrica" / metrica
            ruta.mkdir(parents=True, exist_ok=True)
            manifiesto["metricas"][metrica] = {
                "filas": len(g),
                "bytes": _escribir_tabla(ruta / "bk_panel.json", "bk_panel", g),
            }

    if "bk_grupo" in tablas:
        for optica, g in tablas["bk_grupo"].groupby("optica", sort=True):
            ruta = SALIDA / "optica" / OPTICAS[optica]
            ruta.mkdir(parents=True, exist_ok=True)
            manifiesto["opticas"][OPTICAS[optica]] = {
                "filas": len(g),
                "bytes": _escribir_tabla(ruta / "bk_grupo.json", "bk_grupo", g),
            }

    (SALIDA / "_manifiesto.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")
    particiones = (sum(len(v) for v in manifiesto["bancos"].values())
                   + len(manifiesto["metricas"]) + len(manifiesto["opticas"]))
    total = sum(f.stat().st_size for f in SALIDA.rglob("*") if f.is_file())
    print(f"manifiesto: {len(manifiesto['tablas'])} tablas · {particiones} particiones · data/ {total / 1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
