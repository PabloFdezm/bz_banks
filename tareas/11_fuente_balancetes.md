# Frente 11 · Balancetes mensuales del BCB → `bk_balancete_m` y `bk_sistema_bal_m`

Estado al 10-nov-2026: fase 1 (sondeo) hecha y aprobada el 9-nov (`borradores/balancetes_sondeo.md`: sirve el
documento 4060 por conglomerado; abiertos 2T26 y la cuenta de provisiones en el plan nuevo). **Fase 2 hecha el
11-nov** (`borradores/balancetes_informe.md`): gold con ROE 12m, depósitos y balance desde ene-20; NIM, costo de riesgo
y eficiencia quedan sin publicar porque no cuadran con IF.Data (decisión abierta de Pablo). Encargo pensado para que lo ejecute otra sesión u otra LLM sin contexto previo.
Leer antes `CLAUDE.md`, `spec/README.md`, `spec/08_estado_pendientes_y_riesgos.md` y `tareas/README.md`.
Reemplaza la opción A de `tareas/10_capital_mensual.md` y la amplía a rentabilidad, margen, eficiencia y depósitos.

## Por qué
El IF.Data (`bk_panel`, `bk_grupo`, `bk_capital`) es trimestral. Pablo quiere ROE, NIM, eficiencia, depósitos y una
señal de capital **mensuales**, al menos a nivel sistema y por grupo de bancos. El SGS no publica ninguno de esos
indicadores. La única fuente mensual con resultados y balance por institución son los balancetes COSIF.

## La fuente (verificado en la web el 9-nov; confirmar en el sondeo)
- Dataset «Balancetes (IFs e Conglomerados)»: https://dadosabertos.bcb.gov.br/en/dataset/ifs-balancetes
- Página de descarga: https://www.bcb.gov.br/estabilidadefinanceira/balancetesbalancospatrimoniais
- Formato: CSV dentro de ZIP, sin API. Campos según el dataset: `Data` (AAAAMM), `CNPJ`, `Nome da Instituição`,
  `Atributo`, `Documento`, `Conta`, `Nome da Conta`, `Saldo`. Saldos de todas las cuentas COSIF hasta el nivel 4.
- Patrones de URL vistos como ejemplo en el dataset (no documentados: verificar):
  - por segmento y mes: `http://www.bcb.gov.br/content/estabilidadefinanceira/cosif/Bancos/202601BANCOS.csv.zip`
  - por institución: `https://www4.bcb.gov.br/fis/cosif/cont/balan/individualizados/{AAAAMM}/{doc}/{AAAAMM}-{doc}-{id}.ZIP`
    (ej. doc 4010 con id `00000000`; doc 4040, consolidado financiero, dejó de publicarse en 06/2022).
  - El identificador de conglomerado tiene la misma forma que nuestro `cod_inst` (ej. `C0049906`); confirmar si
    existe un archivo mensual por conglomerado prudencial (doc 4060) o una carpeta «Conglomerados».
- Calendario (Comunicado 44.132/2025): los meses se publican **por trimestre**: ene–mar el 31-may, abr–jun el 31-ago,
  jul–sep el 30-nov y oct–dic el 31-mar del año siguiente. El dato es mensual pero no llega antes que el IF.Data.

## Fase 1 · Sondeo (entregar antes de construir; detenerse y mostrar a Pablo)
Escribir `tareas/borradores/balancetes_sondeo.md` con:
1. Qué segmentos y documentos existen como archivo mensual (Bancos, Conglomerados, Cooperativas…; 4010, 4016, 4060),
   desde qué mes hay datos y el tamaño de un mes.
2. Si existe el nivel **conglomerado prudencial** mensual. Es la unidad buena: sumar instituciones individuales
   (4010) duplica saldos entre entidades del mismo grupo. Si solo hay 4010, proponer cómo consolidar o acotar.
3. Cómo cruzar el identificador del balancete con nuestro `cod_inst` (`definiciones/bancos__dashboard.json`, 34 bancos).
4. Comportamiento de las cuentas de resultado: confirmar que acumulan por semestre (ene–jun y jul–dic) y se cierran
   en jun y dic. Flujo del mes = acumulado del mes − acumulado del mes anterior, salvo ene y jul.
5. El mapa de cuentas antes y después de ene-25: el plan COSIF cambió con la Res. CMN 4.966 / Res. BCB 352
   (ver `pipeline/periodos.py`, `QUIEBRE_2025`). Listar las cuentas candidatas por concepto en las dos épocas.
6. Prueba de cuadre de un trimestre (sugerido 2T26) para Itaú, BB, Bradesco, Santander y BTG: lucro del trimestre,
   patrimonio, activo total, cartera y depósitos del balancete contra `bk_panel` (IF.Data) del mismo `cod_inst`.

## Fase 2 · Construcción (solo con el visto bueno de Pablo sobre el sondeo)
Seguir el patrón de `pipeline/capital.py` y `pipeline/ref.py`:
- `pipeline/balancetes.py` con subcomandos `colectar --desde AAAAMM --hasta AAAAMM` y `--resumen`. Descarga con
  `pipeline/red.py` (`exigir_red`, `bajar_a_disco`), guardado con `almacen` (`ruta_cruda`, `registrar_crudo`,
  `escribir_atomico`, `guardar_derivado`). Crudo en `datos/crudo/bcb_balancetes/<segmento>/actual/`, convertido a
  parquet con `almacen.csv_a_parquet`. Leer los CSV con pandas (separador y encoding a confirmar), nunca con split.
- `definiciones/bcb_balancetes__cuentas.json`: concepto → cuentas COSIF por época, con nota y fuente. Conceptos mínimos:
  `ativo_total`, `patrimonio_liquido`, `carteira_credito`, `provisao_credito` (saldo), `depositos` (vista, ahorro,
  a plazo, interfinancieros por separado), `lucro_liquido`, `receitas_intermediacao`, `despesas_intermediacao`,
  `provisoes_resultado`, `despesas_pessoal`, `despesas_administrativas`, `rendas_servicos_tarifas`.
- Gold, registrado en `definiciones/contrato_gold.json` y en el manifiesto (`pipeline/manifiesto_gold.py`):
  1. `bk_balancete_m`: conglomerado × mes × concepto, con `valor` (saldo de fin de mes o flujo del mes) y `tipo`
     (`saldo`/`flujo`).
  2. `bk_sistema_bal_m`: grupo × mes, con las mismas ópticas y grupos de `bk_grupo` (Total panel, Segmento
     regulatorio, Propiedad, Modelo de negocio, Tradicional vs Fintech; el mapa banco → grupo sale de `bk_panel`).
     Métricas, todas como Σ numerador / Σ denominador:
     - `roe_12m` = lucro 12 meses / patrimonio medio 12 meses;
     - `nim_12m` = (receitas − despesas de intermediación, antes de provisiones, 12 meses) / activo medio;
     - `costo_riesgo_12m` = provisiones 12 meses / cartera media;
     - `eficiencia_12m` = (personal + administrativo) / (margen antes de provisiones + servicios y tarifas);
     - `depositos`, `depositos_aa`, `credito_depositos`, `patrimonio_activo` (apalancamiento contable);
     - `n_bancos` del mes.
- Paso nuevo en `pipeline/actualizar.py` y `actualizar.bat` (después de `capital`), con CRLF en el `.bat`.
- `tests/test_balancetes.py`: unitarios sin red (flujo desde acumulado semestral; meses de corte ene y jul; mapa por
  época) e integración sobre `datos/` (identidades y cuadre contra IF.Data).

## Validación (criterio de aceptación)
- Por banco y trimestre, desde 1T22: la suma de los tres flujos mensuales de lucro calza con `lucro_liquido_q` de
  IF.Data dentro de 1 %; patrimonio, activo, cartera y depósitos de fin de trimestre, dentro de 0,5 %.
- Total panel: `roe_12m` de fin de trimestre contra `roe_ttm` de `bk_grupo` dentro de 0,3 pp; `nim_12m` contra el NIM
  antes de provisiones que usa el canvas (margen de intermediación + transacciones de pago + provisiones, sobre
  activo medio) dentro de 0,2 pp.
- Si algún banco no cuadra, se excluye del panel mensual con su motivo en
  `datos/derivado/bcb_balancetes/huecos_balancetes.csv` (como `huecos_capital.csv`), no se fuerza.
- Informe final en `tareas/borradores/balancetes_informe.md` con cobertura, cuadres y decisiones abiertas.

## Fuera de alcance
- No tocar el sitio (`sitio/`) ni el canvas: las secciones 05–08 se conectan después del rediseño.
- No estimar capital regulatorio: eso es la opción B de `tareas/10_capital_mensual.md`, que puede usar el lucro
  mensual de esta fuente una vez validada.
- Reglas de `CLAUDE.md`: no inventar cifras, no borrar archivos ni hacer commit/push sin pedirlo, `referencias/`
  nunca a git. Todo comando que se le muestre a Pablo lleva su `Set-Location C:\dev\bz_banks`.

## Terminado cuando
Sondeo aprobado por Pablo; `bk_balancete_m` y `bk_sistema_bal_m` en gold con tests verdes; cuadres dentro de las
tolerancias; informe escrito; fila 11 de `tareas/README.md` actualizada con la fecha.
