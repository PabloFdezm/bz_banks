# Frente 12 · Hojas por producto de personas (Tarjeta, Personal sin planilla, Descuento por planilla, Vehículos): datos, pipeline y verificaciones

Estado al 10-nov-2026: **en curso**: Partes A, B y C hechas el 10-nov (C: `borradores/tarjeta_verificaciones.md`). Pendientes: decisiones de Pablo sobre
las propuestas de C (tarjeta con interés, tratamiento de N.D., Selic) y las verificaciones propias de E y F. Encargo pensado para que lo ejecute otra sesión u otra LLM sin contexto previo.
Leer antes `CLAUDE.md`, `tareas/README.md`, `tareas/05_rediseno_graficos.md` y `tareas/09_portada_mensual_segmentos.md`
(anexo B: códigos SGS de personas por producto).

## Contexto
- Pablo aprobó el 10-nov la hoja «Tarjeta» del canvas de rediseño (tablero `Tarjeta.dc.html` del canvas
  «Bancos Brasil · Rediseño de gráficos v3», privado). Es la primera de cinco hojas por producto: tarjeta, descuento
  por planilla (consignado), inmobiliario, vehículos y personal sin planilla con sobregiro.
- Hoy la hoja se alimenta de un borrador, no del pipeline:
  - `tareas/borradores/_salida/extraer_producto.py tarjeta|personal|planilla` (fuera de git) arma `tarjeta.json`,
    `personal.json`, `planilla.json` y `vehiculos.json` (argumento `vehiculos`) en la misma carpeta (reemplazó a `extraer_tarjeta.py`, borrado el 10-nov);
  - lee el crudo SGS (`datos/crudo/bcb_sgs/*/actual/serie_<cod>.json`), el cubo SCR por producto
    (`datos/intermedio/scr_productos/e82fb46f9a/scr_AAAAMM.parquet`) y `datos/gold/bk_cartera_mix7.parquet`.
- Lo que falta en el crudo sale en la hoja como serie vacía con la marca «en preparación».

## Estructura aprobada (9 secciones, dos gráficos por sección; el detalle va en Agrandar)
| Sección | Par A | Par B | Fuente |
|---|---|---|---|
| P1 Volumen | Saldo a/a: total, rotativo, en cuotas, al contado | Saldo con interés (rotativo + cuotas), % del total | SGS |
| P2 Precio | Tasa por submodalidad contra Selic (banda Ley 14.690, ene-24) | Variación a/a de la tasa media: efecto tasa y efecto mezcla | SGS |
| P3 Calidad | Mora > 90 días por submodalidad | Atraso 15–90 días por tramo de renta | SGS, SCR |
| P4 Qué movió la mora | Mora > 90: efecto tasa, mezcla de clientes, mezcla de instituciones | Lo mismo para el atraso 15–90 | SCR |
| P5 Renta | Aporte al crecimiento a/a del saldo por tramo | Aporte a la variación a/a de la mora por tramo | SCR |
| P6 Ocupación | Ídem por ocupación | Ídem por ocupación | SCR |
| P7 Emisor | Ídem por tipo de institución | Ídem por tipo de institución | SCR, IF.Data |
| P8 Ticket y endeudamiento | Ticket medio por operación, por tramo (R$) | Ticket en meses de renta, por tramo | SCR, SGS 1619 |
| P9 Tope por renta | Saldo en clientes hasta 3 SM, % del total (tarjeta y personal) | Mora hasta 3 SM y resto | SCR |

## Parte A · Datos SGS que faltan (bajar desde el equipo de Pablo: la VM no llega a la API del BCB)
1. Bajar y validar con `herramientas/validar_sgs.py`:
   - `22023` tasa de tarjeta en cuotas con interés (personas);
   - `22024` tasa de tarjeta total (personas): confirmar si es solo rotativo + cuotas o incluye otra cosa;
   - `20680` concesiones de tarjeta en cuotas; `20681` concesiones de tarjeta al contado.
   - Revalidar los que ya están en el crudo pero no en `sgs.CODIGOS`: `20587`, `20588`, `20589`, `20679`, `20682`,
     `22022`, `1619` (salario mínimo). `21127` y `21128` ya están en `sgs.CODIGOS` (`mora90_rotativo`,
     `mora90_parcelado`).
2. Agregarlos a `pipeline/sgs.py` (`CODIGOS`) con nombre propio y a `definiciones/bcb_sgs__catalogo.json`
   (`validar_sgs.py --escribir`, revisar a mano). `tests/test_sgs_catalogo.py` debe pasar.
3. Comando de descarga puntual (desde la raíz del repo):
   `python -X utf8 -c "import sys; sys.path.insert(0,'pipeline'); import sgs; [print(c, sgs.bajar(c)) for c in (1619,22022,22023,22024,20679,20680,20681,20682)]"`
4. Contraste: con 22023 y 20680 en el crudo, la tasa media ponderada por concesiones
   (`w·22022 + (1−w)·22023`, `w = 20679 / (20679 + 20680)`) debe quedar cerca de `22024`. Informar la diferencia por
   mes; si supera 1 pp, la descomposición de P2 se hace contra la tasa reconstruida y se dice en la nota.

### Resultado de la Parte A (10-nov, hecha)
- Los 33 códigos de las partes A, E, F y G están en `sgs.CODIGOS` (bloque «personas por producto»), en el catálogo
  (validado contra el SGS el 10-nov; ningún nombre existente cambió) y en el crudo `bancos_sistema` hasta sep-26.
  `pytest`: 219 verdes.
- Identidades: 20576 + 20577 + 20578 = 20579, 20587 + 20588 + 20589 = 20590, 20679 + 20680 + 20681 = 20682 y
  20668 + 20669 + 20670 = 20671, todas con diferencia ≤ 1 (redondeo).
- **Error en la hoja «Personal».** 20574 es «não consignado *total*» y ya incluye la renegociación (20575,
  «vinculado à composição de dívidas»): 20580 = 20574 + 20579 (dif. máx. 635), y sumando 20575 sobra justo su saldo
  (R$ 84 mil millones a sep-26). Lo mismo vale para 20666/20667, 20742/20743 y 21114/21115. El borrador suma
  personal + renegociación + sobregiro (cuenta dos veces ~21 % del personal), el par B de P1 divide por
  (personal + renegociación) y la descomposición de P2 pondera las dos como submodalidades separadas. Corrección:
  total = 20574 + 20573; renegociación / 20574; en P2, submodalidades «personal total» (20742, peso 20666) y
  sobregiro (20741, peso 20665), con la renegociación solo como línea de nivel (o, si Pablo lo pide, el personal sin
  renegociación despejado de la ponderación). No hay serie SGS de personal sin renegociación.
  **Aplicada el 10-nov** (Pablo) en `extraer_producto.py`, con la renegociación solo como línea de nivel. La
  descomposición de P2 suma exacto (sep-26: +3,29 − 1,14 + 0,13 = +2,28 pp). Las cuatro hojas se regeneraron y ya
  no tienen series «en preparación».
- **Contraste A.4.** 22024 (tarjeta total, 100 % a.a. en sep-26) queda por debajo de rotativo (452 %) y cuotas (193 %):
  incluye la tarjeta al contado a tasa 0. Ninguna reconstrucción calza a 1 pp: rotativo + cuotas ponderado por
  concesiones da +269 pp; con el contado a 0, −28 pp por concesiones y −18 pp por saldo (sep-26), con brecha que crece
  desde 2024. Según la regla, P2 se descompone contra la tasa reconstruida (rotativo + cuotas por concesiones), como ya
  hace el borrador, y la nota debe decir que no es 22024.
- `1619` (salario mínimo) ya trae dic-26.

## Parte B · Paso a pipeline (gold)
Llevar las fórmulas del borrador a `pipeline/preparar_gold_bancos_producto_pf.py` (nombre sugerido) con dos gold
genéricos, con columna `producto` (tarjeta, personal, planilla, vehiculos), no una tabla por hoja. Abajo se describen
con tarjeta como ejemplo:
- `bk_producto_pf_m` (SGS, mensual desde 2014): saldos, concesiones, tasas, mora por submodalidad; peso del saldo con
  interés; descomposición de la tasa media (efecto tasa por submodalidad y efecto mezcla).
- `bk_producto_pf_scr_m` (SCR, mensual desde ene-18), en formato largo `fecha × dimension × segmento × medida`:
  - dimensiones: tramo de renta (7 tramos + «sin renta»), tipo de institución, ocupación, y la celda renta × institución;
  - medidas: saldo, mora > 90, atraso 15–90, activo problemático, operaciones, ticket;
  - aportes a/a al crecimiento y a la tasa (mora y atraso), con efecto tasa y efecto mezcla por segmento;
  - descomposición en tres partes (efecto tasa en celdas renta × institución, mezcla de renta, mezcla de institución
    dentro de renta) y la misma con el orden inverso;
  - meses de renta por operación con punto medio, piso y techo del tramo.
Fórmulas (todas en pp, con promedios de t y t−12; deben sumar exacto):
- aporte al crecimiento del segmento i: `(S_i,t − S_i,t−12) / S_total,t−12 × 100`;
- aporte a la tasa: `w_i,t·m_i,t − w_i,t−12·m_i,t−12`, con `w` = peso en la cartera y `m` = tasa del segmento;
- efecto tasa `w̄_i·Δm_i`; efecto mezcla `m̄_i·Δw_i`. Si un segmento no existe en t o t−12, su tasa faltante toma la
  del otro período (todo su aporte cae en mezcla).
Tests mínimos: los aportes suman el total (tolerancia 1e-6) en cada mes; las tres partes suman la variación total;
los pesos por dimensión suman 100 %; el ticket total coincide con `cart_ops / ops` del total.

### Resultado de la Parte B (10-nov, hecha)
- `pipeline/preparar_gold_bancos_producto_pf.py` publica `bk_producto_pf_m` (SGS, 15,5 mil filas: tarjeta, personal,
  planilla, vehículos y las referencias `personas`, Selic y salario mínimo) y `bk_producto_pf_scr_m` (SCR, 643 mil filas;
  agrega la celda renta × ocupación, que usa P6). Paso `producto_pf` en `actualizar.py` (después de `scr`), contrato en
  `definiciones/contrato_gold.json`, manifiesto y spec autogenerada al día. Unidades: razones y efectos en fracción.
- `tests/test_producto_pf.py`: 10 pruebas (unitarias con cubo sintético e integración): aportes = total, tres partes =
  variación, pesos = 1 por dimensión, ticket total = cart_ops / ops, efectos SGS = Δ tasa media, partes = totales.
  `pytest` 229 verdes; `verificar_gold.py --gold` OK.
- `extraer_producto.py` ya lee solo de gold. Los cuatro JSON son iguales a los del borrador (tolerancia 0,01) salvo dos
  mejoras: P4 sin dato en 2018 (antes mostraba 0 por sumar vacíos) y P2 con dato en 2014 (antes vacío porque el a/a se
  calculaba sobre la serie recortada).
- Agrupación de instituciones: se mantiene la del canvas (Fintechs aparte), distinta de `scr_productos.json`.

### Resultado de la Parte C y decisiones (10-nov)
Informe: `borradores/tarjeta_verificaciones.md` (puntos 1–7, con personal y planilla). Decisiones de Pablo, aplicadas:
- **Tarjeta con interés aparte.** `definiciones/scr_productos.json` abre la tarjeta en «Tarjeta · contado» y
  «Tarjeta · con interés» (`partes`); el cubo SCR se reprocesó (versión 45fa235300) y Personas/Mora las vuelven a
  juntar: `bk_scr_tablas` y `bk_scr_series` iguales a las anteriores (diferencias < 1e-12). `bk_producto_pf_scr_m` suma
  los productos `tarjeta_interes` y `tarjeta_contado`. En la hoja, P4 y P7 de tarjeta van sobre la tarjeta con interés
  (sep-26: mora 40,0 %, Δ a/a +5,73 pp, bancos +6,05 pp) y P3 suma la mora con interés / contado / total.
- **«Sin renta / N.D.» aparte de los tramos:** gris y punteado; en los aportes, línea «Tramos con renta»; mix sobre los
  7 tramos con renta y el peso de N.D. en un bloque propio. Falta: bandas en jul-25, ene–feb-26 y jul-26 (el JSON de la
  hoja no tiene campo de bandas; se dibujan en el canvas). P9 sigue con «Más de 3 SM y sin dato».
- **Selic:** la referencia pasa a la Selic efectiva del mes (SGS 4189, `selic_efectiva_mes`), en vez de la meta a fin de mes.
- Corregida la nota de quiebres de `preparar_gold_bancos_scr_productos.py` (no hubo traspaso a N.D. en ago-26).
Aplicadas también el 10-nov (Pablo): ocupación «Otros / no informado (SCR)» en gris; «saldo medio por operación» en
vez de «ticket»; IP de personal sumadas a «Otros» (`OTROS_INSTITUCION` en el gold); notas en P7 de personal y P9 de
planilla (campo `nota` de la sección); P9 con tres grupos (hasta 3 SM, más de 3 SM y sin renta; en tarjeta, sep-26:
14,1 %, 7,7 % y 26,2 %). Los JSON traen un campo `bandas` (sección, mes, texto) con jul-25, ene-26, jul-26, ene-25
(Res. 4.966) y mar-25 (planilla): falta que el canvas lea `bandas` y `nota`.

## Parte C · Verificaciones abiertas (informar antes de cerrar)
1. **Instituciones de pago sin mora.** En tarjeta tienen ~R$ 117 mil millones y 0,4 % de activo problemático (sep-26);
   las financieras, 27 %. Hipótesis: la cartera vencida de la IP pasa a la financiera del mismo grupo. Verificar
   (IF.Data por conglomerado, notas de las compañías o del BCB). Si se confirma, en P4 y P7 agrupar «IP + financieras»
   o mostrar ambas descomposiciones; hoy la expansión de las IP resta mora por mezcla de forma mecánica.
2. **Quiebres de renta del SCR.** Jul-25: reclasificación de renta (salto del mix). Ago-26: ~R$ 15 mil millones de
   tarjeta pasan de «más de 20 SM» a «no disponible». Cuantificar el efecto sobre los aportes (hoy «sin renta» aporta
   +0,78 pp de los +1,78 pp de la mora a/a) y proponer tratamiento: banda, serie empalmada o nota.
3. **Ocupación «Otros».** Aporta +4,4 pp de los +11,7 pp del crecimiento del saldo. Listar los valores de
   `cnae_ocupacao` de personas que caen en «Otros» y proponer un mapeo mejor.
4. **Ticket.** Confirmar que `ops` es número de operaciones (no de clientes) y si el SCR trae algún conteo de clientes.
5. **Selic en la hoja.** Hoy se usa la meta (SGS 432, último dato del mes); confirmar con Pablo si prefiere el
   promedio del mes.

## Parte D · Fuera de alcance de este frente
- Mix y mora por segmento regulatorio (S1–S5): requiere el campo SR del SCR; depende del frente 3 (en pausa).
- Comprometimiento de renta por modalidad, PD y cohortes del REF: son microdatos del BC, no públicos.
- El sitio: la hoja vive en el canvas hasta que Pablo cierre el rediseño (frente 5).

## Parte E · Hoja «Personal sin planilla y sobregiro» (agregada el 10-nov)
Misma estructura de 9 secciones y mismas fórmulas SCR (producto «Personal no consignado»). Diferencias:
- P1: total = personal (`20574`) + renegociación (`20575`) + sobregiro (`20573`); par B: renegociación / (personal +
  renegociación) y sobregiro / total. Concesiones `20666`, `20667`, `20665`.
- P2: tasa media de las tres submodalidades ponderada por concesiones; efecto tasa por submodalidad y efecto mezcla
  `(r̄_i − tasa media promedio) × Δw_i`. Banda: tope del sobregiro (ene-20, Res. CMN 4.765).
- P3: mora `21114`, `21115`, `21113`. El SCR de este producto no incluye el sobregiro.
- P7: IF.Data (`bk_cartera_mix7`, categoría «personal») junta personal y sobregiro.
Datos que faltan: `20742` (tasa personal) y `20743` (tasa renegociación). Revalidar `20573`, `20575`, `20665`,
`20666`, `20667`, `20741`, `21113`, `21115`, que están en el crudo pero no en `sgs.CODIGOS`.
Gold: las mismas `bk_producto_pf_m` y `bk_producto_pf_scr_m` de la parte B, con `producto = personal`.
Verificaciones propias: en personal las instituciones de pago tienen mora de 32 % con un peso mínimo (revisar que no
sea un error de clasificación); las financieras explican +6,2 pp del +5,6 % a/a del saldo y los bancos restan
−1,3 pp (confirmar si es traspaso de cartera entre entidades del mismo grupo); «Otros» en ocupación vuelve a ser el
mayor aporte (+3,5 pp).

## Parte F · Hoja «Descuento por planilla» (agregada el 10-nov)
Misma estructura; producto SCR «Consignado» (el SCR no separa el convenio). Diferencias:
- P1: total = privados (`20576`) + público (`20577`) + INSS (`20578`), porque `20579` no está en el crudo; par B:
  peso de cada convenio, barras apiladas. Concesiones `20671`, `20668`–`20670`.
- P2: tasa media de los tres convenios ponderada por concesiones. Faltan `20744`, `20745`, `20746` (tasas por convenio);
  el total `20747` sí está.
- P9 «Nuevo privado» (banda mar-25, MP 1.292): concesiones mensuales del privado y mora > 90 del privado contra
  personal sin planilla (`21116` contra `21114`) e INSS (`21118`).
Datos que faltan: `20579`, `20744`, `20745`, `20746`. Revalidar `20668`–`20671` y `20747`, que están en el crudo pero
no en `sgs.CODIGOS` (`21117` ya está: `mora90_consignado_publico`).
Verificaciones propias: la mora del privado (10,8 %) ya está casi al nivel del personal sin planilla (11,1 %) a sep-26;
confirmar que `21116` mide la cartera nueva (eSocial) y no solo el stock anterior a mar-25. «Otros» en ocupación
aporta +4,6 pp del +11,2 % a/a del saldo (mismo problema de mapeo que en las otras hojas).

## Parte G · Hoja «Vehículos» (agregada el 10-nov, después de la primera versión de este archivo)
Misma estructura; producto SCR «Vehículos», IF.Data categoría «vehiculos». El SGS no separa submodalidades, así que
las secciones SGS comparan contra el total de personas en vez de descomponer:
- P1: saldo `20581`; par B: concesiones 12 meses a/a de vehículos (`20673`) contra total personas (`20633`).
- P2: tasa `20749` contra total personas (`20716`) y Selic; par B: diferenciales vehículos − Selic y vehículos − total
  personas (sin efecto tasa ni efecto mezcla).
- P3: mora `21121` contra total personas (`21084`).
- P9: tiene una versión propia en el borrador; revisar en `extraer_producto.py` qué muestra antes de pasarlo a gold.
Datos: todo está en el crudo. Revalidar `20673`, `20749` y `20716`, que no están en `sgs.CODIGOS` (`20581`, `21121`,
`20633` y `21084` sí están).

## Terminado cuando
- A: los ocho códigos de tarjeta y los de las partes E, F y G están en `sgs.CODIGOS`, en el catálogo y en el crudo; contraste del punto A.4 informado.
- B: los dos gold existen con los cuatro productos, pasan los tests y `extraer_producto.py` puede leer de ellos en vez
  del crudo.
- C: informe corto en `tareas/borradores/tarjeta_verificaciones.md` con los puntos 1 a 5 y una propuesta por punto.
- Nada se commitea sin pedirlo a Pablo.
