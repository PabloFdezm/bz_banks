# 3 · Réplica del reporte sell-side de crédito por renda

El detalle (mapa de figuras, cifras de contraste, tesis) está en la nota local
`referencias/notas_replica_sellside.md`, fuera de git porque deriva de un reporte de terceros.

## Tarea técnica (sin contenido del reporte)
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
