# 3 · Réplica del reporte sell-side de crédito por renda

El detalle (mapa de figuras, cifras de contraste, tesis) está en la nota local
`referencias/notas_replica_sellside.md`, fuera de git porque deriva de un reporte de terceros.

## Tarea técnica (sin contenido del reporte)

### Resultado del paso 1 (6-nov)
- **La versión 1 sí trae `sr` y está al día.** El dataset dice que se cortó en jun-25, pero no es así:
  - `https://www.bcb.gov.br/pda/desig/planilha_{AAAA}.zip` llega a **sep-26**: `planilha_2026.zip`, actualizado el
    5-nov, va un mes por delante de la versión 2 (ago-26).
- **Cobertura de `sr`:** en jun-25, dic-25 y sep-26, sobre el 99 % de la cartera trae S1–S5 (en sep-26, el 100 %).
  - Total sep-26, en R$ mil millones: S1 4.688 · S2 1.014 · S3 948 · S4 419 · S5 269.
  - Tarjeta PF sep-26: 730,4.
- **Columnas:** data_base, uf, tcb, sr, cliente, ocupacao, cnae_secao, cnae_subclasse, porte, modalidade, origem,
  indexador, numero_de_operacoes, plazos a vencer, vencido_acima_de_15_dias, carteira_ativa,
  carteira_inadimplida_arrastada, ativo_problematico.
  - Separador `;`, UTF-8 con BOM, decimales con coma.
  - Las modalidades son más gruesas que la v2: no hay submodalidade.
- **Ojo:**
  - `tcb` (tipo de institución) viene en «-» en dic-25 y sep-26; en jun-25 todavía venía lleno. El corte por tipo
    de institución queda en la v2, y el corte por S1–S5 en la v1.
  - S2 salta de 686 a 840 entre jun-25 y jul-25. Probablemente es una reclasificación de segmentos: marcarla como
    quiebre.
- **Peso:** cerca de 290–340 MB por mes sin comprimir (ZIP anual de ~300–400 MB).
- **Falta revisar:** desde qué año trae `sr` (¿2017, con la Res. 4.553?) y cuándo se vacía `tcb`.
- **Paso 2 (siguiente):** fuente `bcb_scr_v1` agregando al bajar a fecha × sr × cliente × porte × modalidade, y en PJ
  también × cnae_secao. Muestras bajadas en el scratchpad de la sesión del 6-nov, fuera del repo.
- Conseguir el segmento prudencial S1–S5 por tramo de renda:
  - La metodología del SCR.data menciona el campo «SR — Segmento Resolução nº 4.553/2017».
  - Los ZIP que bajamos («Dados mensais (Versão 2)») traen `segmento` como tipo de institución, sin SR.
- **Paso 1:** bajar en Windows un año de «Dados mensais (Versão 1)» desde
  https://dadosabertos.bcb.gov.br/dataset/scr_data (recurso 529ce436-b070-48b8-99f2-7b07bca04ecf). Revisar:
  1. si trae la columna `sr`;
  2. hasta qué mes llega.

  La VM de Cowork no tiene salida a bcb.gov.br.
- **Paso 2:**
  - Si trae SR y está al día: sumarla como fuente `bcb_scr_v1`, agregando al bajar solo las columnas necesarias, y
    agregar al módulo Personas el corte por S1/S2.
  - Si se cortó antes de 2025: quedarse con el tipo de institución y decirlo en la nota de la tarjeta.
