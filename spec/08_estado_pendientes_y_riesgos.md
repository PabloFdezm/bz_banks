# 08 · Estado, pendientes y riesgos

Estado al 4-nov-2026.

## Hecho

- Repo separado de `Dashboard` y funcionando solo (gold idéntico al del repo original, 115 tests OK).
- Portada y Crédito en v3. Tabla estándar única con Share. Presentar con láminas de posiciones idénticas.
- Arreglos de visualización con fuentes reales: etiquetas de gráficos (fuente fija en ECharts), tablas que
  escalan con el ancho, grilla de 9 columnas en todos los anchos de escritorio, gráfico y tabla nunca
  apilados desde 700 px, letra de los gráficos ×1,5 en Presentar.
- Páginas con tablas grandes: las secciones se muestran de inmediato y las tarjetas usan particiones.

## Pendientes

1. Rehacer **Calidad, Rentabilidad y Ficha** con la estructura v3 (canvas → aprobación → construcción).
2. Páginas nuevas: **Mora, Márgenes, Por banco, Productos** (ver `06_paginas.md`, «Estructura objetivo»).
   Actualizar el menú (`config.js`) cuando existan.
3. Crudo IF.Data en parquet: hecho el 4-nov (3,5 GB → 62 MB, gold idéntico). Falta borrar los CSV
   originales (con permiso de Pablo). SCR sigue en ZIP.
3b. ~~pandas distinto entre equipos~~ Resuelto el 6-nov: `stack(future_stack=True).dropna()` en `_bk_panel`
   (104.396 filas en pandas 2 y 3); `requirements.txt` pide pandas ≥ 2.1.
4. **Entradas congeladas del macro:** endeudamiento, comprometimiento y desocupación se leen del SGS desde el
   6-nov (29037, 29034, 24369). Siguen congeladas `tasa_real_exante` y `expectativas_focus`.
4b. Resuelto el 6-nov: `bk_sistema_m/q` se escribían en `datos/intermedio/Banks/` y el gold no se refrescaba.
5. Validar contra el catálogo del SGS los nombres de las series de modalidades y concesiones.
6. `credito_aa` en 2025 cruza el quiebre COSIF y aparece vacío en la franja; corregir en el gold.
7. Automatizar la actualización: tarea programada de Windows (simple) o GitHub Actions (requiere guardar los
   datos fuera de git; viable si el crudo baja a ~200 MB en parquet).
8. Opcional ofrecido: filas extra en la tabla de ROE de la Portada (ROA, margen, costo del riesgo).
9. Opcional: en Crédito → Líneas, partir mostrando solo Total y las modalidades grandes.

## Trampas de los datos (leer antes de tocar cálculos)

- **Frontera COSIF 2025-03:** códigos de cuenta renumerados; los informes de crédito pasan del escopo
  financiero al prudencial. Bancos con cambio de cobertura llevan `quiebre_2025 = true` y sus variaciones
  que cruzan 2025-T1 quedan vacías.
- **2024-T4 anómalo** en IF.Data: vacío a propósito (`trimestres_anomalos` en definiciones).
- **Res. 4.966 (2025):** cambia la medida de mora/activos problemáticos; las series se leen con banda de
  quiebre.
- **Resultados acumulados con reseteo en julio** (informe 4): se des-acumulan antes de calcular TTM.
- **Mora:** panel ≥ 15 días vs SGS > 90 días; no comparar niveles.
- **Libre y direccionado** del SGS llegan con un mes de rezago respecto al total.
- **API del SGS:** una serie inexistente no da 404; devuelve HTML con 200 o 502 (ver `bcb_api.py`).
- **SCR.data:** CSV en UTF-8 con BOM (no cp1252); `carteira_inadimplencia` está en R$, no en %.
- **Red corporativa:** proxy HTTPS; ver `pipeline/certificados.py`.

## Riesgos técnicos conocidos

- `bancos.css` acumula bloques por versión; el último gana. Al tocar estilos, revisar los bloques
  posteriores que puedan pisarlo.
- Tarjetas que cargan tablas completas (`bk_panel`, `bk_grupo`, `bk_cre_*`) hacen lentas las páginas. Usar
  particiones.
- Capturas automáticas sin fuentes reales no muestran cortes de texto (ver `07_operacion.md`).
- `herramientas/verificar_f0.py` está obsoleto (lo reemplaza `verificar_f1.py`).
