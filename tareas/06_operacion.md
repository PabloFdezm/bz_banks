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
