# Fondeo y liquidez · verificaciones de la parte C (frente 14)

10-nov-2026. Fuentes: crudo SGS `datos/crudo/bcb_sgs/bancos_sistema/actual/`, catálogo `definiciones/bcb_sgs__catalogo.json`,
`bk_fondeo_m`, `bk_ref` (edición 202610 y su Excel crudo `datos/crudo/bcb_ref/anexo/202610/`), `bk_panel` y `bk_grupo`.

## 1. Unidad de la poupança (SGS 1835)
- El catálogo da «u.m.c. (mil)» = R$ mil para 1835 y para los 14 códigos 27789–27815. Saldo a sep-26:
  1.019.549.557 R$ mil = **R$ 1.019,6 mil millones** (ago-26: 1.023,5). Coincide con el REF 1.2.1.1.a «Poupança»
  (jun-26: R$ 1.012,7 mil millones, base sistema bancario) y con el SGS a jun-26 (1.028,4).
- La poupança **está dentro de M2** en la metodología nueva: M2 (27810) = M1 (27791) + títulos privados (27809) +
  1835, exacto en todos los meses (±1 R$ mil). A sep-26 pesa 12,95 % de M2.
- Error del borrador anterior: dividía 1835 por 1e6 (bien: R$ mil → R$ mil millones) y el resto por 1e3 (mal: daba
  R$ millones rotulados «mil millones», 1.000 veces de más). No llegó a mostrarse porque esas series estaban «en
  preparación». Además leía 1835 de `consumo_hogares/actual` (bajada del 4-nov, sin sep-26 y con ago-26 = 1.024,0
  antes de la revisión); ahora todo sale de `bk_fondeo_m` (R$ millones) y la hoja divide por 1.000.
- **Propuesta:** mostrar la poupança como componente de M2 (no «aparte») y retitular el bloque «Componentes de M2, a/a»
  (ya aplicado en el borrador; falta el visto de Pablo). Sumé «Moneda en poder del público» (27789), que el borrador
  omitía: sin ella las partes no suman M2.

## 2. Unidades del stock en `bk_ref` 1.2.1.1.a y 1.2.1.7 (columna `unidad` vacía)
- **1.2.1.1.a está en R$.** La suma de los 10 instrumentos es idéntica, fecha por fecha, a la de 1.2.1.3 (perfil por
  inversionista), que sí trae `unidad = "R$"`: R$ 9.194,7 mil millones a jun-26 (5.173,4 a jun-21). Los saldos
  cuadran con el SGS (depósitos a plazo R$ 3.079 mil millones; LCA/LCI 1.027; poupança 1.013).
- **1.2.1.7 está en R$.** Total jun-26: R$ 413,8 mil millones (S1 privados 27,9; Públicos 100,1; Digitales 114,1;
  SNCC 9,4; Demás 162,3). Sus participaciones reproducen 1.2.1.8 (39 / 28 / 24 / 7 / 2 %) y el total es igual a
  1.2.1.10 (Top 6 362,6 + Demás 51,2).
- Inconsistencia de la fuente (no del pipeline): 1.2.1.5 «Evolução do estoque de captações intermediadas» da
  R$ 200,3 mil millones a jun-26, la mitad de 1.2.1.7/1.2.1.10 (413,8). El cociente 1.2.1.7 / 1.2.1.5 va de 1,7 a 2,3 desde jun-22. Puede ser
  otro perímetro (p. ej., solo bancos o solo un instrumento); la nota del REF no lo aclara en el Excel. No usar 1.2.1.5
  junto con 1.2.1.7 hasta aclararlo.
- Trampa adicional: **la numeración de los gráficos cambia entre ediciones.** En 202605, «1.2.1.7» es «Quantidade de
  IFs por dependência…» y «1.2.1.5» una diferencia de tasas. El borrador lee solo la última edición; ahora además
  valida el título de cada gráfico antes de usarlo (falla si cambia).
- **Propuesta:** que `pipeline/ref.py` complete `unidad = "R$"` en 1.2.1.1.a, 1.2.1.5, 1.2.1.7 y 1.2.1.10 (todos
  en reales en el Excel crudo; 1.2.1.2.a y 1.2.1.3 ya la traen) y que agregue una clave estable por título además del número. Mientras
  tanto el borrador rotula «R$ mil millones» y divide por 1e9 (antes decía «unidad del REF» sin escalar).

## 3. F5: crédito / depósitos de «Desarrollo» (~1.400 %)
- Correcto por construcción. 2T26: crédito total R$ 472,8 mil millones / depósitos R$ 32,8 mil millones = **1.441,9 %**
  (`bk_grupo`, `credito_depositos` = 14,42). Es cociente de sumas, no promedio de cocientes; las sumas por banco de
  `bk_panel` cuadran con el grupo (3 bancos):

  | Banco | Crédito (R$ mm) | Depósitos (R$ mm) | Crédito/depósitos |
  |---|---|---|---|
  | BNDES | 416,3 | 4,3 | 9.759 % |
  | Banco da Amazônia | 38,7 | 13,4 | 290 % |
  | Banco do Nordeste | 17,8 | 15,2 | 117 % |
  | Grupo | 472,8 | 32,8 | 1.442 % |

- El BNDES es el 88 % del crédito del grupo y casi no capta depósitos: en el grupo los depósitos son 2,8 % del fondeo;
  pesan «otros instrumentos de deuda» 44,0 %, «otras obligaciones» 25,9 % (fondos FAT/PIS-PASEP, Tesoro), patrimonio
  17,4 % y préstamos y traspasos 6,4 %. Sin el BNDES el cociente sería 198 %. Serie histórica: 1.317 % (dic-19),
  1.276 % (dic-21), 1.139 % (dic-23), 1.152 % (dic-24).
- **Propuesta:** sacar a «Desarrollo» del gráfico de crédito/depósitos (aplasta la escala de los otros cinco grupos) y
  dejarlo en la tabla con nota «fondeo no depositario (FAT, Tesoro)»; o reemplazar el indicador para ese grupo por
  crédito / fondeo total. Decide Pablo.

## Otros hallazgos de la parte A/B
- **27807 son «Letras de crédito» (LCI/LCA), no letras de cambio** (catálogo: «Letras de crédito»). La spec y el
  borrador decían «letras de cambio»; corregido en el borrador («Letras de crédito (LCI/LCA)») y en `bk_fondeo_m`
  (`letras_credito`). Saldo sep-26: R$ 1.156,6 mil millones, a/a +5,1 %.
- **27811 son «Quotas de fundos monetários»**, no «fondos de renta fija de corto plazo». Sep-26: R$ 6.053,8 mil millones
  (37,7 % de M4).
- **M3 no cierra con sus partes publicadas.** M3 (27813) − M2 − 27811 − 27812 deja un residuo positivo de R$ 9 a 219
  mil millones según el mes (mínimo sep-07) (sep-26: R$ 160,8 mil millones, 1,0 % de M4; máximo 218,7 en mar-16). M1, títulos privados,
  M2 y M4 cuadran al R$ mil. En `bk_fondeo_m` va como serie `m3_sin_desglose` (resta de cifras publicadas) para que las
  participaciones en M4 sumen 100 %. **Propuesta:** buscar en el SGS (códigos 27792–27804, que no bajamos) la partida
  que falta antes de mostrar la composición de M3/M4 en la hoja.
- Tasas por inversionista (28583, 28611, 28614, 28617): sin crudo al 10-nov (la API devolvía HTML/500). `bk_fondeo_m`
  las lee solo si aparece el archivo y la hoja las deja «en preparación». Al llegar, confirmar la unidad (% a.a. o
  % del CDI) antes de dibujarlas: el gold guarda el % / 100 sin más supuestos.
