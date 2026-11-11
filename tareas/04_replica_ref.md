# 4 · Réplica de gráficos del REF (Relatório de Estabilidade Financeira, BCB, oct-26)

Documento público: `referencias/RELESTAB202610-refPub.pdf` (117 páginas, 137 gráficos y tablas). Los datos de casi
todos los gráficos del capítulo 1.2 vienen en el **Anexo Estatístico** (xlsx), en
https://www.bcb.gov.br/publicacoes/ref. Bajarlo desde Windows; la VM no tiene salida a bcb.gov.br.

Columna «Vía»:
- **Propia**: se calcula con lo que el pipeline ya tiene (IF.Data, SGS, SCR.data).
- **Anexo**: el dato es un cálculo del BCB con microdatos y solo sale del Anexo Estatístico.
- **No**: fuera de alcance, o la fuente no es pública ni del BCB.

## A. Replicables con datos propios (prioridad)

| Gráfico | Contenido | Vía | Nota |
|---|---|---|---|
| 1.2.2.1 | Crédito amplio, crecimiento 12 m | Propia (SGS) | Agregar las series de crédito ampliado |
| 1.2.2.3 | Brecha crédito amplio / PIB | Propia (SGS) | Filtro HP de una cola (λ = 400.000, metodología BIS); la proyección del BCB sale del Anexo |
| 1.2.2.7 | Crédito bancario a empresas por tamaño, a/a | Propia (SCR.data) | `porte` PJ |
| 1.2.2.9 | Activos problemáticos PJ por tamaño | Propia (SCR.data) | Quiebre por Res. 4.966 en ene-25 |
| 1.2.2.15 | Cartera activa a/a por grupo de modalidad | Propia (SCR.data) | |
| 1.2.2.16 | Activos problemáticos por modalidad | Propia (SCR.data) | |
| 1.2.2.21.a–c | Mora: total, PF, PJ | Propia (SGS) | Ya está en `bk_sistema_m` |
| 1.2.2.22.a–c | Variación anual de la mora y su descomposición por modalidad | Propia (SGS/SCR) | Contribución = Δ(peso × mora) |
| 1.2.3.1 | ROE por segmento del SFN, 12 m | Propia (IF.Data) | Aproximado: el panel tiene 34 bancos, no el SFN entero. `segmento_ref` ya imita los grupos del REF |
| 1.2.3.2–3.3 | Dispersión y distribución del ROE | Propia (IF.Data) | Percentiles por grupo; ya hay p10/p50/p90 en `bk_panel` |
| 1.2.3.4 | Margen de crédito y sus componentes | Propia (IF.Data) | Parcial: la descomposición exacta sale del Anexo |
| 1.2.3.5 | Costo de provisiones, 12 m | Propia (IF.Data) | `costo_riesgo_ttm` |
| 1.2.3.6 | Ingresos por servicios: a/a y factores | Propia (IF.Data) | Parcial |
| 1.2.3.8 | Índice de eficiencia, 12 m | Propia (IF.Data) | `eficiencia_ttm` |
| 1.2.1.1.a/b | Perfil de captación por instrumento | Propia (IF.Data, informe de pasivo) | Las categorías del BCB difieren algo; contrastar con el Anexo |
| 1.2.4.1–4.2 | Índices de capital y variación del Basilea | Propia (IF.Data, informe de capital) | El pipeline aún no lo ingiere (página Capital, B7) |
| 1.2.5.1–5.5 | Inflación, cambio, PIB, desempleo, Selic | Propia (SGS/Focus) | Histórico propio; las trayectorias de los escenarios salen del Anexo |
| 2.1.3 | Cartera de consignado privado | Propia (SGS) | El SCR.data no separa privado, público ni INSS |

## B. Solo vía Anexo Estatístico (alto valor para Personas, Calidad y Capital)

| Gráfico | Contenido |
|---|---|
| 1.2.2.11–14 | Compromiso de renta (CRI) y endeudamiento individual: por tramo de renta y por modalidad |
| 1.2.2.23.a/b | Participación de la tarjeta y del no consignado en el CRI, por tramo |
| 1.2.2.24.a–d | Perfil del CRI por tramo de CRI y por modalidad, para cada tramo de renta |
| 1.2.2.25–26 | AP por cohorte según el CRI a la contratación; distribución de la cartera por CRI |
| 1.2.2.10, 1.2.2.18 | Probabilidad de default del stock, por tamaño de empresa y por modalidad |
| 1.2.2.8 | Score a la contratación por tamaño de empresa |
| 1.2.2.5–6 | Indicadores económico-financieros de las empresas y cobertura de intereses |
| 1.2.2.17, 1.2.2.19 | Activos problemáticos, pérdida esperada y provisión por segmento |
| 1.2.2.20 | Distribución de castigos por tramo de atraso |
| 1.2.1.2–1.2.1.10 | Captación por segmento y tipo de inversor; captaciones intermediadas (plataformas) |
| 1.2.1.12–14 | Captaciones externas |
| 1.2.1.15–19 | Dispersión del LCR y del NSFR; índices de liquidez |
| 1.2.4.3–4.5, T1.2.4.1–2 | Adecuación del PR, retención de utilidades, estructura de capital, RWA, encuadre por segmento |
| 1.2.5.6–5.13 | Pruebas de estrés: capital, sensibilidad de crédito e inmobiliaria, bottom-up, liquidez, step-in |

Antes de construir, confirmar en el xlsx qué hojas existen: el Anexo suele cubrir el capítulo 1 completo, no los
boxes del capítulo 2.

## C. Fuera de alcance
- 1.1.x (contexto global: EE. UU., China, condiciones financieras): fuentes externas. Si se quiere, se arma con
  Bloomberg, que Pablo tiene.
- 1.2.1.11 y T1.2.1.1 (FGC), 1.3.x (encuesta PEF), 1.4.x (Pix, cámaras B3).
- 2.1.x (box del consignado privado: score Serasa, tomadores, cohortes) salvo 2.1.3; 2.2–2.6 (boxes cualitativos,
  ciberseguridad, clima).

## Construir
1. **Fuente `bcb_ref`:**
   - descarga semestral del Anexo Estatístico a `datos/crudo/bcb_ref/` con su manifiesto;
   - lector por hoja → `datos/gold/bk_ref.parquet` (columnas: grafico, serie, fecha, valor, unidad, edicion_ref);
   - un test que falle si cambia el nombre de una hoja usada.
2. **Grupo A**, priorizando lo que alimenta Calidad y Rentabilidad: 1.2.2.21–22, 1.2.3.1–3.8 y 1.2.2.15–16.
3. **Grupo B:**
   - CRI (1.2.2.11–14 y 23–26) → lámina 06 de Personas;
   - PD y estrés → páginas Calidad y Capital.
4. **Al presentarlo:** cada tarjeta que venga del REF lleva «Fuente: BCB, REF (edición)» y frecuencia semestral.

## Avance 9-nov: fuente `bcb_ref` construida
`pipeline/ref.py` baja el Anexo Estatístico de las 8 ediciones (202304–202610) y publica `bk_ref` (formato largo,
todas las hojas). 1.2.2.16 propio calza con el anexo (≤0,08 pp de media desde 2025). Detalle, trampas y decisiones:
`borradores/ref_informe.md`. El punto «Construir 1» queda hecho; los puntos 2–4 son tarjetas, con el rediseño.

## Avance 6-nov: canvas de réplicas con datos propios
Canvas «Bancos Brasil · Réplicas del REF»: https://claude.ai/artifact/KBCNwmBbBfnsQ1NtwS5o48. Tiene cuatro láminas y
espera la aprobación de Pablo.

| Lámina | REF | Fidelidad a jun-26 |
|---|---|---|
| 01 Activos problemáticos por modalidad (PF) | 1.2.2.16 | **Exacta** (Total 9,2; Habitacional 5,1; Consignado 5,0; Vehículos 8,5; No consignado 14,9; Rural 10,2 vs 10,3; Tarjeta 12,7). El «Total» del REF es el total PF |
| 02 Cartera PF: menor vs. mayor riesgo, a/a | 1.2.2.15 | Cercana. La agrupación es nuestra: menor = habitacional, consignado, vehículos, rural; mayor = tarjeta, no consignado, otros |
| 03 ROE por segmento | 1.2.3.1 | Aproximada. Calzan S1 y públicos; «Demás» queda alto (el panel tiene solo 9 medianos) y digitales bajo (24 vs ~29) |
| 04 Costo de provisiones por segmento | 1.2.3.5 | Calzan S1, públicos y total; digitales 13,2 vs ~18 |

**Descartados por no calzar** (no publicar sin resolver):
- **Mora PF/PJ desde SCR.data (1.2.2.21):** la PJ da 2,9 % contra el 3,2 % del SGS (otro universo). Usar las series SGS
  21082/21083/21084 (total, PJ, PF), que aún no están en `bk_sistema_m`. El contrafactual sale del Anexo.
- **Empresas por tamaño (1.2.2.7 y 1.2.2.9):** el `porte` del SCR.data no es la clasificación del BCB. Micro da 9,6 % de
  activos problemáticos contra 14,4 % en el REF, y crece +71 % a/a por reclasificaciones.
- **Eficiencia por segmento (1.2.3.8):** nuestro `ingreso_total_ttm` se quiebra con COSIF 2025 y el índice salta.
  Revisar la definición antes.

**Cálculo:**
- `tareas/borradores/agg_scr_ref.py <segundos> <años…>`: agrega SCR.data por mes × cliente × grupo de modalidad ×
  porte × tipo de institución, desde dic-2018. Son ~2 s por mes.
- Los segmentos usan `bk_banco.segmento_ref` con Σ lucro 12 m / Σ PL medio y Σ provisiones 12 m / Σ cartera media
  (5 trimestres).
- Para producción hay que pasarlo a un `preparar_gold_ref_propio.py` con tests.

## Avance 6-nov (segunda parte): láminas propias 05–07 en el mismo canvas

**05 · Mora temprana (15–90 días) por modalidad, PF**
- La correlación entre el cambio a/a de la mora temprana y el de la mora a más de 90 días es máxima con 3 meses de
  rezago: 0,88 en el total PF y 0,95 en no consignado. En tarjeta es 0,73 con 4 meses.
- La mora temprana PF tocó techo entre may y jun-26 (1,31 %) y baja a 1,26 % en ago. Rural sigue cerca del máximo
  (1,85 %).
- Tarjeta a más de 90 días salta +1,4 pp en ago-26: revisar castigos.

**06 · Activos problemáticos de empresas por sector CNAE**
- El SCR.data trae la sección CNAE en `cnae_ocupacao` (PJ), y la ocupación en la misma columna para PF.
- El nombre del sector trae «;» (por ejemplo «Comércio; reparação…»), así que el CSV hay que leerlo con pandas y
  comillas, nunca con `split(';')`.
- El nivel total (6,9 %) queda bajo el REF (7,4 %); la lámina sirve para comparar sectores.
- Financieras +38 % a/a: revisar si hay reclasificación.

**07 · Concesiones a/a de 12 meses**
- Series: total, PF, PJ y libre PF, más una tabla de stocks.
- Las concesiones por modalidad no están descargadas.
- Ver 1.7 en `01_correcciones_datos.md` (rótulo de la serie 20631).

**Script:** `tareas/borradores/agg_scr_sector.py` agrega por mes × cliente × sección CNAE u ocupación × grupo de
modalidad.

## Avance 11-nov: tarjetas en el sitio (aprobadas por Pablo)
Hoja `diseno/canvas/Ref.dc.html`, montada debajo de `Ficha` en `/agregados/`. Datos: `tareas/borradores/_salida/extraer_ref.py`
→ `_salida/v2/Ref.json` (última edición de `bk_ref`; valida el título de cada gráfico porque la numeración cambia entre ediciones).

| Sección | Gráfico (izq.) | REF |
|---|---|---|
| 09 Rentabilidad del SFN | ROE 12 m por segmento con la banda del costo del capital (Agrandar: utilidad y patrimonio) | 1.2.3.1 |
| | Costo de provisiones 12 m por segmento | 1.2.3.5 |
| 10 Eficiencia del SFN | Índice de eficiencia por segmento (el BCB lo publica con 2 decimales en fracción) | 1.2.3.8 |
| | Margen de crédito y componentes, con la Selic | 1.2.3.4 |
| 11 Prueba de estrés | Necesidad de capital, % del PR, recesión aguda y crisis de confianza; nota con el pico | 1.2.5.7 |
| | PIB por escenario (Agrandar: Selic, desempleo, inflación con meta, cambio) | 1.2.5.1–5 |

Fuera, por no leerse limpio: bottom-up de Basilea (1.2.5.10, cajas apiladas) y distribución de activos por tramo de
capital (1.2.5.6, categórico). Las series usadas están en `definiciones/bcb_ref.json` («usados»): si el BCB renombra
una, falla el test. Con una edición nueva del REF: `ref.py descargar` y `gold`, `extraer_ref.py`, `construir_v2.py`, publicar.
