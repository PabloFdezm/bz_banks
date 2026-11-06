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
