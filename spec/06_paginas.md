# 06 · Páginas

Sitio v2 (desde el 10-nov-2026). Las páginas están en `diseno/canvas/paginas.json`: cada una monta una o más hojas
del canvas (`diseno/canvas/<Hoja>.dc.html`), que `herramientas/construir_v2.py` convierte en módulos de
`sitio/assets/v2/paginas/`. Detalle autogenerado (grupo, ruta y hojas de cada página): `generado/paginas.md`.
Verificación en navegador: `herramientas/verificar_f1.py` (las 13 páginas en 1920, 1280 y 390 px).

## Cómo está armada cada página

- Secciones numeradas (01, 02…), cada una con uno o más **pares**: gráfico a la izquierda y tabla a la derecha,
  proporción 1,5 : 1, nunca apilados en escritorio (reglas de `spec/01` y `DESIGN.md`).
- Tabla de la página: `Indicador · Corte · Último · Δ a/a` (o `Último · Share · a/a` cuando el gráfico muestra el
  a/a del saldo), con la unidad bajo cada encabezado y el Total al final, en negrita. Bajo una tabla corta va la
  definición del indicador; una nota larga se resume y queda completa en Agrandar.
- **Agrandar**: el gráfico a todo el ancho con período ajustable, la tabla de 8 columnas con la caja de la historia
  y la metodología («Columnas», «Filas y fuentes»).
- **Presentar**: una lámina por par, con el título de sección repetido («(cont.)» desde la segunda), «n de m» de la
  sección y «· fin» en la última.
- **Cómo leer**: ayuda de la barra superior, con las entradas que aplican a la página (Z, bandas, segmentos).
- Excel por gráfico y de la página entera.

## Páginas

| Grupo | Página | Ruta | Secciones |
|---|---|---|---|
| Sistema | Portada | `/portada/` | Franja de 5 cifras · 01 Crédito: colocaciones y ciclo · 02 Precio del crédito · 03 NPL: mora y atraso temprano · 04 Rentabilidad y depósitos (balancetes) |
| Sistema | Bancos por grupo · trimestral | `/trimestral/` | 01 Saldos de crédito · 02 Depósitos por tipo · 03 Rendimientos · 04 Margen y riesgo · 05 Resultado y ROE · 06 Eficiencia · 07 Capital |
| Sistema | Crédito por producto | `/credito/` | 01 Volumen · 02 Precio · 03 Calidad · 04 Emisor · 05 Deudor por renta · 06 Deudor por ocupación |
| Personas | Tarjeta | `/tarjeta/` | 01 Volumen · 02 Precio · 03 Calidad · 04 Qué movió la mora · 05 Renta · 06 Ocupación · 07 Emisor · 08 Saldo medio y endeudamiento · 09 Tope por renta |
| Personas | Personal sin planilla y sobregiro | `/personal/` | Como Tarjeta |
| Personas | Descuento por planilla | `/planilla/` | Como Tarjeta; 09 Nuevo privado |
| Personas | Vehículos | `/vehiculos/` | Como Tarjeta; 09 Operaciones |
| Personas | Inmobiliario | `/inmobiliario/` | 01 Volumen · 02 Precio · 03 Calidad · 04 Deudor · 05 Emisor · 06 Fondeo |
| Empresas | MPME | `/mpme/` | 01 Volumen · 02 Producto · 03 Precio · 04 Calidad · 05 Qué movió la mora · 06 Sector · 07 Porte · 08 Emisor · 09 Riesgo prospectivo · 10 Saldo medio y operaciones |
| Empresas | Grandes | `/grandes/` | Como MPME, sin Porte; 09 Crédito amplio |
| Fondeo | Fondeo y liquidez | `/fondeo/` | 01 Volumen · 02 Precio · 03 Instrumentos · 04 Inversionista y canal · 05 Por grupo de bancos · 06 Liquidez · 07 Captación externa |
| Bancos | Bancos · agregados | `/agregados/` | 01 Rentabilidad · 02 Margen y riesgo · 03 Eficiencia · 04 Crédito · 05 Calidad · 06 Fondeo · 07 Capital · 08 Estructura · 09 Rentabilidad del SFN · 10 Eficiencia del SFN · 11 Prueba de estrés (hoja `Ref`, REF del BCB) |
| Bancos | P&L y balance por banco | `/pyb/` | 01 Estado de resultados · 02 Balance · 03 Resultado · 04 Margen y riesgo · 05 Servicios y gastos · 06 Estructura del balance · 07 Capital · 08 Sensibilidad a la Selic |

Datos: la Portada lleva sus cifras dentro de las hojas (`herramientas/portada_desde_gold.py` las recarga desde
`bk_concesiones`, `bk_portada_m` y `bk_sistema_bal_m`); el resto lee `sitio/data/v2/<Hoja>.json`, que arman los extractores de
`tareas/borradores/_salida/`.

## Pendiente

- Rehacer Calidad, Rentabilidad y Ficha por banco (la v3 anterior quedó fuera del sitio v2).
- Cada página nueva sigue el orden canvas → aprobación de Pablo → construcción.
