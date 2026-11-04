# Resultados — sitio de bancos

## 62b (2026-11-02) — decisiones del arquitecto aplicadas

Mismos dos verificadores, corridos de nuevo después de los cuatro cambios (prefijo «BCB ·»,
B9 · 01, rótulo de B10, pregunta de B8 · 07). Salen con código 0 y sin huecos declarados.

### Conteos (sin cambios: solo se tocaron textos)

```
Tarjetas declaradas en total: 82

Todas las páginas coinciden con el esqueleto
```

### Páginas

```
B0   /                HTTP 200 · 4 secciones · 5 tarjetas · 0 errores de consola
B1   /ciclo/          HTTP 200 · 5 secciones · 11 tarjetas · 0 errores de consola
B2   /competencia/    HTTP 200 · 5 secciones · 11 tarjetas · 0 errores de consola
B3   /credito/        HTTP 200 · 5 secciones · 10 tarjetas · 0 errores de consola
B4   /calidad/        HTTP 200 · 5 secciones · 10 tarjetas · 0 errores de consola
B5   /fondeo/         HTTP 200 · 4 secciones · 6 tarjetas · 0 errores de consola
B6   /rentabilidad/   HTTP 200 · 5 secciones · 9 tarjetas · 0 errores de consola
B7   /capital/        HTTP 200 · 3 secciones · 6 tarjetas · 0 errores de consola
B8   /ficha/          HTTP 200 · 7 secciones · 13 tarjetas · 0 errores de consola
B9   /comparador/     HTTP 200 · 1 secciones · 1 tarjetas · 0 errores de consola
B10  /metodologia/    HTTP 200 · 0 secciones · 0 tarjetas · 0 errores de consola

OK: las 11 páginas cargan sin errores y todas las tarjetas están en preparación
```

B9 ya muestra nombre («Todos los bancos») y pregunta, así que `verificar_f0.py` no informa ningún
hueco del esqueleto. La captura `capturas/b8_f0_1920.png` se regeneró en la misma corrida (B8 no
cambió de estructura: solo la pregunta de la sección 07).

### Lo que se ve en pantalla (texto leído del DOM)

```
/comparador/    rótulo «9 · COMPARADOR» · índice ['01 Todos los bancos']
                01 | Todos los bancos | Trimestral · Panel IF.Data | ¿cómo se comparan los 34 bancos en el último trimestre?
/metodologia/   rótulo «10 · METODOLOGÍA»
/competencia/   05 | Precio y servicio | ¿compiten en precio o en servicio?
                  sub: BCB · reclamos por millón de clientes · último trimestre
                  sub: BCB · tarifas del paquete estándar · por grupo
                  sub: Sistema BCB · Pix como % de los pagos minoristas
/ficha/         07 | Conducta | Trimestral · Olinda | ¿cómo lo evalúan sus clientes frente a sus pares?
                  sub: BCB · reclamos por millón de clientes · banco vs. grupo
```

## F0 (encargo `62`, 2026-11-02) — entregado

Servidor de prueba: `python -m http.server -d sitio_bancos/site 8080`, Chromium real (Playwright).

### 1. Conteo de tarjetas contra el esqueleto

`node sitio_bancos/contar_tarjetas.mjs` (sale con código 0):

```
┌─────────┬────────┬──────────┬────────────┬───────────┬───────────┬───────┬─────────┬───────┬─────┬──────┐
│ (index) │ pagina │ esperado │ declaradas │ colocadas │ secciones │ LISTO │ DERIVAR │ FALTA │ REF │ ok   │
├─────────┼────────┼──────────┼────────────┼───────────┼───────────┼───────┼─────────┼───────┼─────┼──────┤
│ 0       │ 'B0'   │ 5        │ 5          │ 5         │ 4         │ 3     │ 2       │ 0     │ 0   │ 'sí' │
│ 1       │ 'B1'   │ 11       │ 11         │ 11        │ 5         │ 5     │ 4       │ 0     │ 2   │ 'sí' │
│ 2       │ 'B2'   │ 11       │ 11         │ 11        │ 5         │ 4     │ 7       │ 0     │ 0   │ 'sí' │
│ 3       │ 'B3'   │ 10       │ 10         │ 10        │ 5         │ 4     │ 3       │ 3     │ 0   │ 'sí' │
│ 4       │ 'B4'   │ 10       │ 10         │ 10        │ 5         │ 4     │ 6       │ 0     │ 0   │ 'sí' │
│ 5       │ 'B5'   │ 6        │ 6          │ 6         │ 4         │ 1     │ 3       │ 1     │ 1   │ 'sí' │
│ 6       │ 'B6'   │ 9        │ 9          │ 9         │ 5         │ 5     │ 4       │ 0     │ 0   │ 'sí' │
│ 7       │ 'B7'   │ 6        │ 6          │ 6         │ 3         │ 0     │ 0       │ 5     │ 1   │ 'sí' │
│ 8       │ 'B8'   │ 13       │ 13         │ 13        │ 7         │ 5     │ 5       │ 3     │ 0   │ 'sí' │
│ 9       │ 'B9'   │ 1        │ 1          │ 1         │ 1         │ 1     │ 0       │ 0     │ 0   │ 'sí' │
│ 10      │ 'B10'  │ 0        │ 0          │ 0         │ 0         │ 0     │ 0       │ 0     │ 0   │ 'sí' │
└─────────┴────────┴──────────┴────────────┴───────────┴───────────┴───────┴─────────┴───────┴─────┴──────┘

Tarjetas declaradas en total: 82

Todas las páginas coinciden con el esqueleto
```

Los once conteos coinciden con el encargo (B0 5, B1 11, B2 11, B3 10, B4 10, B5 6, B6 9, B7 6,
B8 13, B9 1, B10 0) **y** el reparto por estado coincide con el Anexo A del esqueleto.

### 2. Las once URLs, secciones y tarjetas «en preparación»

`python -X utf8 sitio_bancos/verificar_f0.py` (sale con código 0):

```
B0   /                HTTP 200 · 4 secciones · 5 tarjetas · 0 errores de consola
B1   /ciclo/          HTTP 200 · 5 secciones · 11 tarjetas · 0 errores de consola
B2   /competencia/    HTTP 200 · 5 secciones · 11 tarjetas · 0 errores de consola
B3   /credito/        HTTP 200 · 5 secciones · 10 tarjetas · 0 errores de consola
B4   /calidad/        HTTP 200 · 5 secciones · 10 tarjetas · 0 errores de consola
B5   /fondeo/         HTTP 200 · 4 secciones · 6 tarjetas · 0 errores de consola
B6   /rentabilidad/   HTTP 200 · 5 secciones · 9 tarjetas · 0 errores de consola
B7   /capital/        HTTP 200 · 3 secciones · 6 tarjetas · 0 errores de consola
B8   /ficha/          HTTP 200 · 7 secciones · 13 tarjetas · 0 errores de consola
     s01    01 Identidad
            608 × 372 px · En preparación: dato en construcción · Ficha técnica
            764 × 372 px · En preparación: dato en construcción · Tamaño y cuotas
     s02    02 Posición contra los pares
           1388 × 760 px · En preparación: dato en construcción · Doce métricas, una fila cada una
     s03    03 Cartera
            764 × 372 px · En preparación: dato en construcción · Mix de cartera: banco vs. grupo vs. panel
            608 × 372 px · En preparación: dato en construcción · NPL por modalidad: banco vs. su grupo vs. mora del s
           1388 × 372 px · En preparación: dato en construcción · Crecimiento de cartera y NPL, 12 trimestres, banco v
     s04    04 Rentabilidad
            764 × 520 px · En preparación: dato en construcción · Árbol del ROE: banco vs. mediana del grupo
            608 × 520 px · En preparación: dato en construcción · ROE TTM, 12 trimestres, banco vs. grupo y vs. CDI
     s05    05 Fondeo y capital
            764 × 372 px · En preparación: dato en construcción · Mix de fondeo, banco vs. grupo
            608 × 372 px · En preparación: fuente no incorporada · Basilea y holgura de crecimiento
     s06    06 Último publicado
            764 × 372 px · En preparación: fuente no incorporada · Último trimestre publicado (CVM)
            608 × 372 px · En preparación: dato en construcción · Puente IF.Data ↔ publicado
     s07    07 Conducta
           1388 × 372 px · En preparación: fuente no incorporada · Reclamos por millón de clientes: banco vs. grupo, hi
     captura: C:\Users\pablo\OneDrive\Documentos\Dashboard\sitio_bancos\capturas\b8_f0_1920.png
B9   /comparador/     HTTP 200 · 1 secciones · 1 tarjetas · 0 errores de consola
B10  /metodologia/    HTTP 200 · 0 secciones · 0 tarjetas · 0 errores de consola

HUECOS DEL ESQUELETO (declarados en PENDIENTES.md):
 - B9 s01: el esqueleto §B9 no da nombre ni pregunta para la sección 01

OK: las 11 páginas cargan sin errores y todas las tarjetas están en preparación
```

Los anchos medidos (608, 764 y 1 388 px) son los del §4.5 del spec macro para 4, 5 y 9 columnas
del cuerpo; los altos (372, 520, 760) son los del esqueleto.

### 3. Captura

`sitio_bancos/capturas/b8_f0_1920.png` — B8 a 1 920 px, página completa (1 920 × 4 382).

### 4. Qué no se verificó todavía (y no es parte de la F0)

- Modo presentación (`P`), banco activo, comparador, percentiles, `bancos.css`: ola 2.
- Responsive 1 440 / 1 024 / 390 y Lighthouse: van con el checklist de aceptación (B9, ola 3).
- `data/`: vacío, así que ninguna cifra existe todavía. El sitio no publica ni un número.


## 65 · ola 2, front (2026-11-02)

### 1. `verificar_f0.py` (criterio 1: las once páginas, consola limpia)

Corrido con Playwright de Python sobre `python3 -m http.server -d sitio_bancos/site 8080`.
El Chromium de Playwright no se pudo descargar (red), así que se enlazó el Chromium headless de
`@sparticuz/chromium` que sí arranca; el verificador en sí no cambió.

```
B0   /                HTTP 200 · 4 secciones · 5 tarjetas · 0 errores de consola
B1   /ciclo/          HTTP 200 · 5 secciones · 11 tarjetas · 0 errores de consola
B2   /competencia/    HTTP 200 · 5 secciones · 11 tarjetas · 0 errores de consola
B3   /credito/        HTTP 200 · 5 secciones · 10 tarjetas · 0 errores de consola
B4   /calidad/        HTTP 200 · 5 secciones · 10 tarjetas · 0 errores de consola
B5   /fondeo/         HTTP 200 · 4 secciones · 6 tarjetas · 0 errores de consola
B6   /rentabilidad/   HTTP 200 · 5 secciones · 9 tarjetas · 0 errores de consola
B7   /capital/        HTTP 200 · 3 secciones · 6 tarjetas · 0 errores de consola
B8   /ficha/          HTTP 200 · 7 secciones · 13 tarjetas · 0 errores de consola
     s01    01 Identidad
            608 × 372 px · En preparación: dato en construcción · Ficha técnica
            764 × 372 px · En preparación: dato en construcción · Tamaño y cuotas
     s02    02 Posición contra los pares
           1388 × 760 px · En preparación: dato en construcción · Doce métricas, una fila cada una
     s03    03 Cartera
            764 × 372 px · En preparación: dato en construcción · Mix de cartera: banco vs. grupo vs. panel
            608 × 372 px · En preparación: dato en construcción · NPL por modalidad: banco vs. su grupo vs. mora del s
           1388 × 372 px · En preparación: dato en construcción · Crecimiento de cartera y NPL, 12 trimestres, banco v
     s04    04 Rentabilidad
            764 × 520 px · En preparación: dato en construcción · Árbol del ROE: banco vs. mediana del grupo
            608 × 520 px · En preparación: dato en construcción · ROE TTM, 12 trimestres, banco vs. grupo y vs. CDI
     s05    05 Fondeo y capital
            764 × 372 px · En preparación: dato en construcción · Mix de fondeo, banco vs. grupo
            608 × 372 px · En preparación: fuente no incorporada · Basilea y holgura de crecimiento
     s06    06 Último publicado
            764 × 372 px · En preparación: fuente no incorporada · Último trimestre publicado (CVM)
            608 × 372 px · En preparación: dato en construcción · Puente IF.Data ↔ publicado
     s07    07 Conducta
           1388 × 372 px · En preparación: fuente no incorporada · Reclamos por millón de clientes: banco vs. grupo, hi
     captura: /sessions/rcw-017exdb8anw6yasfko7hmcrc/mnt/Dashboard/sitio_bancos/capturas/b8_f0_1920.png
B9   /comparador/     HTTP 200 · 1 secciones · 1 tarjetas · 0 errores de consola
B10  /metodologia/    HTTP 200 · 0 secciones · 0 tarjetas · 0 errores de consola

OK: las 11 páginas cargan sin errores y todas las tarjetas están en preparación
```

### 2. Criterios 13, 14 y 15 (`_prueba/` y `/ficha/?banco=…`)

Script `verificar.mjs` fuera del repo (en la carpeta de trabajo del worker), con Chromium headless
vía `puppeteer-core`, sobre un servidor estático local en el puerto 8081 que sirve `site/`.
Lo que comprueba:

- **13 (banco activo):** en `/_prueba/` se cambia el banco desde la barra (`nubank`) sin recargar y
  se verifica en el DOM y en la opción de ECharts: en P-01 cambian los valores; en P-03 solo Nubank
  tiene borde navy de 2,5 y el resto `#A9B8CB`; en P-04 la única miniatura destacada es Nubank; en
  P-05 la única fila `cmp-activo` es Nubank; la URL y los enlaces de la cabecera llevan
  `banco=nubank`. P-06 (sin banco) conserva el mismo nodo DOM y el mismo contenido antes y después.
  Al quitar el banco vuelve el panel total sin resaltados. Directo por URL: `/ficha/?banco=itau`
  → grupo `Grandes`; `?banco=nubank` → grupo `Digitales`; todos los enlaces conservan los parámetros.
- **14 (presentación):** a 1920 × 1080 y 1366 × 768 se abre con `P`; en cada lámina el marco de
  la lámina queda dentro de la ventana, el pie queda visible y no hay scroll. `Esc` deja el scroll
  donde estaba (1 200 → 1 200 en `/ficha/`) y devuelve los cuerpos a sus secciones. `→` al final
  de `/capital/?banco=itau` pasa a `/ficha/?banco=itau` con la lámina `1 / 7`.
- **15 (impresión):** `page.pdf` con `preferCSSPageSize` sobre `/_prueba/` da 3 páginas de
  1440 × 810 pt (= 1920 × 1080 px), una por sección, con el pie de hoja de fuente y fecha.

```
ok   / sec=4 tarj=5 enPrep=5 pest=11 barra=true
ok   /ciclo/ sec=5 tarj=11 enPrep=11 pest=11 barra=true
ok   /competencia/ sec=5 tarj=11 enPrep=11 pest=11 barra=true
ok   /credito/ sec=5 tarj=10 enPrep=10 pest=11 barra=true
ok   /calidad/ sec=5 tarj=10 enPrep=10 pest=11 barra=true
ok   /fondeo/ sec=4 tarj=6 enPrep=6 pest=11 barra=true
ok   /rentabilidad/ sec=5 tarj=9 enPrep=9 pest=11 barra=true
ok   /capital/ sec=3 tarj=6 enPrep=6 pest=11 barra=true
ok   /ficha/ sec=7 tarj=13 enPrep=13 pest=11 barra=true
ok   /comparador/ sec=1 tarj=1 enPrep=1 pest=11 barra=true
ok   /metodologia/ sec=0 tarj=0 enPrep=0 pest=11 barra=true
ok   _prueba tarjetas=6
nubank: {"barra":"Nubank · grupo Digitales","url":"?banco=nubank&grupo=Digitales","links":["/?banco=nubank&grupo=Digitales","/ciclo/?banco=nubank&grupo=Digitales"],"p01":"10,2 %|2,8 %|4,1 %|13,3 %|4,7 %|44,7 %|6,3|90,0 %|2,4 %|5,1 %|1.186,5|17,0 %","p01Puntos":12,"p04Destacados":["Nubank"],"p05Activo":["Nubank"],"burbDestacado":["Nubank"],"burbColorActivo":"#123864","burbColorOtros":["#A9B8CB"],"figsIguales":6}
ok   nubank: URL, barra, enlaces, P-01, P-03, P-04, P-05 resaltan; P-06 intacta
sin banco: {"url":"","barra":"Sin banco seleccionado","p01":12,"destacados":0,"filas":0}
ok   quitar banco: vuelve a panel total, sin resaltados
ok   _prueba: consola limpia en el recorrido de bancos
ok   /ficha/?banco=itau: barra «Itaú Unibanco · grupo Grandes», grupo Grandes, 11 enlaces con estado
ok   captura ficha_itau_barra_1920.png
ok   /ficha/?banco=nubank: barra «Nubank · grupo Digitales», grupo Digitales, 11 enlaces con estado
ok   enlaces de cabecera conservan banco, grupo y trimestre
ok   presentación 1920x1080: Percentiles y cascada [1 / 3] 1920x1080 matrix(1, 0, 0, 1, -960, -540) · Burbujas y pequeños múltiplos [2 / 3] 1920x1080 matrix(1, 0, 0, 1, -960, -540) · Comparador y control [3 / 3] 1587x1080 matrix(0.82632, 0, 0, 0.82632, -960, -65
   dentro del marco y sin scroll en las tres láminas (1920x1080)
ok   Esc: sale y devuelve los cuerpos a sus secciones
ok   presentación 1366x768: Percentiles y cascada [1 / 3] 1365x768 matrix(0.711111, 0, 0, 0.711111, -960, - · Burbujas y pequeños múltiplos [2 / 3] 1365x768 matrix(0.711111, 0, 0, 0.711111, -960, - · Comparador y control [3 / 3] 1128x768 matrix(0.587605, 0, 0, 0.587605, -960, -
   dentro del marco y sin scroll en las tres láminas (1366x768)
ok   Esc en /ficha/: scroll 1200 → 1200
cruce de página: {"url":"/ficha/?banco=itau","presentacion":true,"contador":"1 / 7"}
ok   → al final de /capital/ pasa a la primera lámina de /ficha/ con el mismo estado
pdf _prueba: páginas 3 tamaños pt 1440x810,1440x810,1440x810 [
  'Bancos Brasil · Piezas nuevas · DATOS FICTICIOS DE PRUEBA · Percentiles y cascada · Panel ',
  'Bancos Brasil · Piezas nuevas · DATOS FICTICIOS DE PRUEBA · Burbujas y pequeños múltiplos ',
  'Bancos Brasil · Piezas nuevas · DATOS FICTICIOS DE PRUEBA · Comparador y control · Panel ·'
]
ok   impresión: una lámina por hoja (3 secciones → 3 hojas)
ok   captura prueba_1920.png (página completa a 1920 px)

TODO OK
```

### 3. Conteo de tarjetas

```
Tarjetas declaradas en total: 82
Todas las páginas coinciden con el esqueleto
```

### 4. Capturas (para el arquitecto; el worker no las revisó visualmente)

- `sitio_bancos/capturas/prueba_1920.png` (página completa de `_prueba/`, 1 920 px)
- `sitio_bancos/capturas/prueba_presentacion_1920x1080.png` (primera lámina de `_prueba/`)
- `sitio_bancos/capturas/ficha_itau_barra_1920.png` (`/ficha/?banco=itau`, barra visible)
- `sitio_bancos/capturas/prueba_impresion.pdf` (PDF de impresión de `_prueba/`, 3 hojas)
- `sitio_bancos/capturas/b8_f0_1920.png` (regenerada por `verificar_f0.py`)

## 65b · corrección del arquitecto (2026-11-02)

### verificar_f0.py (código final)

```
B0   /                HTTP 200 · 4 secciones · 5 tarjetas · 0 errores de consola
B1   /ciclo/          HTTP 200 · 5 secciones · 11 tarjetas · 0 errores de consola
B2   /competencia/    HTTP 200 · 5 secciones · 11 tarjetas · 0 errores de consola
B3   /credito/        HTTP 200 · 5 secciones · 10 tarjetas · 0 errores de consola
B4   /calidad/        HTTP 200 · 5 secciones · 10 tarjetas · 0 errores de consola
B5   /fondeo/         HTTP 200 · 4 secciones · 6 tarjetas · 0 errores de consola
B6   /rentabilidad/   HTTP 200 · 5 secciones · 9 tarjetas · 0 errores de consola
B7   /capital/        HTTP 200 · 3 secciones · 6 tarjetas · 0 errores de consola
B8   /ficha/          HTTP 200 · 7 secciones · 13 tarjetas · 0 errores de consola
     s01    01 Identidad
            608 × 372 px · En preparación: dato en construcción · Ficha técnica
            764 × 372 px · En preparación: dato en construcción · Tamaño y cuotas
     s02    02 Posición contra los pares
           1388 × 760 px · En preparación: dato en construcción · Doce métricas, una fila cada una
     s03    03 Cartera
            764 × 372 px · En preparación: dato en construcción · Mix de cartera: banco vs. grupo vs. panel
            608 × 372 px · En preparación: dato en construcción · NPL por modalidad: banco vs. su grupo vs. mora del s
           1388 × 372 px · En preparación: dato en construcción · Crecimiento de cartera y NPL, 12 trimestres, banco v
     s04    04 Rentabilidad
            764 × 520 px · En preparación: dato en construcción · Árbol del ROE: banco vs. mediana del grupo
            608 × 520 px · En preparación: dato en construcción · ROE TTM, 12 trimestres, banco vs. grupo y vs. CDI
     s05    05 Fondeo y capital
            764 × 372 px · En preparación: dato en construcción · Mix de fondeo, banco vs. grupo
            608 × 372 px · En preparación: fuente no incorporada · Basilea y holgura de crecimiento
     s06    06 Último publicado
            764 × 372 px · En preparación: fuente no incorporada · Último trimestre publicado (CVM)
            608 × 372 px · En preparación: dato en construcción · Puente IF.Data ↔ publicado
     s07    07 Conducta
           1388 × 372 px · En preparación: fuente no incorporada · Reclamos por millón de clientes: banco vs. grupo, hi
     captura: /sessions/rcw-017exdb8anw6yasfko7hmcrc/mnt/Dashboard/sitio_bancos/capturas/b8_f0_1920.png
B9   /comparador/     HTTP 200 · 1 secciones · 1 tarjetas · 0 errores de consola
B10  /metodologia/    HTTP 200 · 0 secciones · 0 tarjetas · 0 errores de consola

OK: las 11 páginas cargan sin errores y todas las tarjetas están en preparación
```

### contar_tarjetas.mjs (código final)

```
┌─────────┬────────┬──────────┬────────────┬───────────┬───────────┬───────┬─────────┬───────┬─────┬──────┐
│ (index) │ pagina │ esperado │ declaradas │ colocadas │ secciones │ LISTO │ DERIVAR │ FALTA │ REF │ ok   │
├─────────┼────────┼──────────┼────────────┼───────────┼───────────┼───────┼─────────┼───────┼─────┼──────┤
│ 0       │ 'B0'   │ 5        │ 5          │ 5         │ 4         │ 3     │ 2       │ 0     │ 0   │ 'sí' │
│ 1       │ 'B1'   │ 11       │ 11         │ 11        │ 5         │ 5     │ 4       │ 0     │ 2   │ 'sí' │
│ 2       │ 'B2'   │ 11       │ 11         │ 11        │ 5         │ 4     │ 7       │ 0     │ 0   │ 'sí' │
│ 3       │ 'B3'   │ 10       │ 10         │ 10        │ 5         │ 4     │ 3       │ 3     │ 0   │ 'sí' │
│ 4       │ 'B4'   │ 10       │ 10         │ 10        │ 5         │ 4     │ 6       │ 0     │ 0   │ 'sí' │
│ 5       │ 'B5'   │ 6        │ 6          │ 6         │ 4         │ 1     │ 3       │ 1     │ 1   │ 'sí' │
│ 6       │ 'B6'   │ 9        │ 9          │ 9         │ 5         │ 5     │ 4       │ 0     │ 0   │ 'sí' │
│ 7       │ 'B7'   │ 6        │ 6          │ 6         │ 3         │ 0     │ 0       │ 5     │ 1   │ 'sí' │
│ 8       │ 'B8'   │ 13       │ 13         │ 13        │ 7         │ 5     │ 5       │ 3     │ 0   │ 'sí' │
│ 9       │ 'B9'   │ 1        │ 1          │ 1         │ 1         │ 1     │ 0       │ 0     │ 0   │ 'sí' │
│ 10      │ 'B10'  │ 0        │ 0          │ 0         │ 0         │ 0     │ 0       │ 0     │ 0   │ 'sí' │
└─────────┴────────┴──────────┴────────────┴───────────┴───────────┴───────┴─────────┴───────┴─────┴──────┘

Tarjetas declaradas en total: 82

Todas las páginas coinciden con el esqueleto
```

### Verificación de la corrección (verificar.mjs, Chromium headless)

```
ok   / sec=4 tarj=5 enPrep=5 pest=11 barra=true
ok   /ciclo/ sec=5 tarj=11 enPrep=11 pest=11 barra=true
ok   /competencia/ sec=5 tarj=11 enPrep=11 pest=11 barra=true
ok   /credito/ sec=5 tarj=10 enPrep=10 pest=11 barra=true
ok   /calidad/ sec=5 tarj=10 enPrep=10 pest=11 barra=true
ok   /fondeo/ sec=4 tarj=6 enPrep=6 pest=11 barra=true
ok   /rentabilidad/ sec=5 tarj=9 enPrep=9 pest=11 barra=true
ok   /capital/ sec=3 tarj=6 enPrep=6 pest=11 barra=true
ok   /ficha/ sec=7 tarj=13 enPrep=13 pest=11 barra=true
ok   /comparador/ sec=1 tarj=1 enPrep=1 pest=11 barra=true
ok   /metodologia/ sec=0 tarj=0 enPrep=0 pest=11 barra=true
ok   _prueba tarjetas=6
nubank: {"barra":"Nubank · grupo Digitales","url":"?banco=nubank&grupo=Digitales","links":["/?banco=nubank&grupo=Digitales","/ciclo/?banco=nubank&grupo=Digitales"],"p01":"7,4 %|1,7 %|4,6 %|12,9 %|3,8 %|44,5 %|6,2|89,9 %|2,0 %|5,6 %|1.178,6|20,5 %","p01Puntos":12,"p04Destacados":["Nubank"],"p05Activo":["Nubank"],"burbDestacado":["Nubank"],"burbColorActivo":"#123864","burbColorOtros":["#A9B8CB"],"figsIguales":6}
ok   nubank: URL, barra, enlaces, P-01, P-03, P-04, P-05 resaltan; P-06 intacta
sin banco: {"url":"","barra":"Sin banco seleccionado","p01":12,"destacados":0,"filas":0}
ok   quitar banco: vuelve a panel total, sin resaltados
ok   _prueba: consola limpia en el recorrido de bancos
ok   /ficha/?banco=itau: barra «Itaú Unibanco · grupo Grandes», grupo Grandes, 11 enlaces con estado
ok   captura ficha_itau_barra_1920.png
ok   /ficha/?banco=nubank: barra «Nubank · grupo Digitales», grupo Digitales, 11 enlaces con estado
ok   enlaces de cabecera conservan banco, grupo y trimestre
ok   presentación 1920x1080: Percentiles y cascada [1 / 3] 1920x1080 matrix(1, 0, 0, 1, -960, -540) · Burbujas y pequeños múltiplos [2 / 3] 1920x1080 matrix(1, 0, 0, 1, -960, -540) · Comparador y control [3 / 3] 1587x1080 matrix(0.82632, 0, 0, 0.82632, -960, -65
   dentro del marco y sin scroll en las tres láminas (1920x1080)
ok   Esc: sale y devuelve los cuerpos a sus secciones
ok   presentación 1366x768: Percentiles y cascada [1 / 3] 1365x768 matrix(0.711111, 0, 0, 0.711111, -960, - · Burbujas y pequeños múltiplos [2 / 3] 1365x768 matrix(0.711111, 0, 0, 0.711111, -960, - · Comparador y control [3 / 3] 1128x768 matrix(0.587605, 0, 0, 0.587605, -960, -
   dentro del marco y sin scroll en las tres láminas (1366x768)
ok   Esc en /ficha/: scroll 1200 → 1200
cruce de página: {"url":"/ficha/?banco=itau","presentacion":true,"contador":"1 / 7"}
ok   → al final de /capital/ pasa a la primera lámina de /ficha/ con el mismo estado
pdf _prueba: páginas 3 tamaños pt 1440x810,1440x810,1440x810 [
  'Bancos Brasil · Piezas nuevas · DATOS FICTICIOS DE PRUEBA · Percentiles y cascada · Panel ',
  'Bancos Brasil · Piezas nuevas · DATOS FICTICIOS DE PRUEBA · Burbujas y pequeños múltiplos ',
  'Bancos Brasil · Piezas nuevas · DATOS FICTICIOS DE PRUEBA · Comparador y control · Panel ·'
]
ok   impresión: una lámina por hoja (3 secciones → 3 hojas)
ok   captura prueba_1920.png (página completa a 1920 px)
65b: {"filas":12,"fueraMediana":10,"t4Distinto":11,"etiquetas":16,"repetidas":[],"smPaneles":34,"gridVisible":true,"cortados":0,"fuera":[]}
ok   percentiles: 10 de 12 filas con el banco fuera de la mediana; 11 con hace un año visible
ok   eje de la control: 16 etiquetas, ninguna repetida
ok   miniaturas: 34 paneles, todas las filas visibles, ningún nombre cortado
ok   burbujas: ninguna etiqueta cruza el borde derecho
ficha titular: {"sin":["Ficha por banco","8 · FICHA"],"itau":["Itaú Unibanco","8 · FICHA · GRANDES"],"nu":["Nubank","8 · FICHA · DIGITALES"],"quitado":["Ficha por banco","8 · FICHA"]}
ok   ficha: titular y rótulo siguen al banco activo (Itaú Unibanco · GRANDES; Nubank · DIGITALES; sin banco: Ficha por banco)

TODO OK
```

