# Frente 15 · Hoja «P&L y balance por banco»: gold `bk_pyb` y verificaciones

Estado al 10-nov-2026: **A, B y C hechos; falta lo de «Pendiente» al final** (sin commit). Encargo pensado para que lo ejecute otra sesión u otra LLM sin contexto previo.
Leer antes `CLAUDE.md` y `tareas/README.md`.

## Contexto
- Hoja del canvas de rediseño `PyB.dc.html` (tablero «P&L y balance por banco», canvas «Bancos Brasil · Rediseño de
  gráficos v3», privado), aprobada por Pablo el 10-nov. Tiene selector de banco (los 34 de
  `definiciones/bancos__dashboard.json`) y de trimestre (últimos 12).
- Hoy se alimenta de un borrador, no del pipeline: `tareas/borradores/_salida/extraer_pyb.py` (fuera de git) →
  `pyb.json` en la misma carpeta. Lee `datos/gold/bank_hechos.parquet` (IF.Data, informes 2, 3 y 4, conglomerado
  prudencial) y `datos/gold/bk_panel.parquet` (crédito bruto, pérdida esperada acumulada, activo y patrimonio medio
  12m, ROE, modelo de negocio).
- Secciones: P1 Estado de resultados (tabla), P2 Balance (tabla), P3 Resultado (componentes de la utilidad sobre
  activo medio; ROE), P4 Margen y riesgo, P5 Servicios y gastos, P6 Estructura del balance. Clic en una línea de
  P1/P2 abre su historia: banco contra mediana del grupo y panel (%), banco contra cada par (%) y en R$.
- Columnas de P1: R$ del trimestre, R$ de 12 meses, % del activo medio 12m, mediana del grupo (modelo de negocio),
  panel (suma de los 34 / suma de sus activos) y Δ a/a en pp. P2: R$, % del activo, mediana del grupo, panel, Δ a/a
  en pp y variación a/a en R$.

## Parte A · Mapa común de líneas (dos épocas del plan contable)
Desde 1T25 (Res. CMN 4.966) cambian los nombres de cuenta del IF.Data. La época sale de la columna `era`
(`cosif_2025` / `cosif_pre2025`) de `bank_hechos`, no de si la cuenta existe: hay cuentas con el mismo nombre en las
dos épocas y distinta composición. Nombres de `cuenta_base`:

| Línea | `cosif_2025` | `cosif_pre2025` |
|---|---|---|
| Ingresos de crédito | rendas de operacoes de credito + rendas de arrendamento financeiro + rendas de outras operacoes com caracteristicas de concessao de credito | rendas de operacoes de credito + rendas de operacoes de arrendamento mercantil |
| Tesorería | rendas de titulos e valores mobiliarios + resultado com derivativos + rendas de aplicacoes interfinanceiras de liquidez | rendas de operacoes com tvm + rendas de operacoes com instrumentos financeiros derivativos + rendas de aplicacoes compulsorias |
| Gasto de captación | despesas de captacoes + despesas de instrumentos de divida elegiveis a capital | despesas de captacao + despesas de obrigacoes por emprestimos e repasses + despesas de operacoes de arrendamento mercantil |
| Pérdida esperada | resultado com perda esperada | resultado de provisao para creditos de dificil liquidacao |
| Otros de intermediación | residual: resultado de intermediacao financeira − las cuatro anteriores | ídem |
| Margen financiero antes de pérdida esperada | resultado de intermediacao financeira − pérdida esperada | ídem |
| Servicios y tarifas | rendas de tarifas bancarias + outras rendas de prestacao de servicos | rendas de prestacao de servicos + rendas de tarifas bancarias |
| Transacciones de pago | resultado com transacoes de pagamento | — (va dentro de servicios) |
| Personal / administrativos / tributarios / participaciones | despesas de pessoal / despesas administrativas / despesas tributarias / resultado de participacoes | ídem |
| Otros operacionales | residual hasta resultado antes da tributacao e participacoes | residual hasta resultado antes da tributacao, lucro e participacao |
| Impuestos / participación de empleados | imposto de renda e contribuicao social / participacoes no lucro | imposto de renda e contribuicao social / participacao nos lucros |
| Otros bajo la línea | residual hasta lucro liquido | ídem |

Balance (saldo a fin de trimestre). Activo, informe 2: caja (disponibilidades), interfinancieros (aplicacoes
interfinanceiras de liquidez), títulos y derivativos (2025: titulos e valores mobiliarios + instrumentos derivativos;
pre: tvm e instrumentos financeiros derivativos), crédito bruto y pérdida esperada acumulada (de `bk_panel`:
`credito_bruto`, `ecl_saldo`), otras operaciones con características de crédito (solo 2025, neto), leasing (2025:
operacoes de arrendamento financeiro; pre: arrendamento mercantil liquido de provisao), cuentas por cobrar de pagos
(solo 2025: valores a receber de transacoes de pagamentos - usuarios finais), activo permanente (2025: ativo
permanente; pre: permanente ajustado) y otros activos (residual hasta ativo total). Pasivo, informe 3: depósitos a la
vista, de ahorro, a plazo, interfinancieros y otros (depositos outros + conta de pagamento pre-paga), LCI, LCA, letras
financieras, otras emisiones (obrigacoes por tvm no exterior + demais instrumentos de divida + outros recursos de
aceites e emissao de titulos), pactos (obrigacoes por operacoes compromissadas), préstamos y traspasos, deuda elegible
a capital, patrimonio y otros pasivos (residual hasta passivo total).

**Trampas ya detectadas en el borrador:**
1. `ativo total` aparece en el informe 2 y en el 4 (memo de la DRE), e `instrumentos derivativos` en el 2 (activo) y en
   el 3 (pasivo): pivotear por `num_informe` + `cuenta_base`, nunca solo por `cuenta_base`.
2. El trimestre `1T15`…`4T26` ordenado como texto queda mal (1T15, 1T16, …): ordenar por (año, trimestre) antes de
   sumar 12 meses.
3. `periodo` es AAAAMM; la columna `trimestre` de `bank_hechos` es 1–4, no la etiqueta.

## Parte B · Paso a pipeline (gold)
`pipeline/preparar_gold_bancos_pyb.py` (nombre sugerido) con un gold largo `bk_pyb`:
`cod_inst × trimestre × linea × medida`, con `medida` en {`rs_trim`, `rs_12m`, `pct_activo_medio_12m`} para el P&L y
{`rs`, `pct_activo`} para el balance; más `bk_pyb_grupo` con la mediana por modelo de negocio y el panel (razón de
sumas, no promedio de razones). Mapa de cuentas en `definiciones/pyb_lineas.json` (línea, época, informe, cuentas,
signo, residual sí/no), no en el código. Paso en `actualizar.py` después de `bancos`, contrato, manifiesto y spec
autogenerada.
Tests mínimos:
- Por banco y trimestre, las líneas del P&L suman el resultado de intermediación, el resultado antes de impuestos y
  la utilidad publicados (tolerancia R$ 1 mil); el activo suma el ativo total y el pasivo el passivo total.
- 12 meses = suma de cuatro trimestres **consecutivos**; si falta uno, vacío (el borrador hoy suma por posición).
- Contraste con `bk_panel`: `lucro_liquido_ttm`, `antes_tributacao_ttm`, `provisoes_credito_ttm`,
  `resultado_intermediacao_financeira_ttm` iguales (Itaú 2T26: 48.759, 64.607, −35.449 y 58.597 R$ millones; el
  borrador ya calza).
- Mediana del grupo y panel recalculados desde las filas por banco.

### Sección P7 Capital (agregada el 10-nov)
Lee `bk_capital` por banco (capital principal, Basilea, nivel 1, requerimientos, holgura, apalancamiento, densidad,
activos ponderados por tipo de riesgo, `var_cp_4t`, `lucro_ttm`, `otros_var_cp_4t`) y el crédito bruto de `bk_panel`
para el a/a de la cartera. Mediana por modelo de negocio; panel de `bk_capital_grupo` («Total panel», 31 bancos) para
capital principal, Basilea, densidad, holgura y requerimiento, y razón de sumas de los 34 para apalancamiento y
crecimientos. En el gold, una tabla `bk_pyb_capital` o columnas en `bk_pyb_grupo`; decidir si el panel se unifica en
31 o 34 bancos (hoy la hoja mezcla los dos y lo dice en la nota).

## Parte C · Verificaciones (informe corto en `tareas/borradores/pyb_verificaciones.md`)
1. **Servicios y pagos entre épocas.** Antes de 1T25 los ingresos de transacciones de pago (adquirencia, tarjetas) van
   en servicios; desde 1T25 en línea propia. Confirmar contra la nota del BCB del plan 2025 y decidir si la hoja suma las
   dos líneas en todo el período (hoy: separadas en la tabla, sumadas en el gráfico P5).
2. **Crédito antes y después de 1T25.** `credito_bruto` de `bk_panel` toma solo «operações de crédito»; en 2025 la
   tarjeta y otras quedan en «outras operações com características de concessão de crédito» (Itaú 2T26: R$ 240 mil
   millones netos), que antes de 1T25 estaba dentro de «outros créditos». Proponer una línea de crédito total
   comparable entre épocas.
3. **Residuales grandes.** Listar banco-trimestre donde un residual («otros de intermediación», «otros
   operacionales», «otros activos», «otros pasivos») supere el 20 % de su subtotal y explicar qué cuenta lo genera.
4. **12 meses que cruzan 1T25.** Medir el salto de cada línea en 1T25–4T25 por banco; si es por reclasificación, la
   hoja ya muestra la banda «Res. 4.966»: confirmar si basta.
5. **Historia corta.** PicPay, CloudWalk, Neon, Mercado Pago, PagSeguro y Cielo tienen menos de 5 años en el IF.Data
   prudencial; confirmar que no falten trimestres por el escopo (prudencial vs. individual).
6. **Signos.** Gastos e impuestos vienen negativos; confirmar en todos los bancos (Itaú tuvo impuesto positivo en
   2T25 y 1T26, crédito fiscal).

## Parte D · Fuera de alcance
- Desglose del margen por producto o por moneda: no está en el IF.Data.
- Conciliación con los estados contables de la CVM: es el frente 7 (`bk_publicado`); solo 15 bancos.

## Terminado cuando
A aplicado en `definiciones/pyb_lineas.json`; B con gold, tests y contraste con `bk_panel` en verde; C informado;
`extraer_pyb.py` leyendo solo de gold y con el mismo `pyb.json` (tolerancia 0,01) salvo los cambios que justifique C.
Nada se commitea sin pedirlo a Pablo.

## Estado (10-nov-2026)
- **A.** `definiciones/pyb_lineas.json`: 45 líneas (19 P&L, 11 activo, 15 pasivo) por época, con informe, cuentas,
  signo y tipo (`cuentas`, `total`, `panel`, `subtotal`, `residual`), más la lista `fondeo`. Nombres verificados contra
  `bank_hechos` (test `test_cuentas_del_mapa_existen_en_bank_hechos`). Cambios contra la tabla de arriba: «otros
  depósitos» suma `outros depositos` (hasta 1T20) y `depositos outros` (desde 2T20) más la prepaga; no se usan los
  subtotales `outros instrumentos de divida` ni `recursos de aceites e emissao de titulos`.
- **B.** `pipeline/preparar_gold_bancos_pyb.py` → `bk_pyb` (180.794 filas) y `bk_pyb_grupo` (15.573), con contrato y
  paso `pyb` en `actualizar.py` después de `capital` (no de `bancos`: lee `bk_capital`, `bk_capital_grupo` y la Selic de
  `bk_producto_pf_m`). Además de lo pedido lleva la sección capital (P7) y la de sensibilidad a la Selic que el borrador
  agregó el 10-nov. Trimestres sin datos publicados (el BCB da «null») quedan vacíos, no en cero; 12m y a/a sobre
  trimestres consecutivos. `tests/test_pyb.py`: 16 pruebas en verde (incluye el contraste con `bk_panel`: 1.353
  banco-trimestres iguales en las cuatro métricas; Itaú 2T26 48.759 / 64.607 / −35.449 / 58.597).
  `tareas/borradores/_salida/extraer_pyb.py` ya lee solo gold; la versión anterior quedó en
  `extraer_pyb_borrador_previo.py` y su salida en `pyb_previo.json`.
- **C.** `tareas/borradores/pyb_verificaciones.md` (seis puntos con cifras y propuesta).

### Pendiente
- Correr `pipeline/manifiesto_gold.py` (hoy `verificar_gold --gold` marca que `bk_pyb` y `bk_pyb_grupo` no tienen fila
  en `bk_manifiesto`) y `herramientas/generar_spec.py`. No se corrieron por las sesiones en paralelo.
- Decisiones de Pablo: panel de capital 31 o 34 bancos; líneas brutas en 12m que cruzan 1T25 (punto 4 de C); línea de
  crédito total comparable (punto 2); notas de PicPay/Original y BRB (punto 5); rótulo de «otros activos» en Pagos
  (punto 3).

## Decisiones de Pablo del 10-nov (tarde) y pendientes de pipeline
Aplicado en la hoja (`PyB.dc.html`, solo presentación):
- Tesorería, captación, servicios, pagos y los «otros» del P&L: 12 meses y % del activo medio vacíos de 1T25 a 3T25
  y Δ a/a sin comparar entre planes; en balance, Δ a/a sin comparar entre planes para otros activos, otros pasivos,
  deuda elegible, otras operaciones de crédito y cuentas por cobrar de pagos.
- Mediana del grupo recalculada en la página sin Original en 4T24; notas para Original, PicPay, BRB, adquirentes
  (pagos que venían en «otros operacionales») e impuesto positivo (crédito fiscal).
- Grupo Pagos: «Otros activos» se rotula «Recebíveis y otros activos realizables».
Para hacer en pipeline:
1. Columna `comparable_entre_planes` en `definiciones/pyb_lineas.json` y que `bk_pyb` deje vacíos los 12 meses de
   1T25–3T25 de las líneas no comparables (hoy lo hace la página).
2. `bk_pyb_grupo`: excluir Original 4T24 de la mediana de su grupo.
3. Panel de capital: unificar en 34 bancos, con razón de sumas desde `bk_capital` (hoy la hoja usa el panel de
   `bk_capital_grupo`, de 31 bancos, para índices, holgura y densidad, y 34 para apalancamiento y crecimientos).
   Revisar también la hoja «Bancos · agregados», que usa el mismo panel de 31.

## Decisiones de Pablo (11-nov, desde el celular)
- Líneas brutas (tesorería, captación, servicios, pagos, otros de intermediación, otros operacionales; en balance otros
  activos, otros pasivos, deuda elegible, otras op. de crédito, pagos): **12m y % del activo vacíos en 1T25–3T25**;
  el 12m vale desde 4T25 (cuatro trimestres del plan nuevo) y su a/a desde 4T26 (4T26 contra 4T25). Marca
  «comparable entre épocas» por línea en `pyb_lineas.json`. Las netas quedan con la banda «Res. 4.966».
- Crédito: **«Crédito bruto» como línea comparable**; «otras op. con características de crédito» y «pagos» solo desde
  1T25, con banda.
- Panel de capital: **unificar en 34 bancos**, razón de sumas desde `bk_capital`.
- Aplicar: nota PicPay/Original (Original 4T24 fuera de la mediana del grupo); nota BRB «no publica desde 4T25»;
  en el grupo Pagos, «Recebíveis y otros activos realizáveis» en vez de «Otros activos»; impuesto con su signo y nota
  «positivo = crédito fiscal».
