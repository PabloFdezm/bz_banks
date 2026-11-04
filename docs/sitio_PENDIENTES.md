# Pendientes — sitio de bancos

Una línea por problema. Formato: **fecha · encargo · qué · por qué · qué se necesita**.

## De esta entrega (encargo 62, F0)

1. **2026-11-02 · 62 · Base del macro provisoria.** Los módulos comunes se copiaron de
   `pb/pbip/diseno/paginas_desde_cero/qwen3.8-max/site/`, que es el único sitio del macro
   construido y **todavía no está aprobado**. · No hay versión vigente marcada en
   `pb/pbip/diseno/AGENTS.md`. · Cuando Pablo apruebe una versión, volver a copiar
   `tokens.css`, `monitor.css`, `datos.js`, `formato.js`, `charts.js`, `pagina.js` y
   `echarts.min.js`, y reaplicar los cinco cambios `// bancos:` de `pagina.js`.
2. ~~**2026-11-02 · 62 · `estado.js`, `presentacion.js` y `charts_bancos.js` no existen.**~~ **Resuelto en 65**: existen y se verificaron (criterios 13 a 15 en `_prueba/` y `/ficha/?banco=itau`). Las configs `usaBanco`, `optica` y `banco` ya las consume `pagina.js`.
3. **2026-11-02 · 62 · `data/` está vacío y las tarjetas usan `datos: []`.** · En F0 no hay tablas
   `bk_*` y el sitio no debe hacer ningún `fetch` (las once URLs cargan sin 404). · La ola 2
   llena `datos` con las tablas que el esqueleto pide para cada tarjeta; están listadas en el
   comentario de cabecera de cada `assets/js/paginas/bN.js`.
4. **2026-11-02 · 62 · Subtítulos y frecuencias derivados.** · El esqueleto no trae columna de
   subtítulo ni de frecuencia; se derivaron del universo de la columna «Datos» (§0.4) y del texto
   de cada tarjeta. · Confirmar los 82 subtítulos y las 44 frecuencias antes de F1 (o corregirlos
   en el esqueleto y volver a transcribir).
5. **2026-11-02 · 62 · Fuentes por tarjeta propuestas.** · El esqueleto no las fija; se usó la
   fuente pública del universo, más «cálculo propio» en las DERIVAR. Las de Olinda
   (reclamos, tarifas), BNDES (FGI) y FGO/Pronampe son interpretación. · Fijarlas en §B10.
6. ~~**2026-11-02 · 62 · Universo de Olinda fuera de los cinco prefijos.**~~ **Resuelto en 62b**
   por decisión del arquitecto (revisión del encargo 62, 2026-11-02): reclamos y tarifas llevan
   prefijo **«BCB ·»**, que no es un universo nuevo, y Pix sigue «Sistema BCB ·». Aplicado en
   B2-05-0, B2-05-1 y B8-07-0. · Falta que §5 del spec web y el esqueleto v0.2 listen «BCB ·»
   entre los prefijos válidos (fuera del alcance de un worker).
7. ~~**2026-11-02 · 62 · B9 sin nombre ni pregunta de sección.**~~ **Resuelto en 62b**: el arquitecto
   fijó nombre «Todos los bancos» y pregunta «¿cómo se comparan los 34 bancos en el último
   trimestre?». Ya está en `b9.js` y `verificar_f0.py` volvió a exigir nombre en todas las
   secciones (la lista de huecos quedó vacía). Entra al esqueleto v0.2.
8. ~~**2026-11-02 · 62 · B10 sin rótulo y sin contenido.**~~ **Rótulo resuelto en 62b**: «10 ·
   METODOLOGÍA». **Sigue pendiente el contenido:** el texto fijo (universos y rezago,
   definiciones desde `bk_metrica`, quiebres, ópticas, puente y fechas de corte) depende de
   `bk_metrica` y `bk_manifiesto`. Hoy la página muestra rótulo y titular y nada más. · Ola 2/3.
9. ~~**2026-11-02 · 62 · B8 §07 sin pregunta ni riel en el esqueleto.**~~ **Resuelto en 62b**: la
   pregunta es «¿cómo lo evalúan sus clientes frente a sus pares?». El riel sigue sin definir
   (el esqueleto no le da bloques y la tarjeta es única).
10. **2026-11-02 · 62 · Cierre oculto en las once páginas.** · `fuentes` y `comoLeer` (el
    «FUENTES» y el «CÓMO LEER ESTA PÁGINA» del §4.7) no están en el esqueleto. · `pagina.js`
    esconde el bloque cuando están vacíos en vez de pintarlo en blanco. · Escribirlos por página.

## Del esqueleto, que la config no puede resolver

11. **2026-11-02 · 62 · B0-01-0 (LISTO) incluye Basilea, que es FALTA.** · Sin `bk_capital` la
    fila de Basilea de las «seis cifras» no se puede dibujar. · Estado de la tarjeta queda LISTO
    con cinco de seis filas; la sexta espera `bk_capital` (ola 2, B4).
12. **2026-11-02 · 62 · B8-01-0 (LISTO) incluye el último corte Publicado.** · `bk_publicado` es
    FALTA (depende de B6/CVM). · Igual que el anterior: la ficha técnica se dibuja sin esa línea.
13. **2026-11-02 · 62 · B9-01-0 (LISTO) sin columnas de capital.** · El propio esqueleto lo dice:
    «columnas de capital FALTA». · Agregarlas cuando exista `bk_capital`.
14. **2026-11-02 · 62 · B2-05-0 es DERIVAR con la serie incompleta.** · El esqueleto dice «un
    corte hoy; FALTA la serie»: la tarjeta es de un solo trimestre, pero la comparación histórica
    (y B8-07-0, que es FALTA) no se puede. · B8 (reclamos y tarifas históricos) tiene que traerla.
15. **2026-11-02 · 62 · B1-01-0: la línea de tasa neutral es FIJO «a confirmar por Pablo».** · El
    propio esqueleto dice que sin confirmación se omite. · No se escribió ninguna constante. ·
    Pablo confirma el valor y la fuente, o la tarjeta se queda sin esa línea.

## De la ola 2 (encargo 65, front)

16. **2026-11-02 · 65 · Tarjetas [banco] de las fichas siguen en preparación.** · `data/` está vacío,
    así que ninguna `armar` real existe todavía; solo `_prueba/` tiene datos. · Escribir las `armar`
    de B8 (F1) y de B6, B0 (F2) contra `bk_*` cuando el pipeline entregue las tablas.
17. **2026-11-02 · 65 · Selector de trimestre sin opciones reales.** · `fijarTrimestres()` existe,
    pero ninguna página lo llama porque no hay `bk_manifiesto` en `data/`. · Llamarlo desde
    `pagina.js` o desde cada página con los trimestres del panel.
18. **2026-11-02 · 65 · Óptica «Modelo de negocio» sin selector.** · La URL ya acepta `optica`
    (default `modelo`), pero la barra solo tiene banco, grupo y trimestre. · Decidir si la barra
    muestra también las ópticas (Tradicional vs Fintech, segmento, propiedad) del spec §5.
19. **2026-11-02 · 65 · Recorrido de presentación: orden B0 → B10.** · El spec §4 dice «B0 → B1 → …
    → B8». Se implementó el orden completo de `config.js` y las páginas sin láminas se saltan. ·
    Pablo confirma si el recorrido termina en B8 o llega hasta B10.
20. **2026-11-02 · 65 · Impresión en 1920 × 1080 px, no A4 apaisada.** · El spec §4 dice A4, pero
    la lámina está diseñada en 16:9 y no se re-maqueta. · Confirmar la hoja, o que el PDF se
    imprima con escala ajustada a A4 desde el navegador.
21. **2026-11-02 · 65 · Pantalla completa solo con gesto del usuario.** · La API de pantalla
    completa necesita un gesto; al cruzar de página con `→` se pierde y la presentación continúa en
    ventana. · Aceptar así o pedir el gesto al cruzar.
22. **2026-11-02 · 65 · Presentación en pantallas menores de 1024 px sin verificar.** · Dentro de la
    lámina el cuerpo conserva el ancho de 1824 px y el alto de cada tarjeta, así que las reglas de
    responsive (`max-width:1023px`) no aplican. · Verificar a 1 024 px y 390 px cuando haya datos.
23. **2026-11-02 · 65 · `montarPortada` (de `pagina.js`) es código muerto con la marca del macro.**
    · B0 usa `montar()`; `montarPortada()` todavía dice «MONITOR BRASIL». · Borrarlo en la próxima
    ola de `pagina.js` (hoy no afecta a ninguna página).
24. **2026-11-02 · 65 · Signo neutro en `percentiles` sin juicio de mejora.** · Un punto de signo
    `neutro` se pinta en gris (§5: neutro = tinta-3). · Confirmar con Pablo que es el color que
    quiere para cuenta de depósitos o cartera/PL.
25. **2026-11-02 · 65 · Unidades de `cascada_doble`.** · Las líneas se entregan en fracción (0,01 =
    1 pp) y la brecha se muestra en pp multiplicando por 100. · Que el `armar` de B6 entregue
    fracciones, no pp.
26. **2026-11-02 · 65 · `docs/dashboard_bancos/PENDIENTES.md` no se tocó.** · Estaba fuera de los
    archivos permitidos del encargo; los pendientes del worker quedan aquí. · El arquitecto copia
    las líneas 16 a 26 a ese archivo global.
27. **2026-11-02 · 65b · Lista de bancos desde `bk_banco` solo con declaración manual.** · `estado.js` usa
    `data/bk_banco.json` cuando `TABLAS_EXPORTADAS` (config.js) lo incluye; no lo detecta solo, porque un
    `fetch` a un archivo que no existe deja un 404 en la consola y rompe el criterio 1. · El exportador
    de bk_banco agrega `'bk_banco'` a esa lista (una línea) al publicar la tabla.
28. **2026-11-02 · 65b · Titular con banco activo solo en la ficha.** · `pagina.js` lo aplica a B8 (`TITULAR_BANCO`);
    las páginas con `usaBanco` (B2 a B7, B9) conservan su título. · Decidir si también cambian.

