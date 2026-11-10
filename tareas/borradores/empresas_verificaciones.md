# Hojas de empresas (frente 13) · verificaciones de la Parte D

10-nov-2026. Fuentes: cubo SCR `datos/intermedio/scr_productos/45fa235300/` (cliente PJ), gold `bk_empresas_m`,
`bk_empresas_scr_m` y `bk_ref`. Cifras a sep-26 contra sep-25, en R$ mil millones salvo que se diga otra cosa.

## 1. Micro: saldo −17,6 % a/a y operaciones +87,5 % a/a

No es crecimiento ni caída del negocio: son dos reclasificaciones distintas.

**Saldo.** Micro pasa de 157,7 a 130,1 (−17,55 %). Todo sale del sector «Servicios financieros»: en micro va de
46,0 a 5,2 (−40,8). Sin ese sector, micro crece **+11,7 %** (111,7 → 124,8). El bloque se mueve entero, de un mes a
otro:

| Mes | Micro, serv. financieros | Otro porte, el mismo mes |
|---|---|---|
| sep-25 | +38,2 | Grande, serv. financieros: +53,8 |
| mar-26 | −37,1 | «Sin dato»: +45,5 |
| abr-26 | +39,5 | «Sin dato»: −44,2 |
| jul-26 | −46,9 | Pequeña: +26,7 |

En jul-26 cambia además el tipo de institución: en MPME, serv. financieros en bancos va de 69,4 a 22,6 y en
financieras de 0,6 a 27,1. Ver el punto 3.

**Operaciones.** Micro pasa de 6,26 a 11,73 millones. Sin financieras, instituciones de pago y fintechs, crece
+0,9 % (5,46 → 5,51 millones); esas tres pasan de 0,80 a 6,23 millones. El grueso es un cambio de porte en nov-25:
las operaciones de financieras en micro pasan de 672 mil a 3,50 millones y en pequeña de 2,60 millones a 231 mil.
Las de instituciones de pago pasan de 163 mil a 1,14 millones en micro y de 892 mil a 74 mil en pequeña. Son
operaciones de tarjeta PJ (con interés en micro: de 860 mil a 3,23 millones) y casi no mueven saldo: micro sube
6 mil millones ese mes. Pasan unos 3,8 millones de operaciones de pequeña a micro. El resto (~1,6 millones) es
crecimiento de la tarjeta PJ en financieras e instituciones de pago.

**Propuesta.** Bandas en sep-25, mar–abr-26 y jul-26 (saldo) y en nov-25 (operaciones) en P1, P3, P5, P6 y P9.
Línea «Micro sin servicios financieros» en P1. En P9, nota: el a/a de operaciones de micro y pequeña no se
interpreta hasta nov-26 (12 meses después del cambio).

## 2. MPME en el SGS (+5,3 %) contra el SCR (+1,8 %)

| | Sep-26 | a/a |
|---|---|---|
| SGS 27701 (MPME) | 1.326,4 | +5,35 % |
| SCR micro + pequeña + mediana | 1.296,7 | +1,78 % |
| SCR MPME sin serv. financieros | 1.241,0 | +3,87 % |
| SCR MPME sin serv. financieros + «Sin dato» sin serv. financieros | 1.352,0 | +5,17 % |
| SGS 27702 (grandes) / SCR grande | 1.440,5 / 1.549,6 | +6,51 % / +7,92 % |
| SGS 20540 (empresas) / SCR PJ / SCR PJ sin serv. financieros | 2.759,4 / 2.969,9 / 2.654,5 | |

La brecha de 3,6 pp se explica casi entera por dos cosas:
- **Universo:** 20540 es «sociedades no financieras». El SCR PJ incluye «Actividades financieras» (315 en total). Ese
  sector explica 2,1 pp de la brecha (el bloque del punto 1). Se supone que 27701 sigue el universo de 20540; la
  ficha del SGS no lo dice.
- **Porte «Sin dato»** (Indisponível): 111,0 sin serv. financieros, +22,1 % a/a, y fuera de las dos hojas. Si se
  suma a MPME, el SCR da +5,17 %, a 0,2 pp del SGS. Es probable que el BCB asigne un porte a esos deudores en el SGS.

La identidad no es exacta: 27701 + 27702 difiere de 20540 hasta en R$ 37 mil millones.

**Propuesta.** En P1 de MPME, el SCR sin servicios financieros (coherente con el SGS) y una nota sobre «Sin dato»
(9 % del SCR MPME, +22 % a/a). Así la diferencia SGS–SCR baja de 3,6 a 1,5 pp, y queda explicada.

## 3. «Servicios financieros» resta −1,9 pp al crecimiento de MPME

No son entidades financieras chicas. Es un bloque de R$ 38–47 mil millones que cambia de porte y de tipo de
institución de un mes a otro (tabla del punto 1). Es producto «Otros» (en MPME, 74,0 → 50,4). El mismo mes de su
entrada en micro (sep-25), grande en serv. financieros sube +53,8. El patrón es el de pocos deudores grandes del
sector financiero (FIDC, securitizadora o holding), con porte mal informado, más un cambio de segmento de la
institución acreedora (banco → financiera) en jul-26. El SCR.data no identifica deudores ni instituciones: no se
puede confirmar si es un cambio de CNAE o de porte. Sí se descarta un traspaso gradual: los saltos son de un mes.

En MPME, serv. financieros va de 79,4 a 55,7 (−23,6, −1,85 pp de +1,78 %). En cooperativas, desarrollo y fomento,
fintechs y «Otros», el sector está estable (5,4; 1,3; 1,0; ~2).

**Propuesta (decisión de Pablo).** (a) Sacar «Servicios financieros» de las dos hojas, coherente con el SGS, que es
de sociedades no financieras. O (b) dejarlo como segmento aparte, en gris, con las bandas del punto 1 y una línea
«Total sin servicios financieros». Recomiendo (a) en MPME. En Grandes, (b): el sector pesa 16 % (247,1) y también saltó en sep-25
(+53,8 en un mes), así que sacarlo cambia mucho la hoja y conviene verlo antes.

## 4. Ticket de grandes por sector: Administración pública y Electricidad y gas

No es un error de unidad. Todo el cubo está en R$: comercio R$ 0,19 millones por operación, industria 0,30, total
grandes 0,46.

| Sector (grande, sep-26) | Saldo | Operaciones | Ticket, R$ millones | Cobertura del ticket |
|---|---|---|---|---|
| Administración pública | 189,1 | 2.024 | 64,9 | 69 % |
| · Bancos | 140,2 | 1.465 | 95,7 | |
| · Desarrollo y fomento | 48,9 | 491 | 99,6 | |
| Electricidad y gas | 189,4 | 12.427 | 10,4 | 68 % |
| · Desarrollo y fomento | 141,0 | 3.284 | 42,9 | |
| · Bancos | 48,3 | 9.143 | 5,3 | |
| Extractivas | 54,6 | 59.319 | 0,22 | **23 %** |

Son préstamos a estados, municipios y empresas públicas, y project finance eléctrico, sobre todo del BNDES:
pocas operaciones de cientos de millones. La cobertura sale de que el ticket se mide sobre las celdas con operaciones
informadas: las de menos de 15 operaciones son secretas (`ops = −1`). En extractivas mide menos de un cuarto del
saldo.

**Propuesta.** P9 de Grandes en R$ millones y en escala logarítmica. Ticket «en preparación» (o en gris) en los
sectores con cobertura < 50 %. Nota: «saldo medio por operación, sobre las celdas no secretas».

## 5. REF: desfase de la edición

La edición vigente de `bk_ref` es oct-26 (202610). Los gráficos usados (1.2.2.1, 1.2.2.2, 1.2.2.7 a 1.2.2.10) llegan
a jun-26: 3 meses antes que el SCR y el SGS (sep-26). El 1.2.2.3 trae proyecciones a 2028 y no se usa.

**Hecho.** `extraer_empresas.py` agrega una nota en las secciones REF (MPME P8; Grandes P7 y P8): «REF del BCB,
edición oct-26: los datos llegan a jun-26, 3 meses antes que el SCR y el SGS de esta hoja (sep-26)». El bloque REF
de P1 dice «hasta jun-26». La nota se calcula sola en cada edición.

## Otros hallazgos (no estaban en la lista)

- **Riesgo E–H desactivado.** 27706/27707 terminan en dic-24. Desde ene-25 el SGS publica el % de mayor riesgo de
  la Res. 4.966: 29581 (PJ, 6,80 %), 29582 (MPME, 9,61 %) y 29583 (grandes, 4,22 %) a sep-26. Están en gold. La
  hoja muestra las dos series, sin empalmar y con una nota.
- **Error de mapa en `scr_productos.json`.** «Arrendamento financeiro exceto veículos automotores e imóveis» contiene
  «veículos automotores» y cae en Vehículos: R$ 21,3 mil millones en PJ y 0,45 en PF (sep-26). Afecta a las páginas
  Personas y Mora y al cubo. Corregirlo cambia la versión del cubo y obliga a reprocesar (decisión de Pablo).
- **Tasa media de las modalidades libres.** Ponderada por concesiones, da 52,8 % contra 24,4 % de la 20718
  (sep-26): el cheque especial (357 % a.a.) tiene concesiones del mes del orden de su saldo. Ponderada por saldo,
  queda entre −0,4 y +2,1 pp de la 20718 en toda la historia. El gold usa saldo.
