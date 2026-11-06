# 2 · Módulo Personas: crédito a personas por renda (SCR.data)

## Estado
- Canvas de 6 láminas listo, con cifras reales a ago-26 (producto: tarjeta). Link:
  https://claude.ai/artifact/HonVC1nA2y22S9EH3U1gKx. **Falta la aprobación de Pablo**, y puede cambiar con el
  rediseño de gráficos (tarea 5).
- Láminas: 01 Cartera por renda · 02 Mix por renda · 03 Mora por renda · 04 Ticket por renda ·
  05 Exposición hasta 3 SM por tipo de institución · 06 Compromiso de renda (Anexo del REF; por ahora solo espacios
  reservados).
- Selectores: Producto (Tarjeta / Personal no consignado / Consignado / Vehículos / Inmobiliario / Cheque especial) e
  Institución (Todas / Bancos / Financieras / Inst. de pago / Cooperativas).

## Fuente
- SCR.data versión 2, en ZIP anuales: `datos/crudo/bcb_scr/scrdata/actual/scrdata_AAAA.zip` (2012–2026).
  - Formato: CSV separado por `;`, UTF-8 con BOM, decimales con coma.
  - Columnas: data_base, uf, segmento, cliente, cnae_ocupacao, porte, modalidade, submodalidade, origem, indexador,
    numero_de_operacoes, plazos, carteira_ativa, vencidos, carteira_inadimplencia, ativo_problematico.
  - `segmento` es el tipo de institución, no S1–S5.
  - `porte` es la renda en SM para PF y el tamaño para PJ.
  - `numero_de_operacoes = -1` significa menos de 15 operaciones.
  - `carteira_inadimplencia` viene en R$.
- Ya existe `pipeline/preparar_gold_bancos_scr.py`, que genera el gold `bk_scr` hasta ago-26. Revisarlo antes de crear
  uno nuevo.

## Construir
1. **`definiciones/scr_productos.json`**: mapa submodalidade → producto. Saldos PF a ago-26, en R$ mil millones,
   para validar:
   - **Tarjeta = 760,6**, suma de:
     - «Cartão de crédito - compra à vista e parcelado lojista»: 561,1
     - «Cartão de crédito - compra, fatura parcelada ou saque financiado…»: 100,2
     - «Cartão de crédito - não migrado»: 74,8
     - «Crédito rotativo vinculado a cartão de crédito»: 24,4
     - Financiamentos «Cartão de crédito - compra ou fatura parcelada…»: 0,1
   - **Consignado**: «Crédito pessoal - com consignação em folha», 813,7. El SCR.data no lo separa en privado, público e
     INSS; esa apertura está en el SGS.
   - **Personal no consignado**: «Crédito pessoal - sem consignação», 379,9.
   - **Vehículos**: «Aquisição de bens - veículos automotores», 428,0, más el arrendamiento de vehículos.
   - **Inmobiliario**: «Financiamento habitacional - SFH», 1.270,5, más «exceto SFH», 162,3. Home equity (30,5) va
     aparte.
   - **Cheque especial**: 38,7.
   - **Rural**: Investimento + Custeio + Comercialização + Industrialização.
   - **Otros**: el resto, ~137. Revisar el comercio exterior PF.
   - Reconciliar con el SGS: la tarjeta SGS a ago-26 es 740,4. El SCR incluye no bancos y difiere ~3 %.
2. **Gold `bk_scr_pf`** (después `bk_scr_pj`):
   - mensual desde 2012, por producto × tipo de institución × porte;
   - medidas: carteira_ativa, carteira_inadimplencia, vencido_15_90, ativo_problematico, ops (sin los −1) y cart_ops
     (cartera de las celdas con ops válido, para calcular el ticket);
   - particionado por producto para el sitio.
3. **Página Personas** en el sitio, según el canvas aprobado.

## Cifras de control (tarjeta, ago-26)

| Tramo | Cartera (R$ mil mill.) | Mora >90 | Ticket (R$) |
|---|---|---|---|
| Hasta 1 SM | 68,4 | 14,2 % | 614 |
| 1–2 SM | 117,4 | 14,4 % | 816 |
| 2–3 SM | 80,1 | 12,4 % | 1.330 |
| 3–5 SM | 114,3 | 10,5 % | 1.727 |
| 5–10 SM | 139,4 | 8,2 % | 3.052 |
| 10–20 SM | 116,3 | 6,3 % | 5.355 |
| Más de 20 SM | 86,3 | 3,8 % | 7.239 |
| Total | 760,7 (+13,2 % a/a) | 10,6 % | 1.526 |

Hasta 3 SM es el 36,8 % del mix.

**Exposición hasta 3 SM por tipo de institución (%)**

| Producto | Banco | Financeira | Inst. de pago | Cooperativa | Fintech |
|---|---|---|---|---|---|
| Tarjeta | 25,6 | 54,4 | 69,7 | 22,9 | 59,3 |
| Personal | 31,7 | 71,9 | — | 14,0 | — |
| Consignado | 48,3 | 45,1 | — | 25,5 | — |

## Riesgos de los datos
- **«Más de 20 SM» en ago-26 (resuelto 6-nov):** ~R$ 15 mil millones de tarjeta pasan de «más de 20 SM» a
  «Indisponível» (+94 % m/m). Es una reclasificación de la fuente, no una caída real. Mostrar N.D. en la tabla y anotar.
- **Otros quiebres:** jul-25 cambia la clasificación de renta (salta el mix); en 2025 el ticket del personal en los
  tramos altos se multiplica. Marcar las variaciones que cruzan estos meses.
- **Tramos fuera:** «Sem rendimento» e «Indisponível» (~3,4 % de la cartera de tarjeta) no entran en los tramos.
  Mostrarlos aparte.
- **Res. 4.966:** `ativo_problematico` cambia de definición en ene-2025. Tratarlo con banda de quiebre.
- **Tipo de institución:** las fintech grandes aparecen según su licencia (Nubank como financiera o institución de
  pago), no en «Fintech».

## Construido el 6-nov
- **Pipeline:**
  - `pipeline/preparar_gold_bancos_scr_productos.py` con `definiciones/scr_productos.json` (productos, tramos,
    instituciones y sectores CNAE en español);
  - caché mensual incremental en `datos/intermedio/scr_productos/<versión>/`;
  - gold `bk_scr_tablas` (398 filas) y `bk_scr_series` (14 mil filas, 0,75 MB en JSON);
  - paso 8/9 de `actualizar.bat`, con `--descargar` para el ZIP del año en curso.
- **Tests:** `tests/test_gold_scr_productos.py`. El total PF calza exacto con `bk_scr`; los shares y el mix suman 100 %.
- **Sitio:**
  - `paginas/b11.js` (Personas): cuatro secciones con selector de producto (tarjeta, personal, consignado,
    vehículos, inmobiliario, rural, cheque especial, total);
  - `paginas/b12.js` (Mora): activos problemáticos por modalidad, mora temprana, menor vs. mayor riesgo, sector;
  - menú en `config.js`; carpetas `sitio/personas/` y `sitio/mora/`.
- **Pendiente:**
  - correr `actualizar.bat` en Windows: regenera `bk_manifiesto` (hasta entonces `test_gold_reales_sin_errores` falla
    porque no lista las dos tablas nuevas) y exporta los JSON;
  - publicar;
  - revisar con fuentes reales (`verificar_f1.py --url`);
  - borrar `datos/intermedio/scr_productos/_a_borrar_12bbead977` (caché de una corrida abortada).
