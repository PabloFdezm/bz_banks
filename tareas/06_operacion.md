# 6 · Operación y deuda técnica

1. **Automatizar la actualización:** tarea programada de Windows (lo simple) o GitHub Actions, que exige guardar los
   datos fuera de git.
2. **Limpiar los archivos de bancos que quedaron en el repo `Dashboard`:** mostrarle la lista a Pablo antes de borrar.
3. ~~Borrar `referencias/_prueba.txt`, `datos/gold_antes_parquet` y `datos/intermedio/Banks/`~~ Hecho el 6-nov.
4. ~~Commit pendiente de `.gitignore`, README, `CLAUDE.md` y `tareas/`~~ Hecho (5e73679 y siguientes).
   Borrados el 8-nov `sitio/netlify.toml` (lo reemplaza `sitio/_headers`) y la carpeta vacía `others/`.
5. **Regenerar la spec** después de cada cambio: `python -X utf8 herramientas/generar_spec.py`.
6. **Pendientes que siguen abiertos en `spec/08`:**
   - rehacer Calidad, Rentabilidad y Ficha en v3;
   - páginas nuevas: Mora, Márgenes, Por banco, Productos;
   - validar las series SGS de modalidades;
