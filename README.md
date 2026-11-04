# bz_banks — Dashboard de bancos de Brasil

Sitio estático (HTML + JS + ECharts) con el sector bancario brasileño: crédito, mora, rentabilidad y ficha por banco.
Datos del BCB (IF.Data, SGS, SCR). Se publica en Netlify: https://banks-bz.netlify.app

## Estructura

| Carpeta | Qué hay |
|---|---|
| `pipeline/` | Scripts de Python: descarga (IF.Data, SGS, SCR), cálculo del gold y exportación a JSON |
| `definiciones/` | Universo de bancos, grupos, equivalencias y validaciones (JSON) |
| `sitio/` | La web que se publica. `sitio/data/` lo genera `exportar_web_bancos.py` (no va a git) |
| `herramientas/` | Verificadores: `verificar_f1.py` (sitio en Chromium), `contar_tarjetas.mjs`, `verificar_gold.py` |
| `tests/` | `pytest` |
| `docs/` | Especificaciones, esqueleto de páginas, pendientes y bitácora |
| `datos/` | **No va a git.** `crudo/` (IF.Data, SCR, SGS), `derivado/`, `intermedio/`, `gold/` (parquets `bk_*`) |

## Uso diario

```powershell
Set-Location "C:\Users\pablo\OneDrive\Documentos\bz_banks"
.\publicar.bat          # publica lo que hay en sitio\
.\publicar.bat datos    # antes recalcula el gold y los JSON (actualizar.bat)
```

`actualizar.bat` corre, en orden: `preparar_bancos_powerbi` → `preparar_metricas_bancos` →
`preparar_credito_paginas_powerbi --descargar` → `preparar_gold_bancos todo` → `_qcambio` → `_portada` →
`_pag_credito` → `exportar_web_bancos`. Las series SGS que falten se bajan solas.

## Trimestral: bajar IF.Data nuevo

```powershell
python -X utf8 pipeline\ifdata.py colectar --desde 201403 --hasta AAAAMM --escopo prudencial --informe 2 --informe 3 --informe 4
python -X utf8 pipeline\ifdata.py colectar --desde 201403 --hasta AAAAMM --escopo prudencial --informe 11 --informe 13
.\publicar.bat datos
```

## Entradas que vienen del dashboard macro (congeladas)

`preparar_gold_bancos_sistema.py` lee cuatro tablas que construye el dashboard macro y que se copiaron a
`datos/intermedio/` el 4-nov-2026: `fh_deuda` (SGS 29034 y 29037), `tasa_real_exante`, `tasas_pnad` (desocupación,
PNAD) y `expectativas_focus`. **No se actualizan desde aquí.** Pendiente: leer las tres del SGS directamente y
dejar solo la desocupación como entrada externa.

## Instalación (una vez)

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
npm install -g netlify-cli
netlify login
```

## Reglas del sitio

- Cálculos en Python; el navegador solo filtra y dibuja.
- Cada sección es una lámina (botón Presentar). Gráfico a la izquierda, tabla a la derecha, nunca apilados.
- Tabla estándar: Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m (trimestral: t/t · — · a/a · 4T/4T).
- Nunca gráfico y tabla de la misma serie temporal.
