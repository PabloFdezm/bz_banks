# bz_banks — Dashboard de bancos de Brasil

Sitio estático (HTML + JS + ECharts) con el sector bancario brasileño: crédito, mora, rentabilidad y ficha por banco.
Datos del BCB (IF.Data, SGS, SCR). Se publica en Cloudflare Pages: https://banks-bz.pages.dev

## Estructura

| Carpeta | Qué hay |
|---|---|
| `pipeline/` | Scripts de Python: descarga (IF.Data, SGS, SCR), cálculo del gold y exportación a JSON |
| `definiciones/` | Universo de bancos, grupos, equivalencias y validaciones (JSON) |
| `sitio/` | La web que se publica. `sitio/data/` lo genera `exportar_web_bancos.py` (no va a git) |
| `herramientas/` | Verificadores: `verificar_f1.py` (sitio en Chromium), `contar_tarjetas.mjs`, `verificar_gold.py` |
| `tests/` | `pytest` |
| `docs/` | Especificaciones, esqueleto de páginas, pendientes y bitácora |
| `spec/` | **Especificación completa del repo** (empezar por `spec/README.md`); `spec/generado/` se regenera con `herramientas/generar_spec.py` |
| `referencias/` | **No va a git ni al sitio.** Reportes de terceros (sell-side) para consulta local |
| `datos/` | **No va a git.** `crudo/` (IF.Data, SCR, SGS), `derivado/`, `intermedio/`, `gold/` (parquets `bk_*`) |

## Uso diario

```powershell
Set-Location "C:\dev\bz_banks"
.\publicar.bat          # publica lo que hay en sitio\
.\publicar.bat datos    # antes recalcula el gold y los JSON (actualizar.bat)
```

`actualizar.bat` corre `pipeline/actualizar.py`: baja las series SGS del catálogo, recalcula cada paso en orden
(ver `spec/03_pipeline_de_datos.md`), arma el manifiesto, corre `pytest` y `verificar_gold --gold` y recién
entonces exporta. `actualizar.bat --sin-red` hace lo mismo sin descargas.

## Trimestral: bajar IF.Data nuevo

```powershell
python -X utf8 pipeline\ifdata.py colectar --desde 201403 --hasta AAAAMM --escopo prudencial --informe 2 --informe 3 --informe 4
python -X utf8 pipeline\ifdata.py colectar --desde 201403 --hasta AAAAMM --escopo prudencial --informe 11 --informe 13
.\publicar.bat datos
```

## Entradas del dashboard macro

Ya no queda ninguna: desde el 8-nov todo se lee de la fuente (SGS, Focus por la API Olinda, IF.Data, SCR.data).

## Instalación (una vez)

```powershell
Set-Location "C:\dev\bz_banks"
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.lock   # versiones exactas que funcionan
.venv\Scripts\python -m playwright install chromium
npx wrangler login
powershell -ExecutionPolicy Bypass -File herramientas\registrar_tarea.ps1   # actualización automática
```

`actualizar.bat` y `publicar.bat` usan `.venv` si existe. `requirements.txt` lleva los rangos mínimos;
`requirements.lock`, las versiones exactas (las mismas que instala el CI de GitHub).

## Reglas del sitio

- Cálculos en Python; el navegador solo filtra y dibuja.
- Cada sección es una lámina (botón Presentar). Gráfico a la izquierda, tabla a la derecha, nunca apilados.
- Tabla estándar: Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m (trimestral: t/t · — · a/a · 4T/4T).
- Nunca gráfico y tabla de la misma serie temporal.
