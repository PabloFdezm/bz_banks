"""Regenera spec/generado/: el inventario automático del repo (tablas gold, métricas, bancos, páginas,
componentes, scripts y definiciones). La parte narrativa de spec/ se escribe a mano; esta se regenera
para que no quede desactualizada.

Uso (desde la raíz del repo):  python -X utf8 herramientas/generar_spec.py
Requiere los parquet de datos/gold (no van a git) y Node para leer la configuración de páginas.
"""
from __future__ import annotations

import argparse
import ast
import functools
import json
import re
import subprocess
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
GOLD = RAIZ / "datos" / "gold"
INTER = RAIZ / "datos" / "intermedio"
SAL = RAIZ / "spec" / "generado"
# Sin fecha: regenerar sin cambios en los datos no produce diferencias.
CAB = "> Generado por `herramientas/generar_spec.py`. No editar a mano: se sobrescribe.\n\n"


def md_celda(v, n=70) -> str:
    s = "" if v is None else str(v)
    s = s.replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def rango(d: pd.DataFrame) -> str:
    for c in ("periodo", "fecha", "trimestre"):
        if c in d.columns and d[c].notna().any():
            v = d[c].dropna().astype(str)
            return f"{c}: {v.min()} → {v.max()}"
    return "—"


def tablas(carpeta: Path, titulo: str) -> str:
    out = [f"## {titulo}\n\nCarpeta `{carpeta.relative_to(RAIZ).as_posix()}/`.\n"]
    for p in sorted(carpeta.glob("*.parquet")):
        d = pd.read_parquet(p)
        out.append(f"### `{p.stem}`\n\n{len(d):,} filas · {d.shape[1]} columnas · {rango(d)} · {p.stat().st_size/1e6:.2f} MB\n")
        out.append("| Columna | Tipo | % nulos | Ejemplo | Valores distintos |\n|---|---|---|---|---|")
        for c in d.columns:
            s = d[c]
            ej = s.dropna().iloc[0] if s.notna().any() else None
            try:
                nu = s.nunique(dropna=True)
            except TypeError:
                nu = "—"
            if s.dtype == object and isinstance(nu, int) and nu <= 12:
                ej = ", ".join(map(str, sorted(s.dropna().astype(str).unique())))
            out.append(f"| `{c}` | {s.dtype} | {s.isna().mean()*100:.0f} | {md_celda(ej, 90)} | {nu} |")
        out.append("")
    return "\n".join(out)


def gold_md() -> None:
    txt = "# Tablas de datos (gold e intermedio)\n\n" + CAB
    txt += ("Unidades: las tasas y ratios van en **fracción** (0,05 = 5 %); los cambios de tasas, en pp cuando la columna lo dice; "
            "los saldos en R$ (IF.Data) o R$ millones (SGS) salvo que la columna diga otra cosa. Ver `spec/04_modelo_de_datos.md`.\n\n")
    txt += tablas(GOLD, "Gold (`datos/gold/`) — lo que exporta el sitio y lee Power BI") + "\n"
    txt += tablas(INTER, "Intermedio (`datos/intermedio/`) — entradas del gold")
    (SAL / "tablas.md").write_text(txt, encoding="utf-8")


def metricas_md() -> None:
    m = pd.read_parquet(GOLD / "bk_metrica.parquet").sort_values("orden")
    out = ["# Catálogo de métricas (`bk_metrica`)\n", CAB,
           f"{len(m)} métricas. `signo`: mejora_sube / mejora_baja / neutro (colorea cambios). `universo`: panel o sistema.\n",
           "| # | metrica | Nombre | Familia | Unidad | Formato | Signo | Fuente | Definición |", "|---|---|---|---|---|---|---|---|---|"]
    for _, r in m.iterrows():
        out.append(f"| {r.orden} | `{r.metrica}` | {md_celda(r.nombre, 50)} | {r.familia} | {r.unidad} | {r.formato} | {r.signo} | "
                   f"{md_celda(r.fuente, 40)} | {md_celda(r.definicion, 300)} |")
    (SAL / "metricas.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def bancos_md() -> None:
    b = pd.read_parquet(GOLD / "bk_banco.parquet")
    cols = ["cod_inst", "slug", "nombre_corto", "modelo", "segmento_reg", "propiedad", "fintech", "cotizado", "ticker", "ficha", "primer_periodo", "ultimo_periodo", "nota"]
    cols = [c for c in cols if c in b.columns]
    out = ["# Universo de bancos (`bk_banco`)\n", CAB, f"{len(b)} bancos. Fuente de verdad: `definiciones/bcb_ifdata__bancos_balances.json` y `definiciones/bancos__dashboard.json`.\n",
           "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in b.sort_values(["modelo", "nombre_corto"]).iterrows():
        out.append("| " + " | ".join(md_celda(r[c], 60) for c in cols) + " |")
    (SAL / "bancos.md").write_text("\n".join(out) + "\n", encoding="utf-8")


@functools.lru_cache(maxsize=1)
def inventario_sitio() -> dict:
    """Configs de página y registro de componentes, cargados por herramientas/inventario_paginas.mjs (una sola vez)."""
    r = subprocess.run(["node", str(RAIZ / "herramientas" / "inventario_paginas.mjs")], capture_output=True, text=True, check=True, encoding="utf-8")
    return json.loads(r.stdout)


def paginas_md() -> None:
    inv = inventario_sitio()
    out = ["# Páginas, secciones y tarjetas del sitio\n", CAB,
           f"Datos en `{inv['RUTA_DATOS']}` (relativo a `sitio/`). Páginas con `oculta: true` no salen en el menú pero se abren por URL.\n"]
    for p in inv["paginas"]:
        out.append(f"## {p['clave']} · {p['nombre']} — `/{p['ruta']}`{' (oculta)' if p.get('oculta') else ''}\n")
        out.append(f"Archivo: `{p.get('archivo')}` · rótulo: {p.get('rotulo')} · usaBanco: {p.get('usaBanco')}"
                   f"{' · titular por banco' if p.get('titularPorBanco') else ''}\n")
        if p.get("franja"):
            out.append("**Franja de indicadores (arriba):** " + "; ".join(f"{k['rotulo']} ← `{k['tabla']}`{' (banco)' if k['banco'] else ''}" for k in p["franja"]) + "\n")
        for s in p.get("secciones", []):
            out.append(f"### {s['numero']} {s['nombre']} · {s.get('frecuencia') or ''}\n\n{s.get('pregunta') or ''}\n")
            for sel in s["selectores"]:
                out.append(f"- Selector `{sel['clave']}` ({sel['rotulo']}): {' / '.join(sel['opciones'])}; por defecto `{sel['defecto']}`")
            for i, f in enumerate(s["filas"], 1):
                out.append(f"- Fila {i}: " + " + ".join(f"`{c['clave']}` (ancho {c['ancho']}/9, alto {c['alto']})" for c in f))
            out.append("")
        if p.get("tarjetas"):
            out.append("| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |\n|---|---|---|---|---|---|---|")
            for k, t in p["tarjetas"].items():
                out.append(f"| `{k}` | {md_celda(t.get('titulo'), 60)} | `{t.get('componente')}` | {', '.join(f'`{x}`' for x in (t.get('datos') or []))} | "
                           f"{t.get('estado')} | {'sí' if t.get('banco') else ''} | {md_celda(t.get('fuente'), 60)} |")
            notas = [(k, t["nota"]) for k, t in p["tarjetas"].items() if t.get("nota")]
            if notas:
                out.append("\nNotas visibles en las tarjetas:\n")
                out += [f"- `{k}`: {md_celda(n, 400)}" for k, n in notas]
        out.append("")
    (SAL / "paginas.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def componentes_md() -> None:
    inv = inventario_sitio()
    out = ["# Componentes de dibujo\n", CAB,
           "Registro único `COMPONENTES` (charts_bancos.js; los generales vienen de charts.js). Cada tarjeta declara "
           "`componente` y `armar()` puede elegir otro según la vista; `pagina.js` llama `dibujar(contenedor, entrada, { titulo })`, "
           "donde `entrada` es lo que devolvió `armar()`. Si devuelve una instancia de ECharts, la zona lleva role=img y un "
           "ResizeObserver; si devuelve null, dibujó HTML. La lista de claves de entrada la declara cada componente.\n"]
    for c in inv["componentes"]:
        out.append(f"- **`{c['nombre']}`** — {md_celda(c['descripcion'], 400)}  \n"
                   f"  Entrada (`e.*`): {', '.join(f'`{x}`' for x in c['entrada']) or '—'}")
    out.append("")
    (SAL / "componentes.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def scripts_md() -> None:
    out = ["# Scripts del pipeline (docstring completo y argumentos)\n", CAB]
    for p in sorted((RAIZ / "pipeline").glob("*.py")) + sorted((RAIZ / "herramientas").glob("*.py")):
        src = p.read_text(encoding="utf-8")
        t = ast.parse(src)
        doc = ast.get_docstring(t) or "(sin docstring)"
        imps = sorted({(n.module if isinstance(n, ast.ImportFrom) else a.name).split(".")[0]
                       for n in ast.walk(t) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in (n.names if isinstance(n, ast.Import) else [n]) if (n.module if isinstance(n, ast.ImportFrom) else a.name)})
        locales = [i for i in imps if (RAIZ / "pipeline" / f"{i}.py").exists()]
        args = re.findall(r"add_argument\(\s*\"([^\"]+)\"[^)]*?help=\"([^\"]+)\"", src)
        subs = re.findall(r"add_parser\(\s*\"([^\"]+)\"[^)]*?help=\"([^\"]+)\"", src)
        out.append(f"## `{p.relative_to(RAIZ).as_posix()}` ({src.count(chr(10))} líneas)\n")
        if locales:
            out.append("Importa del pipeline: " + ", ".join(f"`{i}`" for i in locales) + "\n")
        if subs:
            out.append("Subcomandos: " + "; ".join(f"`{a}` — {h}" for a, h in subs) + "\n")
        if args:
            out.append("Argumentos: " + "; ".join(f"`{a}` — {h}" for a, h in args) + "\n")
        out.append("```text\n" + doc.strip() + "\n```\n")
    (SAL / "scripts.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def definiciones_md() -> None:
    out = ["# Archivos de `definiciones/`\n", CAB]
    for p in sorted((RAIZ / "definiciones").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        out.append(f"## `{p.name}` ({p.stat().st_size/1e3:.0f} kB)\n")
        if isinstance(d, dict):
            for k, v in d.items():
                desc = f"lista de {len(v)}" if isinstance(v, list) else (f"objeto con {len(v)} claves" if isinstance(v, dict) else md_celda(v, 160))
                ej = ""
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    ej = " · campos: " + ", ".join(f"`{c}`" for c in list(v[0])[:14])
                out.append(f"- `{k}`: {desc}{ej}")
        out.append("")
    (SAL / "definiciones.md").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    SAL.mkdir(parents=True, exist_ok=True)
    for f in (gold_md, metricas_md, bancos_md, paginas_md, componentes_md, scripts_md, definiciones_md):
        f()
        print("ok", f.__name__)
