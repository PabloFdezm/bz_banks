# 1 · Correcciones de datos (auditoría del 6-nov-2026)

Resultado de la auditoría: los datos están sanos (115 tests OK, `verificar_gold` OK, sin infinitos ni duplicados;
mora del sistema, crecimiento del crédito y lucro de Itaú/Bradesco calzan con lo publicado). Lo que sigue son los
hallazgos a corregir. Después de cada arreglo: `actualizar.bat`, tests, `comparar_gold.py` contra el gold anterior
para confirmar que solo cambia lo esperado.

## Avance 6-nov (tarde)
Cerradas 1.1–1.5. Verificación: 117 tests OK, `verificar_gold` OK, `verificar_f1` OK, `comparar_gold` contra el gold
previo con diferencias solo en lo esperado (grupos por segmento; `bk_panel` sin filas nulas; `bk_sistema_m/q`).
Abierta: 1.6 (notas de lectura).

- **1.1 hecho.** `leer_cadastro()` toma el Sr más frecuente del conglomerado cuando la fila propia viene nula. Daycoval
  → S3, XP → S2; solo Cielo queda «Sin segmento». Test `test_sin_segmento_solo_si_la_fuente_no_lo_trae`. Cambian los
  grupos S2/S3/«Sin segmento» en `bk_grupo`, `bk_cre_*` y `bk_roe_arbol`.
- **1.2 no era error de cálculo.** `tot[x.index[-1]]` busca por fecha: el share de agosto ya usa el total de agosto
  (tarjeta 740,4 / 7.412,4 = 9,99 %). Lo único es que la tabla mezcla filas a ago y a sep, con el Corte visible por
  fila. Decisión de Pablo (6-nov): se deja así, cada fila con su Corte. Cerrada.
- **1.3 hecho, y con un hallazgo mayor:** `preparar_gold_bancos_sistema.py` escribía `bk_sistema_m/q` en
  `datos/intermedio/Banks/` (ruta heredada de Dashboard), no en `datos/gold/`. El gold que lee el sitio no se
  refrescaba con `actualizar.bat`. Corregido. Además endeudamiento (29037), comprometimiento (29034) y desocupación
  (24369) se leen ahora del SGS: llegan a ago-26 (50,1 % / 29,0 %) y sep-26 (5,2 %). `selic_real_exante` y Focus
  siguen congelados en `datos/intermedio/` (pendiente 4 de spec/08, parcial).
  `datos/intermedio/Banks/` quedó huérfana: borrada el 6-nov.
- **1.4 hecho.** `verificar_f1` lee el `<strong>` de `.estado-datos`. También estaba roto el chequeo de errores
  (buscaba `.error-dato`, que ya no existe): ahora marca los mensajes «No pudimos…».
- **1.5 hecho.** Causa: `stack()` descarta NaN en pandas 2 y no en pandas 3. `_bk_panel` usa
  `stack(future_stack=True).dropna()` (104.396 filas en cualquier versión); `requirements.txt` pide pandas ≥ 2.1. Dos
  tests de 78d que fallaban con pandas 3 quedaron compatibles.

## 1.1 Segmento S1–S5 mal asignado (error real)
- Daycoval (C0081744) y XP (C0082475) salen «Sin segmento» en `bk_banco.segmento_reg`; en el cadastro del BCB son
  **S3** y **S2**. Cielo (C0084710) sí viene sin segmento en la fuente (correcto).
- Causa: `pipeline/preparar_bancos_powerbi.py` → `leer_cadastro()` filtra `CodInst == código del conglomerado`. Para
  estos dos la fila propia tiene `Sr = null` desde 2025-T4; las filas de sus instituciones
  (`CodConglomeradoPrudencial == código`) traen el segmento.
- Arreglo: si `sr` de la fila propia es nulo, tomar el valor no nulo más frecuente entre las filas con
  `CodConglomeradoPrudencial == cod_inst` del mismo período. Corrige también `preparar_credito_paginas_powerbi.bancos()`,
  que lee `bank_instituciones`.
- Test nuevo: ningún banco del panel con `segmento_reg == "Sin segmento"` salvo los que la fuente deja sin segmento
  en todas sus filas (hoy solo Cielo).

## 1.2 Crédito lámina 01: corte mezclado en la tabla «tipos»
- `bk_cred_tablas`, bloque `tipos`: las modalidades libres (tarjeta, consignado, personal, vehículos, empresas libre)
  vienen a ago-26 y las direccionadas y el Total a sep-26 (libre/direccionado del SGS llegan con un mes de rezago,
  ver spec/08). El Share divide saldo de agosto por total de septiembre.
- Arreglo en `pipeline/preparar_gold_bancos_pag_credito.py` (líneas ~84–92): calcular `share` con el total del
  **mismo mes** de cada fila (`tot[x.index[-1]]` ya lo intenta: revisar que el índice del total y de la fila
  coincidan en fecha y no en posición). Mostrar el Corte real en cada fila (ya está).

## 1.3 Insumos macro con un mes de rezago (B1)
- `bk_sistema_m`: endeudamiento, comprometimiento y desocupación llegan a jul-26; agosto ya está publicado
  (endeudamiento 50,1 %). Es el pendiente 4 de spec/08: leer `fh_deuda`, `tasa_real_exante` y similares directo del SGS.

## 1.4 verificar_f1 da falso negativo
- Busca el texto «En preparación:» en `.preparacion`; la página ahora muestra «Sin datos disponibles» vía
  `estadoDatos()` en `sitio/assets/js/pagina.js`. Ajustar `herramientas/verificar_f1.py` (líneas ~67 y ~138) al
  marcado actual. Criterio: corre en OK con el sitio actual.

## 1.5 pandas distinto entre equipos
- Pendiente 3b de spec/08: fijar versión en `requirements.txt` o filtrar `valor` nulo en `bk_panel`.

## 1.6 Notas de lectura (no son errores; agregar nota en la tarjeta o en la ficha)
- **Nubank 2T26:** vencido ≥15 días cae 26 % t/t con saldo plano (tarjeta 15,8 → 11,9; personal 7,6 → 5,1 mil
  millones); NPL15 de 12,9 % a 9,5 %. Probable venta de cartera castigada o cambio de política de castigos. PagSeguro
  −43 %. Confirmar con el release de Nu 2T26 y anotar.
- **Nubank ROE ~51 %:** el conglomerado prudencial en Brasil tiene poco patrimonio frente a la holding (Nu Holdings
  ~30 %). Correcto con datos del BCB; requiere nota.
- **BRB** no reporta 2T26 (último 3T25). **2024-T4** vacío a propósito (trimestre anómalo de IF.Data).

## Contrastes usados (para repetir la auditoría)
| Dato | Gold | Publicado |
|---|---|---|
| Mora total SFN jun-26 / jul-26 | 4,59 % / 4,88 % | 4,6–4,7 % / 4,9 % (BCB, nota de crédito) |
| PJ libre jul-26 | 4,21 % | 4,2 % |
| Crédito real a/a jun-26 | 4,8 % (≈ 9,7 % nominal) | 9,7 % nominal |
| Lucro Itaú 2T26 (prudencial) | R$ 12,52 mil mill. | R$ 12,4 mil mill. gerencial |
| Lucro Itaú / Bradesco 2T25 | 11,50 / 6,05 | 11,5 / 6,07 |

## 1.7 Concesiones mal rotuladas (hallazgo del 6-nov)
- `pipeline/preparar_gold_bancos_pag_credito.py`, línea ~48: `CONCESIONES = [("Concesiones libres", 20631), …]`.
- 20631 es el **total** de concesiones, libres más direccionadas: 20631 = 20632 (PJ) + 20633 (PF), con el mismo
  patrón que los stocks 20539/20540/20541.
- Las concesiones libres son 20634 (total), 20635 (PJ) y 20662 (PF). Hoy solo está descargada 20662.
- Arreglo:
  - renombrar la fila a «Concesiones totales» o cambiar a 20634;
  - descargar 20634 y 20635.
- Validar contra el catálogo del SGS antes de cerrar.
