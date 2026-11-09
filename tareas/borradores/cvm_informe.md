# Fuente CVM (ITR/DFP) → `bk_publicado` — informe del 9-nov-2026

Frente 7 (`tareas/07_fuente_cvm.md`). Construido de punta a punta hasta la tabla gold. Nada de lo que sigue
toca el sitio, el CSS ni las páginas: la tarjeta B8-06-0 sigue «en preparación» y se conecta cuando Pablo lo
decida. No se hizo commit ni push, no se publicó y no se borró ningún archivo.

**Resumen.** `bk_publicado` tiene 1.421 filas: 16 de los 34 bancos del panel (los únicos que entregan ITR/DFP),
9 trimestres de 4T23 a 3T26 y 11 líneas, con el 3T26 ya disponible en los siete bancos que lo habían publicado
al 8-nov. Itaú 2T26 calza al R$ mil contra su ITR y contra lo que el repo ya tenía anotado en
`validacion_bancos.json` (depósitos 1.134,49 mm exactos). El contraste contra IF.Data da diferencias medias de
3-4 % en activo, depósitos y PL, y 0,0 % en los tres bancos cuyos estados individuales *son* el conglomerado
prudencial: la extracción está bien. Quedan 38 huecos y 7 líneas vacías por diseño, todos porque el banco no
llena la cuenta en el archivo estructurado, ninguno inventado. Hay seis decisiones abiertas en §7, la más
incómoda el −17 % sistemático del PL de Santander contra IF.Data, que no pude cerrar sin leer sus estados.

---

## 1. Qué se hizo

| Capa | Qué hay | Dónde |
|---|---|---|
| Crudo | 6 ZIP íntegros de la CVM (ITR 2025 y 2026; DFP 2023, 2024, 2025 y 2026) y el registro de compañías abiertas, con URL, sha256, tamaño, `Last-Modified` del servidor y fecha de descarga en su manifiesto | `datos/crudo/cvm/{itr,dfp}/<año>/`, `datos/crudo/cvm/cadastro/actual/` |
| Derivado | Solo las filas de los 16 bancos del panel que entregan, en BPA, BPP y DRE: 40.200 filas con las columnas de la fuente sin tocar, más el índice de entregas (195) y la lista de huecos | `datos/derivado/cvm/bancos/` |
| Definiciones | Mapa CNPJ → `cod_inst` con la base de cada banco; mapeo de cuentas por banco; columnas del derivado y del gold | `definiciones/cvm__bancos.json`, `cvm__bancos_lineas.json`, `cvm__estados_bancos.json` |
| Gold | `bk_publicado`: 1.421 filas, 16 bancos, 9 periodos (202312–202609), 11 líneas | `datos/gold/bk_publicado.parquet` |
| Código | Descarga, extracción, resolución de cuentas, gold y contraste | `pipeline/cvm.py` (1.090 líneas) |
| Verificador | Estructura, escala contra el derivado, aritmética del balance, cobertura y contraste | `herramientas/verificar_cvm.py` (371 líneas) |
| Tests | 38 pruebas (32 unitarias sintéticas sin red + 6 de integración sobre `datos/`) | `tests/test_cvm.py` (512 líneas) |
| Integración | Paso `cvm` en `actualizar.py` (antes de `manifiesto`), contrato de `bk_publicado` en `contrato_gold.json` | `pipeline/actualizar.py`, `definiciones/contrato_gold.json` |
| Documentación | `cvm__dfp_bancos.json` marcado obsoleto; trampas nuevas en `spec/08`; spec autogenerada al día | `spec/08_estado_pendientes_y_riesgos.md`, `spec/generado/` |

Cómo se corre (todo desde la raíz, con el `.venv` del repo):

```powershell
Set-Location C:\dev\bz_banks
.venv\Scripts\python.exe -X utf8 pipeline\cvm.py descargar      # ZIP y registro, solo si cambiaron en el servidor
.venv\Scripts\python.exe -X utf8 pipeline\cvm.py extraer        # derivado filtrado a los bancos del mapa
.venv\Scripts\python.exe -X utf8 pipeline\cvm.py gold           # bk_publicado + huecos
.venv\Scripts\python.exe -X utf8 pipeline\cvm.py contrastar     # contra IF.Data (bk_panel)
.venv\Scripts\python.exe -X utf8 herramientas\verificar_cvm.py  # verificador de solo lectura
.venv\Scripts\python.exe -m pytest -q                            # 168 pruebas OK
```

`actualizar.bat` ya lo incluye: el paso `cvm` va después de `scr` y antes de `manifiesto`. Con `--sin-red` no
baja nada y trabaja con los ZIP que ya estén en el crudo. La descarga se repite sola cuando cambia el tamaño
que anuncia el servidor (la CVM regenera el ZIP del año en curso casi todas las semanas).

El paso `verificacion` de `actualizar.py` corre pytest y `verificar_gold.py --gold`, y con eso la fuente CVM
queda cubierta dos veces: `tests/test_cvm.py` incluye el verificador de la CVM y `bk_publicado` está en
`contrato_gold.json`, así que `--gold` le aplica las comprobaciones generales (columnas, clave única, períodos,
infinitos). `verificar_cvm.py` se corre aparte cuando se quiere el detalle del contraste.

**Decisiones de diseño que conviene conocer.** (1) El ZIP se vuelve a bajar comparando `Content-Length`, no
hash: comparar el sha256 obligaría a bajarlo siempre. (2) El filtro de bancos es el mapa de
`definiciones/cvm__bancos.json`, no el `SETOR_ATIV` del registro: un CNPJ que no está en el mapa no entra, y
si el derivado trae alguno la corrida falla. (3) Una línea que no se puede resolver no se publica en 0 ni en
NaN: va a `datos/derivado/cvm/bancos/huecos.csv` con su motivo. (4) El 4T no lo publica nadie, así que se
deriva (DFP anual − ITR acumulado a setiembre) y la fila lo dice en `documento=DFP−ITR`. (5) En el 1T la CVM
entrega una sola DRE porque el trimestre y el acumulado arrancan el mismo día: se duplica como
`medida=trimestre` con la nota correspondiente.

---

## 2. Cobertura: quién entrega y quién no

**Entregan ITR/DFP 16 de los 34 bancos del panel.** Los otros 18 quedan con `bk_publicado` vacío, cada uno con
su motivo en `definiciones/cvm__bancos.json`:

| Grupo | Bancos | Motivo (verificado contra el registro de la CVM y los ZIP) |
|---|---|---|
| Reportan en EE.UU. (20-F/6-K) | Nubank, Inter, XP, Stone, PagSeguro | Fuera de alcance en la v1, como dice la tarea. Inter tiene el registro CVM cancelado desde el 02-dic-2022 |
| No son emisores CVM | Caixa, BNDES, C6 Bank, Votorantim, Original, Mercado Pago, Neon, PicPay, CloudWalk | No figuran en `cad_cia_aberta.csv` con el CNPJ líder del conglomerado prudencial. En BNDES el que tiene registro es BNDESPAR, otra compañía |
| Registro cancelado | Safra, Sofisa (24-nov-2016), Agibank (18-ene-2019) | Bancos cerrados o deslistados: no entregan nada en 2023-2026 |
| Caso aparte | Porto Seguro | El CNPJ líder del conglomerado prudencial no es el del emisor CVM (Porto Seguro S.A., aseguradora). Sus estados no tienen líneas bancarias |

Tres bancos del panel que la tarea daba por revisar quedaron resueltos por CNPJ: **ABC Brasil y BRB sí están
en el sector «Bancos» del registro y sí entregan** (no salían con el filtro viejo porque ABC entrega estados
individuales desde el DFP 2024 y BRB no tiene ninguna entrega en 2026); **Banco Pan no** (registro cancelado:
su último ITR es el 3T25, y de todos modos no está en el panel, entra en el conglomerado de BTG).

### Tabla de control (líneas distintas presentes por trimestre, de 11)

| Banco | 4T25 · 1T26 · 2T26 · 3T26 | Detalle en 2T26 |
|---|---|---|
| ABC Brasil | 10 · 10 · 10 · 10 | Ativo, Créd.bruto, PDD, Depós., PL, PL ctrl, Res.int., Lucro, Lucro ctrl, ROE |
| BMG | 10 · 10 · 10 · 10 | idem |
| BRB | — · — · — · — | Última entrega: ITR 2T25, y solo individual |
| BTG Pactual | 9 · 9 · 9 · — | Sin PDD (no la divulga) |
| Banco da Amazônia | 10 · 10 · 10 · — | Todo, en estados individuales |
| Banco do Brasil | 9 · 9 · 9 · — | Sin PDD; crédito neto |
| Banco do Nordeste | 10 · 10 · 10 · — | Todo, en estados individuales |
| Banestes | 9 · 9 · 9 · — | Sin PDD; crédito neto |
| Banrisul | 10 · 10 · 10 · — | Completo |
| Bradesco | 10 · 10 · 10 · 10 | Completo |
| Cielo | 6 · 6 · 6 · — | Solo Ativo, PL, PL ctrl, Lucro, Lucro ctrl, ROE (ver §7.1) |
| Daycoval | 10 · 10 · 10 · 10 | Completo |
| Itaú Unibanco | 10 · 10 · 10 · 10 | Completo |
| Mercantil do Brasil | 10 · 10 · 10 · 10 | Completo |
| Pine | 9 · 9 · 9 · — | Sin PDD; crédito neto |
| Santander Brasil | 7 · 7 · 7 · 7 | Sin crédito, sin PDD y sin depósitos (ver §4) |

En 3T26 solo hay 7 bancos (Itaú, Bradesco, Santander, Mercantil, BMG, ABC y Daycoval): es lo que la CVM tiene
publicado al 8-nov-2026, y coincide con lo que ya había verificado la tarea. BB, BTG, Banrisul, Banestes,
Pine, Amazônia y Nordeste todavía no habían entregado el 3T26 al bajar los ZIP.

De las 11 líneas, 7 son las mínimas de la tarea y 4 son apoyo que hizo falta para no mentir con los rótulos:
`credito_liquido` (cuando el banco entrega la cartera neta), `patrimonio_liquido_controlador` (denominador del
ROE), `lucro_liquido` (total, antes de la atribución) y `roe_anualizado` (derivada).

---

## 3. Itaú 2T26 verificado a mano contra su ITR

Criterio de «terminado» de la tarea: que coincida al R$ mil. Columna 2 = `VL_CONTA` literal del
`itr_cia_aberta_BPA/BPP/DRE_con_2026.csv`, versión 1, `ORDEM_EXERC=ÚLTIMO`, `DT_REFER=2026-06-30`, en R$ mil.
Columna 3 = lo que publicó `bk_publicado`, en R$.

| Línea | Cuenta | VL_CONTA (R$ mil) | bk_publicado (R$) | Cuadra |
|---|---|---|---|---|
| ativo_total | 1 Ativo Total | 3.202.125.000 | 3.202.125.000.000 | ✓ |
| credito_bruto | 1.02.03.05 Operações de Crédito e Arrendamento Mercantil Financeiro | 1.082.266.000 | 1.082.266.000.000 | ✓ |
| provisao_perda | 1.02.03.07 (-) Provisão para Perda Esperada | −49.896.000 | +49.896.000.000 | ✓ (signo) |
| depositos | 2.03.01 Depósitos | 1.134.485.000 | 1.134.485.000.000 | ✓ |
| patrimonio_liquido | 2.08 Patrimônio Líquido Consolidado | 228.026.000 | 228.026.000.000 | ✓ |
| patrimonio_liquido_controlador | 2.08 − 2.08.09 | 228.026.000 − 10.247.000 | 217.779.000.000 | ✓ |
| resultado_intermediacion (trim.) | 3.03, `DT_INI_EXERC=2026-04-01` | 37.059.000 | 37.059.000.000 | ✓ |
| resultado_intermediacion (acum.) | 3.03, `DT_INI_EXERC=2026-01-01` | 71.756.000 | 71.756.000.000 | ✓ |
| lucro_liquido_controlador (trim.) | 3.09.01 | 11.979.000 | 11.979.000.000 | ✓ |
| lucro_liquido_controlador (acum.) | 3.09.01 | 23.615.000 | 23.615.000.000 | ✓ |
| roe_anualizado | derivado | — | 0,2248 (22,5 %) | ✓ (ver §7.2) |

Tres comprobaciones independientes, además del calce cuenta por cuenta:

1. **Contra lo que ya tenía el repo.** `definiciones/validacion_bancos.json` anota para Itaú 2T26
   «Depósitos gaap 1.134,49» (en R$ mil millones): la CVM da 1.134.485.000 mil = R$ 1.134,49 mil millones,
   **calce exacto**. Su «Ativo total gaap 3.226,84» es la cifra IFRS del reporte; la CVM da R$ 3.202,13 mil
   millones (−0,8 %), diferencia esperable entre el CPC de la CVM y el IFRS del ADR.
2. **Aritmética del estado.** `verificar_cvm.py` comprueba que la cuenta 1 iguala la suma de sus componentes
   1.0x en cada entrega: **131 de 131 cuadran al R$**. Si se leyera otra versión u otro tipo de estado, esto
   saltaría.
3. **Escala.** El verificador vuelve a calcular una muestra de 40 filas del gold desde el derivado
   (`VL_CONTA × 1000` cuando `ESCALA_MOEDA=MIL`) y exige coincidencia al centavo. Es la prueba de que no se
   publicó en R$ mil.

---

## 4. Huecos y líneas vacías

**38 huecos** (líneas buscadas que no dieron número) en `datos/derivado/cvm/bancos/huecos.csv`, todos por
limitaciones de lo que el banco llenó en el archivo estructurado:

| Banco | Línea | Cuántos | Por qué |
|---|---|---|---|
| Santander | crédito, PDD, depósitos | 32 | Llena el archivo estructurado de forma irregular: en el DFP 2023 y 2025 vuelca todo el costo amortizado en una sola cuenta (1.02.04.01) y deja las demás en 0; en los ITR de 2025 en adelante no abre el nivel 3. Solo el DFP 2024 trae la cartera bruta (R$ 594.776 millones) con su provisión (R$ −33.598 millones) y solo el ITR 1T25 trae «Empréstimos e Adiantamentos a Clientes» (R$ 536.194 millones, neto) |
| ABC Brasil, Mercantil | provisao_perda | 4 | En el DFP 2023 y 2024 dejan 1.02.04.05 en 0 y recién publican la provisión desde el 1T25. Por eso su cartera de 2023-2024 se publica como `credito_liquido` y la de 2025 en adelante como `credito_bruto`, con ventanas explícitas en el mapeo |
| Pine | depositos | 2 | En el DFP 2023 y 2024 no abre 2.03 «Passivos Financeiros ao Custo Amortizado» |

**7 líneas vacías por diseño** (no se buscan; el motivo está en `definiciones/cvm__bancos_lineas.json`, no
generan hueco y jamás se publican en 0):

- **Banco do Brasil, Banestes y Pine**: `credito_bruto` y `provisao_perda`. Los tres dejan 1.02.04.05 en 0 en
  *todos* los periodos, o sea que entregan la cartera ya neta y no divulgan el saldo de la provisión. Su
  cartera se publica como `credito_liquido`. En BB lo confirma `validacion_bancos.json` («Neto de provisión
  p.64; bruto 1.245,87»). La despesa del periodo sí está (3.04.01), pero es un flujo y la tarea pedía el saldo.
- **BTG Pactual**: `provisao_perda`. No la divulga en cuentas estructuradas (2.04.02 es provisión de avales y
  fianzas, otra cosa). Su cartera se publica como bruta; el contraste contra `credito_total` de IF.Data da
  +8,2 % en 2T26, consistente con bruto.
- **Cielo**: no tiene `credito_*`, `provisao_perda`, `depositos` ni `resultado_intermediacion`, porque entrega
  el plan de cuentas de una compañía no financiera.

**BRB** es un caso aparte: su última entrega es el ITR 2T25 y solo en versión individual (el consolidado se
corta en el 1T25). El registro de la CVM lo sigue dando como ATIVO, Categoria A. Además, en la DFP 2023 y 2024
entregó una DRE que cubre **solo diciembre** (`DT_INI_EXERC` = 2023-12-01 y 2024-12-01), así que esas dos
filas anuales se descartan con aviso y BRB queda sin flujos anuales. Vale la pena averiguar por qué dejó de
entregar antes de mostrar sus cifras en el sitio.

---

## 5. Contraste contra IF.Data

`pipeline/cvm.py contrastar` compara cada banco y trimestre presente en los dos universos. No corrige nada:
informa la diferencia en % como `(IF.Data − CVM) / CVM`. Son **755 comparaciones**, 555 «principales» (la
métrica de IF.Data que mejor se compara con cada línea) y 200 secundarias. Salida completa en
`datos/derivado/cvm/bancos/contraste_ifdata.csv`.

### 2T26, activo y PL (lo que pedía la tarea)

| Banco | Ativo CVM | Ativo IF.Data | dif | PL CVM | PL IF.Data | dif |
|---|---|---|---|---|---|---|
| ABC Brasil | 67.784 | 69.585 | +2,7 % | 7.259 | 7.279 | +0,3 % |
| BMG | 49.732 | 49.001 | −1,5 % | 5.075 | 4.319 | −14,9 % |
| BTG Pactual | 929.990 | 858.357 | −7,7 % | 89.941 | 84.250 | −6,3 % |
| Banco da Amazônia | 67.353 | 67.353 | −0,0 % | 7.274 | 7.274 | −0,0 % |
| Banco do Brasil | 2.588.104 | 2.583.569 | −0,2 % | 190.768 | 181.838 | −4,7 % |
| Banco do Nordeste | 81.040 | 81.143 | +0,1 % | 16.813 | 16.916 | +0,6 % |
| Banestes | 42.442 | 42.582 | +0,3 % | 2.512 | 2.505 | −0,3 % |
| Banrisul | 172.694 | 172.605 | −0,1 % | 11.848 | 11.555 | −2,5 % |
| Bradesco | 2.468.827 | 2.015.224 | **−18,4 %** | 182.737 | 185.191 | +1,3 % |
| Cielo | 115.147 | 115.136 | −0,0 % | 14.163 | 15.322 | +8,2 % |
| Daycoval | 108.141 | 107.666 | −0,4 % | 7.811 | 7.656 | −2,0 % |
| Itaú Unibanco | 3.202.125 | 2.846.418 | −11,1 % | 228.026 | 249.766 | +9,5 % |
| Mercantil do Brasil | 38.958 | 42.662 | +9,5 % | 3.151 | 3.134 | −0,5 % |
| Pine | 35.354 | 37.630 | +6,4 % | 1.831 | 1.832 | +0,1 % |
| Santander Brasil | 1.290.559 | 1.314.933 | +1,9 % | 129.093 | 106.733 | **−17,3 %** |

*(R$ millones. dif = (IF.Data − CVM) / CVM; negativo significa que la CVM es mayor.)*

**Solo tres comparaciones principales superan el 15 % en 2T26**, y las tres tienen lectura:

1. **Bradesco, activo −18,4 %**: el consolidado societario incluye seguros y previdência, que el conglomerado
   prudencial no consolida igual. Es exactamente el −18,4 % que ya anotaba
   `definiciones/validacion_bancos.json` («el consol. IFRS da −18,4 % (seguros)»): la fuente nueva reproduce
   un número que el repo ya tenía a mano desde el reporte.
2. **Santander, PL −17,3 %**: sistemático en los 8 trimestres (−14,1 % a −18,5 %). El PL de la CVM trae R$ 65.000
   millones de capital social y R$ 66.859 millones de reservas de lucros, total R$ 129.093 millones, contra
   R$ 106.733 millones del PL prudencial. **No tengo explicación cerrada**: la hipótesis razonable es
   tratamiento distinto de instrumentos híbridos o del goodwill (R$ 27.770 millones en la CVM), pero no lo pude
   verificar sin leer los estados, y `referencias/` está fuera de alcance. Queda para Pablo (§7.3).
3. **Santander, lucro +23,1 %**: consecuencia de la trampa del impuesto en 0 (§6). El total que publicamos
   (R$ 2.963 millones en el trimestre) se reconstruye sumando la atribución a controladores y no controladores,
   que sí viene después de impuestos; el 3.09 que entrega Santander (R$ 8.104 millones acumulados) es antes de
   impuestos.

### El resto del contraste, en cifras

| Comparación principal | n | >15 % | dif abs. media | máx |
|---|---|---|---|---|
| ativo_total (2025 en adelante) | 92 | 6 | 3,6 % | 19,0 % |
| ativo_total (antes de 2025) | 32 | 2 | 2,9 % | 16,8 % |
| depositos (2025+) | 81 | 1 | 2,8 % | 19,0 % |
| patrimonio_liquido (2025+) | 92 | 10 | 4,5 % | 30,1 % |
| credito → `credito_total` (2025+) | 81 | 4 | 6,9 % | 21,5 % |
| credito → `credito_total` (pre-2025) | 27 | 19 | 21,5 % | 68,1 % |
| lucro_liquido → `lucro_liquido_q` (2025+) | 92 | 15 | 28,7 % | 1.850 % |

Tres lecturas:

1. **El activo, los depósitos y el PL calzan bien**: diferencia media de 3-4 %, y 0,0 % en Banco da Amazônia,
   Banco do Nordeste y Cielo (cuyos estados individuales *son* el conglomerado prudencial). Es la mejor
   evidencia de que la extracción está bien.
2. **El crédito pre-2025 no es comparable** (21,5 % de diferencia media, 68 % máximo): la frontera COSIF de
   2025-T1 cambió la definición de `credito_total` en IF.Data (el salto ya está documentado en `spec/08`).
   De 2025 en adelante la diferencia media baja a 6,9 %. Además la «Operações de Crédito» de la CVM se parece al
   `credito_total` del COSIF, no a su `credito_bruto`: en 2T26 BB da +1,1 % contra `credito_total` y −17,3 %
   contra `credito_liquido`; Santander +0,3 % y Pine +2,8 %. Por eso la comparación principal es contra
   `credito_total` y la de mismo nombre queda como secundaria.
3. **El lucro trimestral tiene cola pesada.** 15 de 92 comparaciones pasan el 15 %, casi todas en 1T25 y en
   bancos chicos: Banestes 2T25 da +1.850 % porque su trimestre CVM fue de R$ 7,1 millones contra R$ 139,2
   millones del IF.Data (un trimestre realmente malo en la contabilidad societaria, no un error de extracción:
   el acumulado de 1S25 de Banestes es R$ 118,8 millones y el de 1T25 R$ 111,7 millones, así que al 2T le toca
   7,1). Santander (+23 a +94 %) arrastra la trampa del impuesto. En los grandes el calce es bueno: Cielo
   −0,0 %, Amazônia y Nordeste +0,0 %, Bradesco −2,4 %, Itaú +1,6 %, BB +2,7 %.

---

## 6. Trampas nuevas (detalle en `spec/08`)

Todas verificadas sobre el dato, todas con prueba en `tests/test_cvm.py`:

1. **El plan de cuentas cambió con el CPC 48 y cada banco migró cuando quiso.** Itaú, BMG y BTG usan el
   esqueleto nuevo desde 2023 (PL en 2.08, lucro en 3.09); BB, Bradesco, Banrisul y el resto siguen en el viejo
   (PL en 2.07, lucro en 3.11). **Pine fue del nuevo al viejo entre el DFP 2024 y el ITR 1T25**: el mismo
   `CD_CONTA` 2.07 fue «Patrimônio Líquido Consolidado» y hoy es «Passivos sobre Ativos Não Correntes a Venda».
   Por eso el mapeo exige código **y** texto de la descripción, con alternativas ordenadas y ventanas
   `desde`/`hasta`. Si una regla no casa, la línea queda vacía: nunca se adivina.
2. **Santander entrega el impuesto (3.06) en 0** en varios ITR, con lo que su «Lucro/Prejuízo Consolidado»
   queda antes de impuestos. Se reconstruye sumando 3.09.01 + 3.09.02.
3. **Cuentas duplicadas en 0**: en el ITR 3T25 BB llenó también las cuentas del esqueleto nuevo (3.09.01/02)
   con 0 junto a las suyas (3.11.01/02). Regla: si de las que casan solo una trae número, vale esa; si dos
   traen número, es ambigüedad y la línea queda vacía con aviso.
4. **Un 0 en una cuenta de saldo no es un dato** (`cero_es_vacio`): BB, Banestes, Pine, ABC y Mercantil dejan
   la provisión en 0, y Santander entrega la cartera y los depósitos en 0 en los años que no detalla. Esos 0
   van a `huecos.csv`, no al gold.
5. **Banestes deja la atribución del lucro en 0** en los ITR de 1T y 3T: se resuelve por la segunda
   alternativa (total − no controladores), que en su caso da casi lo mismo porque su participación minoritaria
   es R$ 3,8 millones sobre R$ 11.848 millones de PL.
6. **En el 1T la DRE es una sola fila** (trimestre = acumulado) y **el 4T no existe**: se duplica la del 1T y
   se deriva el 4T restando el acumulado de setiembre del anual.
7. **BRB entrega en la DFP una DRE mensual** (`DT_INI_EXERC` = 01-12): se descarta con aviso.
8. **Los ZIP de estados traen una sola versión por entrega**, pero el índice lista todas las reentregas con su
   `DT_RECEB`: la fecha de entrega se cruza por la versión que se usó.
9. **Tres bancos solo entregan estados individuales** (ABC desde 2024, Amazônia y Nordeste siempre) y BRB
   desde el 2T25. La base va en la columna `consolidacion` y el mapa fija una sola base por banco para que la
   serie no cambie a mitad de camino. Excepción declarada: Daycoval 3T26, donde la CVM todavía no publicó el
   consolidado y se usa el individual con `usar_individual_si_falta`.

---

## 7. Decisiones que quedan para Pablo

### 7.1 Cielo dentro o fuera de `bk_publicado`
Cielo está en el panel como institución de pagos (modelo «Pagos») y sí entrega ITR/DFP, pero con el plan de
cuentas de una compañía no financiera: tiene ativo (R$ 115.147 millones, calca al 0,0 % con IF.Data), PL y lucro, y no
tiene cartera, depósitos ni resultado de intermediación. **Hoy está adentro con esas 6 líneas.** Las otras
«Pagos» del panel (Stone, PagSeguro, Mercado Pago, CloudWalk) no tienen nada, así que el grupo queda
desparejo. Alternativas: dejarlo como está, sacarlo del mapa (poner `entrega: false` con nota), o publicar
solo las tres líneas que sí son comparables. Es una decisión de presentación, no de datos.

### 7.2 Bajar también el ITR 2024
El ROE anualizado usa el PL promedio de 12 meses ((PL_t + PL_t−4)/2, la convención del repo para el ROE de
IF.Data). Con la ventana actual (ITR 2025-2026 + DFP 2023-2025) el ROE existe desde 4T25; los trimestres 1T25,
2T25 y 3T25 quedan sin ROE porque falta el PL de 1T24, 2T24 y 3T24. Sumar `2024` a `ANIOS_ITR` en
`pipeline/cvm.py` (una línea) llena esos tres trimestres a cambio de ~30 MB más de crudo y ~2 minutos más por
corrida. La tarea pedía ITR 2025-2026, así que no lo cambié por mi cuenta.

También queda la duda de fondo sobre el ROE: la tarea dice «lucro trimestral × 4 / PL promedio» y el repo
calcula el ROE de IF.Data como TTM sobre PL promedio de 12 meses. Hice el anualizado del trimestre con el
promedio de 12 meses. Si se prefiere el promedio del trimestre ((PL_t + PL_t−1)/2, que es lo que usan los
bancos en sus releases) es un cambio de dos líneas en `_roe_anualizado`.

### 7.3 Santander: PL −17 % y lucro +23 % contra IF.Data
Son las dos diferencias sistemáticas sin explicación cerrada (§5). El PL es consistente en los 8 trimestres,
así que no es un error de extracción sino de perímetro o de clasificación. Hace falta leer las notas de sus
estados (fuera de mi alcance: `referencias/` no se toca) o aceptar la diferencia y rotularla.

### 7.4 `bk_puente`
La tarea pedía revisar si puede consumir `bk_publicado`. **Puede, pero no conviene todavía.** `bk_puente`
(`preparar_gold_bancos.py::_bk_puente`) lee `definiciones/validacion_bancos.json`, que son 26 cifras cargadas a
mano con notas de página («Individual p.14», «Neto de provisión p.64») y líneas que la CVM no tiene
(«Repos», «Crédito (nota 8a)», «Lucro 1H»). `bk_publicado` cubriría bien cuatro de esas líneas
(ativo, depósitos, crédito y lucro) para 16 bancos × 9 trimestres en vez de 8 bancos × 1 trimestre, pero
perdería las notas de página y el criterio de selección de Pablo, que es justamente lo que hace útil al
puente. Propuesta: dejar `bk_puente` como está y usar `bk_publicado` para una tarjeta nueva de «último
trimestre publicado», y si en algún momento se quiere automatizar el puente, hacerlo con una línea nueva
(`bk_puente_auto`) que no pise la cargada a mano. No toqué nada de esto.

### 7.5 Rótulo de la base contable
La tarea pedía «IFRS o BR GAAP» por banco. El archivo de la CVM no trae ese campo y no quise inventarlo:
todas las filas llevan `base = "CPC"`, que es lo que son (pronunciamientos del CPC que exige la CVM, BR GAAP
convergido con IFRS), distinto de COSIF (IF.Data) y distinto del IFRS que emite el IASB y que los bancos con
ADR publican por separado. Si Pablo quiere el rótulo IFRS/BR GAAP por banco, hay que definirlo a mano en
`definiciones/cvm__bancos.json` (campo `base`) y decirme el criterio.

### 7.6 Crédito bruto contra neto
Clasifiqué la cartera de cada banco como `credito_bruto` o `credito_liquido` según si divulga la provisión en
las cuentas estándar, y lo verifiqué contra IF.Data donde se pudo (Mercantil 2023: CVM R$ 13.323 millones contra
`credito_liquido` de IF.Data R$ 13.420 millones → neto; Mercantil 1T25: CVM R$ 18.985 millones contra
`credito_bruto` R$ 18.510 millones → bruto).
Es una clasificación contable, no un dato de la fuente: si Pablo prefiere una sola línea `credito` con un
atributo `bruto_o_neto`, es un cambio chico pero rompe la comparación simple entre bancos.

### 7.7 Archivos de trabajo en `tareas/borradores/`
Quedaron los scripts de exploración y sus volcados. Los scripts (`cvm_explorar.py`, `cvm_explorar2.py`,
`cvm_cuentas.py`, `cvm_sondeo.py`, `cvm_sondeo2.py`, `cvm_generar_mapa.py`, `cvm_generar_lineas.py`,
`cvm_notas_mapa.py`) sirven para repetir el relevamiento cuando la CVM cambie el plan de cuentas. Los
volcados pesan: `cvm_inventario.csv` (4,0 MB), `cvm_panel_todos.csv`, `cvm_coberturas.csv`, `_sondeo*.txt`,
`_mapa_preview.txt`, `_extraer.log`, `_todo.log`, `_informe_datos.txt`, `_informe_tabla.txt`. **No borré nada**:
con su permiso se borran los volcados y se guardan los scripts.

### 7.8 Lo que falta para cerrar el frente
- Conectar la tarjeta B8-06-0 (fuera de alcance: otra sesión está con el diseño).
- Decidir 7.1 a 7.6.
- Averiguar por qué BRB dejó de entregar después del 2T25.
- Vigilar Daycoval 3T26: si la CVM publica el consolidado, hay que volver a correr `extraer` y `gold` para que
  la fila pase de `ind` a `con`.
