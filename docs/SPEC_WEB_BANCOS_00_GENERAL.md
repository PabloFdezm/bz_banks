# Dashboard Bancos Brasil · Spec del sitio web (00 · General)

Versión 0.2 · 3-nov-2026 (v0.1: 2-nov-2026). Diseño: Pablo (Principal AM) con Claude. Destinatario: el LLM o la persona que construye el sitio.

Lee este archivo entero antes de escribir código. Después trabaja una página a la vez con su sección de `ESQUELETO_BANCOS_v0.1.md`, que dice qué tarjetas lleva y de qué tabla sale cada una.

**Este sitio es hermano del Monitor Brasil.** Comparte el sistema de diseño, el stack y la anatomía de página del spec web del macro (`pb/pbip/diseno/paginas_desde_cero/web/SPEC_WEB_00_GENERAL.md`, en adelante «spec macro»). Todo lo que este archivo no dice, lo dice el spec macro, y se cumple igual. Este archivo solo agrega lo propio de bancos: banco activo, modo presentación, ficha, comparador y piezas nuevas.

---

## Cambios v0.2 (2026-11-03) — mandan sobre el resto de este archivo

1. **Impresión:** hoja 16:9 de 1920 × 1080 px (no A4), una lámina por hoja, con fuente y fecha al pie.
2. **Recorrido de presentación:** B0 → B10, saltando las páginas sin láminas.
3. **Qué tablas existen:** el sitio lee `data/_manifiesto.json`, que el exportador escribe siempre (aunque esté vacío). `TABLAS_EXPORTADAS` de `config.js` se retira cuando el exportador esté listo. La lista fija de bancos en `estado.js` queda solo como respaldo de `data/bk_banco.json`.
4. **Titular de la Ficha:** nombre del banco activo y rótulo «8 · FICHA · <GRUPO>».
5. **Prefijo «BCB ·»** para reclamos y tarifas. «Olinda» no aparece en pantalla.
6. **Módulos comunes:** copiados de `pb/pbip/diseno/paginas_desde_cero/qwen3.8-max/site/` como base provisoria (no aprobado aún por Pablo como versión vigente del macro).
7. **Página de prueba** `site/_prueba/` con datos ficticios: no publicable, fuera de los enlaces, con `X-Robots-Tag`.

## 0. Reglas de oro

Las nueve del spec macro (§0), con estos cambios:

1. **No inventes cifras, nunca.** Un número que no sale de `data/*.json` o de un FIJO del esqueleto no se publica. La tarjeta queda «en preparación» con el motivo.
2. **No hay diseño cerrado en HTML todavía.** A diferencia del macro, no existen maquetas `AMx_*.html`. La referencia visual es: (a) las piezas de la galería que cita el esqueleto (`pb/pbip/diseno/patrones/<ID>.html`), (b) la anatomía del spec macro §4 y (c) `ref/AM5_pagina.jpg` del macro como ejemplo de página terminada. **No diseñes piezas nuevas por tu cuenta**: las cuatro piezas nuevas del Anexo B del esqueleto se agregan primero a la galería y luego se construyen.
3. **Python calcula, el navegador dibuja.** El navegador filtra, ordena, re-basa, cambia de banco y de grupo. No calcula ratios, TTM, percentiles, agregados de grupo ni regresiones: todo eso viene hecho en las tablas `bk_*`. Si una tarjeta necesita un cálculo que no está, es FALTA y se anota en `PENDIENTES.md`.
4. **Nada interno a la vista.** Ni nombres de tablas (`bk_cartera`), ni claves de tarjeta (`B8-02-0`), ni rutas. En el pie va la fuente pública: «BCB, IF.Data (conglomerado prudencial)», «BCB, SGS», «BCB, SCR.data», «CVM», «BCB, Relatório de Estabilidade Financeira», y «cálculo propio» cuando corresponda.
5. **Bloomberg nunca entra al sitio.** Ningún JSON de `data/` puede contener precios, múltiplos ni estimaciones de Bloomberg u otros proveedores con licencia. El verificador lo comprueba (§9).
6. **Si no puedes hacer algo, no lo simules.** Anótalo en `PENDIENTES.md` y sigue.

---

## 1. Qué se construye

| URL | Página | Esqueleto |
|---|---|---|
| `/` | B0 Portada | §B0 |
| `/ciclo/` | B1 Ciclo y condiciones | §B1 |
| `/competencia/` | B2 Estructura y competencia | §B2 |
| `/credito/` | B3 Crédito | §B3 |
| `/calidad/` | B4 Calidad | §B4 |
| `/fondeo/` | B5 Fondeo y liquidez | §B5 |
| `/rentabilidad/` | B6 Rentabilidad | §B6 |
| `/capital/` | B7 Capital | §B7 |
| `/ficha/` | B8 Ficha por banco (`?banco=<slug>`) | §B8 |
| `/comparador/` | B9 Comparador | §B9 |
| `/metodologia/` | B10 Metodología y fuentes | §B10 |

Stack (igual que el macro): HTML + CSS + JS sin frameworks ni bundler, módulos ES nativos, **ECharts 5.5.1** local en `assets/vendor/echarts.min.js` con renderizador SVG, datos en JSON ya exportados. Idioma español, formatos es-CL. Nada se carga de internet.

---

## 2. Estructura de carpetas

```
sitio_bancos/
  site/
    index.html  ciclo/  competencia/  credito/  calidad/  fondeo/  rentabilidad/  capital/
    ficha/  comparador/  metodologia/   (cada una con index.html casi vacío, como el macro)
    assets/
      css/tokens.css        ← copia del macro; no editar
      css/monitor.css       ← copia del macro + bancos.css
      css/bancos.css        ← solo lo nuevo: barra de banco activo, modo presentación, comparador, percentiles
      js/datos.js  js/formato.js  js/charts.js  js/pagina.js   ← los del macro (copiar, no bifurcar sin motivo)
      js/estado.js          ← NUEVO: banco activo y grupo (§3)
      js/presentacion.js    ← NUEVO: modo presentación (§4)
      js/charts_bancos.js   ← NUEVO: componentes de §6
      js/paginas/b0.js … b10.js
      js/derivados/          ← vacío por diseño; si algo cae aquí, es una tabla que falta en Python
      vendor/echarts.min.js
    contenido/textos.json   ← solo titular e intro fijos por página; sin lecturas del analista (supuesto S3)
    data/*.json             ← lo escribe exportar_web_bancos.py; no editar a mano
    netlify.toml  _headers  404.html
  PENDIENTES.md  BITACORA.md  RESULTADOS.md
```

Si en algún momento los dos sitios se publican juntos, `charts.js`, `formato.js` y `datos.js` pasan a una carpeta común. Por ahora se copian para no acoplar las dos publicaciones.

La config de cada página tiene la misma forma que en el macro (spec macro §3), con dos campos nuevos:

```js
export default {
  clave: 'B6', ruta: 'rentabilidad', nombre: 'Rentabilidad', rotulo: '6 · RENTABILIDAD',
  signo: 'bancos',                       // un solo sentido de signo para todo el sitio (§5)
  ultimoDato: {tabla: 'bk_manifiesto', universo: 'panel'},
  usaBanco: true,                        // NUEVO: la página reacciona al banco activo
  optica: 'Modelo de negocio',           // NUEVO: óptica por defecto de los selectores de grupo
  secciones: [ … ],                      // igual que el macro
  tarjetas: {
    'B6-03-0': { titulo: 'ROE vs. costo del riesgo, por banco', sub: 'Panel IF.Data · TTM · 8 trimestres',
                 fuente: 'BCB, IF.Data (conglomerado prudencial); cálculo propio',
                 componente: 'burbujas_trayectoria', datos: ['bk_panel'], banco: true,
                 armar: (d, estado) => ({ … }) },   // NUEVO: armar recibe el estado (banco, grupo)
  },
};
```

---

## 3. Banco activo y grupo (`estado.js`)

Un solo estado para todo el sitio:

```js
{ banco: 'itau' | null, optica: 'Modelo de negocio', grupo: 'Grandes' | null, trimestre: '202606' }
```

- **Fuente de verdad: la URL.** `?banco=itau&optica=modelo&grupo=Grandes&t=202606`. Al cambiar de página, los enlaces de la cabecera conservan los parámetros. Un link copiado abre exactamente la misma vista. Sin parámetros: banco nulo, óptica Modelo de negocio y el último trimestre del panel.
- **Barra de banco activo** bajo la cabecera, de 48 px y fija al hacer scroll: selector de banco (lista agrupada por modelo, con buscador), selector de grupo de comparación, selector de trimestre y botón «Quitar banco». Con banco activo muestra su nombre en navy y su grupo.
- **Al elegir un banco**, por defecto `grupo = modelo del banco` (se puede cambiar).
- **Tarjetas [banco]:** se re-dibujan con `estado` (solo filtran y resaltan, no recalculan). Resaltado: el banco en navy y grosor 2,5; el resto de los bancos en `--acero-claro`; la mediana del grupo como línea discontinua `--texto-2`. En barras: la barra del banco en navy, el resto en acero claro. En tablas: fila del banco con fondo `--fondo` y texto 600.
- **Tarjetas sin banco:** no cambian.
- Se puede guardar el último banco en `localStorage` como comodidad, siempre dentro de `try/catch`. Pero la URL manda: si trae `banco`, ese gana.

---

## 4. Modo presentación (`presentacion.js`)

Es la razón principal de partir en HTML: el sitio funciona como presentación sin exportar nada.

- **Entrar:** tecla `P` o botón «Presentar» en la cabecera. **Salir:** `Esc`.
- **Unidad:** cada sección de la página es una lámina. La lámina ocupa la pantalla completa (Fullscreen API) en 16:9 con márgenes de 48 px: arriba el nombre de la sección (32 px, 300, navy) y la pregunta (18 px); debajo, el cuerpo de la sección escalado para caber (`transform: scale`, sin re-maquetar). El riel pasa a una franja inferior de 64 px con el KPI o el dato de la sección. La cabecera y la barra de banco se ocultan; el banco activo se muestra como un rótulo pequeño arriba a la derecha.
- **Navegación:** `→` / `Espacio` lámina siguiente; `←` anterior; `Inicio` / `Fin`; un número + `Enter` salta a la sección. Al final de una página, `→` pasa a la primera lámina de la página siguiente del recorrido (B0 → B1 → … → B8), con el mismo estado.
- **Tooltips:** activos con el mouse. Sin animaciones de transición.
- **URL:** `#presentar=s03` para abrir directo en una lámina.
- **Imprimir** (`Ctrl+P`) con `@media print`: una lámina por hoja A4 apaisada, con fuente y fecha de corte al pie de cada hoja. Así el PDF que queda para los PM es la misma presentación.

---

## 5. Sistema de diseño

Tokens, tarjeta, tipografía, responsive y reglas de color: spec macro §5. Lo propio de bancos:

- **Signo único** (`signo: 'bancos'`): el sentido de mejora sale de `bk_metrica.signo` y no de la página. `mejora_sube` → ▲ navy; `mejora_baja` → ▲ cobre-texto; `neutro` → gris tinta-3. Una página puede mezclar métricas de sentidos distintos (B8 lo hace), así que el color de cada cifra se decide por métrica.
- **Colores de categoría para grupos** (fijos en todo el sitio): Grandes = navy `#123864`, Digitales = petróleo `#2F7A86`, Medianos y nicho = acero `#6C819B`, Pagos = ciruela `#7B5E8C`, Desarrollo = acero claro `#A9B8CB`. Panel o total = tinta `#1B2433`. Nunca cobre ni arena para un grupo.
- **Muchos bancos en un gráfico:** nunca 34 colores. El banco activo en navy, los demás en acero claro, y opcionalmente los Grandes rotulados. Leyenda HTML solo con lo resaltado.
- **Quiebres** (esqueleto §0.7): línea vertical `--referencia` discontinua de 1 px con un rótulo de 11 px arriba («COSIF 2025», «Res. 4.966», «sin dato BCB»). 2024-T4 vacío se dibuja como hueco en la línea (`connectNulls: false`), nunca interpolado.
- **Universo en el subtítulo:** todo subtítulo empieza con «Panel IF.Data ·», «Sistema BCB ·», «SCR ·», «Publicado CVM ·», «REF ·» o «BCB ·» (este último solo para conducta: reclamos y tarifas). El término «Olinda» no aparece en pantalla: es el nombre de la API, no de la fuente.

---

## 6. Componentes

Todos los del spec macro §6 (`linea`, `columnas`, `barras_h`, `pesas`, `dispersion`, `burbujas`, `trayectoria`, `cascada`, `apilada_100`, `heatmap`, `mosaico_uf`, `small_multiples`, `tabla`, `kpi`, `escala`…), con la misma entrada y el mismo tema. Nuevos en `charts_bancos.js`:

| Componente | Entrada | Cómo |
|---|---|---|
| `percentiles` | `{filas:[{metrica, nombre, p10, p50, p90, valor, valor_t4, signo, formato}]}` | HTML/SVG, una fila de 40 px por métrica: nombre a la izquierda (13 px); barra gris `--regla` de p10 a p90; marca vertical `--texto-2` en p50; punto de 10 px del banco (navy si está del lado bueno de la mediana según `signo`, cobre-texto si no) y punto de 8 px acero claro en `valor_t4`, unidos por una línea fina; valor formateado a la derecha. Escala propia por fila (p10–p90 del grupo con 15 % de margen, incluyendo al banco) |
| `cascada_doble` | `{lineas:[{nombre, banco, grupo}], total:{nombre, banco, grupo}}` | Dos cascadas horizontales paralelas con las mismas líneas en el mismo orden: banco (navy/cobre por signo) y mediana del grupo (acero claro). Totales ROA y ROE como barras completas en `--acero`. Columna derecha con la brecha banco − grupo en pp, con signo y color |
| `burbujas_trayectoria` | `{puntos:[{banco, x, y, tamaño, grupo}], trayectorias:[{banco, puntos:[[x,y,trimestre]]}]}` | `burbujas` del macro; trayectoria (8 trimestres, línea 1,5 px + puntos de 4 px, «hoy» de 10 px) solo para el banco activo y, sin banco, para los Grandes |
| `small_multiples_bancos` | `{paneles:[{banco, puntos, destacado}], escala, columnas: 6}` | `small_multiples` del macro con el panel del banco activo con borde navy de 2 px; orden por tamaño del activo |
| `comparador` | `{columnas, filas, orden, filtros}` | Tabla HTML con cabecera fija; ordenar al hacer clic en la cabecera; filtros por modelo, segmento y propiedad (chips); sparkline SVG 80 × 18 en columnas marcadas; fila clicable → `/ficha/?banco=…`; botón «CSV» que baja exactamente las filas y columnas visibles |

---

## 7. Datos

- **Formato:** igual que el spec macro §7.1: `data/<tabla>.json` = `{tabla, columnas, filas}`. Fechas `AAAA-MM-DD`; períodos `AAAAMM`; unidad 0,05 = 5 %.
- **Partición por banco** para las tablas grandes: `bk_panel` y `bk_cartera` se exportan también partidas (`data/banco/<slug>/bk_panel.json`) para que la ficha cargue solo lo de un banco. Las páginas de sistema usan los archivos agregados.
- **Carga perezosa** por tarjeta con `IntersectionObserver` (spec macro §7.2).
- **Formatos:** spec macro §7.3. Montos de bancos en **R$ mil millones** con un decimal («R$ 2.846,4 mil millones»; en tablas, encabezado «R$ mil mm» y la cifra sola). Trimestres `2T26`.
- **Estados:** LISTO / DERIVAR / FALTA / REF / FIJO como en el esqueleto §0.9. Aquí DERIVAR significa que **la tabla `bk_*` todavía no está construida**: la tarjeta va «en preparación: dato en construcción» hasta que el pipeline la entregue. No se deriva en JavaScript.
- **Último dato:** cada sección muestra el último corte de *su* universo (de `bk_manifiesto`). La portada muestra los cinco.

---

## 8. Netlify

Igual que el spec macro §10 (`netlify.toml` con `X-Robots-Tag: noindex, nofollow`, caché de `data/` 1 h y de `assets/` 1 día; publicar `site/` sin build). Además:

- **Acceso:** el link no se comparte fuera del equipo hasta que Pablo decida el mecanismo (contraseña de Netlify según el plan disponible, o acceso corporativo delante). Mientras tanto, solo deploys de vista previa.
- **Nada con licencia** en `data/` (regla de oro 5).

---

## 9. Criterios de aceptación (por página)

Los doce del spec macro §12 (verificador automático, cero `[` visibles, toda cifra trazable, colores, ejes, formatos, consola limpia, responsive 1 920 / 1 440 / 1 024 / 390, Lighthouse ≥ 90, `PENDIENTES.md`, componentes implementados). Más:

13. **Banco activo:** con `?banco=itau`, `?banco=nubank` y sin banco, todas las tarjetas [banco] resaltan bien y ninguna otra cambia. Los enlaces de la cabecera conservan los parámetros.
14. **Modo presentación:** en 1 920 × 1 080 y en 1 366 × 768, cada sección cabe en su lámina sin scroll; las flechas recorren toda la página y pasan a la siguiente; `Esc` vuelve al mismo punto del scroll.
15. **Impresión:** `Ctrl+P` da una lámina por hoja con fuente y fecha al pie.
16. **Quiebres:** 2024-T4 aparece como hueco y los rótulos de COSIF 2025 y Res. 4.966 están en todas las series del panel que los cruzan.
17. **Licencias:** un script busca en `data/` columnas o valores con `px_`, `pe_`, `pbv`, `bbg`, `bloomberg`, `consenso` o `target` y falla si encuentra alguno.
18. **Universos:** ningún gráfico mezcla dos universos en el mismo eje; cada subtítulo empieza con su universo.

---

## 10. Orden de trabajo

| Fase | Entregable | Hecho cuando |
|---|---|---|
| F0 | Estructura de §2 con los módulos del macro copiados; `estado.js`, barra de banco activo; `presentacion.js` funcionando sobre una página vacía | Cabecera, barra, apertura y secciones vacías se ven como el macro; `P` abre láminas |
| F1 | **Ficha (B8)** con las tarjetas LISTO; las DERIVAR y FALTA «en preparación»; piezas `percentiles` y `cascada_doble` agregadas a la galería y construidas | Pablo revisa la ficha de Itaú, Nubank y Banrisul en pantalla y en modo presentación |
| F2 | **Rentabilidad (B6)** y **Portada (B0)** | Pasan §9 |
| F3 | B2, B3, B4, B5, B9 | Pasan §9 |
| F4 | B1, B7, B10 y deploy de vista previa en Netlify | Pablo revisa la URL |

El sitio se construye en paralelo con el pipeline (spec de datos §5). Una tarjeta pasa de «en preparación» a dato real cuando su tabla `bk_*` aparece en `data/`, sin tocar la config.

---

## 11. Power BI (después)

Nada del sitio debe impedir la réplica: Power BI va a leer los mismos `pb/Banks/bk_*.parquet`. Por eso ninguna cifra vive solo en JSON ni en JavaScript. Lo que **no** se replica: link profundo por banco, modo presentación tal cual (se aproxima con marcadores), `percentiles`, `cascada_doble` y `burbujas_trayectoria` (en Power BI requieren Deneb o un visual SVG por DAX).

---

## 12. Prompt sugerido para el LLM que construye

> Vas a construir el sitio estático «Bancos Brasil». Lee, en este orden: `docs/dashboard_bancos/SPEC_WEB_BANCOS_00_GENERAL.md` (entero), `pb/pbip/diseno/paginas_desde_cero/web/SPEC_WEB_00_GENERAL.md` (§3–§7 y §10–§12), y la sección de la página que te toca en `docs/dashboard_bancos/ESQUELETO_BANCOS_v0.1.md`. Las tablas están en `sitio_bancos/site/data/`; antes de usar una columna, confírmala en `data/_manifiesto.json`. No calcules nada financiero en JavaScript, no inventes cifras y no diseñes piezas nuevas. Todo lo que no puedas hacer va a `PENDIENTES.md`. Empieza por la fase F0 y detente al terminarla para revisión.
