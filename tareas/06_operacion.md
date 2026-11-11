# 6 · Operación y deuda técnica

1. ~~Automatizar la actualización~~ Descartado el 8-nov: Pablo actualiza a mano (no hay tarea programada). Sí
   quedaron el CI de pytest en GitHub y `.venv` con `requirements.lock`; repo movido de OneDrive a `C:\dev\bz_banks`. Pasar el SCR a parquet se descartó: un mes
   pesa igual en parquet (16 MB) que en ZIP (15 MB) y el pipeline ya cachea el agregado por año.
2. **Limpiar los archivos de bancos que quedaron en el repo `Dashboard`:** mostrarle la lista a Pablo antes de borrar.
3. ~~Borrar `referencias/_prueba.txt`, `datos/gold_antes_parquet` y `datos/intermedio/Banks/`~~ Hecho el 6-nov.
4. ~~Commit pendiente de `.gitignore`, README, `CLAUDE.md` y `tareas/`~~ Hecho (5e73679 y siguientes).
   Borrados el 8-nov `sitio/netlify.toml` (lo reemplaza `sitio/_headers`) y la carpeta vacía `others/`.
5. **Regenerar la spec** después de cada cambio: `python -X utf8 herramientas/generar_spec.py`.
6. **Pendientes que siguen abiertos en `spec/08`:**
   - rehacer Calidad, Rentabilidad y Ficha en v3;
   - páginas nuevas: Mora, Márgenes, Por banco, Productos;
   - validar las series SGS de modalidades;
7. **Documentación que quedó con el armado anterior (anotado el 11-nov):** desde el 11-nov la proporción es gráfico
   1,5 : tabla 1 y la tabla tiene dos formas (corta en la página, 8 columnas en Agrandar); ver `CLAUDE.md`, `spec/01`
   y `DESIGN.md`.
   - `spec/06_paginas.md` (línea 8) describe la estructura v3 retirada (gráfico 4/9, `tabla_estandar` 5/9): reescribir
     para el sitio v2.
   - `spec/generado/paginas.md` sigue saliendo del armado viejo (anchos 4/9 y 5/9): cambiar
     `herramientas/generar_spec.py` para que lea las páginas de `sitio/assets/v2/paginas/`.
8. **`herramientas/verificar_f1.py` quedó obsoleto con el sitio v2 (detectado el 11-nov):** lee
   `sitio/assets/js/config.js` (vía `inventario_paginas.mjs`), que se retiró al pasar v2 a la raíz (8cbc7dd), y falla
   con ERR_MODULE_NOT_FOUND. Reescribirlo para v2: recorrer las rutas de `diseno/canvas/paginas.json` y comprobar
   HTTP 200, sin errores de página ni de consola, sin `{{` sin reemplazar, sin scroll horizontal en 1920/1280/390,
   rótulos del eje X sin pisarse y fuentes cargadas (ojo: `document.fonts.check` da falso negativo con Plex Mono por
   los subconjuntos unicode; mirar `document.fonts` con status «loaded»). El 11-nov se usó un script equivalente fuera
   del repo y pasaron las 13 páginas en los 3 anchos.
