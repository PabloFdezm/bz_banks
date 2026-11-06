# Tareas pendientes · estado al 6-nov-2026

Lista ordenada por prioridad. Cada frente tiene su archivo con el detalle, los datos de contraste y el criterio de
«terminado». Al cerrar una tarea, marcarla aquí con la fecha y actualizar `spec/08_estado_pendientes_y_riesgos.md`.

| # | Frente | Archivo | Estado |
|---|---|---|---|
| 1 | Correcciones de datos detectadas en la auditoría del 6-nov | `01_correcciones_datos.md` | 1.1–1.5 cerradas el 6-nov (1.2: se deja el corte mixto); falta 1.6 (notas) |
| 2 | Módulo Personas (SCR.data por renda) | `02_modulo_personas_scr.md` | páginas Personas (B11) y Mora (B12) construidas el 6-nov; falta correr `actualizar.bat` y publicar |
| 3 | Réplica del reporte sell-side de crédito por renda (detalle en `referencias/`, fuera de git) | `03_replica_sellside.md` | fuente S1–S5 encontrada el 6-nov (SCR.data v1, hasta sep-26); falta construirla |
| 4 | Réplica de gráficos del REF (BCB, oct-26) | `04_replica_ref.md` | 1.2.2.15 y 1.2.2.16 en la página Mora; ROE/provisiones por segmento y Anexo pendientes |
| 5 | Rediseño de gráficos (cambio grande anunciado por Pablo) | `05_rediseno_graficos.md` | por definir |
| 6 | Operación: automatización, limpieza, deuda técnica | `06_operacion.md` | pendiente |

Orden sugerido: 1 → 2 → 4 (fuente `bcb_ref`) → 3 → 5 → 6. El 5 puede cambiar cómo se construyen 2–4: preguntar a
Pablo antes de construir páginas nuevas.

## Archivos de referencia (locales, fuera de git)
- `referencias/` guarda reportes de terceros y las notas que se derivan de ellos. Nada de su contenido (cifras,
  tesis, figuras de reportes sell-side) se copia a archivos versionados: aquí solo se apunta a la nota local.
- `referencias/RELESTAB202610-refPub.pdf`: Relatório de Estabilidade Financeira del BCB, oct-26 (documento público).
