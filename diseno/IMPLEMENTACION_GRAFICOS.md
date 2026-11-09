# Implementación de los gráficos

**Entrada:** [maqueta-graficos-frecuentes.html](maqueta-graficos-frecuentes.html).  
**Alcance:** ocho ejemplos, cuatro familias y datos locales extraídos el 5 de noviembre de 2026.

## Entrega

Abre el HTML directamente en un navegador moderno: contiene estilos, fuentes, datos y JavaScript; no requiere servidor ni conexión. Para compartir la maqueta y esta guía, entrega ambos archivos en la misma carpeta.

| Archivo | Uso |
|---|---|
| [maqueta-graficos-frecuentes.html](maqueta-graficos-frecuentes.html) | Referencia funcional: compacto, Agrandar, filtros y tooltips |
| [IMPLEMENTACION_GRAFICOS.md](IMPLEMENTACION_GRAFICOS.md) | Guía breve de implementación |
| [GUIA_GRAFICOS_FRECUENTES_LLM.md](GUIA_GRAFICOS_FRECUENTES_LLM.md) | Fórmulas, contratos de datos, excepciones y prompts completos |
| [assets/generar_graficos_frecuentes.py](assets/generar_graficos_frecuentes.py) | Extracción y generación reproducible |
| [assets/graficos_frecuentes_extra.js](assets/graficos_frecuentes_extra.js) | Adaptadores de los cuatro ejemplos añadidos |

## Pasos de integración

1. **Localizar el caso por su ID** en los adaptadores originales assets/js/derivados/am1.js a am4.js. Conservar sus fuentes y fórmulas.
2. **Separar datos y presentación.** El adaptador entrega fechas, valores, unidades y referencias; el renderizador dibuja.
3. **Mantener un único estado por tarjeta:** filtros, fecha o elemento seleccionado, grupos abiertos y consulta fijada. Compacto y Agrandar deben leer ese estado.
4. **Reutilizar por familia.** En el monitor, adaptar los componentes existentes de assets/js/charts.js y los renderizadores particulares. La maqueta usa SVG autónomo; no requiere sustituir páginas enteras ni incorporar otra biblioteca.
5. **Aplicar las reglas de interacción** descritas abajo y comprobar cada variante antes de extenderla a tarjetas repetidas.

## Reglas de los ocho ejemplos

| Caso / ID | Regla que debe conservarse |
|---|---|
| IPCA y núcleos · AM2-03-1 | aa × 100; promedio sólo con los cinco núcleos del mes; meta ausente permanece ausente |
| Primario fiscal · AM4-02-0 | Valores ya en % del PIB; brecha = estabilizador − observado, en pp; dividir el relleno en cada cruce |
| Amplitud · AM1-03-0 | Comparar m3a − m12; igual si su valor absoluto es ≤ 0,001; denominador sólo con ambos datos válidos |
| Aportes IPCA · AM2-01-0 | Nueve grupos; aporte × 100 en pp y total en %; positivos y negativos se apilan por separado |
| Actividad · AM1-01-4 | a12 × 100; cuatro series por cesta y hasta 48 meses; todas son observadas |
| Brecha de desocupación · AM3-02-3 | (desocupacion_sa − mediana 2012–2019) × 100; referencia fija; no usar el campo brecha_pp del archivo |
| Gasto · AM4-07-3 | Campos en fracción: convertir una vez × 100; peso en % PIB, cambios en pp y crecimiento real en %; no sumar padres e hijos |
| Cascada · AM4-04-0 | Datos ya escalados; inicio + contribuciones = cierre calculado; conservar residuo y mostrar diferencia con el final; tolerancia 0,0001 pp |

En todos los casos: unir por periodo, conservar null, no arrastrar datos rezagados ni inventar ceros. No normalizar los aportes a 100 %. No aplicar una conversión × 100 a todos los archivos fiscales.

## Interacción obligatoria

- **Hover:** muestra una vista previa con fecha o elemento, valores, unidades y “Sin dato” cuando corresponda. No cambia la selección fijada.
- **Clic/toque:** conserva la consulta en el panel de valores. En táctil, esa lectura sustituye al hover.
- **Agrandar:** conserva filtros, selección y grupos abiertos; añade detalle y metodología. Cerrar devuelve el foco a la tarjeta.
- **Teclado:** controles con etiqueta y foco visible; flechas e Inicio/Fin recorren el gráfico; botones con Enter/espacio. Escape cierra primero el tooltip y después, si se vuelve a pulsar, el diálogo.
- **Tablas:** nombres completos, jerarquía explícita y acceso a hijos. El gasto tiene un corte único: no añadirle un selector mensual ficticio.
- **Presentación:** reutilizar tokens y fuentes existentes, controles de al menos 44 px y texto HTML como alternativa a leer el gráfico.

## Regeneración

Desde el proyecto, con Python 3.8 o posterior:

~~~powershell
python assets/generar_graficos_frecuentes.py --html
python assets/generar_graficos_frecuentes.py --guide
~~~

En otro equipo, ajustar SOURCE en el generador. Requiere assets/fonts.css, assets/graficos_frecuentes_extra.js, .od-frames/layout.css y estos JSON del monitor:

infj_serie, od_bcb, od_total, fiscal_mensual, grafico_inflacion_v2, actv_serie, actv_miembro, empleo_pagina, fis_gasto y fiscal_cascada.

Guardar los cambios en el generador o en el JavaScript adicional antes de regenerar: --html reemplaza el HTML; --guide reemplaza la guía extensa. Esta guía breve se mantiene como documento independiente.

## Antes de integrar

Comprobar valores contra los JSON, unidades, ausencias, signos y cierre de cascada. Recorrer filtros, tooltips, teclado y retorno de foco. Revisar móvil y escritorio a 375, 768, 1024 y 1440 px. La entrega no incluye pruebas en navegador ni integración en el monitor original.

**Instrucción breve para otro LLM:** “Implementa los casos de esta maqueta conservando IDs, fuentes, fórmulas y unidades de esta guía. Comparte el estado entre compacto y Agrandar. Mantén tooltips, consulta persistente, teclado y datos ausentes. Reutiliza los componentes del monitor. Documenta las excepciones y no afirmes pruebas que no ejecutaste.”

**Referencia anterior:** [maqueta de relojes](maqueta-relojes.html) y [guía de relojes](GUIA_RELOJES_LLM.md).
