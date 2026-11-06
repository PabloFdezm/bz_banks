# Spec de bz_banks

Esta carpeta describe el repo completo para que una persona o un LLM pueda entenderlo, auditarlo y
modificarlo sin haber visto las conversaciones en que se construyó. Está escrita en castellano, igual que
el código, los comentarios y el sitio.

## Qué es

Un dashboard web estático del sistema bancario de Brasil para un analista buy-side (Pablo, Principal Asset
Management, Santiago). Lee datos públicos del Banco Central do Brasil (IF.Data, SGS y SCR.data), los procesa
en Python hasta una capa «gold» de parquets `bk_*`, los exporta a JSON y un sitio HTML + JS + ECharts los
dibuja. Se publica en Cloudflare Pages (https://banks-bz.pages.dev). Cada sección del sitio se puede presentar
como una lámina tipo PowerPoint.

## Cómo leer esta spec

| Archivo | Para qué |
|---|---|
| `01_proposito_y_reglas.md` | Audiencia, objetivo y **reglas no negociables** de diseño y de datos. Leer primero. |
| `02_arquitectura.md` | Flujo de punta a punta, carpetas, tecnologías y por qué están así. |
| `03_pipeline_de_datos.md` | Fuentes del BCB, almacén crudo/derivado, cada script, orden de corrida, convenciones de cálculo. |
| `04_modelo_de_datos.md` | La capa gold: grano, claves, unidades y quién produce y consume cada tabla. |
| `05_sitio_web.md` | Cómo funciona el sitio: montaje de página, config de tarjetas, componentes, tabla estándar, estado en la URL, presentación, CSS, rendimiento. |
| `06_paginas.md` | Qué muestra cada página y en qué estado está (v3 construida, estructura antigua u oculta). |
| `07_operacion.md` | Instalar, actualizar datos, publicar, verificar, tests, git. |
| `08_estado_pendientes_y_riesgos.md` | Qué falta, deudas técnicas conocidas y trampas de los datos. |
| `09_glosario.md` | Términos del BCB, del sistema financiero brasileño y del repo. |
| `10_como_extender.md` | Recetas: agregar una tarjeta, una página, una tabla gold, una serie SGS. |
| `generado/` | Inventario **autogenerado** (no editar): tablas y columnas, métricas, bancos, páginas y tarjetas, componentes, scripts y definiciones. Se regenera con `python -X utf8 herramientas/generar_spec.py`. |

Si hay contradicción entre la parte narrativa y `generado/`, manda `generado/` (sale del código y de los
datos) y la narrativa está desactualizada.

## Mapa del repo

```
bz_banks/
├── pipeline/          Python: descarga, cálculo y exportación (17 módulos, sin paquete: se importan por nombre)
├── definiciones/      JSON de configuración de datos: universo de bancos, modalidades, equivalencias, validación
├── sitio/             La web que se publica (HTML + JS módulos ES + CSS + ECharts vendorizado)
│   ├── index.html, <ruta>/index.html     una carpeta por página, cada una monta su config
│   ├── assets/js/      pagina.js, charts*.js, presentacion.js, estado.js, datos.js, formato.js, config.js, paginas/b0..b10.js
│   ├── assets/css/     tokens.css (paleta y fuentes), monitor.css (plantilla base), bancos.css (todo lo propio)
│   └── data/           JSON generados por pipeline/exportar_web_bancos.py (NO va a git)
├── herramientas/      verificar_f1.py, contar_tarjetas.mjs, verificar_gold.py, generar_spec.py, inventario_paginas.mjs
├── tests/             pytest sobre el gold (115 tests)
├── docs/              especificaciones y bitácoras históricas (v0.1) — contexto, no contrato vigente
├── spec/              esta carpeta
├── datos/             crudo, derivado, intermedio y gold (NO va a git; ~6 GB)
├── actualizar.bat     recalcula gold + JSON
└── publicar.bat       sube sitio/ a Cloudflare Pages (producción)
```
