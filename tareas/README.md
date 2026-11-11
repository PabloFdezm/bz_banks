# Tareas pendientes · estado al 10-nov-2026

Lista ordenada por prioridad. Cada frente tiene su archivo con el detalle, los datos de contraste y el criterio de
«terminado». Al cerrar una tarea, marcarla aquí con la fecha y actualizar `spec/08_estado_pendientes_y_riesgos.md`.

| # | Frente | Archivo | Estado |
|---|---|---|---|
| 1 | Correcciones de datos detectadas en la auditoría del 6-nov | `01_correcciones_datos.md` | 1.1–1.5 cerradas el 6-nov (1.2: se deja el corte mixto); 1.6 hecha el 9-nov (falta publicar); 1.7 hecha y publicada el 8-nov; 1.8 (S4 4.095 % a/a en Trimestral) anotada el 11-nov, por revisar |
| 2 | Módulo Personas (SCR.data por renda) | `02_modulo_personas_scr.md` | páginas Personas (B11) y Mora (B12) publicadas el 6-nov; canvas sin revisar por Pablo |
| 3 | Réplica del reporte sell-side de crédito por renda (detalle en `referencias/`, fuera de git) | `03_replica_sellside.md` | **en pausa** (Pablo, 9-nov): la fuente sirve (sondeo en `03_replica_sellside.md`), pero bajar 2017–2026 son ~3,5 GB y medio día de trabajo |
| 4 | Réplica de gráficos del REF (BCB, oct-26) | `04_replica_ref.md` | fuente `bcb_ref` construida el 9-nov (`bk_ref`, 8 ediciones del Anexo; informe en `borradores/ref_informe.md`); faltan las tarjetas, con el rediseño |
| 5 | Rediseño de gráficos (cambio grande anunciado por Pablo) | `05_rediseno_graficos.md` | hojas del canvas aprobadas el 10-nov; sitio v2 construido (`/v2/`, motor `sitio/assets/v2/dc.js`); pendiente: datos de v2 desde el pipeline, pasar la raíz a v2 y móvil |
| 6 | Operación: automatización, limpieza, deuda técnica | `06_operacion.md` | sitio en Cloudflare Pages desde el 6-nov; resto pendiente |
| 7 | Fuente CVM (ITR/DFP) → `bk_publicado` | `07_fuente_cvm.md` | construido y commiteado el 9-nov; decisiones §7 cerradas el 9-nov (15 bancos, 202312–202609, ROE desde 1T24); la tarjeta B8-06-0 espera el rediseño |
| 8 | Capital: informe 5 de IF.Data → `bk_capital` (página B7) | `08_fuente_capital.md` | construido el 9-nov (`pipeline/capital.py`, `bk_capital`, `bk_capital_grupo`, tests); 2T26 calza con el Pilar 3 de los 5 grandes; decisiones en `borradores/capital_informe.md` §6; B7 espera el rediseño |
| 9 | Portada mensual (01 colocaciones, 02 precio, 03 NPL): series SGS por segmento y gold `bk_portada_m` | `09_portada_mensual_segmentos.md` | **terminado el 11-nov**: A1–A4, `bk_portada_m`, `herramientas/portada_desde_gold.py`; la Portada sin «en preparación» (spread dirigido de personas: el BCB no lo publica) |
| 10 | Capital mensual: balancetes 4060 o estimación de la holgura (sección 04 de la Portada) | `10_capital_mensual.md` | cerrado el 9-nov: B descartada (no pasa 0,3 pp); A pasa al frente 11 |
| 11 | Fuente nueva: balancetes mensuales COSIF → ROE, NIM, eficiencia, depósitos y capital mensuales | `11_fuente_balancetes.md` | fase 2 hecha el 11-nov: `bk_balancete_m` y `bk_sistema_bal_m` (ROE 12m, depósitos, balance) desde ene-20; NIM, costo de riesgo y eficiencia no cuadran y no se publican (`borradores/balancetes_informe.md`) |
| 12 | Hojas por producto de personas (Tarjeta, Personal sin planilla, Descuento por planilla y Vehículos): códigos SGS que faltan, gold por producto, verificaciones | `12_hoja_tarjeta.md` | datos cerrados el 10-nov; falta la revisión visual de Pablo. A (códigos SGS) y B (`bk_producto_pf_m`, `bk_producto_pf_scr_m`) hechas el 10-nov; corregido el doble conteo de la hoja Personal; C informada el 10-nov (`borradores/tarjeta_verificaciones.md`); aplicadas tarjeta con interés aparte, «sin renta» aparte y Selic efectiva; rótulos, notas y P9 en tres grupos aplicados el 10-nov; el canvas ya lee `bandas` y `nota` (10-nov, versión 73) |
| 13 | Hojas de empresas (MPME y Grandes): códigos SGS que faltan, modalidades PJ en el SCR, gold y verificaciones | `13_hojas_empresas.md` | A, C y D hechas el 10-nov (66 series PJ por modalidad en el SGS, `bk_empresas_m`, `bk_empresas_scr_m`, `borradores/empresas_verificaciones.md`); B: sondeo de costo entregado, falta el visto bueno de Pablo para el cubo PJ |
| 14 | Hoja «Fondeo y liquidez»: agregados monetarios y tasas de captación del SGS, gold `bk_fondeo_m` | `14_hoja_fondeo.md` | A, B y C hechas el 10-nov (`bk_fondeo_m`, `borradores/fondeo_verificaciones.md`); tasas por inversionista 28583–28617 no existen en el SGS: códigos por encontrar |
| 15 | Hoja «P&L y balance por banco»: mapa de cuentas entre épocas del plan contable, gold `bk_pyb` y verificaciones | `15_hoja_pyb.md` | A, B y C hechas el 10-nov (`pyb_lineas.json`, `bk_pyb`, `bk_pyb_grupo`, `borradores/pyb_verificaciones.md`); decisiones de Pablo pendientes |
| 16 | Hoja «Inmobiliario»: códigos SGS que faltan (20610, 20611), producto inmobiliario en los gold de personas y verificaciones | `16_hoja_inmobiliario.md` | A y B hechas el 10-nov (20610 y 20611 en el catálogo; producto `inmobiliario` en `bk_producto_pf_m` y `bk_producto_pf_scr_m`; borrador lee de gold); C por hacer |

Orden sugerido (6-nov; no incluye los frentes 7–12, falta que Pablo lo reordene): 1 → 2 → 4 (fuente `bcb_ref`) → 3 → 5 → 6. El 5 puede cambiar cómo se construyen 2–4: preguntar a
Pablo antes de construir páginas nuevas.

## To do (al cierre del 6-nov)
Hecho el 6-nov: frente 1 (1.1–1.5); sitio movido a Cloudflare Pages (https://banks-bz.pages.dev) y sitios de
Netlify borrados; Personas y Mora publicadas y verificadas en 3 anchos; fuente S1–S5 encontrada.

**Decisiones de Pablo**
- [ ] Revisar las páginas Personas y Mora ya publicadas (y el canvas de Personas,
      https://claude.ai/artifact/HonVC1nA2y22S9EH3U1gKx): ¿quedan visibles o se ocultan hasta el rediseño?
- [ ] Cerrar el rediseño de gráficos (frente 5; decisiones del 9-nov en `05_rediseno_graficos.md`, hoja Tarjeta
      aprobada el 10-nov); mientras, no se construyen páginas nuevas.
- [ ] Coordinar las sesiones en paralelo: un frente por sesión.

**Datos**
- [x] Frente 8 (capital): decisiones cerradas el 9-nov (Pablo): Santander 2019 = 1 %, puente del CP con residuo
      «otros», `holgura_crecimiento` sobre RWA, trimestres repetidos publicados con `alerta`. Queda conectar B7.
- [x] Frente 7 (CVM): decisiones cerradas el 9-nov (§7 de `borradores/cvm_informe.md`). Quedan: borrar los volcados
      de `borradores/` (lista mostrada a Pablo), BRB sin entregas desde 2T25, Daycoval 3T26 consolidado, y
      conectar B8-06-0 después del rediseño.
- [x] 1.6 Notas de lectura (9-nov), en `bancos__dashboard.json` → `bk_banco.nota` (ficha B8). El release 2T26 de Nu
      **no** confirma la caída del vencido de IF.Data (sin venta de cartera ni cambio de castigos; su 90+ consolidado
      sube): la nota pide leerla con cautela. PagSeguro: vencido ínfimo, no es señal. BRB sí tiene 2T26 (la nota vieja
      ya no valía): cartera −13 % t/t, NPL15 a 10,8 %, fuera de la CVM y excluido del REF. 2024-T4 ya estaba anotado
      en B4 y B6. Falta publicar.
- [x] 1.7 Concesiones: rotuladas «totales» el 8-nov (validado contra la API), publicadas y verificadas en vivo el 9-nov. Filas de libres por aprobar.
- [ ] Frente 3 en pausa (decisión de Pablo, 9-nov: ~3,5 GB y medio día). Sondeo hecho: `sr` desde 2017-06,
      `tcb` vacío desde 2025-07. Si se retoma, una alternativa más chica es bajar solo los últimos 2–3 años.
- [ ] Frente 4: fuente `bk_ref` hecha el 9-nov. Decidido (Pablo, 9-nov): Mora sigue con SCR.data propio y el REF
      como control; ROE y provisiones por segmento desde el REF. Faltan la tarjeta de estrés, qué exportar y las
      tarjetas (con el rediseño).
- [x] spec/08 punto 5: nombres SGS validados contra el catálogo oficial el 9-nov (`herramientas/validar_sgs.py`).
- [x] spec/08 punto 6: crecimientos a/a de crédito, activo y depósitos vacíos en 2025 (8-nov; antes salían mal).
      Opcional: medirlos con `bk_cartera`. El a/a de 2024-T4 se deja (revisado el 9-nov): el trimestre es anómalo
      solo en los informes de cartera por modalidad (8, 11, 13), que ya están vacíos; el a/a de crédito, activo y
      depósitos sale del balance (informes 2 y 3), que es válido. Pablo había elegido vaciarlo con una
      recomendación mal fundada; queda a su confirmación.
- [x] spec/08 punto 4: Focus (`focus.py`) y Selic real ex ante (SGS 432) se leen de la fuente desde el 8-nov.
      Ninguna tarjeta visible los usa (B1 está oculta). Tablas viejas de `datos/intermedio/` borradas.

**Operación**
- [x] Actualización manual (Pablo, 8-nov; sin tarea programada). CI pytest + `.venv`/`requirements.lock`; repo fuera de OneDrive
      (8-nov). SCR a parquet descartado (no achica). `valores/` y la carpeta vieja en OneDrive, borradas (9-nov).
- [x] Repo `Dashboard` limpio de bancos el 9-nov (commit fb680e6 allí: sitio_bancos, bancos_web, scripts gold y
      métricas, definiciones bancos__*; ~474 MB). Se quedan porque el macro los usa: ifdata.py,
      preparar_bancos_powerbi.py, diccionario_ifdata.py, bcb_ifdata__*/cvm__* y el crudo bcb_ifdata/bcb_scr (5 GB,
      duplicado con bz_banks; liberarlo exige reapuntar el macro). Docs de bancos en `Dashboard/docs/` conservados.
- [ ] Rehacer Calidad, Rentabilidad y Ficha en v3 (después del rediseño).

## Archivos de referencia (locales, fuera de git)
- `referencias/` guarda reportes de terceros y las notas que se derivan de ellos. Nada de su contenido (cifras,
  tesis, figuras de reportes sell-side) se copia a archivos versionados: aquí solo se apunta a la nota local.
- `referencias/RELESTAB202610-refPub.pdf`: Relatório de Estabilidade Financeira del BCB, oct-26 (documento público).
