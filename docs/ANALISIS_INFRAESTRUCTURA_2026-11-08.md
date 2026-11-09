# Análisis de infraestructura · bz_banks

**Fecha:** 8-nov-2026 · **Propósito:** documento de lectura para que otra LLM (o un revisor humano) entienda
la arquitectura del repo sin recorrerlo entero. **Alcance:** backend (pipeline de datos en Python) y frontend
(sitio estático). No cubre metodología de negocio salvo donde afecta a la infraestructura.

**Fuentes de este análisis:** `spec/02_arquitectura.md`, `spec/03_pipeline_de_datos.md`,
`spec/08_estado_pendientes_y_riesgos.md`, `docs/PENDIENTES.md`, `README.md`, `CLAUDE.md`, inspección directa
del árbol de archivos y ejecución de `pytest` el 8-nov-2026.

---

## 1. Qué es

Sitio estático (HTML + módulos ES nativos + ECharts, sin build ni framework) con el sector bancario
brasileño, publicado en Cloudflare Pages (`https://banks-bz.pages.dev`). Los datos salen de fuentes
públicas del BCB (IF.Data, SGS, SCR.data, Focus) procesadas por un pipeline de Python que corre **manual**
en el equipo del dueño (Windows 11, `.venv` con `requirements.lock`). No hay servidor de aplicación:
el backend termina en archivos JSON dentro de `sitio/data/`.

```
BCB ──▶ pipeline/ (Python, local, manual) ──▶ datos/gold/*.parquet ──▶ exportador ──▶ sitio/data/*.json
                                                                                          │
                                                              publicar.bat (robocopy + wrangler pages deploy)
                                                                                          ▼
                                                                            Cloudflare Pages (estático)
```

## 2. Backend: el pipeline (`pipeline/`, ~7.600 líneas en 33 módulos)

### 2.1 Estructura y convención de módulos

- **No es un paquete Python.** Los módulos se importan por nombre (`import almacen as A`) porque Python
  pone la carpeta del script en `sys.path` al ejecutar `python pipeline/x.py`. Los tests agregan
  `pipeline/` al path en `tests/conftest.py`. Funciona, pero es frágil: cualquier herramienta que importe
  desde otra raíz (IDE, linter, otro runner) tiene que replicar ese truco.
- **Dueño de rutas único:** `almacen.py` define `RAIZ`, `GOLD`, `INTERMEDIO`, `DEFINICIONES` y todas las
  rutas de crudo; el resto de los módulos las importa de ahí. Buena centralización.
- **Orquestador:** `actualizar.py` corre los 17 pasos en orden, cada uno como `main(argv) -> int` de un
  módulo; si uno devuelve ≠ 0 la corrida se corta y no se exporta. `--sin-red` (CI/local sin descargas),
  `--desde/--hasta`, `--sin-verificacion`.

### 2.2 Cadena de pasos

`sgs → balances → metricas → credito → sistema → cartera → base → rentabilidad → exposicion → qcambio →
portada → pag_credito → scr_productos → scr → manifiesto → verificacion → exportar`

(detalle paso a paso en `spec/03_pipeline_de_datos.md`; la lista viva es `PASOS` en `actualizar.py`).

Solo dos pasos usan red: `sgs` (refresco de series) y `scr_productos` (baja el ZIP del año). IF.Data se
baja aparte, a mano y trimestral (`ifdata.py colectar …`). Los pasos `sistema`, `cartera` y `scr`
verifican antes de publicar: si la verificación falla, no escriben nada (fail-closed).

### 2.3 Capas de datos y procedencia

```
datos/crudo/<fuente>/<dataset>/<version>/   lo que sirvió la fuente; no se edita
datos/derivado/<fuente>/<dataset>/          salida del código, con manifiesto de entradas y comando
datos/intermedio/                           tablas intermedias (métricas por banco, cre_*)
datos/gold/                                 capa de publicación: bk_*.parquet + bank_* + bk_manifiesto
```

- `almacen.py` escribe todo de forma **atómica** (temporal + rename) y deja `_manifiesto.json` con URL,
  sha256, fecha, entradas y comando en cada capa. `publicar_gold()` valida contra
  `definiciones/contrato_gold.json` antes de escribir. Los sha256 se recomprueban con
  `verificar_gold.py`. Es un diseño de almacén serio para ser un repo personal.
- **Crudo en parquet sin pérdida:** IF.Data baja como CSV de la API OLinda y se recodifica de inmediato a
  parquet (todas las columnas texto, verificación celda por celda contra el CSV, luego se borra el CSV).
  3,5 GB → 62 MB. El código sigue nombrando los crudos `.csv` y un lector transparente
  (`leer_crudo_tabla`, `glob_crudo`) resuelve parquet-si-existe. Buen patrón de migración.
- `datos/` (≈2,1 GB, sobre todo ZIP de SCR.data) y `sitio/data/` (≈119 MB) están fuera de git. El repo
  versiona código y definiciones; los datos viven solo en el equipo.

### 2.4 Módulos compartidos (los que hacen de "librería")

`bancos.py` (universo y membresía de grupos, única regla de qué banco va en qué grupo), `periodos.py`
(aritmética de trimestres, quiebres, regla de variación publicable), `registro_metricas.py` (lee
`definiciones/metricas_bancos.json`: códigos COSIF, TTM, razones), `sgs.py` (catálogo `CODIGOS`, único
lector del SGS, CDI y deflactor), `ifdata_credito.py`, `mora_sistema.py`, `tabla_estandar.py`,
`scr_zip.py`, `red.py` (única política de reintentos y modo sin red), `reglas_gold.py` (tolerancias
compartidas por preparadores, exportador y verificador), `manifiesto_gold.py`.

### 2.5 Las trampas de datos que la infraestructura tiene que respetar

(documentadas en `spec/08`; cualquier revisor debe leerlas antes de juzgar cálculos)

- **Frontera COSIF 2025-03:** el BCB renumeró cuentas y movió informes de crédito del escopo financiero
  al prudencial. Los bancos con cambio de cobertura llevan `quiebre_2025 = true` y sus variaciones que
  cruzan 2025-T1 quedan vacías; además los crecimientos a/a de saldos de balance se vacían en 2025 para
  todo el panel (cambio de definición, no solo de cobertura).
- **2024-T4 anómalo** en IF.Data: vacío a propósito (`trimestres_anomalos`).
- **Res. 4.966 (2025):** cambia la medida de activos problemáticos; las series se leen con banda de quiebre.
- **Resultados acumulados con reseteo en julio** (Lei 4.595): se des-acumulan antes de calcular TTM.
- **Mora:** panel IF.Data = ≥ 15 días; SGS = > 90 días. No comparables en nivel.
- **API del SGS:** una serie inexistente no da 404 (devuelve HTML con 200 o 502). `bcb_api.py` lo maneja.
- **SCR.data:** CSV UTF-8 con BOM (no cp1252); `carteira_inadimplencia` en R$, no %.
- **Red corporativa:** proxy HTTPS que re-firma certificados; `certificados.py` usa `truststore`.

## 3. Frontend: el sitio (`sitio/`, ~4.500 líneas de JS propio)

### 3.1 Decisiones estructurales

- **Sin build, sin npm, sin framework.** HTML + módulos ES nativos + ECharts 5 vendorizado
  (`assets/vendor/echarts.min.js`, render SVG). Se despliega copiando la carpeta.
- **Un motor, configuraciones declarativas.** Cada página es un objeto JS en `assets/js/paginas/bN.js`
  (secciones, filas, tarjetas); `pagina.js` (542 líneas) la monta. Las configs solo importan módulos sin
  DOM, lo que permite cargarlas con `import()` en Node para verificación estática
  (`inventario_paginas.mjs`, `contar_tarjetas.mjs`, `generar_spec.py`) — truco inteligente que hace
  testeable la config sin navegador.
- **Componentes propios:** `charts_bancos.js` (763 líneas) concentra las piezas (barras_linea,
  tabla_estandar, mapa_cuotas, cascada, mix_banco…); `charts.js` las base. Gráficos además mezclan SVG
  propio y ECharts (deuda admitida en `docs/PENDIENTES.md`, revisión 76).
- **Estado en la URL** (`url.js`, `estado.js`): banco activo, selectores y modo Presentar viajan en la
  URL (compartible, sin servidor).
- **Presentar:** cada sección es una lámina 16:9 con posiciones idénticas entre páginas
  (`presentacion.js`, 331 líneas); impresión 1920×1080.

### 3.2 Datos en el front

- Contrato único: JSON tabular `{tabla, columnas, filas}` (filas = arrays). `datos.js` los convierte a
  objetos y cachea por sesión. Regla de oro del repo: **cálculos en Python; el navegador solo filtra y
  dibuja.**
- **Particiones para rendimiento:** `bk_panel` pesa ~27 MB y `bk_grupo` ~12 MB completos; se exportan
  partidos por banco (`data/banco/<slug>/…`), por métrica y por óptica. Las tarjetas deben pedir la
  partición (las páginas que cargaban tablas completas eran lentas; la carga inicial de la Portada bajó
  de 10,9 MB a 4,0 MB tras la ola 78e).
- `data/_manifiesto.json` declara qué tablas existen; el sitio lee de ahí (transición desde el
  `TABLAS_EXPORTADAS` hardcodeado de `config.js`, retirable cuando el exportador B7 quede completo).

### 3.3 CSS

Tres capas: `tokens.css` (toda la paleta y escala tipográfica; fuente de verdad de colores, espejada en
`comun.js` para ECharts y verificada por `verificar_f1.py`), `monitor.css` (maqueta base heredada del
proyecto macro) y `bancos.css` (38 KB, la piel FARO v2/v3 que pisa a la base). **Deuda conocida:** ~10
selectores tienen más de una regla entre los dos archivos; fusionarlos cruza especificidad
(documentado en `spec/08` — al tocar uno, buscar el selector en ambos).

## 4. Verificación y calidad

| Capa | Herramienta | Qué exige |
|---|---|---|
| Unitarias/contratos | `pytest` (128 tests) | códigos, definiciones, contratos gold, sitio sin DOM |
| Datos gold | `herramientas/verificar_gold.py --gold` | sha256, rangos, tolerancias de `reglas_gold.py` |
| Sitio publicado | `herramientas/verificar_f1.py` (Playwright + Chromium) | 0 errores de consola, conteos de tarjetas del esqueleto, render en 3 anchos (1920/1280/390) |
| Config de páginas | `contar_tarjetas.mjs`, `inventario_paginas.mjs` (Node, sin DOM) | las configs cargan y cuentan bien |
| Spec autogenerada | `generar_spec.py` | documentación derivada del código |

- **CI:** GitHub Actions (`.github/workflows/tests.yml`) corre pytest en cada push/PR sobre Python 3.14 en
  Ubuntu, instalando `requirements.lock` menos playwright (con un `grep -v`). Los tests de datos
  (`integracion`) se omiten solos en CI porque `datos/` no va a git.
- **Estado real al 8-nov:** 123 pasan, 2 fallan, 5 dan error — todos los fallos/errores son de tests que
  invocan `node` (herramientas `.mjs`) y no lo encuentran en el PATH del proceso en este entorno; no hay
  fallos de lógica ni de datos. Riesgo operativo menor: la suite completa solo corre limpia donde node
  está en PATH para el proceso de Python.
- **Regla de integración aprendida (documentada):** después de correr cualquier subcomando suelto del
  pipeline hay que correr `base` (o `todo`), porque el sha256 del manifiesto se invalida — ya hubo un
  incidente por esto (PENDIENTES, revisión 71).

## 5. Operación y despliegue

- **Actualización de datos: manual.** Decisión del dueño (8-nov): sin tarea programada ni modo auto.
  `actualizar.bat` corre el pipeline completo (descarga SGS, pasos en orden, manifiesto, pytest,
  verificador gold, exportación); `--sin-red` sin descargas. IF.Data se baja aparte cada trimestre.
- **Publicación:** `publicar.bat` arma `deploy_web/` con `robocopy /MIR` y despliega con
  `wrangler pages deploy --project-name banks-bz --branch main`. Cabeceras `no-cache` en `/assets/*` y
  `/data/*` (vía `sitio/_headers`) para que un deploy se vea sin limpiar caché. Requiere
  `npx wrangler login` una vez — credencial interactiva, no automatizable.
- Migrado de Netlify a Cloudflare Pages el 6-nov; sitios de Netlify borrados.

## 6. Riesgos y deuda técnica (ordenados por impacto)

1. **La línea IF.Data depende de un servicio inestable.** La API OLinda de IF.Data tuvo caídas largas
   (HTTP 500 incluso en combinaciones existentes) y el portal REST tiene IDs no estables; los informes
   5, 7, 9, 10, 12 y 14 quedaron en pausa (PENDIENTES, 60b/60c). `bk_capital` puede tener que arrancar en
   2020-12. Es el mayor riesgo de continuidad de datos.
2. **Acoplamiento con el repo hermano `Dashboard`:** nombres `_powerbi`, tablas intermedias del macro
   (ya ninguna en uso, pero quedan archivos muertos en `datos/intermedio/`) y, sobre todo, **un Power BI
   (PBIP) del repo original lee la misma capa gold** — romper el contrato gold rompe ese consumidor
   invisible desde este repo.
3. **Pipeline sin paquete y sin tipado de contratos en runtime** más allá de `contrato_gold.json`:
   los imports por `sys.path` y los nombres de columnas acordados por convención hacen que el sistema
   dependa fuertemente de pytest + verificadores para detectar regresiones.
4. **Datos solo en un equipo:** `datos/` (2,1 GB) no está en git ni en backup visible; la recreación
   completa depende de que el BCB siga sirviendo historia (no garantizado, ver punto 1). Limpiezas
   manuales pendientes: `datos/derivado/bcb_ifdata/valores/` (149 MB de CSV sin uso), `bk_conducta.parquet`
   (borrable tras cancelar reclamos), carpeta vieja en OneDrive.
5. **Deuda CSS:** duplicación monitor/bancos (~10 selectores), y `tokens.css` importa Google Fonts remoto
   aunque el kit de diseño trae las OFL locales — dependencia de red innecesaria y contradicción con la
   regla del propio kit.
6. **Entorno de verificación no hermético:** los tests de sitio necesitan `node` en PATH del proceso
   (fallan en este entorno, ver §4); `verificar_f1` necesita Chromium de Playwright y fuentes reales
   (capturas sin red no detectan cortes de texto).
7. **Series SGS identificadas por cuadre de montos:** los nombres de modalidades/concesiones del catálogo
   `CODIGOS` aún no están validados contra el catálogo oficial del SGS (pendiente 5 de spec/08).
8. **Frente de rediseño abierto:** la carpeta `diseno/` (kit importado de Monitor Brasil, ~9 documentos +
   assets) está sin commitear y sin decisión de si entra a git; su `DESIGN.md` habla de otro producto
   (`--mb-*`, tarjetas AM*) y puede inducir a error a un revisor que la tome por verdad vigente. La verdad
   viva del diseño es `sitio/assets/css/tokens.css`.

## 7. Guía de lectura para el revisor

1. `spec/README.md` → `spec/02_arquitectura.md` → `spec/03_pipeline_de_datos.md` (el flujo de datos).
2. `spec/08_estado_pendientes_y_riesgos.md` (trampas de datos — imprescindible antes de juzgar cálculos).
3. `pipeline/almacen.py` y `definiciones/contrato_gold.json` (el corazón del almacén).
4. `pipeline/actualizar.py` (orquestación) y un preparador representativo (`preparar_gold_bancos.py`).
5. Front: `sitio/assets/js/pagina.js` (motor), una config (`paginas/b0.js`), `charts_bancos.js`,
   `datos.js`, `tokens.css`.
6. `docs/PENDIENTES.md` (bitácora de decisiones del arquitecto — la historia del porqué).
7. `tareas/README.md` (frentes abiertos y decisiones que esperan al dueño).

## 8. Ficha técnica rápida

| Dimensión | Valor |
|---|---|
| Backend | Python 3.14 (3.10+ soportado), pandas ≥ 2.1, numpy, pyarrow, requests, truststore |
| Frontend | HTML + ES modules, ECharts 5 vendorizado (SVG), sin build |
| Tamaño código | pipeline ~7.600 líneas (33 módulos) · sitio ~4.500 líneas JS propio |
| Datos locales | `datos/` ≈ 2,1 GB · `sitio/data/` ≈ 119 MB (ambos fuera de git) |
| Tests | 128 (123 OK · 2 failed · 5 errors por `node` fuera de PATH — 8-nov) |
| CI | GitHub Actions, pytest en push/PR, ubuntu-latest + Python 3.14 |
| Deploy | Cloudflare Pages vía wrangler (manual), headers `no-cache` en assets y data |
| Actualización de datos | Manual (`actualizar.bat`), IF.Data trimestral aparte |
| Entorno | Windows 11, PowerShell, repo fuera de OneDrive, proxy HTTPS corporativo |
