# Tareas pendientes · estado al 6-nov-2026

Lista ordenada por prioridad. Cada frente tiene su archivo con el detalle, los datos de contraste y el criterio de
«terminado». Al cerrar una tarea, marcarla aquí con la fecha y actualizar `spec/08_estado_pendientes_y_riesgos.md`.

| # | Frente | Archivo | Estado |
|---|---|---|---|
| 1 | Correcciones de datos detectadas en la auditoría del 6-nov | `01_correcciones_datos.md` | 1.1–1.5 cerradas el 6-nov (1.2: se deja el corte mixto); falta 1.6 (notas); 1.7 hecha y publicada el 8-nov |
| 2 | Módulo Personas (SCR.data por renda) | `02_modulo_personas_scr.md` | páginas Personas (B11) y Mora (B12) publicadas el 6-nov; canvas sin revisar por Pablo |
| 3 | Réplica del reporte sell-side de crédito por renda (detalle en `referencias/`, fuera de git) | `03_replica_sellside.md` | fuente S1–S5 encontrada el 6-nov (SCR.data v1, hasta sep-26); falta construirla |
| 4 | Réplica de gráficos del REF (BCB, oct-26) | `04_replica_ref.md` | fuente `bcb_ref` construida el 9-nov (`bk_ref`, 8 ediciones del Anexo; informe en `borradores/ref_informe.md`); faltan las tarjetas, con el rediseño |
| 5 | Rediseño de gráficos (cambio grande anunciado por Pablo) | `05_rediseno_graficos.md` | por definir |
| 6 | Operación: automatización, limpieza, deuda técnica | `06_operacion.md` | sitio en Cloudflare Pages desde el 6-nov; resto pendiente |
| 7 | Fuente CVM (ITR/DFP) → `bk_publicado` | `07_fuente_cvm.md` | construido y commiteado el 9-nov; decisiones §7 cerradas el 9-nov (15 bancos, 202312–202609, ROE desde 1T24); la tarjeta B8-06-0 espera el rediseño |
| 8 | Capital: informe 5 de IF.Data → `bk_capital` (página B7) | `08_fuente_capital.md` | construido el 9-nov (`pipeline/capital.py`, `bk_capital`, `bk_capital_grupo`, tests); 2T26 calza con el Pilar 3 de los 5 grandes; decisiones en `borradores/capital_informe.md` §6; B7 espera el rediseño |

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
- [ ] Frente 8 (capital): decisiones de `borradores/capital_informe.md` §6 — Santander 2019 (ACP
      sistémico 1 % o 0), dividendos en el puente del CP, definición de `holgura_crecimiento`, trimestres repetidos.
- [x] Frente 7 (CVM): decisiones cerradas el 9-nov (§7 de `borradores/cvm_informe.md`). Quedan: borrar los volcados
      de `borradores/` (lista mostrada a Pablo), BRB sin entregas desde 2T25, Daycoval 3T26 consolidado, y
      conectar B8-06-0 después del rediseño.
- [ ] 1.6 Notas de lectura: confirmar con el release 2T26 de Nu la caída del vencido (y PagSeguro); nota de ROE
      ~51 % de Nubank, BRB sin 2T26 y 2024-T4 vacío.
- [x] 1.7 Concesiones: rotuladas «totales» el 8-nov (validado contra la API), publicadas y verificadas en vivo el 9-nov. Filas de libres por aprobar.
- [ ] Frente 3: construir la fuente `bcb_scr_v1` (SCR.data v1 con `sr`, hasta sep-26); revisar desde qué año trae
      `sr`, cuándo se vacía `tcb` y el quiebre de S2 en jul-25.
- [ ] Frente 4: fuente `bk_ref` hecha el 9-nov. Decisiones en `borradores/ref_informe.md` §4 (Mora propio vs REF,
      ROE/provisiones por segmento desde el anexo, tarjeta de estrés, qué exportar). Faltan las tarjetas.
- [ ] spec/08 punto 5: validar los nombres de las series SGS de modalidades.
- [x] spec/08 punto 6: crecimientos a/a de crédito, activo y depósitos vacíos en 2025 (8-nov; antes salían mal).
      Opcional: medirlos con `bk_cartera`. Ojo: el a/a de 2024-T4 (trimestre anómalo) sigue publicado; ¿vaciarlo?
- [x] spec/08 punto 4: Focus (`focus.py`) y Selic real ex ante (SGS 432) se leen de la fuente desde el 8-nov.
      Ninguna tarjeta visible los usa (B1 está oculta). Tablas viejas de `datos/intermedio/` borradas.

**Operación**
- [x] Actualización manual (Pablo, 8-nov; sin tarea programada). CI pytest + `.venv`/`requirements.lock`; repo fuera de OneDrive
      (8-nov). SCR a parquet descartado (no achica). Falta que Pablo borre `datos/derivado/bcb_ifdata/valores/`
      (149 MB, CSV sin uso) y la carpeta vieja en OneDrive.
- [ ] Limpiar los archivos de bancos que quedaron en el repo `Dashboard` (mostrar la lista antes).
- [ ] Rehacer Calidad, Rentabilidad y Ficha en v3 (después del rediseño).

## Archivos de referencia (locales, fuera de git)
- `referencias/` guarda reportes de terceros y las notas que se derivan de ellos. Nada de su contenido (cifras,
  tesis, figuras de reportes sell-side) se copia a archivos versionados: aquí solo se apunta a la nota local.
- `referencias/RELESTAB202610-refPub.pdf`: Relatório de Estabilidade Financeira del BCB, oct-26 (documento público).
