# Pendientes del dashboard de bancos

Una línea por problema: fecha, encargo, qué, por qué, qué se necesita. Lo que no cuadra
no se arregla por cuenta propia (plan 57 §2.4): se anota aquí y se sigue.

- 2026-11-02 · B2 (sgs_sistema) · `pb/hogares_modalidades.parquet` "Personal total" NO es
  SGS 21114 (pessoal livre, 11,1 % en sep-26): es otra definición (~PF total/21084, 6,0 %).
  `mora90_personal` se bajó del SGS 21114. El spec §3.9 no dice cuál definición quiere;
  hace falta decisión del arquitecto (A3 también trabaja equivalencias de modalidad).
- 2026-11-02 · B2 (sgs_sistema) · Las cuatro mora90 leídas de `hogares_modalidades`
  (consignado_total, vehículos, rotativo, inmobiliario_total) quedan con vintage jul-2026
  mientras el resto de la tabla llega a sep-2026; además 21127 difiere 0,3 pp en jul-26
  (revisión del SGS posterior a la construcción de la tabla pb). El spec §3.9 manda preferir
  esa tabla. Si se prefiere vintage uniforme: `MORA_HOGARES` en
  `preparar_gold_bancos_sistema.py` pasa esas series a SGS (cambio de una línea).
- 2026-11-02 · B2 (sgs_sistema) · `selic_real_exante` arranca en 2021-01 (límite de la serie
  pb), así que en `bk_sistema_q` tiene 23 observaciones: el criterio «ninguna serie con
  menos de 24» no se puede cumplir sin inventar historia.
- 2026-11-02 · B2 (sgs_sistema) · `pix_share` (§3.9) no se construyó: el spec exige definirla
  en `bk_metrica` antes de publicar (H1) y su fuente es Olinda MPV, fuera de los códigos
  validados de este encargo. Hace falta encargo propio o extensión del actual.
- 2026-11-02 · B2 (sgs_sistema) · `docs/dashboard/codigos_y_formulas.md` marca 21082 como
  «ya» bajado, pero en `datos/crudo/bcb_sgs/` solo estaba 21084. La tabla del paso 1 del
  encargo 61 refleja el estado real del disco. Corregir el doc o dejarlo anotado.
- 2026-11-02 · B1 (ifdata_informes) · Informes 7, 9, 12 y 14 de IF.Data (y 10, salvo 202606
  prudencial) NO son servidos por la API Olinda bajo ningún escopo probado: HTTP 500
  consistente en 285 combinaciones informe×escopo×trimestre (incluye todo financeiro
  201403–202412). Contradice la premisa del encargo 60 y la nota de `ifdata.py relatorios`
  («crédito: financeiro hasta 2024-12, prudencial desde 2025-03»). Los de crédito que el
  BCB sí sirve: 8, 11, 13 (financeiro 201403–202412) y 8/11/13/16 (prudencial 202412–202606).
  Hace falta decisión del arquitecto: ¿otro set de informes, sitio web en vez de API, o SCR.data?
- 2026-11-02 · B1 (ifdata_informes) · Informe 5 (Capital) prudencial solo existe en 14 de 50
  trimestres (202012–202309, 202412, 202603; el resto da 500). Si `bk_capital` (A4/B4)
  necesita historia 2014–2026, no está en la API con este escopo. ¿Probar el 5 en escopo
  financeiro/individual o aceptar la ventana corta?

## Decisiones del arquitecto (2026-11-02, revisión del encargo 61)

- 61 · Unidades: toda `bk_sistema_m`/`_q` pasa a fracción (0,05 = 5 %); impulso de crédito e hiato BIS en pp con sufijo `_pp`. Corrección en encargo 61b.
- 61 · Nombres: `dirigido_rural_real_aa`, `dirigido_imob_real_aa`, `dirigido_bndes_real_aa`, `credito_mpme_real_aa`, `credito_grande_real_aa`, `mora90_mpme`, `mora90_grande`. El error de origen fue la abreviatura del spec §3.9 (corregir en v0.2).
- 61 · Vintage: las mora90 de `bk_sistema` salen todas del SGS (21119, 21121, 21127, 21151). `hogares_modalidades` queda solo para B4-02.
- 61 · Tarjeta: equivalencia de «Tarjeta de crédito» = 21129 (total); 21127 y 21128 quedan como detalle. Spec §3.9/§4.3 a corregir en v0.2.
- 61 · Personal: `mora90_personal` = 21114 (incluye consignado). La mora del personal sin consignación se deriva por saldos en A3.
- 61 · `selic_real_exante` con 23 trimestres: excepción aceptada; extender historia queda para después (Focus + Selic desde 2001).
- 61 · `pix_share`: encargo propio en la ola 2.
- 61 · `codigos_y_formulas.md` marca 21082 como «ya» y no estaba en disco: queda anotado; no se corrige ese doc del macro desde este proyecto.

## Decisiones del arquitecto (2026-11-02, revisión del encargo 62)

- 62 · Aprobado. Conteos, anchos y altos coinciden con el esqueleto; captura B8 revisada.
- 62 · Prefijo de universo para reclamos y tarifas: «BCB ·» (no es un universo nuevo; Pix sigue «Sistema BCB ·»).
- 62 · B9 sección 01: nombre «Todos los bancos», pregunta «¿cómo se comparan los 34 bancos en el último trimestre?». B10 rótulo «10 · METODOLOGÍA». B8-07 pregunta «¿cómo lo evalúan sus clientes frente a sus pares?». Entran al esqueleto v0.2.
- 62 · Subtítulos y frecuencias derivados por el worker: se aceptan provisoriamente; se revisan en el esqueleto v0.2.
- 62 · Cierre (FUENTES / CÓMO LEER): se arma en la ola 2 a partir de las fuentes de cada tarjeta.
- 62 · Base de módulos comunes: qwen3.8-max, provisoria hasta que Pablo marque el sitio vigente del macro.

## Decisiones del arquitecto (2026-11-02, revisión del encargo 60)

- 60 · No se da por «no disponible» ningún informe todavía. Los 15 archivos que «sí sirve» son exactamente los bajados antes (el colector no los re-pidió), así que los 500 de hoy pueden ser la caída intermitente de Olinda ya documentada (fuentes §14-15) y no ausencia del dato. Diagnóstico en encargo 60b: control contra un archivo que existe + sondeo del portal REST (www3.bcb.gov.br/ifdata/rest).
- 60 · SCR.data no reemplaza las aperturas por banco (solo abre por segmento). Mientras tanto B3-04 queda FALTA; no bloquea la Ficha.
- 60 · Informe 5: probar también escopo financeiro en el 60b; la decisión sobre la ventana de bk_capital se toma con el resultado.
- 60 · Lección para encargos de red: limitar reintentos (máx. 3 por combinación, pausa ≥ 10 s) y abortar si 3 combinaciones seguidas dan el mismo error.

## Decisiones del arquitecto (2026-11-02, revisión de 60b y 60c)

- 60b/60c · Olinda IFDATA caída (500 incluso en combinaciones que existen en disco) y descarga del portal REST rota («Erro interno»). La línea IF.Data queda en pausa; no se acepta ningún hueco como definitivo.
- 60c · Hallazgo: el portal REST tiene los informes 5, 7, 9, 10, 12 y 14 como trel<q>_<ID>.json hasta 202412 (IDs no estables entre trimestres); 2025-2026 solo por Olinda.
- 60c · Cartera por modalidad (informes 11/13) no se ve afectada: ya está en disco para todo el panel y alimenta cre_* hoy.
- 60c · Orden cuando vuelva el servicio: (1) re-correr el 60 por Olinda; (2) solo si Olinda no sirve los años previos, encargo de cliente del portal REST resolviendo nombre→ID por trimestre.
- 60c · Capital: si Olinda tampoco sirve antes de 2020, bk_capital arranca en 2020-12 y B7 se diseña con esa ventana.
- 60c · Control diario: `python -X utf8 extraer_fuentes.py status` hasta que IF.data API Olinda dé OK.

## Decisiones del arquitecto (2026-11-02, revisión de 58 y 59)

- 58 · Aprobado tras verificar ROE de Grandes (15,28 %) y Digitales (30,62 %) a mano. Corrección 58b: signos de montos de resultado → neutro (vienen en negativo); share_* vuelven a bk_grupo como suma.
- 58 · BRB sin dato en 2T26: el total del último trimestre se muestra con 33 bancos y nota «33 de 34 con dato».
- 58 · Asignaciones propias del worker (familia, unidad, formato, nombres, rank_panel en métricas de tamaño y cuota, pct_grupo null con n < 3): aceptadas; se fijan en el spec v0.2. en_comparador se define en v0.2 con B9.
- 59 · Aprobado. Las variaciones a/a con signo (lucro_ttm_aa) no llevan regla de rango: confirmado.
- 59 · Nombres de columnas de bk_manifiesto (tabla, universo, ultimo_corte) y de bk_scr que fijó el verificador: se adoptan en el spec v0.2.
- 59 · bk_cartera_totales.parquet autorizada como tabla auxiliar de pb/Banks (fuera del contrato del sitio); la escribe el refactor A1 junto con la cartera por banco.

## Decisiones del arquitecto (2026-11-02, revisión de 64/64b, 65 y A1)

- A1 · bk_cartera y bk_cartera_totales hechas por el arquitecto sin tocar preparar_credito_paginas_powerbi.py (importa sus funciones). Coinciden exacto con cre_panorama por grupo. Columna d_cuota_aa en pp.
- 64b · Aprobado. Exclusiones de la regresión: 202412 y 202503 solo en los 10 bancos con quiebre_2025.
- 64b · no_operacional sin dato desde 202503 (renumeración COSIF 2025): queda null y «otros» la absorbe. Pendiente del arquitecto: ubicar la cuenta nueva en bank_cuentas / ifdata_diccionario y agregarla a la extracción de bank_resultados.
- 64b · Cambio de una línea en verificar.py fuera de la lista del encargo (identidad hasta la línea anterior a roa): aceptado.
- 64b · Betas con n < 24 (Neon 16): se publican, pero la tarjeta B6-04-0 las marca «pocos trimestres» y muestra el IC. Agregar al esqueleto v0.2.
- 65 · Recorrido de presentación B0 → B10 saltando páginas sin láminas: aprobado. Impresión 16:9 (1920×1080) en vez de A4: aprobado; corregir spec web §4 en v0.2. Constante de bancos solo como respaldo de data/bk_banco.json.
- 65 · Corrección 65b en curso: percentiles (escala), pequeños múltiplos (nombres y corte), eje repetido, etiqueta cortada, título de la ficha con el nombre del banco.
- 65b · Aprobado (captura revisada). Detalle para la ola 3: en burbujas_trayectoria el título del eje Y se superpone a las etiquetas.
- 65b · Titular con el banco activo solo en la Ficha; las demás páginas conservan su título y muestran el banco en la barra.
- 65b · Detección de tablas exportadas por manifiesto: el exportador (B7) escribe siempre data/_manifiesto.json (aunque esté vacío) y el sitio lee de ahí qué tablas existen; TABLAS_EXPORTADAS en config.js se retira cuando B7 esté listo.

## Decisiones del arquitecto (2026-11-03, A3)

- A3 · Corrección: SGS 21114 es crédito personal NO consignado (no el total). La equivalencia de «Personal sin consignación» es directa. Anula la línea «Personal: mora90_personal = 21114 (incluye consignado)» del 2026-11-02.
- A3 · bk_exposicion: mora implícita solo con cobertura ≥ 50 % de la cartera; las modalidades dirigidas sin serie SGS quedan fuera. Pendiente: series de mora rural PF y PJ dirigido (subiría la cobertura de BB, ABC y los bancos de desarrollo).
- 2026-11-03 · CVM (B6 y H5) postergado por decisión de Pablo.
- 2026-11-03 · Pix (B2-05-2) fuera del alcance por decisión de Pablo: foco en bancos. La tarjeta se elimina del esqueleto en la próxima versión.
- 71 · Aprobado. La falla de sha256 del manifiesto era del arquitecto (regeneró bk_sistema sin volver a correr base); corregido: verificar --gold limpio y 75 tests pasan. Regla: después de cualquier subcomando suelto, correr `base` (o usar `todo`).
- 71 · n mínimo 16 (beta nula) y n < 24 (marca «pocos trimestres» en la tarjeta) conviven: son reglas distintas. El contrato de bk_conducta se confirma cuando llegue el encargo 69.
- 2026-11-03 · Tarifas (B2-05-1) también fuera por decisión de Pablo: foco en bancos. Encargo 72 descartado (movido a docs/orquestacion/descartados/). La sección B2-05 queda solo con reclamos por banco (B2-05-0).

## Decisiones del arquitecto (2026-11-03, ola 3: páginas)

- 74/B3 · Parcial aceptado: 2 tarjetas con datos (sistema real a/a y dirigido), cifras verificadas. Segunda pasada cuando data/ tenga bk_cre_panorama (aa4, aporte_aa4, total_aa4: copia de cre_*, sin recalcular).
- 74/B3 · `cuota_modalidad` = cuota del banco dentro de esa modalidad en el panel (no suma 1 por banco). La composición de la cartera del banco es `peso_banco`.
- 74 · Piezas compartidas que faltan (apilada_100 y las que reporten las demás páginas): un solo encargo al final de la tanda, para no tocar charts*.js en paralelo.
- 74 · verificar_f0.py quedó obsoleto (exige todo «en preparación»): reemplazarlo por un verificador F1 que acepte tarjetas con datos y siga exigiendo 0 errores de consola y conteos del esqueleto.
- 74 · Riel (KPI) y selectores de sección: pagina.js no los implementa; van al mismo encargo de piezas compartidas.
- 74/B6 · Parcial aceptado: 3 de 9 tarjetas con datos (ROE por grupo, árbol, ROE vs costo del riesgo); cifras verificadas.
- 74/B6 · `cre_contexto` medida «ROE» = ROE TTM − CDI medio 12m (línea 519 de preparar_credito_paginas_powerbi.py), no un ROE trimestral. B6-01-1 se arma directo con esa columna desde bk_cre_contexto. El ROE de cre_calidad coincide con bk_grupo.
- 74/B6 · Cascada que termina en ROA (título «al ROA»): aceptada por ahora; el paso × apalancamiento → ROE va como cifra al pie hasta tener una pieza con dos totales.
- 74/B6 · La brecha banco − mediana que muestra cascada_doble es una resta de presentación entre dos valores visibles: aceptada.
- 74 · Piezas compartidas acumuladas para un solo encargo: apilada_100, pesas, dispersión, barras con intervalo, KPI del riel y selectores de sección; ajustar el título del eje Y de burbujas.
- 74/B6 · Carpeta vacía `capturas/` en la raíz del repo, creada por error: borrarla a mano (la máquina virtual no puede borrar).
- 2026-11-03 · Reclamos fuera por decisión de Pablo (foco en bancos): se eliminan B2-05 (sección completa) y B8-07 del esqueleto en la próxima versión. Encargo 69 cancelado; bk_conducta.parquet se borra (Pablo, a mano) y su contrato sale del verificador.
- 74/B0 · Parcial aceptado (3 de 5 con datos; cifras verificadas). Δ trimestre y Δ año: ahora en bk_sistema_q (d_tt, d_aa), calculados en Python. Spread del riel: usar ICC (costo total del crédito, SGS 25351), no spread_livre. Crédito real del panel: falta deflactar credito_aa de bk_grupo (pendiente del arquitecto); mientras, fila en preparación. Reloj del ciclo: pieza G3 va al encargo de piezas compartidas.
- 74/B4 · Parcial aceptado (5 de 10 con datos; cifras verificadas). NPL total por grupo y del panel: ahora en bk_cartera_grupo (modalidad_id total_pf, total_pj, total_total; panel 2T26 = 3,42 %). Mora adelantada 3 meses: pendiente como serie en Python.
- 74/B4 · Incidente: un worker cerró servidores con pkill por patrón; regla nueva para workers: solo cerrar el PID que lanzaron en la misma llamada.
- 74 · verificar_f0.py se reemplaza por verificar_f1 (encargo de piezas compartidas): «en preparación» solo exigido a tarjetas sin armar.
- 73 · Ficha aprobada (captura revisada; cifras verificadas). Banda sombreada para COSIF 2025 / Res. 4.966: aceptada en vez de la línea vertical.
- 73 · Nuevas métricas en bk_panel/bk_grupo (con percentiles por grupo): npl15_total, pf_share, tarifas_ativo_ttm, cartera_saldo, cartera_vencido15, cartera_saldo_pf y fondeo_* (mix del pasivo + PL, suma 1). `todo` corre ahora cartera antes de base.
- 67 · SCR aprobado: 2012-07 a 2026-08 sin huecos; Banco y Cooperativa calzan exacto; SP jun-26 verificado contra el CSV crudo. Financeira y Fintech difieren de la referencia de agosto porque el BCB reclasificó segmentos (apareció «Instituição de pagamento»): se adopta el dato vigente y se actualiza TASA_JUN26 en el verificador. Para B2-04 (riesgo por tipo de institución): mostrar Fintech e Instituição de pagamento por separado, con nota de la reclasificación.
- 67 · Descarga por ZIP anual con registrar_crudo (no `extraer_fuentes.py scrdata`, que pisa un CSV combinado): aceptada. Los CSV de SCR.data son UTF-8 con BOM, no cp1252.
- 67 · Porte PJ: columna `porte_es` (Micro, Pequeña, Mediana, Grande, Sin dato) para el sitio; `porte` conserva el texto del BCB. `base` registra bk_scr y el universo SCR en el manifiesto.

## 2026-11-03 · Revisión 76 (piezas compartidas) y arranque de 77

- 76 aprobado: piezas nuevas dibujan bien en `_prueba/`; verificar_f1 OK 22/22.
- Decisiones: `linea` no une huecos en ningún sitio; B8 puede subir alto de B8-01-0 y B8-03-1; `verificar_f1.py` reemplaza a `verificar_f0.py`.
- Abierto de 76: pesas/dispersión/trayectoria/barras_ic mezclan SVG y ECharts (aceptado por ahora, revisar al replicar en Power BI); criterio 17 de licencias pendiente; `_to_delete/charts_copia_accidental_76.js` lo borra Pablo.
- MVP: B1, B2, B5, B7, B9, B10 ocultas del menú (`config.js` `oculta: true`, filtro en `pagina.js`). Se abren por URL.
- 77a–e lanzados en paralelo sobre b0, b3, b4, b6, b8.
- 69 (reclamos) llegó parcial tras haberse cancelado: fuera del alcance. Script, encargo y resultado a `docs/orquestacion/descartados/`. El crudo bajado (38 trimestres RDR) queda en `datos/crudo/bcb_rdr/`. Hallazgo para si vuelve: el RDR publica conglomerados sin CNPJ; haría falta un puente manual (28 de 34 sin mapeo).
- 77a (B0) revisado: aprobado para MVP. Cifras cruzan (crédito real 4,5 %, NPL15 panel 3,4 %, ROE panel 16,1 %). verificar_f1 criterio 6 corregido por el arquitecto: cuenta pestañas visibles desde config.js.
  Abierto B0: (a) selector de óptica carga las 5 particiones (~8,7 MB) al abrir → cargar solo modelo y el resto al hacer clic; (b) Δ trimestre del Panel (ROE, NPL) no existe en bk_grupo → agregar valor_tt al gold; (c) crédito real del Panel necesita deflactor en bk_grupo; (d) sección 04 «Puertas» vacía → enlaces a las páginas visibles; (e) bk_qcambio.
- 77b–e revisados con capturas propias (`capturas/arq_*`). Aprobados para MVP con ajustes del arquitecto:
  B3: leyendas en saldo real PF/PJ, dirigido y crecimiento por grupo; eje de crecimiento por grupo topado en 100 % (Pagos 942 % en 2022).
  B4: costo del riesgo y cobertura muestra el grupo del banco activo (sin banco, top 15); fila 04 a 680 px.
  B6: ejes en % (no fracción) y leyendas en ROE por grupo y NIM vs CDI.
  B8: sección 07 Conducta eliminada (reclamos fuera); puente a 430 px. verificar_f1 B8 = 12 tarjetas.
  Nubank: ROE prudencial 51 % es correcto (lucro TTM 10,8 mm / PL medio ~21 mm); nota en `bancos__dashboard.json` y en bk_banco (base suma nota de balances + nota del dashboard).
- Abierto tras 77 (post-MVP): brecha por línea del ROE y ROE − CDI en Python (B6-01-1, B6-02-1); gasto e ingreso totales a/a por grupo (B6-05-1); pesas de eficiencia dominadas por CloudWalk 184 %; NPL y crecimiento en dos paneles (B8-03-2, B6-04-1); mora > 90 adelantada 3 meses (B4-01-1); mosaico_uf (B4-05-1); peso del dirigido por grupo (B3-05-1); 7 categorías del mix (B3-03-0) con PJ agrupado en Python; flechas 1 y 4 del KPI K42; Δ trimestre del panel; selector de óptica en B0 con carga diferida; Basilea (Olinda).

## 2026-11-03 · Ola 4 (encargo 78) lanzada

- 78a gold base/rentabilidad (valor_tt, crédito real, gasto/ingreso totales, brecha del árbol), 78b cartera (mix 7 categorías, dirigido aproximado), 78c sistema (IPCA 12m, IPCA esperado, ICC real ex ante, mora adelantada 3m, d_1m/d_3m), 78d bk_qcambio, 78e front B0 (carga diferida, Puertas) y pieza mosaico_uf.
- Respuesta a 77d duda 1: en `bk_cre_contexto` la medida «ROE» ya es ROE TTM − CDI medio de 4 trimestres (Grandes 4T24: 0,169 − ~0,109 ≈ 0,061). B6-01-1 se arma directo de esa fila en la ola 79, sin cálculo nuevo.
- Integración (arquitecto): `todo`, verificador gold, exportador (Pablo), ola 79 reconecta B3, B4, B6, B8.
- 78b revisado: aprobado. Decisiones: `dirigido_peso` repetido por fila está bien (tabla ancha para el front); el dirigido aproximado incluye Inmobiliario (empresas) e Infraestructura, como dice el encargo, rotulado «aproximado». Pendiente de integración: `bk_cartera_mix7` en el manifiesto y corrida completa de cartera (sin `--solo-mix7`) dentro de `todo`.
- 78c revisado: aprobado. Promedio trimestral para ipca_esperado_12m, icc_real_exante y mora adelantada: confirmado. ICC contra Focus del mismo mes: confirmado (es la expectativa disponible al momento). Quitar las tres últimas filas de la serie adelantada: aceptado.
- 78d revisado: aprobado. Exclusión 2025-T1→T2 en bancos con quiebre: confirmada (misma regla que el gold). Filas sin trimestre anterior: la página las omite (rango vacío). Agregado por el arquitecto: `cuota_credito`, `relevante` (≥ 0,5 % del crédito del panel, 17 bancos) y `rango_relevantes`; la Portada usa la lista de relevantes. Los extremos (CloudWalk NPL −9,8 pp, CoR −13,7 pp) coinciden con IF.Data; probable baja a pérdida, no mejora real: el «sentido» es mecánico por signo.
- 78a revisado: aprobado. Arquitecto agregó NOMBRES de gasto_total_ttm, ingreso_total_ttm, credito_real_aa (base fallaba con KeyError). Brecha en filas de grupo = grupo − mediana de sus bancos: aceptado (la página usa filas de banco). credito_real_aa de grupo hereda el crédito nominal del grupo: aceptado.
- ABIERTO (importante): `credito_aa` del Total panel da −2 % a −4 % en 2025-T2…T4 y +9,5 % en 2026-T2; el salto de valor_tt de credito_real_aa en 2026-T1 (+12 pp) indica que las comparaciones a/a de 2025 cruzan la frontera COSIF 2025 (credito_total cambia de definición). Revisar si credito_aa debe quedar vacío en 2025-T1…T4 para bancos con quiebre o usar muestra constante por era.
- 78e revisado: aprobado. Puertas como tarjeta B0-04-0 → B0 = 6 tarjetas (verificar_f1 y contar_tarjetas actualizados; B8 = 12). import() dinámico en b0.js aceptado por ahora; pasar a un cargador de pagina.js si se repite en otras páginas. Carga inicial de B0: 10,9 MB → 4,0 MB.
- Integración 78 (arquitecto): base → qcambio → base; verificador gold OK (excepción de 20 obs. para series Focus en _q); 108 tests OK. Falta: exportar (Pablo) y ola 79.

## 2026-11-03 · Piel v2 (FARO + paleta Monitor suavizada)

- Pablo encontró el sitio feo en Netlify; canvas «Bancos Brasil — propuesta visual» aprobado con colores suavizados. Aplicado por el arquitecto: tokens.css (paleta suave, Plex Sans/Mono, Bricolage), bancos.css bloque v2 (menú lateral, barra superior con título, secciones a todo el ancho, tarjetas sin dato ocultas), pagina.js (rail, título en barra, repartirFilas), hex fuertes de b*.js suavizados, verificar_f1 ignora fuentes de Google sin red.
- Ola 79 detenida por Pablo a mitad: b3, b4, b6, b8 quedaron con cambios parciales de los workers; el sitio carga sin errores (verificar_f1 OK). Revisar qué alcanzó cada uno antes de relanzar.
- B0: crédito real del Panel visible (a/a omitido por quiebre), Δ trimestre del Panel con valor_tt, «Qué se movió» con relevantes, Basilea fuera.
- Pendiente v2 paso 2: franja de cinco indicadores por página.

## 2026-11-03 · v3: estructura del canvas en las cinco páginas (arquitecto, sin Pablo presente)

- pagina.js: franja declarativa de cinco indicadores (`cfg.franja`: tabla, filtro, delta, tono, vaciar quiebre 2025, banco), tarjetas `plana`, armar recibe codBanco y grupoBanco; estado.js guarda cod_inst del banco.
- charts_bancos.js: componentes `barras_simple` y `mix_banco`. bancos.css: bloque v3.
- B0: franja (crédito real, mora PF, NPL panel, ROE panel, costo real) + Qué se movió / ROE por grupo + drivers + páginas. B3 reescrita (franja + crecimiento PF/PJ + crédito real por grupo + mix del banco). B4, B6, B8: franja + 3–5 secciones con las tarjetas buenas; las demás salen (copias en paginas/*.v1.txt y b0_v1.js.txt, b3_v1.js.txt).
- Conteos: B0 4, B3 3, B4 5, B6 5, B8 8 (verificar_f1 y contar_tarjetas actualizados). verificar_f1 OK.
- Pendiente: Ficha mix de cartera en 7 categorías (hoy 16 modalidades); numeración de secciones salta cuando una sección se oculta sin banco (B6 02); quiebre COSIF 2025 en credito_aa del gold (hoy se vacía en la franja); deploy por Pablo.

## 2026-11-03 tarde · Portada v3 según pedido de Pablo (canvas tablero 05, aprobado)

- Regla de Pablo: tablas siempre descriptivas con estructura fija (m/m, 3m/3m, a/a, 12m/12m; trimestrales t/t, a/a, 4T/4T); nunca gráfico + tabla de la misma serie. ROE sin línea de CDI (solo ROE y ROE − CDI). Cuota por banco: un solo mapa con selector.
- Cada sección es una lámina 16:9 en «Presentar»: botón en la barra superior y en el menú; los selectores de la sección viajan a la lámina; la fila de tarjetas llena el alto.
- Nuevo: preparar_gold_bancos_portada.py → bk_portada_credito, _mora, _roe, _tablas, _cuotas (cuotas desde informes IF.Data r3, r11, r13). Componentes barras_linea y mapa_cuotas.
- Falta en el crudo: SGS 21083 (mora PJ total), 21085 (mora libre total), 21132 (mora direccionado total; código a validar). El script los baja en Windows; si el SGS no los sirve, la fila no aparece.
- Siguiente: páginas Crédito (SCR, contribución m/m, crédito/PIB con HP), Mora, Rentabilidad (cascada NIM→ROE), Márgenes (costo de captación IF.Data r4), Por banco, Productos.

## 3-nov · Crédito v3 construida
- b3.js nuevo (respaldo b3_v2.js.txt): 4 láminas (Por tipo, Qué lo movió, Crédito nuevo, Ciclo); gráfico 5 col izq + tabla_estandar 4 col der, alto 420.
- Posición de tarjetas idéntica a la Portada en Presentar: [60,264,817,598] / [889,264,651,598].
- Contribuciones: «Último» ahora es saldo en R$ mil millones (brl_mm); cambios en pp.
- barras_linea acepta rangoIzq/rangoDer ({escala,min,max}); ciclo con brecha simétrica en torno a 0.
- Tabla estándar: reglas CSS con más especificidad; se quitó `estandar: true` de b0 (la cabecera era distinta entre páginas).
- ESPERADO B3 = 8 en verificar_f1.py y contar_tarjetas.mjs.
- Pendiente: validar nombres SGS de modalidades/concesiones; Mora → canvas.
