# Frente 8 · Capital: informe 5 de IF.Data → `bk_capital`

Estado al 9-nov-2026: **construido** (informe en `borradores/capital_informe.md`). Lo que sigue era el encargo original. Pensado para que lo ejecute un worker (otra sesión u otra LLM) sin
contexto previo. Puede correr en paralelo al frente 7 (CVM).

## Por qué
La página B7 · Capital tiene cinco tarjetas en FALTA y su pregunta es la central para un analista de bancos:
**¿cuánto capital sobra para crecer o repartir?** El Basilea también se usa en B0, B8 y B9.

## Lo que ya se sabe (verificado el 9-nov)
- El IF.Data publica el informe **5, «Informações de Capital»** (catálogo en
  `datos/crudo/bcb_ifdata/catalogo/actual/relatorios.json`).
- El crudo actual (`datos/crudo/bcb_ifdata/valores/actual/valores_<AAAAMM>_1_r<N>.parquet`) trae los informes 2, 3,
  4, 8, 10, 11, 13 y 16. **No trae el 5.**
- La descarga es trimestral y a mano: `python pipeline/ifdata.py colectar ...`. Ver los argumentos en `ifdata.py`
  (`resolver_informes`, línea ~759). `actualizar.bat` no baja IF.Data.
- **Trampas conocidas de IF.Data** (documentadas en el encabezado de `pipeline/ifdata.py` y en `spec/08`):
  - en 2025-03 el BCB renumeró los códigos de cuentas y migró informes; hay que mapear por nombre y época, no solo
    por código;
  - los informes disponibles varían por escopo y época;
  - la base de diciembre republica;
  - 2024-T4 es un trimestre anómalo y queda vacío a propósito en el panel.
- El esqueleto B7 sugiere que el informe 5 podría no estar antes de 2020. Hay que confirmarlo; si es así, B7 parte
  en 2020-T4 y se dice.
- Hay cinco cortes viejos en `datos/derivado/bcb_ifdata/valores/ifdata_capital_*.csv`. **No usarlos:** sirven
  solo como contraste.
- Diseño de datos ya aprobado: `docs/SPEC_DATOS_BANCOS_v0.1.md` §3.11. Tarjetas: `docs/ESQUELETO_BANCOS_v0.1.md`,
  sección «B7 · Capital».

## Sondeo de la API (9-nov-2026, antes de construir)
- OLinda `IfDataValores` con `TipoInstituicao=1` (conglomerado prudencial) y `Relatorio='5'` responde HTTP 200 y
  trae datos **desde 2015-03** (2014-12 sale vacío) hasta **2026-06**. «El crudo no trae el 5» era solo que nunca
  se bajó: la fuente existe y está viva.
- Columnas en 2026-06 (1.398 filas cada una): Capital Principal (a), Capital Complementar (b), Nível I (c), Nível II
  (d), PR (e), RWA crédito (f), mercado (g, con g1–g6), operacional (h), RWAsp (i), RWA total (j), Exposição Total
  (k), **índices ya calculados** de CP (l), Nível I (m) y Basileia (n), Razão de Alavancagem (o), Índice de
  Imobilização (p), Adicional de Capital Principal e IRRBB.
- **Las letras cambian por época**: hasta 2020-12 el RWA total es (i) = (f)+(g)+(h) y la exposición (j); desde
  2023-12 entra RWAsp (i) y el total pasa a (j); el mercado suma g1–g4, luego g1–g5 y desde 2024-12 g1–g6; el
  «Adicional de Capital Principal» e IRRBB aparecen en 2024-12 (no en 2020-12). Mapear por nombre sin la letra,
  nunca por la etiqueta completa.

## Qué construir
1. **Descarga** del informe 5, escopo prudencial (el mismo de la tabla `bk_panel`), para toda la historia que
   exista. Usar `ifdata.py colectar` tal como está. Si hay que ampliarlo, que sea sin romper lo existente. El crudo
   queda junto a los otros informes, con su manifiesto (`almacen.registrar_crudo`).
2. **Mapeo de cuentas** en `definiciones/bcb_ifdata__capital.json`: qué `Conta`/`NomeColuna` del informe 5 da cada
   campo, separado por época (antes y después de 2025-03). Campos:
   - `pr`
   - `nivel1`
   - `capital_principal`
   - `rwa_total`
   - `rwa_credito`
   - `rwa_mercado`
   - `rwa_operacional`
   - `basilea`
   - `indice_nivel1`
   - `indice_cp`

   Si el informe trae un índice ya calculado, se usa el del BCB y se verifica contra el cociente propio.
3. **Mínimos regulatorios** en `definiciones/minimos_regulatorios.json` (en `definiciones/`, no en `manual/`).
   Va por fecha de vigencia:
   - mínimo de capital principal 4,5 %, de nivel 1 6 % y de PR 8 %;
   - adicional de conservación, con su calendario de entrada;
   - contracíclico (ACCP, hoy 0 %);
   - adicional sistémico (ACSP) **por banco**, para los que lo tengan.

   Cada fila lleva la resolución CMN/BCB y la URL de donde sale. Si un valor no se puede respaldar con la norma, se
   deja vacío y se anota: **no se inventa.** El Pilar 2 no es público y queda fuera.
4. **Tabla gold `bk_capital`** (banco × trimestre), con `almacen.publicar_gold` y declarada en
   `definiciones/contrato_gold.json`. Columnas según §3.11:
   - los campos del punto 2;
   - `densidad_rwa` = rwa_total / activo total de `bk_panel`;
   - `requerimiento_cp` con los colchones vigentes en la fecha;
   - `holgura_cp_pp`;
   - `holgura_crecimiento` = (capital principal − mínimo con colchones) / (densidad de RWA × mínimo), en % de la
     cartera actual;
   - para B7-02-0: la variación del capital principal en 4T separada en resultado (lucro de `bk_panel`), dividendos
     e intereses sobre capital (si el informe 5 o la DRE los traen) y «otros» como residuo.

   Agregados por grupo, igual que en las demás tablas gold: ver `pipeline/bancos.py` (`membresia`, `pertenencia`)
   y cómo se arma `bk_grupo` en `pipeline/preparar_gold_bancos.py`. Para grupos, el índice se calcula como suma de
   capital / suma de RWA, no como promedio de índices.
5. **Métricas:** registrar en `definiciones/metricas_bancos.json` (familia `capital`; ya existen apalancamiento y PL)
   las métricas nuevas, con el mismo formato que las demás. Revisar si `bk_panel` o `bk_manifiesto` deben listarlas.
6. **Integración:** dejar el paso documentado para que Pablo lo corra a mano junto con la colecta trimestral de
   IF.Data. La generación de `bk_capital` sí entra en `pipeline/actualizar.py`, mirando cómo están los otros pasos.
7. **Tests** en `tests/test_capital.py`, con fixture pequeño y sin red:
   - el mapeo por época;
   - basilea ≥ índice de nivel 1 ≥ índice CP;
   - RWA total ≥ suma de componentes, o igual con tolerancia;
   - índice de grupo = Σcapital / ΣRWA;
   - vigencia de los mínimos por fecha.
8. **Documentación:** correr `python -X utf8 herramientas/generar_spec.py` y anotar en
   `spec/08_estado_pendientes_y_riesgos.md` las trampas nuevas que aparezcan.

## Contrastes obligatorios (2T26)
- Basilea y capital principal de Itaú, BB, Bradesco, Santander y BTG contra lo que cada banco publica en su
  release o en su informe de Pilar 3. Tolerancia: 0,1 pp. Si no calza, explicar la causa (alcance prudencial,
  fecha, criterio) antes de seguir.
- El índice CP del agregado del panel contra el del sistema que informa el BCB (REF o estadísticas de estabilidad),
  sabiendo que el panel tiene 34 conglomerados y no el SFN entero.

## Fuera de alcance
- Páginas web, tarjetas, CSS y `config.js`: otra sesión está con el diseño. B7 se conecta después.
- B7-03-1, el test de estrés, que sale del REF (frente 4).
- Commit, push, publicar o borrar archivos: lo decide Pablo.

## Coordinación con el frente 7 (CVM, en paralelo)
- En `pipeline/actualizar.py`, `definiciones/contrato_gold.json`, `definiciones/metricas_bancos.json` y
  `tareas/README.md`, **solo agregar** entradas propias, sin reordenar ni reescribir las ajenas.
- Volver a leer cada uno de esos archivos justo antes de editarlo.

## Criterio de «terminado»
- `bk_capital` cubre los 34 bancos del panel en todos los trimestres que tenga el informe 5, con los huecos
  explicados por banco y trimestre.
- `python -m pytest -q` pasa entero.
- Contrastes 2T26 en tolerancia, o con la diferencia explicada.
- Informe en `tareas/borradores/capital_informe.md`:
  - qué se hizo;
  - desde cuándo hay datos;
  - el mapeo por época;
  - la tabla de contraste;
  - las fuentes de los mínimos;
  - decisiones que quedan para Pablo (por ejemplo, cómo tratar los dividendos si el informe 5 no los separa).
