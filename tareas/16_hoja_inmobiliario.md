# Frente 16 · Hoja «Inmobiliario»: códigos SGS que faltan y paso a gold

Estado al 10-nov-2026: **por hacer**. Encargo pensado para que lo ejecute otra sesión u otra LLM sin contexto previo.
Leer antes `CLAUDE.md`, `tareas/README.md` y `tareas/12_hoja_tarjeta.md` (mismo patrón de gold por producto).

## Contexto
- Hoja del canvas `Inmobiliario.dc.html` (6 secciones: Volumen, Precio, Calidad, Deudor, Emisor, Fondeo), construida el
  10-nov con la propuesta aprobada `ProdInmobiliario.dc.html`. Borrador: `tareas/borradores/_salida/extraer_inmobiliario.py`
  (fuera de git) → `inmobiliario.json`.
- Fuentes: crudo SGS (20612, 20702–20704, 20772–20774, 21149–21151, 4189), cubo SCR producto «Inmobiliario» (el
  borrador lo calcula en memoria con `preparar_gold_bancos_producto_pf.construir_scr`, sin publicar), IF.Data
  (`bk_cartera_mix7`, categoría hipotecario) y `bk_fondeo_m` (ahorro y letras de crédito).

## Parte A · Datos SGS que faltan (bajar desde el equipo de Pablo)
- `20610` saldo inmobiliario PF con tasa de mercado y `20611` con tasa regulada (hoy «en preparación» en P1).
- Agregar a `sgs.CODIGOS` y al catálogo los que ya están en el crudo pero sin nombre: 20612, 20702, 20703, 20704,
  20772, 20773, 20774 (y revisar 21340, 21387, 21395, 240 y 192 de la carpeta `crudo/bcb_sgs/inmobiliario`: confirmar
  qué son o sacarlos). Identidad a verificar: 20702 + 20703 = 20704 (concesiones) y, con 20610/20611, 20610 + 20611 = 20612.

## Parte B · Paso a gold
- Agregar `inmobiliario` a `PRODUCTOS_SGS` y `PRODUCTOS_SCR` de `preparar_gold_bancos_producto_pf.py` (submodalidades:
  mercado y regulada; SCR: «Inmobiliario»; instituciones de pago y fintechs a «Otros», como hace el borrador).
- El borrador pasa a leer solo de gold, igual que `extraer_producto.py`.
- Tests: los de la parte B del frente 12 con el producto nuevo.

## Parte C · Verificaciones
1. Activo problemático 5,1 % contra mora 1,5 % (sep-26): confirmar que la diferencia son reestructuraciones y no un
   cambio de definición de la Res. 4.966; medir desde cuándo.
2. Concesiones con tasa de mercado −39 % a/a y regulada +26 % (sep-26): confirmar con las notas del BCB o de la Abecip
   si es traslado de originación de SBPE-mercado a SFH/MCMV.
3. Cobertura poupança / crédito inmobiliario PF: 71 % a sep-26 (80 % un año antes). Confirmar que el denominador
   correcto es el saldo PF (20612) o PF + PJ (20600).
4. Cuántas LCI hay dentro de «letras de crédito» (27807 junta LCI y LCA): buscar una serie de LCI sola (B3 o REF
   1.2.1.1.a) para reemplazar la cota superior de P6.

## Terminado cuando
A y B en verde (catálogo, gold, tests), C informado en `tareas/borradores/inmobiliario_verificaciones.md`, y la hoja
regenerada desde gold sin series «en preparación». Nada se commitea sin pedirlo a Pablo.
