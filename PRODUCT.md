# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Pablo** (usuario principal): Senior Equity Research Analyst buy-side (Principal Asset Management, Santiago), cubre
  bancos de LatAm; Brasil es nuevo para él. Usa el sitio para seguir el ciclo de crédito, la calidad, la rentabilidad
  y la competencia del sistema bancario brasileño, y para comparar un banco contra su grupo.
- **Analistas del equipo de research**: entran por su cuenta, con un nivel técnico similar al de Pablo.
- **PMs**: entran directamente a buscar un dato o un gráfico, sin que Pablo se los presente. Tienen que poder leerlo
  rápido y sin contexto previo.
- **Comité**: ve las secciones como láminas (modo Presentar) cuando Pablo presenta.

El sitio no es público ni está pensado para gente fuera de Principal (confirmado el 11-nov-2026).

## Product Purpose

Dashboard del sector bancario de Brasil, publicado como sitio estático en https://banks-bz.pages.dev. Ordena el
crédito del sistema (volumen, precio, riesgo y fondeo), las hojas por producto y segmento, y el P&L, el balance y el
capital por banco. Cumple su propósito si quien entra encuentra la cifra correcta, con su corte y su variación, sin
tener que ir a la fuente ni rehacer el gráfico.

## Positioning

Lo que ninguna fuente por separado entrega:

- **Todo en un lugar**: SGS, SCR.data, IF.Data, CVM (ITR/DFP), REF y balancetes COSIF, con un mismo formato y las
  mismas definiciones.
- **Réplica de sell-side con fuentes públicas**: reconstruye cortes que hoy solo traen los reportes de terceros.
- **Banco contra su grupo**: agregados auditables (sumas o cocientes de sumas, nunca promedios de ratios).
- **Listo para presentar**: cada sección es una lámina de 1920×1080 para el comité, sin pasar por PowerPoint.

## Operating Context

- Se usa en escritorio. En celular basta con que se lea (una columna, nada se sale de la pantalla).
- El modo Presentar convierte cada sección en una lámina a pantalla completa. Agrandar abre el detalle de un gráfico
  o de una tabla. Cada bloque se puede bajar a Excel. Banco, agrupación, corte y vista viajan en la URL para
  compartir un enlace exacto.
- Los datos se actualizan con `actualizar.bat` (pipeline Python → tablas gold `bk_*`) y se publican con
  `publicar.bat`. Python calcula todo; el navegador solo filtra y dibuja.
- Los cambios grandes de diseño siguen un orden fijo: canvas → aprobación de Pablo → construcción.

## Capabilities and Constraints

- Idioma: castellano en todo (sitio, código, commits). Los términos del BCB van en portugués cuando no hay traducción
  estable (consignado, IF.Data, COSIF).
- **No se inventan cifras.** Si falta un dato, la tarjeta queda «en preparación» o «falta». Lo que no tiene una
  definición segura queda null.
- Se respetan los quiebres conocidos y no se suavizan: COSIF 2025-03, Res. 4.966 desde 2025, 2024-T4 de IF.Data.
- No se publica nada con licencia de terceros: ni precios, ni consenso, ni targets, ni datos de Bloomberg.
  `referencias/` (reportes sell-side y del BCB) nunca va a GitHub ni al sitio.
- Las reglas de diseño del sitio (par gráfico-tabla, tabla estándar, Total en otro color) las dicta Pablo y no se
  cambian sin preguntarle. Su detalle vive en `spec/01_proposito_y_reglas.md`, `diseno/DECISIONES_UX_2026-11.md` y
  `diseno/DESIGN.md`.

## Evidence on Hand

- Datos reales del pipeline en las tablas gold `bk_*` (ver `spec/04_modelo_de_datos.md`).
- Sitio vigente en `sitio/` (motor v2 en `sitio/assets/v2/`). Canvas del rediseño en `diseno/canvas/`.
- No hay testimonios, usuarios externos ni métricas de uso. No se deben fabricar.

## Product Principles

1. **El número primero, sin adjetivos.** Se muestran cifras, cortes y variaciones. Las lecturas («sube»,
   «preocupa») las hace quien mira.
2. **Cada cifra se puede auditar.** Cualquier valor del sitio se reconstruye desde la fuente pública y el pipeline.
3. **Se lee sin contexto.** Un PM que llega por primera vez entiende el gráfico por su título, sus ejes y su tabla.
4. **Una lámina por idea.** Lo que se ve en la página es lo que se presenta. El detalle va en Agrandar.
5. **Mejor vacío que inventado.** Un dato que falta se declara como faltante.
