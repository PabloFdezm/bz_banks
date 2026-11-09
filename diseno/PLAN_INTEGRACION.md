# Plan de integración por olas · Monitor Brasil

**Fecha:** 8 de noviembre de 2026.
**Anexo a:** [INFORME_GRAFICOS.md](INFORME_GRAFICOS.md) (sección 9, orden de trabajo) y [PROPUESTAS-2026-11-05.md](PROPUESTAS-2026-11-05.md).
**Alcance:** llevar el contrato UX del catálogo (`graficos/`, verificado el 8-nov con 160 tarjetas) al sitio vivo `monitor/qwen3.8-max/site`, familia a familia, sin romper lo que ya funciona.

Este plan cubre las dos piezas que la propuesta original dejó abiertas: **cómo se integra** (la maqueta es SVG autónomo; el sitio tiene sus propios renderizadores) y **cuándo se considera hecho** (criterio verificable por familia, incluida una medida de éxito externa).

## 1. Principios de integración

1. **Se reimplementa, no se porta.** El SVG de las maquetas es referencia de comportamiento; el código destino vive en `assets/js/charts.js` y en los registros específicos de cada página (`derivados/am1.js`…`am5.js`, `paginas/am6.js`). Ningún archivo de `design/` se copia al sitio.
2. **La mejora vive en la primitiva compartida.** Un cambio en `linea` beneficia a sus 32 tarjetas; los adaptadores conservan fórmulas, unidades y textos. Antes de tocar un componente hay que localizar *todos* sus registros (casos conocidos: `barras_div` existe dos veces, `tabla` tiene envoltorio en AM2, `tabla_am1` y `lineaL` se reutilizan entre AM1 y AM2).
3. **No se toca la gestión común.** Agrandar, cierre, foco e inercia del fondo (`pagina.js:219`), estados bloqueados (`pagina.js:192`), exportación (`excel.js`) y resaltado cruzado (`destacar.js`) se conservan. El cuerpo de detalle cambia por familia; la infraestructura no.
4. **Una familia = una entrega revisable.** Cada ola se integra en rama propia, pasa el verificador del sitio (`monitor/qwen3.8-max/herramientas/verificar.mjs`) y se publica solo cuando su criterio de hecho está completo.
5. **Las 4 tarjetas FALTA no se rellenan.** Siguen bloqueadas hasta resolver su dependencia de datos (SCR por porte, crédito pyme trimestral, descomposición CAGED, RTN tabla 1.6). Su estado vacío forma parte de la prueba, no de la excepción.
6. **Datos intactos.** No se cambia ninguna fórmula, unidad o fuente sin corrección semántica autorizada y documentada. Las comparaciones visual/dato se hacen contra los JSON de `data/`.

## 2. Criterio de «hecho» por familia

Una familia está **integrada** cuando cumple los nueve puntos siguientes, registrados en su matriz de cobertura:

| # | Criterio | Cómo se verifica |
| --- | --- | --- |
| 1 | **Componente actualizado** en todos sus registros, con variantes representadas | Revisión de código + tabla de registros afectados en la guía de la familia |
| 2 | **Datos idénticos**: valores, unidades, signos, faltantes y fórmulas sin cambio respecto al adaptador previo | Muestreo de 3 fechas por tarjeta piloto contra los JSON; cierre de cascada con tolerancia declarada donde aplique |
| 3 | **Estados completos**: con datos, vacío, filtro sin coincidencias, error de carga y FALTA si existe en la familia | Recorrido forzado de cada estado en al menos una tarjeta |
| 4 | **Interacción**: tooltip de vista previa, consulta fijada por clic/toque, estado preservado entre compacto y Agrandar | Recorrido manual en las tarjetas piloto |
| 5 | **Teclado y foco**: controles etiquetados, flechas/Inicio/Fin, Escape cierra tooltip y luego diálogo, foco devuelto a la tarjeta | Recorrido solo-teclado de una tarjeta por variante |
| 6 | **Reflujo**: 375, 768, 1024 y 1440 px sin desborde, con los nombres y valores extremos de la familia | Capturas en los cuatro anchos de las tarjetas piloto |
| 7 | **Sin regresión**: exportación a Excel, `destacar.js`, selectores de página y verificador del sitio en verde | `node monitor/qwen3.8-max/herramientas/verificar.mjs` + prueba manual de exportar |
| 8 | **Revisión visual de todas las tarjetas de la familia**, no solo las piloto | Matriz de cobertura firmada: cada clave AM* marcada como revisada o pendiente con motivo |
| 9 | **Documentación**: guía de la familia actualizada con lo que cambió, invariantes y excepciones | Diff de la guía incluido en la entrega |

Una familia **no se declara integrada** con el componente mergeado pero sin el punto 8. Reutilizar el dibujante no equivale a inspección completada.

## 3. Criterio de éxito externo

La verificación técnica no demuestra que el rediseño se lea mejor. Antes de la Ola 1 y al cerrarla:

1. **Prueba de lectura con 3–5 usuarios del monitor** (PMs o quien lo use a diario), 20 minutos, sobre las tarjetas piloto de F01/F03/F02, versión actual contra versión integrada.
2. **Tres tareas medibles por tarjeta piloto**: localizar el último dato y su fecha; decir si una serie está por encima o por debajo de su referencia; explicar qué muestra un Agrandar.
3. **Éxito**: mejora o igualdad en tiempo de respuesta y cero errores nuevos de interpretación (signo, unidad, referencia). Si una variante empeora la lectura, se ajusta antes de extenderla a las repeticiones de su familia.

Es una prueba de calibración, no un estudio estadístico: su función es detectar regresiones de lectura antes de multiplicarlas por 53.

## 4. Olas de trabajo

Orden heredado del informe (sección 9). Las olas 1 y 2 cubren 116 de las 160 tarjetas y comparten la mayor parte de la infraestructura.

### Ola 0 · Preparación (sin tarjetas)

- Levantar la matriz de cobertura (una hoja: clave AM*, familia, componente, registros afectados, estado de revisión).
- Resolver la fuente maestra de `DESIGN.md` (raíz vs. `design/`): una queda como enlace a la otra.
- Ejecutar la prueba de lectura inicial (sección 3) sobre el sitio actual para tener línea base.
- Confirmar en git una rama por ola; el sitio publicado no se toca hasta cerrar cada una.

**Hecho cuando:** matriz creada, línea base de lectura registrada, verificador del sitio en verde sobre `main`.

### Ola 1 · Líneas → tablas → columnas (F01, F03, F02 · ~91 tarjetas)

- **F01 (53):** casos piloto AM2-03-1 (multiserie), AM1-01-4 (varias series con leyenda), AM4-02-0 (observado vs. contrafactual con relleno y cruces), AM6-02-0 (expectativas). Cubre los tres registros: `linea`, `lineaL`, `serie_tiempo`. Riesgo principal: faltantes filtrados en silencio (H04) y rellenos con signos cruzados (H05).
- **F03 (20):** pilotos AM1-03-0, AM2-02-0, AM4-07-3, AM5-09-0. Incluye los micrográficos internos (sparklines, barras de cambio, tiras de composición) y las filas desplegables con disparador de teclado (H01).
- **F02 (16):** pilotos AM2-01-0, AM2-06-1, AM3-02-3, AM4-07-2. Invariante: no normalizar aportes a 100 %; positivos y negativos apilados por separado.

**Hecho cuando:** los 9 criterios por familia + prueba de lectura final con mejora o igualdad frente a la línea base.

### Ola 2 · Barras horizontales → cascadas → dispersión (F07, F04, F05 · ~27 tarjetas)

- **F07 (9):** unificar la señal de «fuera de escala» en los topes (H02) y localizar las dos implementaciones de `barras_div` antes de tocar ninguna.
- **F04 (8):** cierre aritmético inicio + contribuciones = final con tolerancia; nombres completos accesibles en la variante fiscal y decisión sobre el scroll horizontal de 640 px en móvil (H03) antes de extenderlo.
- **F05 (10):** regla explícita de área/radio de burbuja; conservar la diagonal de la variante CLU.

### Ola 3 · Antes/después, composición, paneles, KPI, cajas, matrices (F10, F08, F09, F11, F14, F16 · ~22 tarjetas)

- Riesgos específicos: no intercambiar `apilada_100` con `barras_cien`; no convertir cajas de ±1σ en boxplots; no tratar el termómetro fiscal como velocímetro ni el mapa de sostenibilidad como geográfico.

### Ola 4 · Mosaico UF, abanico, embudos, calendario, señales (F12, F13, F15, F17, F18 · ~6 tarjetas)

- Incluye rotular el universo del balance de señales frente al subconjunto visible (H06).

### Ola 5 · Especializados (F19–F24 · ~6 tarjetas)

- Una tarjeta por familia; se revisan individualmente con los mismos 9 criterios.

### Transversal · F06 y bloques auxiliares

- **F06 (5):** el patrón de relojes ya está definido; esta ola solo adapta las tres trayectorias que no son reloj (AM4-08-0, AM5-06-2 y la FALTA AM3-08-2 si se desbloquea). El bloque laboral **no** se copia a otras trayectorias.
- **65 bloques de encabezado** (dato, texto, kpi_galeria, selector): se revisan junto a la familia que usa sus primitivas; los 4 selectores entran en la prueba de estado de cada página afectada.

## 5. Seguimiento

- **Matriz de cobertura viva** (una fila por tarjeta): componente, ola, estado (pendiente / integrada / revisada visualmente / bloqueada por datos), evidencia (captura o enlace a commit).
- **Verificador del sitio en verde** como condición de merge de cada ola; la publicación en Cloudflare Pages sigue el flujo habitual (`publicar.bat`) solo con la ola cerrada.
- **Al cerrar cada ola**, actualizar `DESIGN_GRAFICOS.md` (sección «Cobertura actual») para que el catálogo refleje qué contrato está ya en el sitio vivo y cuál solo en catálogo.

## 6. Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| El rediseño en primitiva cambia tarjetas no inspeccionadas | Criterio 8: ninguna familia se cierra sin revisión visual de todas sus instancias |
| Cambios semánticos disfrazados de cambios visuales | Criterio 2 + invariantes por familia del informe; cualquier corrección de fórmula se documenta aparte |
| Regresión en exportación o resaltado cruzado | Criterio 7 con prueba manual obligatoria |
| La documentación diverge del código | Criterio 9 + actualización de cobertura al cerrar cada ola |
| Mejora técnica que empeora la lectura | Prueba de lectura antes/después en Ola 1 (sección 3) |
