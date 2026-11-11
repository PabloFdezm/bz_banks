# Pendientes al 11-nov-2026 (cierre de la sesión desde el celular)

Todo lo de hoy está publicado en https://banks-bz.pages.dev. Detalle de cada frente en su `tareas/xx_*.md`.

## 1. Inmediato
- [x] **Commit y push del pulido** (570cee0) (publicado, sin commit; el filtro de permisos pidió confirmación explícita):
      `DESIGN.md`, `diseno/canvas/*.dc.html` (13 hojas), `sitio/assets/v2/sitio.js`, `sitio/assets/v2/v2.css` y el
      informe `.impeccable/critique/2026-11-11T15-11-58Z__sitio-portada-index-html.md`.
- [ ] Decidir si se agrega una regla de permiso para commits en este repo (como la de `publicar.bat`).
- [ ] Sin commit y no son de esta sesión (no tocar sin revisar): `diseno/graficos/`, `diseno/reportes/`,
      `tareas/pendientes_10nov.md`.

## 2. Decisiones de Pablo
- [x] Tablas cortas (3 filas) que se estiran al alto de la tarjeta: ¿alinearlas arriba (dos alturas distintas en el
      par) o usar el espacio, p. ej. para la definición que hoy solo está en Agrandar? Con esto se cierra la crítica 3.
      Hecho: «Definición.» bajo la tabla (11 hojas) cuando hay ≤ 8 filas; con saldo/share/a/a se omite la frase «Último:».
- [ ] Revisión visual de las 4 hojas de personas (Tarjeta, Personal, Descuento por planilla, Vehículos) en el sitio.
- [ ] Ideas abiertas: sección 02 de la Portada como un solo par mientras falten cortes.
- [ ] Frente 3 (réplica sell-side): ¿retomarlo solo con 2024–2026 (~1 GB, 1–2 horas)?

## 3. Diseño (crítica 3, menores; `tareas/05_rediseno_graficos.md`)
- [ ] MPME y Grandes: tabla de volumen con saldo y share (falta el saldo en R$ por porte en el par).
- [x] «Corte» nombra dos cosas (selector de segmento y columna de fecha): renombrar una. Hecho: el selector es «Segmentos» (Portada) y «Agrupar por» (Trimestral).
- [x] «Cómo leer» igual en todas las páginas: hacerlo contextual (Z solo donde hay Z; explicar las bandas). Hecho: Z, «Banda gris», franja y segmentos solo donde aplican.
- [x] Presentar: «1 de 2» dentro de la sección; barra a 14 px; lámina centrada en el alto; P&L ya no es una sola lámina.
- [ ] Presentar en P&L a 1280×800: las tarjetas altas (balance) no caben ni a zoom 0,6; ¿partirlas o dejar desplazar?
- [x] Teclado: «Cómo leer» aclara que Inicio/Fin son del período visible; Alt + ↓ ↑ salta entre secciones.
- [x] Celular: deslizar el dedo sobre el gráfico fija el mes más cercano (columnas de 9,7 px).
- [x] Crítica 4 (25/40; `.impeccable/critique/2026-11-11T18-23-35Z__…`). Hechos sus dos P1: unidad bajo «Último» y «Δ a/a»
      en todas las tablas de página, Total siempre al final, prefijos de sección numéricos (01, 02…); encabezados
      h1/h2/h3 (role=heading), caption y scope en las tablas, «Agrandar: título» y grupo con nombre en los períodos.
- [x] Crítica 4, P2: chips ▲▼ en tinta (borde en el color de la serie); «Mora > 90 días» en todo el sitio; «el gráfico
      de la izquierda» → «el gráfico de mora > 90 días de esta sección»; «Tramos con renta» en gris referencia.
- [ ] Paleta de 8 tramos (renta, ocupación) en DESIGN.md: vecinos navy/gris no se distinguen (diseño: canvas primero).
- [ ] Crédito: varias series no Total en cobre (Vehículos, Sobregiro, «Atraso 15–90 días»…); revisar si son el Total
      de su tarjeta o hay que pasarlas a la paleta.
- [x] Crítica 4, P3: Presentar con «(cont.)» en su color y «· fin» con ‹ › inactivos en los bordes; notas de página de
      más de 250 caracteres reducidas a su primera oración + «Más en Agrandar» (completas en Agrandar).
- [ ] Decisión de Pablo: franja de la Portada con Z 10 años o percentil histórico en vez de repetir el Total (canvas).

## 4. Datos
- [x] Frente 11, fase 2: `bk_balancete_m` y `bk_sistema_bal_m` (ROE 12m, depósitos, crédito/depósitos, PL/activo)
      desde ene-20; 97 % de los banco-trimestres cuadra con IF.Data (`borradores/balancetes_informe.md`).
- [ ] Decisión de Pablo (frente 11): NIM, costo de riesgo y eficiencia mensuales no cuadran con IF.Data en el plan
      viejo; ¿quedan trimestrales, mensuales solo desde ene-25, o se sigue buscando el mapa?
- [ ] Sección 04 de la Portada con `bk_sistema_bal_m` (canvas → aprobación).
- [ ] Frente 4 (REF): tarjeta de estrés y tarjetas por segmento.
- [ ] Rehacer Calidad, Rentabilidad y Ficha en v3.
- [ ] Frente 14: partida que falta en M3 (no está en 27792–27802); buscar en la nota metodológica del BCB.
- [ ] Frente 16: confirmar con notas del BCB/Abecip el traslado de concesiones de mercado a regulada; poupança SBPE
      sin la rural para la cobertura.
- [ ] Frente 6 (operación): automatización, limpieza de disco (caché viejo `datos/intermedio/scr_productos/45fa235300`
      y `e82fb46f9a`, mostrar la lista antes de borrar), deuda técnica.

## Hecho hoy (11-nov)
Etapas 1–3 completas (frentes 9, 13, 14, 15, 16 y el arrendamiento), sección «Producto» en Empresas, «Cómo leer»,
tercera crítica y sus arreglos (Total siempre en la escala, MPME alineada, Agrandar en celular, franja de la Portada,
tablas con saldo y share), y pulido final. Permiso local para `publicar.bat`; `actualizar.bat` recarga la Portada.
