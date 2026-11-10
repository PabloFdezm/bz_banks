# Frente 12 · Parte C: verificaciones de la hoja Tarjeta

Fecha: 10-nov-2026. Fuentes: crudo SCR.data (`scrdata_2025.zip`, `scrdata_2026.zip`, meses 202509 y 202609, PF) y el
gold `bk_producto_pf_scr_m`. Cifras en R$ mil millones salvo indicación. No se cambió el pipeline por este informe.

## 1. Instituciones de pago sin mora: confirmado, por mezcla de producto
- En sep-26 las IP tienen R$ 116,8 de tarjeta y el **100 %** está en «compra à vista e parcelado lojista» (factura
  corriente y cuotas sin interés del comercio). No tienen rotativo, cuotas con interés ni «não migrado». Esa
  submodalidad tiene mora cerca de 0 en todos los emisores: bancos 0,4 %, financieras 0,0 %, cooperativas 0,0 %.
- La deuda que paga interés vive en bancos y financieras. Financieras: contado 40 %, cuotas/saque financiado 36 %
  (mora 17 %), «não migrado» 17 % (mora 86 %), rotativo 6 % (mora 33 %). Por eso su activo problemático es de 27 %.
- Que la factura impaga de la IP pase a la financiera *del mismo grupo* es consistente con el marco (la IP no da
  crédito; el financiamiento lo hace una institución financiera), pero el SCR.data no identifica a la institución y no
  se verificó por conglomerado. Para eso haría falta IF.Data por conglomerado o las notas de cada compañía.
- Efecto en la hoja (sep-26, tarjeta): el aporte de las IP a la Δ mora a/a es −0,02 pp y su efecto mezcla propio es 0,0
  (su tasa es ~0). La expansión de las IP resta por dilución en el resto: la mezcla por institución suma −0,33 pp (de
  ella, financieras −0,22 pp).
- **Propuesta:** separar la tarjeta en «con interés» (rotativo, cuotas/saque financiado, «não migrado») y «contado» en
  el cubo SCR (dos productos en `definiciones/scr_productos.json`) y hacer P4 y P7 sobre la tarjeta con interés, que
  además es comparable con la mora SGS (21127/21128). Costo: cambia la versión del caché y obliga a reprocesar los
  ZIP 2018–2026 una vez. Alternativa barata, peor: agrupar «IP + financieras» en P4 y P7.
- **Hallazgo adicional:** el +1,78 pp de mora a/a de la tarjeta lo explican los bancos (+1,85 pp). En bancos, el
  «não migrado» pasó de 40,9 a 54,3 y la mora del rotativo de 5,9 % a 15,9 % entre sep-25 y sep-26. Conviene una
  nota o una línea de la hoja con la mora por submodalidad del SCR (sale gratis si se hace la separación de arriba).

## 2. Quiebres de renta del SCR: el diagnóstico de la spec estaba incompleto
- **Jul-25** (reclasificación): en los cuatro productos los tramos de hasta 2 SM pierden peso de golpe (tarjeta: 1–2 SM
  18,5 % → 15,7 %; vehículos: hasta 1 SM 5,4 % → 3,3 %) y suben los tramos altos. Ya **no** afecta el a/a de sep-26,
  porque la base (sep-25) es posterior; sí distorsionó los a/a de jul-25 a jun-26.
- **Jul-26, no ago-26:** en tarjeta, «más de 20 SM» salta de 85,7 a 100,3 en jul-26 y vuelve a 86,3 en ago-26. Es un
  pico de un mes; «sin renta / N.D.» casi no se mueve (35,5 → 38,4). No hay R$ 15 mil millones que pasen a N.D. en
  ago-26: la nota de `preparar_gold_bancos_scr_productos.py` («ago-26 ~R$ 15 mil millones de tarjeta pasan de «más de
  20 SM» a «Indisponível»») está mal y hay que corregirla. En planilla y vehículos sí hay un salto de N.D. en jul-26
  (planilla 3,6 % → 5,1 %; vehículos 5,8 % → 7,7 %) que persiste.
- **El +0,78 pp de «sin renta / N.D.» en tarjeta es sobre todo efecto tasa (+0,66), no mezcla (+0,12).** La mora del
  segmento pasa de 12,6 % a 26,2 % entre sep-25 y sep-26, con un escalón en ene–feb-26 (9,1 % en dic-25 → 18,7 % →
  28,5 %), y su saldo oscila entre 30 y 42 de un mes a otro. Es lo que se ve si la cartera morosa queda con la renta
  «Indisponível» (clientes en atraso a los que no se les actualiza la renta): composición del segmento, no riesgo
  nuevo. No se puede probar con datos agregados. En personal pasa lo mismo (11,3 % → 21,4 %; aporte +0,37 de +2,59 pp).
- **Propuesta:**
  1. «Sin renta / N.D.» va aparte, como segmento sin tramo y con nota, no entre los tramos (en el mix, renormalizar a
     los 7 tramos con renta, como ya hace `bk_scr_series`).
  2. En los aportes por renta, mostrar el total de los 7 tramos y el de N.D. por separado, para que el lector vea
     cuánto de la Δ mora viene de clientes con renta conocida (en tarjeta: +1,00 de +1,78 pp).
  3. Bandas rotuladas en jul-25 («reclasificación de renta»), ene–feb-26 («mora de N.D.: cambio de composición») y
     jul-26 («pico de un mes en más de 20 SM»).
  No se recomienda empalmar series: no hay información para repartir lo reclasificado.

## 3. Ocupación «Otros»: es una categoría de la fuente, no un problema del mapeo
- Los valores de `cnae_ocupacao` de personas en el SCR son ocho: Aposentado/pensionista, Autônomo, Empregado de empresa
  privada, Empregado de entidades sem fins lucrativos, Empresário, MEI, **Outros** y Servidor ou empregado público. El
  mapeo actual cubre siete; «Otros» de la hoja es exactamente «Outros» del SCR. No hay valores sueltos que reasignar.
- «Outros» pesa ~31 % del saldo en los cuatro productos (tarjeta 240,6 de 758,0 en sep-26) y crece más que el resto
  (tarjeta +14,1 % a/a; aporta +4,39 pp de +11,7 pp). Su mix de renta es mucho más bajo: en tarjeta 47 % hasta 2 SM
  contra 14 % en el resto, y 22,5 % está en IP. Parece «ocupación no informada o informal» más que un grupo propio.
- **Propuesta:** rotular «Otros / no informado (SCR)», dejarlo como último segmento con color neutro y nota. Es el
  dato de la fuente: no hay mejor mapeo posible con el SCR.data.

## 4. Ticket: `ops` son operaciones, y el SCR no trae clientes
- El CSV del SCR.data trae `numero_de_operacoes` y ninguna columna de clientes (encabezado completo revisado:
  data_base, uf, segmento, cliente, cnae_ocupacao, porte, modalidade, submodalidade, origem, indexador,
  numero_de_operacoes, vencimientos por plazo, carteira_ativa, carteira_inadimplencia, ativo_problematico).
- `-1` es secreto estadístico (menos de 15 operaciones): 35.762 filas de PF en sep-26, pero solo el 0,01 % del saldo de
  tarjeta y de planilla queda fuera del ticket. No sesga.
- **Propuesta:** el rótulo dice «saldo medio por operación», no «por cliente». En tarjeta una persona puede tener
  varias operaciones (tarjetas, submodalidades), así que el ticket subestima la deuda por cliente; decirlo en la nota.
  El conteo de clientes por renta solo existe en microdatos del BC (fuera de alcance, Parte D).

## 5. Selic en la hoja: decisión de Pablo
- Hoy: meta Selic (SGS 432), último dato del mes, en `bk_producto_pf_m` (producto `referencia`).
- Las tasas del SGS por modalidad son promedios del mes de las concesiones. Lo consistente es comparar contra la Selic
  efectiva promedio del mes (SGS 4189, «Taxa de juros - Selic acumulada no mês anualizada base 252», % a.a., mensual;
  nombre confirmado contra el SGS el 10-nov). La diferencia importa solo en los meses de cambio de meta.
- **Recomendación:** pasar al promedio del mes. Pendiente de confirmación.

## 6. Personal sin planilla (parte E)
- **IP con mora de 32 %:** son R$ 0,14 mil millones (0,04 % del saldo) y el 100 % figura con renta «Sem rendimento»;
  parece una sola entidad que informa así. Mora 39 % en sep-25 y 32 % en sep-26. Aporte a la Δ mora: 0,00 pp. No es
  material; **propuesta:** sumarla a «Otros» en esta hoja.
- **Financieras +22 mil millones contra bancos −4,5 (sep-25 → sep-26):** no hay escalón de traspaso. Las financieras
  crecen R$ 2–3 mil millones por mes de forma pareja, con operaciones que acompañan (ticket estable en ~R$ 1.250), y
  los bancos se estancan desde dic-25 con operaciones planas. En IF.Data (conglomerados) el crecimiento del personal
  2T25 → 2T26 está en Nubank (+13,7), Mercado Pago (+7,8) y PicPay (+3,3): fintechs que prestan desde sociedades
  financieras. Es crecimiento orgánico de ese grupo, no traspaso. Solo se ve un posible movimiento dentro de un grupo:
  Original −5,5 y PicPay +3,3. El SCR no identifica instituciones, así que el cruce es inferencia.
- **Propuesta:** nota en P7: «financieras = sobre todo fintechs (Nubank, Mercado Pago, PicPay)». Sin cambio de cálculo.

## 7. Descuento por planilla (parte F)
- **21116 mide toda la cartera del consignado privado**, sin separar el programa nuevo (MP 1.292, mar-25). Pero el saldo
  pasó de 41,6 (mar-25) a 124,1 (sep-26) con R$ 127,7 de concesiones desde abr-25: al menos dos tercios del stock es
  cartera nueva, y la serie ya refleja sobre todo el programa nuevo.
- La trayectoria lo confirma: la mora cae de 7,7 % (mar-25) a 5,0 % (nov-25) porque la cartera nueva, aún sin atrasos,
  diluye el denominador; después sube a 10,8 % (sep-26) a medida que esas camadas maduran. La tasa salta de 44 % a 59 %
  a.a. en abr-25 con el cambio de producto.
- El saldo en mora > 90 días pasa de ~R$ 3,1 mil millones (sep-25) a ~R$ 13,5 (sep-26).
- **Propuesta:** en P9 rotular «Mora > 90 días de toda la cartera del privado (≥ 2/3 originada desde abr-25)» y agregar
  una banda en mar-25. La mora de la cartera nueva por camada no es pública.
