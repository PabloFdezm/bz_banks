# 1 · Correcciones de datos (auditoría del 6-nov-2026)

Resultado de la auditoría: los datos están sanos (115 tests OK, `verificar_gold` OK, sin infinitos ni duplicados;
mora del sistema, crecimiento del crédito y lucro de Itaú/Bradesco calzan con lo publicado). Lo que sigue son los
hallazgos a corregir. Después de cada arreglo: `actualizar.bat`, tests, `comparar_gold.py` contra el gold anterior
para confirmar que solo cambia lo esperado.

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
