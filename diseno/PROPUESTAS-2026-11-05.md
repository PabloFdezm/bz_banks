# Propuestas de gráficos — 5 de noviembre de 2026

Este índice reúne el trabajo realizado sobre los gráficos de **Monitor Brasil**. Los archivos están en esta carpeta del proyecto. El recorrido va de las alternativas exploradas a las maquetas elegidas y sus instrucciones de réplica; **ninguna de estas maquetas modifica el monitor original**.

## Por dónde empezar

| Si quieres… | Abre… | Estado |
| --- | --- | --- |
| Comparar las siete alternativas para los relojes | [Exploración de relojes](exploracion-relojes.html) | Propuestas para comparar |
| Ver el patrón elegido para la tarjeta y **Agrandar** | [Maqueta de relojes](maqueta-relojes.html) | Referencia funcional |
| Identificar tipos repetidos y decidir qué revisar después | [Informe de gráficos](INFORME_GRAFICOS.md) | Inventario y prioridades |
| Recorrer ocho casos de líneas, tablas, columnas y cascadas | [Maqueta de gráficos frecuentes](maqueta-graficos-frecuentes.html) | Referencia funcional |
| Integrar o replicar esos ocho casos | [Implementación concisa](IMPLEMENTACION_GRAFICOS.md) | Instrucciones de implementación |
| Llevar el contrato al monitor original, ola a ola | [Plan de integración](PLAN_INTEGRACION.md) | Añadido el 8-nov-2026 |

## 1. Relojes: exploración de alternativas

[**exploracion-relojes.html**](exploracion-relojes.html) permite comparar siete opciones con los escenarios de inflación y mercado laboral: **A · reloj depurado**, **B · reloj con contexto**, **C · por períodos**, **D · vista general con lupa**, **E · rastro temporal**, **F · dos líneas sincronizadas** y **G · secuencia de estados**. Es una exploración de alternativas, no la especificación final del comportamiento de «Agrandar».

Para abrir esta exploración desde una copia de la carpeta, conserva junto a `exploracion-relojes.html` sus dependencias `assets/opciones.css`, `assets/opciones.js` y `assets/fonts.css`.

## 2. Relojes: solución seleccionada

[**maqueta-relojes.html**](maqueta-relojes.html) muestra el **reloj depurado** en la tarjeta compacta. Al pulsar **Agrandar**, el contenido aparece en este orden: **reloj con contexto → por períodos → reloj del ciclo laboral**. La maqueta incluye selección de escenario y fecha, y se abre directamente como archivo HTML.

[**GUIA_RELOJES_LLM.md**](GUIA_RELOJES_LLM.md) especifica estructura, datos, fórmulas, estados, accesibilidad y un prompt reutilizable para replicar el patrón en otros escenarios. **Maqueta y guía forman un par**: usa la primera como referencia de funcionamiento y la segunda como contrato de implementación.

## 3. Inventario para continuar el proceso

[**INFORME_GRAFICOS.md**](INFORME_GRAFICOS.md) inventaría **155 tarjetas** de seis páginas, **40 nombres técnicos de componentes** y **24 familias visuales de trabajo**. Distingue repeticiones, variantes y tarjetas pendientes; propone casos piloto y un orden de revisión. Es un inventario basado en código: la inspección visual completa de todas las tarjetas sigue pendiente.

La prioridad de reutilización identificada allí es **líneas (53 tarjetas), tablas analíticas (20) y columnas (16)**. La maqueta siguiente toma ejemplos de esas familias y añade cascadas.

## 4. Gráficos frecuentes: ocho casos de referencia

[**maqueta-graficos-frecuentes.html**](maqueta-graficos-frecuentes.html) reúne vistas compactas y ampliadas, filtros, tooltips de vista previa y consulta persistente mediante clic o toque. Los casos son:

| Familia | Casos incluidos |
| --- | --- |
| Líneas | IPCA y núcleos; primario observado frente al estabilizador de deuda; índices de actividad |
| Tablas analíticas | Componentes que aceleran por agregado; gasto partida por partida |
| Columnas | Aportes al IPCA por grupo; brecha de desocupación |
| Cascadas | Deuda pública y conciliación de sus contribuciones |

[**IMPLEMENTACION_GRAFICOS.md**](IMPLEMENTACION_GRAFICOS.md) es la guía breve: archivos, pasos de integración, reglas de los ocho ejemplos e interacciones. [**GUIA_GRAFICOS_FRECUENTES_LLM.md**](GUIA_GRAFICOS_FRECUENTES_LLM.md) conserva el diagnóstico, los contratos de datos, las excepciones y los prompts detallados para otros LLMs.

La maqueta HTML contiene los datos, estilos, fuentes y scripts necesarios para abrirla sin servidor. Para **regenerarla** desde las fuentes locales, conserva también `assets/generar_graficos_frecuentes.py`, `assets/graficos_frecuentes_extra.js`, `assets/fonts.css` y los datos del monitor original indicados en la guía. El generador tiene una ruta `SOURCE` específica de este equipo que debe adaptarse en otro entorno.

## Orden recomendado de uso

1. Usa la exploración de relojes para comparar opciones; toma la maqueta de relojes y su guía como patrón seleccionado.
2. Consulta el informe para elegir la siguiente familia y sus casos piloto, evitando rediseñar tarjetas equivalentes por separado.
3. Revisa los ocho casos de gráficos frecuentes; usa la guía concisa para integrar y la guía extensa cuando necesites fórmulas, estados o prompts de réplica.

Las maquetas son referencias independientes. La revisión visual de las 155 tarjetas quedó como trabajo posterior; la integración en el monitor original tiene ahora su propio documento: [PLAN_INTEGRACION.md](PLAN_INTEGRACION.md).
