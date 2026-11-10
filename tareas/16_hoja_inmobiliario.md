# Frente 16 · Hoja «Inmobiliario»: códigos SGS que faltan y paso a gold

Estado al 10-nov-2026: **A y B hechas; C por hacer**. Encargo pensado para que lo ejecute otra sesión u otra LLM sin contexto previo.
Leer antes `CLAUDE.md`, `tareas/README.md` y `tareas/12_hoja_tarjeta.md` (mismo patrón de gold por producto).

## Contexto
- Hoja del canvas `Inmobiliario.dc.html` (6 secciones: Volumen, Precio, Calidad, Deudor, Emisor, Fondeo), construida el
  10-nov con la propuesta aprobada `ProdInmobiliario.dc.html`. Borrador: `tareas/borradores/_salida/extraer_inmobiliario.py`
  (fuera de git) → `inmobiliario.json`.
- Fuentes: crudo SGS (20612, 20702–20704, 20772–20774, 21149–21151, 4189), cubo SCR producto «Inmobiliario» (el
  borrador lo calcula en memoria con `preparar_gold_bancos_producto_pf.construir_scr`, sin publicar), IF.Data
  (`bk_cartera_mix7`, categoría hipotecario) y `bk_fondeo_m` (ahorro y letras de crédito).

## Parte A · Datos SGS · hecha el 10-nov
- 20610 (saldo PF con tasa de mercado) y 20611 (con tasa regulada) se bajaron de la API (en el crudo
  `bancos_sistema`, R$ millones, desde mar-07). Identidades verificadas (±1 por redondeo): 20610 + 20611 = 20612
  (sep-26: 170.988 + 1.272.018 = 1.443.006) y 20702 + 20703 = 20704 (concesiones).
- En `sgs.CODIGOS` y en el catálogo (196 series): `credito_pf_inmobiliario_{mercado,regulada}`,
  `conc_pf_inmobiliario_{mercado,regulada,total}` y `tasa_pf_inmobiliario_{mercado,regulada,total}`. Ya estaban:
  20612 (`credito_pf_inmobiliario`), 21149–21151 (mora90; ojo: 21150 se llama `mora90_inmobiliario_dirigido` pero es
  la de tasas reguladas) y 4189 (Selic del mes). 20600 (`credito_pj_inmobiliario`) también.
- Resto de la carpeta `crudo/bcb_sgs/inmobiliario` (identificado contra el catálogo del SGS): 21340 = IVG-R (índice de
  valor de garantía de inmuebles residenciales financiados), 21387 / 21395 = encuesta trimestral de crédito
  habitacional (demanda / oferta observada), 240 = captación líquida diaria de poupança SBPE (R$ mil), 192 = INCC,
  433 = IPCA. Propuesta: IVG-R a la sección Calidad (valor de la garantía) y 240 a Fondeo (flujo de poupança); los
  demás quedan de contexto. Decide Pablo.

## Parte B · Paso a gold · hecha el 10-nov
- `preparar_gold_bancos_producto_pf.py`: producto `inmobiliario` en `PRODUCTOS_SGS` (subs total, mercado y regulada,
  con saldo, concesiones, tasa y mora90), en `DESCOMPONER` (mercado / regulada, peso = concesiones del mes) y en
  `PRODUCTOS_SCR` («Inmobiliario»). En el SCR los bancos son el 99,3 % del saldo (sep-26): fintechs (0,03 %, mora
  ~37 %), financieras (0,002 %) e instituciones de pago (no hay) van a «Otros» (`OTROS_INSTITUCION`). Con eso la
  dimensión «institución» casi no informa: Bancos, Cooperativas y Otros.
- Gold reconstruido: `bk_producto_pf_m` 19.181 filas, `bk_producto_pf_scr_m` 1.106.404. SCR contra SGS a sep-26:
  R$ 1.471 mil millones contra 1.443 (+2 %).
- Tests: el cuadre de partes (mercado + regulada = total, ±1) entra en `test_gold_sgs_totales_cuadran`, y
  `test_gold_inmobiliario_scr_calza_con_sgs` es nuevo (suite: 262 pasan; verificador de gold OK).
- El borrador `extraer_inmobiliario.py` lee solo gold (copia del anterior en el scratchpad de la sesión). Cambios
  contra el JSON previo: P1 mercado / regulada ya con datos (antes «en preparación»), concesiones y tasas con sep-26
  (el crudo viejo llegaba a ago-26) y «Financieras» sumada a «Otros» en las vistas por institución.

## Parte C · Verificaciones
1. Activo problemático 5,1 % contra mora 1,5 % (sep-26): confirmar que la diferencia son reestructuraciones y no un
   cambio de definición de la Res. 4.966; medir desde cuándo.
2. Concesiones con tasa de mercado contra regulada. Las cifras del spec original (−39 % / +26 %) no se reproducen; a
   sep-26: 12 meses a/a −1,2 % y +28,1 %; mes contra mismo mes del año anterior −34 % y +7 % (peso de mercado en las
   concesiones del mes: 17,6 %): confirmar con las notas del BCB o de la Abecip
   si es traslado de originación de SBPE-mercado a SFH/MCMV.
3. Cobertura poupança / crédito inmobiliario: 71 % a sep-26 (80 % un año antes) es una sobreestimación con dos
   sesgos. Denominador: el SBPE financia también a constructoras, así que corresponde PF + PJ (20612 + 20600), no
   solo PF. Numerador: 1835 es la poupança total e incluye la poupança rural (va a crédito rural, no a vivienda);
   buscar el saldo de la poupança SBPE sola (SGS o Abecip) antes de publicar el ratio. Sin ese código, la tarjeta va
   con nota o «en preparación»; no estimar.
4. Cuántas LCI hay dentro de «letras de crédito» (27807 junta LCI y LCA). El REF no sirve: el 1.2.1.1.a también las
   publica juntas («Letras com isenção tributária (LCA/LCI)»; revisado en `bk_ref` el 10-nov). Queda B3 o Abecip
   (fuente nueva, preguntar a Pablo) o dejar P6 como cota superior con su nota.

## Terminado cuando
A y B en verde (catálogo, gold, tests), C informado en `tareas/borradores/inmobiliario_verificaciones.md`, y la hoja
regenerada desde gold sin series «en preparación». Nada se commitea sin pedirlo a Pablo.
