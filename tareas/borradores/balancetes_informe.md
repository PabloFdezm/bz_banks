# Frente 11 · Informe de la fase 2 (balancetes 4060 → gold)

11-nov-2026. Código: `pipeline/balancetes.py`; mapa de cuentas: `definiciones/bcb_balancetes__cuentas.json`;
tests: `tests/test_balancetes.py`; paso `balancetes` en `pipeline/actualizar.py` (después de `capital`).

## Qué quedó en gold
- **`bk_balancete_m`** (banco × mes × concepto, 19.012 filas): activo, patrimonio, crédito neto, depósitos (total,
  vista, ahorro, interfinancieros, a plazo) y lucro del mes. Columna `cuadra_ifdata`: si el trimestre del mes cuadra
  con `bk_panel` (vacía cuando IF.Data todavía no tiene ese trimestre). La columna de tiempo es `mes` (AAAAMM): en
  gold, `periodo` es trimestral.
- **`bk_sistema_bal_m`** (óptica × grupo × mes, 1.485 filas): `roe_12m`, `depositos`, `depositos_aa`,
  `credito_depositos`, `patrimonio_activo`, con las ópticas y grupos de `bk_grupo`. Todo como Σ / Σ sobre los bancos
  con dato; solo entran meses que cuadran.
- Derivados en `datos/derivado/bcb_balancetes/gold/`: `cuadre_balancetes.csv` (cada banco-trimestre contra
  IF.Data) y `huecos_balancetes.csv` (los que no cuadran, con motivo).

## Cobertura
- Crudo: 4060 de los líderes de conglomerado, ene-18 a mar-26 (≈ 3.140 archivos, ~60 MB) en
  `datos/crudo/bcb_balancetes/4060/actual/`, con manifiesto. Para conglomerados de un solo miembro sin 4060
  (Banco da Amazônia y otros) se usa el 4010 del líder (233 archivos).
- Publicado desde **ene-20** (30–34 bancos por mes; 33 en mar-26). El ROE de 12 meses empieza en mar-21.
- **Abr-26 en adelante: el BCB no publicó todavía** la carpeta (404 al 11-nov). El paso la baja sola cuando aparezca.
- **BRB (C0080288)**: no publica balancetes (ni 4060 ni 4010) desde jul-25. Queda sin dato desde entonces.

## Cuadre contra IF.Data (`bk_panel`)
Criterio: activo, patrimonio, crédito y depósitos de fin de trimestre ≤ 0,5 %; lucro del trimestre (suma de los
tres meses) ≤ 1 %.
- **Desde 1T20: 788 de 811 banco-trimestres cuadran (97 %).** Crédito y depósitos, exactos.
- **Patrimonio de junio y diciembre**: el 4060 es anterior al cierre del semestre (no destinó dividendos ni JCP) y
  queda 1–6 % sobre IF.Data (BB ~1 %, Amazônia ~6 %). No se exige en esos meses; es la única diferencia sistemática.
- 23 banco-trimestres no cuadran y quedan fuera del agregado (`huecos_balancetes.csv`): C0081744 (activo −0,5 a
  −1,2 % en 2022–24), C0084813 y C0084844 (lucro de algunos trimestres), C0084686 (2T21), BRB (4T21), C0084820 (4T20,
  trimestre incompleto).
- **Antes de 4T19 no cuadra** (lucro con diferencias de 40–100 %, crédito de 2–40 %): no se publica. Causa no
  verificada.

## ROE de 12 meses del Total panel contra `roe_ttm` de `bk_grupo`
Dentro de 0,3 pp en 20 de 21 trimestres (1T21–1T26); dic-24 queda en −0,36 pp (patrimonio previo al cierre). Los
grupos chicos (S3, S4, Digitales, Pagos) difieren más (hasta 5 pp) porque el conjunto de bancos no es el mismo
(huecos y bancos sin 12 meses completos); para esos grupos el dato mensual es indicativo.

| Mes | Bancos | ROE 12m | Depósitos a/a | Crédito / depósitos | PL / activo |
|---|---:|---:|---:|---:|---:|
| dic-23 | 31 | 15,1 % | 11,9 % | 98,1 % | 9,0 % |
| dic-24 | 33 | 16,8 % | 9,4 % | 99,9 % | 8,5 % |
| dic-25 | 33 | 16,8 % | 7,9 % | 100,7 % | 8,5 % |
| mar-26 | 33 | 16,2 % | 12,6 % | 100,0 % | 8,4 % |

Ojo con mar-26: los depósitos de BB, Caixa y Bradesco suben ~R$ 150 mil millones entre feb y mar (BB 927 → 991).
Es el dato publicado y cuadra exacto con IF.Data a mar-26; no lo expliqué.

## Lo que NO se publica (decisión abierta)
- **NIM, costo de riesgo y eficiencia.** El margen de intermediación armado con las cuentas de nivel 3 (rentas de
  crédito, arrendamiento, cambio, interfinancieros y TVM, menos captación, repasses, cambio y TVM) queda bajo el de
  IF.Data en el plan viejo (mediana −7 % en todos los banco-trimestres; −15 % a −25 % en los grandes), y no hay cómo separar en el 4060 viejo lo que IF.Data
  suma (por ejemplo, las rentas de compulsorios van dentro de «Outras receitas operacionais»). En el plan nuevo
  (desde ene-25) cuadra mejor (mediana −1,5 %) pero con dispersión. Las provisiones del plan nuevo vienen en bruto
  (gasto y reversión de ~100 mil millones por trimestre en BB). Personal y administrativos no se separan antes de
  2025. Las cuentas candidatas quedan en la definición con `"publica": false`.
- Opciones: (a) dejar NIM, costo de riesgo y eficiencia trimestrales (IF.Data) y usar el balancete solo para ROE,
  depósitos y balance; (b) publicar NIM mensual solo desde ene-25, con el plan nuevo, tras un cuadre más fino;
  (c) seguir buscando el mapa del plan viejo en el nivel 4 del masivo «Bancos» (individual, otro perímetro).

## Pendiente
- Decidir lo de arriba (NIM, costo de riesgo, eficiencia).
- Conectar `bk_sistema_bal_m` a la sección 04 de la Portada: es diseño (canvas → aprobación).
- La opción B de `tareas/10_capital_mensual.md` (capital mensual) puede usar ahora el lucro mensual validado.
