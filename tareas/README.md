# Tareas pendientes · estado al 6-nov-2026

Lista ordenada por prioridad. Cada frente tiene su archivo con el detalle, los datos de contraste y el criterio de
«terminado». Al cerrar una tarea, marcarla aquí con la fecha y actualizar `spec/08_estado_pendientes_y_riesgos.md`.

| # | Frente | Archivo | Estado |
|---|---|---|---|
| 1 | Correcciones de datos detectadas en la auditoría del 6-nov | `01_correcciones_datos.md` | 1.1–1.5 cerradas el 6-nov (1.2: se deja el corte mixto); falta 1.6 (notas); 1.7 hecha el 8-nov, falta publicar |
| 2 | Módulo Personas (SCR.data por renda) | `02_modulo_personas_scr.md` | páginas Personas (B11) y Mora (B12) publicadas el 6-nov; canvas sin revisar por Pablo |
| 3 | Réplica del reporte sell-side de crédito por renda (detalle en `referencias/`, fuera de git) | `03_replica_sellside.md` | fuente S1–S5 encontrada el 6-nov (SCR.data v1, hasta sep-26); falta construirla |
| 4 | Réplica de gráficos del REF (BCB, oct-26) | `04_replica_ref.md` | 1.2.2.15 y 1.2.2.16 en la página Mora; ROE/provisiones por segmento y Anexo pendientes |
| 5 | Rediseño de gráficos (cambio grande anunciado por Pablo) | `05_rediseno_graficos.md` | por definir |
| 6 | Operación: automatización, limpieza, deuda técnica | `06_operacion.md` | sitio en Cloudflare Pages desde el 6-nov; resto pendiente |

Orden sugerido: 1 → 2 → 4 (fuente `bcb_ref`) → 3 → 5 → 6. El 5 puede cambiar cómo se construyen 2–4: preguntar a
Pablo antes de construir páginas nuevas.

## To do (al cierre del 6-nov)
Hecho el 6-nov: frente 1 (1.1–1.5); sitio movido a Cloudflare Pages (https://banks-bz.pages.dev) y sitios de
Netlify borrados; Personas y Mora publicadas y verificadas en 3 anchos; fuente S1–S5 encontrada.

**Decisiones de Pablo**
- [ ] Revisar las páginas Personas y Mora ya publicadas (y el canvas de Personas,
      https://claude.ai/artifact/HonVC1nA2y22S9EH3U1gKx): ¿quedan visibles o se ocultan hasta el rediseño?
- [ ] Definir el rediseño de gráficos (frente 5); mientras, no se construyen páginas nuevas.
- [ ] Coordinar las sesiones en paralelo: un frente por sesión.

**Datos**
- [ ] 1.6 Notas de lectura: confirmar con el release 2T26 de Nu la caída del vencido (y PagSeguro); nota de ROE
      ~51 % de Nubank, BRB sin 2T26 y 2024-T4 vacío.
- [x] 1.7 Concesiones: rotuladas «totales» el 8-nov (validado contra la API). Falta publicar; filas de libres por aprobar.
- [ ] Frente 3: construir la fuente `bcb_scr_v1` (SCR.data v1 con `sr`, hasta sep-26); revisar desde qué año trae
      `sr`, cuándo se vacía `tcb` y el quiebre de S2 en jul-25.
- [ ] Frente 4: ROE y provisiones por segmento, y Anexo del REF.
- [ ] spec/08 punto 5: validar los nombres de las series SGS de modalidades.
- [ ] spec/08 punto 6: `credito_aa` 2025 vacío en la franja del quiebre COSIF.
- [ ] spec/08 punto 4: `tasa_real_exante` y Focus siguen congelados; leerlos del SGS y Focus.

**Operación**
- [ ] Pasar el SCR de ZIP a parquet (como IF.Data el 4-nov) y borrar los CSV originales del IF.Data (con permiso).
- [ ] Automatizar la actualización (tarea programada de Windows o GitHub Actions).
- [ ] Limpiar los archivos de bancos que quedaron en el repo `Dashboard` (mostrar la lista antes).
- [ ] Rehacer Calidad, Rentabilidad y Ficha en v3 (después del rediseño).

## Archivos de referencia (locales, fuera de git)
- `referencias/` guarda reportes de terceros y las notas que se derivan de ellos. Nada de su contenido (cifras,
  tesis, figuras de reportes sell-side) se copia a archivos versionados: aquí solo se apunta a la nota local.
- `referencias/RELESTAB202610-refPub.pdf`: Relatório de Estabilidade Financeira del BCB, oct-26 (documento público).
