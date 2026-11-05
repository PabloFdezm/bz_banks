# 02 · Arquitectura

## Flujo de punta a punta

```
BCB (fuentes públicas)                     pipeline/ (Python)                                  sitio/ (estático)
──────────────────────                     ──────────────────                                  ─────────────────
IF.Data  OLinda/OData ──ifdata.py──▶ datos/crudo/bcb_ifdata/  (CSV + manifiesto)
SGS      api.bcb.gov.br ──(sgs())──▶ datos/crudo/bcb_sgs/     (JSON por serie)
SCR.data ZIP anuales ──_scr.py────▶ datos/crudo/bcb_scr/      (ZIP)
                                         │
                                         ▼
                     preparar_bancos_powerbi ──▶ datos/gold/bank_*.parquet  (balances y resultados por banco)
                     preparar_metricas_bancos ─▶ datos/intermedio/metricas_bancos.parquet (TTM, ROE, ROA, cuotas…)
                     preparar_credito_paginas ─▶ datos/intermedio/cre_*.parquet (crédito por grupo y modalidad)
                     preparar_gold_bancos todo ▶ datos/gold/bk_*.parquet  (sistema, cartera, base, rentabilidad, exposición)
                     _qcambio / _portada / _pag_credito ▶ más bk_*
                     preparar_gold_bancos base ▶ bk_manifiesto al día
                                         │
                     exportar_web_bancos ──────▶ sitio/data/*.json  (+ particiones por banco, métrica y óptica)
                                                                                        │
                                                         publicar.bat (robocopy + netlify deploy --prod)
                                                                                        ▼
                                                                        https://banks-bz.netlify.app
```

## Decisiones y por qué

- **Sitio estático, sin build ni framework.** HTML + módulos ES nativos + ECharts vendorizado
  (`sitio/assets/vendor/echarts.min.js`, render SVG). Se abre con cualquier servidor estático y se despliega
  copiando la carpeta. No hay npm en el sitio.
- **Configuración declarativa por página.** Cada página es un objeto en `sitio/assets/js/paginas/bN.js`
  (secciones, filas, tarjetas). Un único motor, `pagina.js`, la monta. Las configs **no importan nada**: así
  `herramientas/contar_tarjetas.mjs` y `inventario_paginas.mjs` pueden leerlas sin el resto del sitio.
- **Los datos llegan como JSON tabular** `{tabla, columnas, filas}` (filas = arrays). `datos.js` los
  convierte en objetos y los cachea por sesión.
- **Particiones para rendimiento.** Las tablas grandes se exportan también partidas:
  `banco/<slug>/<tabla>.json` (bk_panel, bk_cartera, bk_roe_arbol), `metrica/<metrica>/bk_panel.json` y
  `optica/<slug>/bk_grupo.json`. Las tarjetas deben pedir la partición, no la tabla completa
  (bk_panel pesa 27 MB y bk_grupo 12 MB).
- **Almacén con procedencia** (`pipeline/almacen.py`): crudo (lo que sirvió la fuente) separado de derivado
  (lo que produce el código), ambos con `_manifiesto.json` (URL, sha256, fecha, entradas y comando).
- **Pipeline sin paquete Python.** Los módulos de `pipeline/` se importan por nombre (`import almacen as A`).
  Funciona porque Python pone la carpeta del script en `sys.path` al correr `python pipeline/x.py`. Los tests
  agregan `pipeline/` al path en `tests/conftest.py`. Cada módulo calcula la raíz del repo como
  `Path(__file__).resolve().parents[1]`.
- **Datos fuera de git.** `datos/` (≈6 GB, sobre todo CSV de IF.Data y ZIP de SCR) y `sitio/data/` están en
  `.gitignore`. El repo guarda código y definiciones; los datos viven en el equipo (carpeta en OneDrive).
- **Netlify** publica `sitio/` tal cual. `publicar.bat` arma `deploy_netlify/` con `robocopy /MIR` (sin
  `_prueba` ni `.netlify`) y corre `netlify deploy --prod --site 992a0e15-6b15-45ea-bc43-ddafa60032b4`.
  Cabeceras `no-cache` en `/assets/*` y `/data/*` para que un deploy se vea sin limpiar caché.

## Tecnologías

| Capa | Herramienta |
|---|---|
| Datos | Python 3.10+ (se usa 3.14 en Windows), pandas, numpy, pyarrow, requests, truststore |
| Gráficos | ECharts 5 (SVG) + componentes HTML propios |
| Verificación del sitio | Playwright + Chromium (`herramientas/verificar_f1.py`), Node (`contar_tarjetas.mjs`) |
| Tests | pytest |
| Publicación | Netlify CLI |
| Entorno | Windows 11, PowerShell, OneDrive; red corporativa con proxy HTTPS (ver `pipeline/certificados.py`) |

## Origen

El repo nació dentro de un proyecto más grande (`Dashboard`, que también tiene un dashboard macro de Brasil
en Power BI) y se separó el 4-nov-2026. Por eso algunos nombres conservan el sufijo `_powerbi` y algunas
tablas intermedias vienen de ese proyecto (ver `03_pipeline_de_datos.md`, «Entradas congeladas»). La capa
gold también la lee un Power BI (PBIP) que sigue en el repo original.
