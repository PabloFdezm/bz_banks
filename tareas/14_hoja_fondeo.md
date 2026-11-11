# Frente 14 · Hoja «Fondeo y liquidez»: datos SGS que faltan y pipeline

Estado al 10-nov-2026: **A y B hechas, C informada; faltan decisiones de Pablo y las tasas por inversionista.**
Leer antes `CLAUDE.md` y `tareas/README.md`.

### Avance (10-nov)
- A: 14 códigos de agregados monetarios (`mp_*`, 27789–27815) y `mp_ahorro` (1835) en `sgs.CODIGOS`, catálogo y crudo.
  Todos en R$ mil. 27807 = letras de **crédito** (LCI/LCA), no de cambio; 27811 = cuotas de fondos monetarios. La
  poupança está dentro de M2 (M2 = M1 + 27809 + 1835, exacto). Las tasas 28583/28611/28614/28617 fallan en la API del
  SGS (HTML/500): fuera de `CODIGOS` hasta poder bajarlas. Alternativa parcial ya en gold: REF 1.2.1.4 («Taxas
  médias mensais de captação», % del DI, jun-22 a jun-26 en `bk_ref`), por segmento (S1 privado, públicos, digitales,
  SNCC, demás) y no por inversionista. Decide Pablo si cubre la sección mientras.
- B: `pipeline/preparar_gold_bancos_fondeo.py` → `bk_fondeo_m` (serie, medida, fecha, valor; saldo en R$ millones,
  aa, share_m2, share_m4 y tasa si hay crudo), contrato en `definiciones/contrato_gold.json`, paso `fondeo` en
  `pipeline/actualizar.py` después de `producto_pf`, pruebas en `tests/test_fondeo.py` (8, pasan). El borrador
  `extraer_fondeo.py` lee ahora `bk_fondeo_m`, `bk_ref` y `trimestral_pagina.json`; copia del JSON anterior en
  `tareas/borradores/_salida/fondeo_previo_20261110.json`.
- C: `tareas/borradores/fondeo_verificaciones.md`. 1835 en R$ mil (R$ 1.019,6 mil millones a sep-26); bk_ref
  1.2.1.1.a y 1.2.1.7 en R$; «Desarrollo» 1.442 % correcto (BNDES).
- Pendiente: (1) M3 no cierra con 27811 + 27812 (residuo R$ 161 mil millones a sep-26, va como `m3_sin_desglose`):
  buscar el código que falta; (2) tasas por inversionista; (3) decisiones de Pablo listadas en el informe de C
  (poupança dentro de M2, «Desarrollo» en el gráfico de crédito/depósitos, unidades en `ref.py`, 1.2.1.5 vs 1.2.1.7);
  (4) spec autogenerada y manifiesto: correr `generar_spec.py` y `manifiesto_gold.py` cuando no haya otras sesiones.

## Contexto
Hoja del canvas de rediseño `Fondeo.dc.html`, armada con el borrador `tareas/borradores/_salida/extraer_fondeo.py`
(fuera de git) → `fondeo.json`. Fuentes: crudo SGS, `bk_ref` (REF, sección 1.2.1) y `trimestral_pagina.json`
(IF.Data por modelo de negocio). Siete secciones: F1 Volumen (componentes de M2 y cuentas de ahorro), F2 Precio (tasa de
captación % CDI por segmento; costo de captación por grupo), F3 Instrumentos, F4 Inversionista y canal (plataformas),
F5 Por grupo de bancos (depósitos por tipo; crédito/depósitos), F6 Liquidez (LCR y NSFR), F7 Captación externa.

## Parte A · Códigos SGS que faltan (bajar desde el equipo de Pablo y validar con `herramientas/validar_sgs.py`)
- Agregados monetarios, metodología nueva, saldo a fin de período: `27789` moneda, `27790` depósitos a la vista,
  `27791` M1, `27805` depósitos a plazo, `27806` letras financieras, `27807` letras de cambio, `27808` otros títulos
  privados, `27809` títulos privados, `27810` M2, `27811` fondos de renta fija de corto plazo, `27812` pactos con títulos
  privados, `27813` M3, `27814` títulos federales, `27815` M4.
- Tasas de depósitos a plazo por inversionista (promedio diario del mes): `28583` personas, `28611` empresas,
  `28614` institucionales, `28617` instituciones financieras.
- Opcional: captación neta diaria de depósitos a plazo `243`, `244`, `1169` (agregar a mensual).
- Confirmar en la nota metodológica del BCB si las cuentas de ahorro (`1835`, ya en el crudo) están dentro de M2 en la
  metodología nueva; la hoja hoy las muestra aparte.

## Parte B · Pipeline
Gold `bk_fondeo_m` (SGS mensual) y uso directo de `bk_ref` para F3, F4, F6 y F7. Tests: la suma de componentes cuadra
con M2 (tolerancia por redondeo) y las participaciones suman 100 %.

## Parte C · Verificaciones
1. Unidad de `1835` (la hoja asume R$ mil; saldo ~R$ 1,02 billones a ago-26).
2. Unidades del stock en `bk_ref` 1.2.1.1.a y 1.2.1.7 (la columna `unidad` viene vacía).
3. F5: el cociente crédito/depósitos de «Desarrollo» (~1.400 %) es correcto por construcción; confirmar que no haya un
   error de agregación del grupo.

## Terminado cuando
Códigos en `sgs.CODIGOS`, catálogo y crudo; gold y tests; informe corto de C en `tareas/borradores/fondeo_verificaciones.md`.
Nada se commitea sin pedirlo a Pablo.

## Decisiones de Pablo del 10-nov (tarde) y pendientes de pipeline
Aplicado en la hoja: «Desarrollo» fuera del gráfico de crédito/depósitos (queda en la tabla, con nota); título
«Componentes de M2» con la poupança dentro de M2.
Para hacer:
1. Tasas de depósitos a plazo por inversionista: 28583, 28611, 28614 y 28617 no existen en el SGS. Buscar los códigos
   correctos (catálogo del SGS, «Taxa média de captação» o «CDB») y, si no existen, usar el REF 1.2.1 (tasas de
   captación % del CDI por segmento) y decirlo en la nota.
2. `pipeline/ref.py`: completar `unidad = "R$"` en 1.2.1.1.a, 1.2.1.5, 1.2.1.7 y 1.2.1.10, y agregar una clave estable
   por título del gráfico además del número (la numeración cambia entre ediciones).
3. Buscar la partida que falta para cerrar M3 (códigos 27792–27804) antes de mostrar la composición de M3/M4.

## Decisiones de Pablo (11-nov, desde el celular)
- «Desarrollo» **fuera del gráfico** crédito/depósitos; queda en la tabla con nota «fondeo no depositario (FAT, Tesoro)».
- Residuo de M3: **buscar la partida** en el SGS (27792–27804) antes de mostrar la composición de M3/M4; mientras,
  «en preparación».
- Tasas de captación por inversionista: **usar el REF 1.2.1.4** (% del DI por segmento) con nota de fuente y rezago
  mientras el SGS no responda.
- Poupança **como componente de M2**; bloque «Componentes de M2, a/a».
- Técnico (sin decisión): `ref.py` completa `unidad = "R$"` en 1.2.1.1.a, 1.2.1.5, 1.2.1.7 y 1.2.1.10 y agrega clave por título.

## Hecho el 11-nov (sin publicar)
- `ref.py`: columna `clave` en `bk_ref` y `bk_ref_sitio` (título sin «Gráfico x.y.z –»: la numeración cambia entre
  ediciones, la clave no) y `unidades_por_clave` en `definiciones/bcb_ref.json` (R$ en perfil por instrumento y en los
  tres de captaciones intermediadas). Contrato del gold actualizado; test de la clave.
- Desarrollo fuera del gráfico de crédito/depósitos con serie `oculta` (sigue en la tabla) y nota con su valor
  (1.442 % a 2T26). Tasas por inversionista: el bloque SGS vacío sale; nota que remite al REF 1.2.1.4 (hasta jun-26).
- Residuo de M3: 27792–27802 dan error 500 en la API de datos y en el servicio de metadatos del SGS (no publicados);
  27803 y 27804 son tasas diarias, no agregados. La partida no está ahí. La hoja muestra solo M1–M4 a/a, así que el
  residuo no afecta nada publicado; la composición de M3/M4 sigue fuera. Próxima pista: nota metodológica del BCB
  de los agregados (metodología nueva).
