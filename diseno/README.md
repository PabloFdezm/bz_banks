# diseno/ · Kit de propuesta de gráficos

Copiado el 8-nov-2026 desde `macro_bz/design/` (Monitor Brasil) como punto de partida del frente 5
(`tareas/05_rediseno_graficos.md`). Es material de referencia y tooling: no toca `sitio/`, `pipeline/` ni los datos.

## Qué hay

| Pieza | Qué es |
|---|---|
| `DESIGN.md` | Identidad y tokens. Los valores ya coinciden con `sitio/assets/css/tokens.css`; lo que cambia es el nombre del producto. |
| `DESIGN_GRAFICOS.md` | Contrato de las 24 familias de gráficos (F01–F24) con sus reglas de lectura. |
| `PLAN_INTEGRACION.md` | Método de integración por olas con criterios de «hecho» y seguimiento por tarjeta. |
| `PROPUESTAS-2026-11-05.md` | La propuesta original completa (contexto y decisiones). |
| `GUIA_*.md`, `IMPLEMENTACION_GRAFICOS.md`, `INFORME_GRAFICOS.md` | Guías especializadas (relojes, gráficos frecuentes) y el informe de verificación original. |
| `assets/` | Tokens, sistema de componentes, tipografías OFL locales (IBM Plex, Bricolage). |
| `graficos/` | Tooling del catálogo navegable: `catalogo.js/.css`, `vista.*`, `preparar.mjs`, `construir-offline.mjs`, `rutas.mjs`, `instalar.mjs`. |
| `reportes/` | `revisar-coherencia.mjs` y `probar-datos.mjs` como plantillas de verificación sin navegador. |

## Qué falta a propósito

- `graficos/inventario.js`: era el inventario de las 160 tarjetas del monitor (macro). Aquí se regenera
  desde el sitio de bancos: `node graficos/preparar.mjs --sitio ../sitio` (pendiente de adaptar las rutas).
- `graficos/offline/`, `graficos/monitor/`, capturas y JSON de `reportes/`: evidencia del monitor (70 MB).
  `graficos/verificacion.html` queda como plantilla; sus capturas no se copiaron.
- Archivos `*.artifact.json` y `anteriores/`.

## Avisos

- Los documentos hablan de «Monitor Brasil» y de tarjetas `AM*`: son la referencia de origen, no la verdad
  de este repo. La adaptación empieza por decidir qué familias aplican a banca (varias ya existen en
  `sitio/assets/js/charts_bancos.js`).
- El kit está sin commitear; decidir si entra a git completo o solo los documentos.
- Proceso vigente: canvas → aprobación de Pablo → construcción. Esta carpeta es el canvas.
