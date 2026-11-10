# Frente 15 · Verificaciones de la hoja «P&L y balance por banco» (parte C)

10-nov-2026. Fuente: `bk_pyb` / `bk_pyb_grupo` recién publicados (mapa en `definiciones/pyb_lineas.json`),
`bank_hechos`, `bk_panel` y el cadastro crudo de IF.Data. R$ en millones salvo indicación; «% activo» = flujo del
trimestre × 4 / activo total del panel (bancos con dato). Cada punto cierra con una propuesta; las decisiones son de
Pablo.

## 1. Servicios y transacciones de pago entre épocas

**Confirmado con la composición COSIF de `bank_hechos`** (no se consultó la nota del BCB en línea): desde 1T25
«resultado com serviços por transações de pagamento» es la cuenta 7.1.7.05, que se resta de «outras rendas de
prestação de serviços» (7.1.7 − tarifas − 7.1.7.05); antes de 1T25 estaba dentro de «rendas de prestação de
serviços» (7.1.7). Pero la línea nueva tiene tres partes y solo la primera venía de servicios:

| 12m a 2T26, panel | R$ mm |
|---|---|
| Servicios por transacciones de pago (l1, antes en servicios) | 63.806 |
| Pérdida esperada de transacciones de pago (l2) | −2.164 |
| Otros resultados con transacciones de pago (l3; cuentas 7.1.9.18/7.1.9.81, antes en «outras receitas operacionais») | 48.305 |
| Transacciones de pago (total) | 109.947 |
| Servicios y tarifas (sin pagos) | 140.173 |

Continuidad en el panel (% activo anualizado): servicios solos 1,73 (4T24) → 0,93 (1T25); servicios + pagos
1,73 → 1,69 → 1,71 (2T25); servicios + solo l1 1,73 → 1,42. La suma completa es la que empalma en el agregado. En
las adquirentes no alcanza: Stone pasa de servicios 1.001 + otros operacionales 1.431 (4T24) a pagos 2.842 + otros
−277 (1T25); PagSeguro 2.260 + 381 → 2.901 − 132; Mercado Pago 3.748 − 2.384 → 2.222 − 83. En ellas l3 (MDR y
descuento de recebíveis) venía en «otros operacionales».

**Propuesta:** mantener la hoja como está (tabla separada, gráfico P5 con servicios + pagos sumados en todo el
período) y agregar en la nota que en adquirentes (grupo Pagos) parte de «pagos» venía antes en «otros
operacionales», así que su salto de 1T25 no es crecimiento. No recomiendo partir «pagos» en l1/l2/l3 en la tabla: el
grano no existe antes de 1T25.

## 2. Crédito antes y después de 1T25

`credito_bruto` (bk_panel) es solo «operações de crédito» en las dos épocas. Lo demás:

| Panel (34) | 3T24 | 4T24 | 1T25 | 2T25 | 2T26 |
|---|---|---|---|---|---|
| Crédito bruto | 5.031.705 | 5.213.353 | 5.336.178 | 5.427.395 | 5.876.329 |
| «Outros créditos − líquido» (solo antes de 1T25) | 1.809.839 | 2.002.311 | — | — | — |
| Otras op. con características de crédito, neto (desde 1T25) | — | — | 770.763 | 782.964 | 863.667 |
| Cuentas por cobrar de pagos (desde 1T25) | — | — | 428.230 | 438.291 | 504.854 |
| `credito_total` de bk_panel | 6.589.170 | 6.960.845 | 6.208.842 | 6.310.096 | 6.853.502 |
| Cartera del informe de crédito (`cartera_saldo`) | 5.073.470 | (sin 4T24) | 5.479.572 | 5.581.012 | 6.173.554 |

Itaú: 4T24 crédito 836.321 + outros créditos 483.749; 1T25 crédito 827.012 + otras op. 223.226 + pagos 125.595. De
los 2,0 billones de «outros créditos» del panel en 4T24 solo ~1,2 billones reaparecen como otras op. + pagos; el
resto (créditos tributarios, deudores diversos, rentas a cobrar) pasó a «outros ativos realizáveis». Por eso
`credito_total` de bk_panel cae −10,8 % en 1T25: no es comparable entre épocas.

**Propuesta:** (a) en P2 dejar «Crédito bruto» como línea comparable (operaciones de crédito en las dos épocas) y
mostrar «otras op. con características de crédito» y «pagos» solo desde 1T25, con la banda; (b) para una línea de
«crédito total» comparable usar la cartera del informe de crédito (`cartera_saldo`, que ya incluye tarjeta y otras
modalidades en las dos épocas; +8,0 % 3T24→1T25 contra +6,1 % del crédito bruto), sabiendo que le falta 4T24 y
que el escopo de esos informes cambió en 2025 (spec/08). No se puede reconstruir la tarjeta dentro de «outros
créditos» antes de 1T25 con el informe 2.

## 3. Residuales grandes

Qué cuenta los genera (verificado con diferencia 0 contra `bank_hechos`):
- **Otros de intermediación** = «resultado de operações de câmbio» antes de 1T25; «outros resultados de
  intermediação financeira» desde 1T25.
- **Otros operacionales** = «outras receitas/despesas operacionais» + resultado no operacional antes de 1T25;
  «outras receitas» + «outras despesas» + pérdida esperada de otras operaciones desde 1T25.
- **Otros activos** = «outros ativos realizáveis» (+ ajustes de hedge del crédito, R$ 23 mm en Itaú 2T26); antes de
  1T25 además «outros créditos − líquido» (Itaú 2T24: 463.751 de 717.275).
- **Otros pasivos** = «outras obrigações» + derivativos del pasivo (diferencia 0); antes de 1T25 también la deuda
  subordinada y los resultados de ejercicios futuros.

Casos sobre 20 % del subtotal (12m para P&L; saldo para balance): en toda la historia 221 de 1.353 banco-trimestres
en otros de intermediación / |resultado de intermediación|, 985 en otros operacionales / |antes de impuestos|
(denominador chico: no es buena medida), 709 de 1.475 en otros activos / activo y 666 en otros pasivos / pasivo. En
2T26: 6, 27, 11 y 13. Los más grandes en 2T26:
- Otros activos / activo: Cielo 90,6 %, CloudWalk 87,4 %, Stone 86,5 %, PagSeguro 84,3 %, Mercado Pago 68,2 %,
  Nubank 32,9 %, PicPay 32,0 %, BNDES 29,9 %. En las adquirentes es la cuenta de recebíveis de tarjeta
  («outros ativos realizáveis»): es su activo principal, no un resto.
- Otros pasivos / pasivo: Cielo 77,7 %, Banco da Amazônia 66,0 %, Porto Seguro 61,1 %, Banco do Nordeste 44,4 %,
  Stone 38,3 %, Mercado Pago 33,7 %. Fondos constitucionales (BASA, BNB), obligaciones con establecimientos
  (adquirentes) y provisiones técnicas o de tarjeta (Porto).
- Otros de intermediación / |RIF| 12m: Santander 134,5 %, CloudWalk 132,6 %, Safra −43,5 %, Original 37,5 %,
  Bradesco 23,1 %, BB 21,8 %.
- Panel: otros activos 25,4 % del activo en 4T24 y 17,8 % en 2T26; otros pasivos 21,1 % y 14,1 %.

**Propuesta:** para el grupo Pagos agregar una línea de activo «Recebíveis y otros activos realizáveis» con
rótulo propio en vez de «Otros activos» (es la misma cuenta, cambia la lectura); en el resto dejar los residuales
como están. Si se quiere bajar el residual de pasivos, la siguiente cuenta a abrir es «outras obrigações» (no está
desagregada en el informe 3; requeriría otra fuente).

## 4. 12 meses que cruzan 1T25

Panel, % activo anualizado, 4T24 → 1T25 → 2T25: tesorería 6,51 → 2,20 → 2,59; captación −10,59 → −5,24 → −6,69;
servicios 1,73 → 0,93 → 0,95; otros operacionales −0,55 → +0,73 → +0,34; ingresos de crédito 7,58 → 6,15 → 6,92.
Pero el margen antes de pérdida esperada 4,25 → 3,69 → 3,61 → 4,04 (2T26) y el resultado antes de impuestos
1,73 → 2,09 → 1,41 se mueven dentro de su rango normal. Desde 1T25 la variación cambial y los ajustes de hedge van
dentro de cada línea (Itaú 2T26: +21.195 de variación cambial dentro de captaciones en el semestre), cuando antes
iban en cambio (otros de intermediación) y derivativos: las líneas brutas se achican a ambos lados. Saltos por banco
(1T25 contra 4T24, > 3 veces su variación trimestral típica 2018–4T24): pagos 30 bancos, servicios 22, crédito 19,
otros operacionales 18, captación 16, otros de intermediación 13, tesorería 10; margen 5, antes de impuestos 4,
utilidad 2. Balance (pp del activo, mediana): otros activos −5,4, otros pasivos −2,6, deuda elegible a capital +1,9,
otras op. de crédito +1,0, pagos +1,0. Itaú: tesorería −8,6 pp y captación +9,0 pp en el mismo trimestre.

**Propuesta:** la banda «Res. 4.966» basta para las líneas netas (margen, pérdida esperada, resultado de
intermediación, antes de impuestos, utilidad, ROE). No basta para las brutas: tesorería, captación, servicios,
pagos, otros de intermediación y otros operacionales, y en balance otros activos, otros pasivos, deuda elegible,
otras op. de crédito y pagos. Para esas, dejar vacío (o rayado) el 12m y el % del activo medio de 1T25–3T25 (los
que mezclan planes) y comparar a/a solo desde 4T25 contra 4T25. Pide una columna o lista «comparable entre épocas»
en `pyb_lineas.json`; no lo apliqué.

## 5. Historia corta

No faltan trimestres por el escopo en el prudencial. Cadastro de IF.Data contra `bank_hechos`:
- Nubank y Cielo figuran en el cadastro desde 2T17 y Stone desde 3T17, pero el BCB no publica valores para esos
  conglomerados hasta 4T17 (los archivos de 2T17 y 3T17 no traen filas de ellos). Mercado Pago y PagSeguro
  empiezan en 4T18, Neon en 2T21 y CloudWalk en 4T22, igual en cadastro y valores.
- **PicPay** es el caso a mirar: de 3T23 a 3T24 estuvo dentro del conglomerado prudencial «ORIGINAL» (C0080903,
  liderado por la IP PicPay); en 4T24 se separa en «PICPAY − PRUDENCIAL» (C0088022). Original cae de R$ 49.944 mm de
  activo (3T24) a 28.278 (4T24) y PicPay arranca con 27.620. La historia previa de PicPay está mezclada con la de
  Original y no se puede separar con el prudencial; además el 4T24 de Original sale de desacumular un semestre de
  dos perímetros distintos (gasto de personal +180, tributarios +63, servicios −419: ver punto 6).
- Huecos de origen (el BCB publica «null»), que ahora quedan vacíos y no en cero: BRB 3T22 y 4T25–2T26 (y sin
  resultados en 4T22), XP 3T15–3T16 (y sin resultados en 4T16), Agibank 1T14–1T15 (y sin resultados en 2T15), Neon
  2T25 (todo el trimestre). El primer trimestre de
  resultados de cada banco nuevo tampoco existe (es un 4T o un 2T y no hay trimestre anterior para desacumular):
  Stone, Nubank y Cielo 4T17, Mercado Pago y PagSeguro 4T18, Neon 2T21, CloudWalk 4T22, PicPay 4T24.
- El escopo individual no está bajado (solo hay escopo 1 para los informes 2–4), así que no se probó si PicPay o los
  otros tienen historia individual anterior.

**Propuesta:** nota en la hoja para PicPay y Original («hasta 3T24 Original incluye PicPay; 4T24 de Original no es
comparable») y excluir Original 4T24 de la mediana de su grupo, o marcarlo. Para BRB, decir en la nota que no
publica desde 4T25.

## 6. Signos

Sobre 1.464 banco-trimestres con resultados: personal positivo 3 (BTG 4T16 +191, Original 4T24 +180, PagSeguro
4T19 +60), administrativos 1 (BTG 4T16 +85), tributarios 5 (Original 4T24 +63, C6 4T19 +9 y tres menores a 5),
captación positiva 13 (2T21 en Itaú +2.137, Santander +5.164, BNDES +890, Votorantim, ABC, Daycoval; 4T20 en
varios: variación cambial con el real apreciándose), participación de empleados positiva 22 (casi todas < 15; Caixa
4T18 +253, Votorantim 2T15 +140). Ingresos de crédito negativos en 20 (Stone 2018–2023, PagSeguro 4T23 −1.667, ABC
2020–21 y 1T25): ajustes a valor justo o cambiales. Los gastos positivos son reversiones de un 4T o 2T al
desacumular (BTG 4T16, Original 4T24, PagSeguro y C6 4T19), no errores del mapa. El impuesto positivo es normal: 516
de 1.464 trimestres y 486 de 1.353 en 12m (16 bancos en 2T26); Itaú lo tiene en 2T25 (+2.738) y 1T26 (+417), además
de 13 trimestres anteriores (crédito fiscal y JCP).

**Propuesta:** no forzar signos. En la tabla, mostrar el impuesto con su signo y una nota «positivo = crédito
fiscal». El test `test_signos_de_gastos` tolera menos de 1 % de trimestres positivos en personal, administrativos,
tributarios y captación.
