# bz_banks · guía para Claude Code

Dashboard del sector bancario de Brasil (sitio estático en Cloudflare Pages: https://banks-bz.pages.dev; Netlify quedó en desuso).
Dueño: Pablo (analista buy-side, bancos LatAm). Responder en español, directo y crítico, prosa sobria.

## Antes de tocar nada
1. Leer `spec/README.md` (cómo está armado el repo) y `spec/08_estado_pendientes_y_riesgos.md` (trampas de datos).
2. Leer `tareas/README.md`: lista ordenada de lo que falta, con el detalle en un archivo por frente.

## Reglas fijas
- Todo comando que se le muestre a Pablo lleva su `Set-Location` (Windows/PowerShell) o `cd`.
- `referencias/` tiene reportes de terceros (sell-side, BCB): **nunca** a GitHub ni al sitio. Está en `.gitignore`; no sacarlo.
- No borrar archivos ni hacer commit/push sin pedirlo. Mostrar la lista antes de borrar.
- Diseño: proceso canvas → aprobación de Pablo → construcción. Gráfico a la izquierda y tabla a la derecha, nunca
  apilados; nunca gráfico y tabla de la misma serie; una sola tabla estándar sin colores (Indicador · Corte · Último ·
  Share · m/m · 3m/3m · a/a · 12m/12m); el Total siempre en otro color.
- No inventar cifras: si falta el dato, la tarjeta va «en preparación».
- Verificar en el sitio publicado con fuentes reales y en varios anchos, no solo en capturas locales.

## Comandos
- Datos: `actualizar.bat` (pipeline completo). Publicar: `publicar.bat` (o `publicar.bat datos`).
- Tests: `python -m pytest -q`. Verificadores: `python -X utf8 herramientas/verificar_gold.py` (intermedio) y `--gold` (tablas bk_*), `herramientas/verificar_f1.py`
  (sitio publicado: `--url https://banks-bz.pages.dev --anchos 1920,1280,390`), `herramientas/verificar_cvm.py` (fuente CVM y `bk_publicado`).
- Spec autogenerada: `python -X utf8 herramientas/generar_spec.py`.
