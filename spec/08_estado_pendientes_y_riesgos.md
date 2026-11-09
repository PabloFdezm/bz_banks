# 08 · Estado, pendientes y riesgos

Estado al 9-nov-2026.

## Hecho

- **Capital (IF.Data informe 5) construido el 9-nov** (frente 8): `pipeline/capital.py` publica `bk_capital`
  (34 bancos, 2015-03–2026-06) y `bk_capital_grupo`; requerimiento de CP desde el ACP que publica el BCB (desde
  2023-03) o desde `definiciones/minimos_regulatorios.json`. 2T26 calza con el Pilar 3 de Itaú, BB, Bradesco,
  Santander y BTG (±0,1 pp). Informe y decisiones: `tareas/borradores/capital_informe.md`. B7 todavía no lo consume.

- **Fuente CVM (ITR/DFP) construida el 9-nov** (frente 7): `pipeline/cvm.py` baja los ZIP oficiales a
  `datos/crudo/cvm/`, filtra a los 16 bancos del panel que entregan, resuelve el plan de cuentas de cada banco
  y publica `bk_publicado` (1.421 filas, 202312–202609, 11 líneas). Verificador en `herramientas/verificar_cvm.py`,
  paso `cvm` en `actualizar.py`, pruebas en `tests/test_cvm.py`. El informe y las decisiones pendientes están en
  `tareas/borradores/cvm_informe.md`. La tarjeta B8-06-0 todavía no la consume.
- Repo separado de `Dashboard` y funcionando solo (gold idéntico al del repo original, 115 tests OK).
- Portada y Crédito en v3. Tabla estándar única con Share. Presentar con láminas de posiciones idénticas.
- Arreglos de visualización con fuentes reales: etiquetas de gráficos (fuente fija en ECharts), tablas que
  escalan con el ancho, grilla de 9 columnas en todos los anchos de escritorio, gráfico y tabla nunca
  apilados desde 700 px, letra de los gráficos ×1,5 en Presentar.
- Páginas con tablas grandes: las secciones se muestran de inmediato y las tarjetas usan particiones.

## Pendientes

1. Rehacer **Calidad, Rentabilidad y Ficha** con la estructura v3 (canvas → aprobación → construcción).
2. Páginas nuevas: **Mora, Márgenes, Por banco, Productos** (ver `06_paginas.md`, «Estructura objetivo»).
   Actualizar el menú (`config.js`) cuando existan.
3. Crudo IF.Data en parquet: hecho el 4-nov (3,5 GB → 62 MB, gold idéntico). Falta borrar los CSV
   originales (con permiso de Pablo). SCR sigue en ZIP.
3b. ~~pandas distinto entre equipos~~ Resuelto el 6-nov: `stack(future_stack=True).dropna()` en `_bk_panel`
   (104.396 filas en pandas 2 y 3); `requirements.txt` pide pandas ≥ 2.1.
4. ~~Entradas congeladas del macro~~ Resuelto: endeudamiento, comprometimiento y desocupación se leen del SGS
   desde el 6-nov; Focus (`focus.py`) y la Selic real ex ante (SGS 432 + Focus) desde el 8-nov. Las tablas viejas
   de `datos/intermedio/` (`tasa_real_exante`, `expectativas_focus`, `fh_deuda`, `tasas_pnad`) quedan sin uso.
4b. Resuelto el 6-nov: `bk_sistema_m/q` se escribían en `datos/intermedio/Banks/` y el gold no se refrescaba.
5. Validar contra el catálogo del SGS los nombres de las series de modalidades. Concesiones validadas el 8-nov:
   20631 es el total (= 20632 PJ + 20633 PF); las libres son 20634 (= 20635 + 20662).
6. ~~`credito_aa` en 2025~~ Resuelto el 8-nov. No estaba vacío sino mal: comparaba `credito_total` de dos
   definiciones (balance COSIF nuevo contra viejo) y daba Santander −25 %, XP −44 %, total panel −4 %. Ahora
   `credito_aa`, `ativo_aa` y `depositos_aa` (y `credito_real_aa`) quedan vacíos de 2025-T1 a 2025-T4 en todos los
   bancos y grupos (`vacia_en_quiebre_2025` en `metricas_bancos.json`, `PER.cruza_quiebre`). Pendiente opcional:
   medir el crecimiento de 2025 con la cartera por modalidad (`bk_cartera`), que tiene sus propios saltos.
7. ~~Automatizar la actualización~~ Descartado el 8-nov: Pablo actualiza a mano (ver `07_operacion.md`).
   Quedan el CI de tests en GitHub y `.venv` con `requirements.lock`.
8. Opcional ofrecido: filas extra en la tabla de ROE de la Portada (ROA, margen, costo del riesgo).
9. Opcional: en Crédito → Líneas, partir mostrando solo Total y las modalidades grandes.
10. Fuente CVM (frente 7), decisiones **cerradas el 9-nov** (Cielo fuera, ITR 2024 bajado, ROE con PL promedio
    del trimestre, Santander rotulado, `bk_puente` sin tocar; ver §7 del informe). Lo que sigue era la pregunta: si Cielo (institución de pagos) entra a
    `bk_publicado` con las tres líneas que sí tiene; si se baja también el ITR 2024 para que el ROE anualizado
    exista en 1T25–3T25; si la tarjeta B8-06-0 se conecta ya a `bk_publicado`; y si `bk_puente` pasa de
    `validacion_bancos.json` (cargado a mano) a `bk_publicado`. Detalle en `tareas/borradores/cvm_informe.md`.

## Trampas de los datos (leer antes de tocar cálculos)

- **Frontera COSIF 2025-03:** códigos de cuenta renumerados; los informes de crédito pasan del escopo
  financiero al prudencial. Bancos con cambio de cobertura llevan `quiebre_2025 = true` y sus variaciones
  que cruzan 2025-T1 quedan vacías.
- **Crecimientos a/a de saldos del balance** (crédito, activo, depósitos): vacíos en 2025 en todos los bancos, porque
  el saldo cambia de definición en la frontera (no solo en los bancos con `quiebre_2025`).
- **2024-T4 anómalo** en IF.Data: vacío a propósito (`trimestres_anomalos` en definiciones).
- **Res. 4.966 (2025):** cambia la medida de mora/activos problemáticos; las series se leen con banda de
  quiebre.
- **Resultados acumulados con reseteo en julio** (informe 4): se des-acumulan antes de calcular TTM.
- **Mora:** panel ≥ 15 días vs SGS > 90 días; no comparar niveles.
- **Series SGS: un solo dataset.** Todo el pipeline lee el SGS de `datos/crudo/bcb_sgs/bancos_sistema` (`pipeline/sgs.py`).
  Hasta el 8-nov la Portada y Crédito leían copias congeladas del macro (`credito`, `credito_hogares`, `credito_pib`) y
  por eso libre, direccionado, mora de Personas y las modalidades parecían llegar uno o dos meses atrás del total.
- **API del SGS:** una serie inexistente no da 404; devuelve HTML con 200 o 502 (ver `bcb_api.py`).
- **SCR.data:** CSV en UTF-8 con BOM (no cp1252); `carteira_inadimplencia` está en R$, no en %.
- **Red corporativa:** proxy HTTPS; ver `pipeline/certificados.py`.

### Fuente CVM (ITR/DFP) — trampas nuevas, todas verificadas sobre el dato el 9-nov-2026

- **El plan de cuentas de la CVM cambió con el CPC 48 y cada banco migró cuando quiso.** Itaú, BMG y BTG usan
  el esqueleto nuevo (PL en 2.08, lucro en 3.09) desde 2023; BB, Bradesco, Banrisul y los demás siguen en el
  viejo (PL en 2.07, lucro en 3.11); **Pine volvió del nuevo al viejo entre el DFP 2024 y el ITR 1T25**. Un mismo
  `CD_CONTA` significa cosas distintas según banco y año (en Pine 2.07 fue «Patrimônio Líquido Consolidado» y hoy
  es «Passivos sobre Ativos Não Correntes a Venda»). Por eso el mapeo exige código **y** texto de la descripción
  (`definiciones/cvm__bancos_lineas.json`): si el código se corrió, la regla lo encuentra; si cambió de
  significado, no casa y la línea queda vacía en vez de publicar un número equivocado.
- **Tres bancos del panel no entregan estados consolidados**: ABC Brasil (desde el DFP 2024), Banco da Amazônia y
  Banco do Nordeste solo tienen `ind`. BRB dejó de entregar el consolidado en el 2T25 y no volvió a entregar nada.
  `bk_publicado` lleva la base en la columna `consolidacion`; mezclar con e ind en una serie rompe la comparación.
- **Hay bancos que no llenan el archivo estructurado.** Santander entrega el impuesto (3.06) en 0 en varios ITR,
  con lo que su 3.09 «Lucro consolidado» queda ANTES de impuestos: el total se reconstruye sumando 3.09.01 +
  3.09.02. Además solo detalla la cartera en el DFP 2024 y los depósitos en el ITR 1T25. BTG no publica la
  provisión de crédito; BB, Banestes y Pine dejan la provisión en 0 y entregan la cartera neta.
- **Una cuenta en 0 no es un dato.** BB, Banestes, Pine, ABC y Mercantil (estos dos hasta el DFP 2024) dejan
  1.02.04.05 «Provisão para Perdas Esperadas» en 0: significa «no la divulgo» en el archivo estructurado, no
  «no tengo provisión». Las líneas de saldo llevan `cero_es_vacio` y el 0 va a `huecos.csv`, nunca a gold.
- **Cuentas duplicadas en 0.** En el ITR 3T25 BB llenó además las cuentas del esqueleto nuevo (3.09.01/3.09.02)
  con 0 junto a las suyas (3.11.01/3.11.02). Regla: si de las cuentas que casan solo una trae número, vale esa;
  si hay dos con número, es ambigüedad y la línea queda vacía con aviso.
- **En el 1T el trimestre y el acumulado son la misma cifra** (los dos arrancan el 1 de enero) y la CVM entrega
  una sola fila: se duplica como `medida=trimestre` para que el 1T no quede sin flujo ni sin ROE.
- **El 4T no lo publica nadie.** La DFP trae solo el año completo; el cuarto trimestre se deriva restando el
  acumulado a setiembre (ITR 3T) y esas filas van marcadas `documento=DFP−ITR`. Si el banco reexpresó cifras
  entre las dos entregas, la resta lo arrastra.
- **BRB entrega en la DFP una DRE que cubre solo diciembre** (`DT_INI_EXERC` = 2023-12-01 y 2024-12-01). No es ni
  el año ni el trimestre: se descarta con aviso y BRB queda sin flujos anuales.
- **Los ZIP de estados traen una sola versión por entrega** (la vigente), pero el índice (`<doc>_cia_aberta_<año>.csv`)
  lista todas las reentregas con su `DT_RECEB`: al cruzar la fecha de entrega hay que tomar la versión que se usó.
- **CVM ≠ IF.Data, siempre.** La CVM es el consolidado societario bajo CPC; el IF.Data es el conglomerado
  prudencial bajo COSIF. En 2T26 el activo difiere −18,4 % en Bradesco (seguros y previdência, el mismo número que
  anota `definiciones/validacion_bancos.json`), −11,1 % en Itaú y −7,7 % en BTG; el PL de Santander difiere −17,3 %
  de forma sistemática. La «Operações de Crédito» de la CVM se parece al `credito_total` del COSIF, no a su
  `credito_bruto`. Se mide y se informa (`pipeline/cvm.py contrastar`), no se corrige.

### Capital (IF.Data informe 5) — trampas verificadas sobre el dato el 9-nov-2026

- **El informe 5 empieza en 2015-03.** Los trimestres de 2014 responden vacíos (sin filas): `bk_capital` arranca
  en 2015-03 y el panel de 2014 queda como hueco `INFORME_5_VACIO`.
- **Las letras de las columnas cambian por época** («RWA (i) = (f)+(g)+(h)» hasta 2022-12, «(j) = …+(i)» desde
  2023-03, cuando entra RWAsp) y **en 2023-03 y 2023-06 el nombre del índice de CP viene sin salto de línea**
  («Índice de Capital Principal (k) = (a) / (i)»). Se casa por nombre sin la letra (`capital.nombre_base`).
- **En 2025-09 la API sirve cada fila tres veces** (99.000 filas para 1.375 entidades). Se deduplica exigiendo que
  las copias sean idénticas; si alguna vez difieren, el paso falla.
- **Trimestres repetidos al centavo**: Agibank 2015-06 a 2016-06 y PagSeguro 4T25 = 2T25 traen CP, PR y RWA
  idénticos. Se publica lo que dice el BCB con la columna `alerta`; no usar esos puntos para variaciones.
- **Las instituciones de pago y digitales no tienen capital principal antes de 2023-07** (Nubank, Stone, PagSeguro,
  Mercado Pago, Neon, CloudWalk; Cielo solo informa Basilea y RWA): huecos `SIN_CAPITAL_PRINCIPAL_O_RWA`.
  Los agregados de grupo suman solo los bancos con dato y llevan `n_bancos`.
- **Desde 2023-03 el informe trae el «Adicional de Capital Principal» exigido en R$** y el requerimiento sale de
  ahí, no de suponer colchones: 2,5 % en la mayoría, 3,5–3,75 % en los sistémicos, y niveles propios en los
  conglomerados de pago (Neon y PagSeguro 5 %, Nubank, Stone y Mercado Pago 1,25 %). Antes de 2023-03 se usa
  `definiciones/minimos_regulatorios.json` y lo que la norma no respalde queda vacío.
- **El panel no es el sistema**: en 2T26 cubre el 85 % del RWA de los 440 conglomerados prudenciales y su índice
  de CP (12,9 %) queda 1 pp por debajo del sistema (13,9 %), ambos calculados con el mismo informe 5.

## Riesgos técnicos conocidos

- `bancos.css` va encima de `monitor.css` (que también usa `404.html`). Quedan unos diez selectores con más
  de una regla porque fusionarlos cruzaría otra regla de igual especificidad: al tocarlos, buscar el selector
  en ambos archivos.
- Tarjetas que cargan tablas completas (`bk_panel`, `bk_grupo`, `bk_cre_*`) hacen lentas las páginas. Usar
  particiones.
- Capturas automáticas sin fuentes reales no muestran cortes de texto (ver `07_operacion.md`).
