# 02 · Arquitectura

## Flujo de punta a punta

```
BCB (fuentes públicas)                     pipeline/ (Python)                                  sitio/ (estático)
──────────────────────                     ──────────────────                                  ─────────────────
IF.Data  OLinda/OData ──ifdata.py colectar (a mano)──▶ datos/crudo/bcb_ifdata/  (parquet + manifiesto)
SGS      api.bcb.gov.br ──sgs.py (catálogo CODIGOS)──▶ datos/crudo/bcb_sgs/bancos_sistema/  (JSON por serie)
SCR.data ZIP anuales ──scr_zip.py────────────────────▶ datos/crudo/bcb_scr/scrdata/  (ZIP)
                                         │
                                         ▼  pipeline/actualizar.py (pasos en orden; cada uno en su proceso)
   sgs → balances → metricas → credito → sistema → cartera → base → rentabilidad → exposicion → qcambio
   → portada → pag_credito → scr_productos → scr → manifiesto → verificacion → exportar
                                         │
           datos/gold/bank_*.parquet, datos/intermedio/*, datos/gold/bk_*.parquet (+ bk_manifiesto)
                                         │
                     exportar_web_bancos ──────▶ sitio/data/*.json  (+ particiones por banco, métrica y óptica)
                                                                                        │
                                                         publicar.bat (robocopy + wrangler pages deploy)
                                                                                        ▼
                                                                        https://banks-bz.pages.dev
```

El detalle de cada paso (qué lee, qué escribe, si usa red) está en `03_pipeline_de_datos.md`; la lista de
pasos es `PASOS` en `pipeline/actualizar.py`.

## Decisiones y por qué

- **Sitio estático, sin build ni framework.** HTML + módulos ES nativos + ECharts vendorizado
  (`sitio/assets/vendor/echarts.min.js`, render SVG). Se abre con cualquier servidor estático y se despliega
  copiando la carpeta. No hay npm en el sitio.
- **Configuración declarativa por página.** Cada página es un objeto en `sitio/assets/js/paginas/bN.js`
  (secciones, filas, tarjetas). Un único motor, `pagina.js`, la monta. Las configs solo importan módulos sin
  DOM (`comun.js`, `tokens.js`, `paginas/_series.js`): así `herramientas/inventario_paginas.mjs` las carga con
  `import()` en Node (`--sin-dom` lo comprueba) para `contar_tarjetas.mjs`, `verificar_f1.py` y `generar_spec.py`.
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
  agregan `pipeline/` al path en `tests/conftest.py`. La raíz del repo y las carpetas de datos las define
  `almacen.py` (`RAIZ`, `GOLD`, `INTERMEDIO`, `DEFINICIONES`); el resto las importa de ahí.
- **Datos fuera de git.** `datos/` (≈2 GB, sobre todo ZIP del SCR.data; IF.Data va en parquet) y `sitio/data/` están en
  `.gitignore`. El repo guarda código y definiciones; los datos viven en el equipo (`C:\dev\bz_banks\datos`, fuera de OneDrive desde el 8-nov).
- **Cloudflare Pages** publica `sitio/` tal cual (desde el 6-nov; antes Netlify). `publicar.bat` arma `deploy_web/`
  con `robocopy /MIR` (los encabezados HTTP van en `sitio/_headers`) y corre `wrangler pages deploy deploy_web --project-name banks-bz --branch main`.
  Cabeceras `no-cache` en `/assets/*` y `/data/*` para que un deploy se vea sin limpiar caché.

## Tecnologías

| Capa | Herramienta |
|---|---|
| Datos | Python 3.10+ (se usa 3.14 en Windows), pandas, numpy, pyarrow, requests, truststore |
| Gráficos | ECharts 5 (SVG) + componentes HTML propios |
| Verificación del sitio | Playwright + Chromium (`herramientas/verificar_f1.py`), Node (`contar_tarjetas.mjs`) |
| Tests | pytest |
| Publicación | Cloudflare Pages (wrangler vía npx) |
| Entorno | Windows 11, PowerShell, Python 3.14 en `.venv` (`requirements.lock`); repo fuera de OneDrive; red corporativa con proxy HTTPS (ver `pipeline/certificados.py`) |

## Origen

El repo nació dentro de un proyecto más grande (`Dashboard`, que también tiene un dashboard macro de Brasil
en Power BI) y se separó el 4-nov-2026. Por eso algunos nombres conservan el sufijo `_powerbi` y algunas
tablas intermedias vienen de ese proyecto (ver `03_pipeline_de_datos.md`, «Entradas congeladas»). La capa
gold también la lee un Power BI (PBIP) que sigue en el repo original.
