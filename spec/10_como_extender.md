# 10 · Cómo extender

## Agregar una tarjeta a una página existente

1. **Datos primero (Python).** Si la tarjeta necesita un cálculo nuevo, agregarlo al script de gold que
   corresponda (o crear `pipeline/preparar_gold_bancos_<tema>.py` con `main(argv) -> int`), publicar con
   `almacen.publicar_gold` (valida contra `definiciones/contrato_gold.json`: agregar ahí la tabla). Si es
   tabla descriptiva, usar `tabla_estandar.py`. Una métrica nueva del panel se declara en
   `definiciones/metricas_bancos.json`. Agregar el paso a `PASOS` de `pipeline/actualizar.py`, antes de
   «manifiesto».
2. Correr `python -X utf8 pipeline/actualizar.py --sin-red --desde <paso>`.
3. En `sitio/assets/js/paginas/bN.js`: agregar la clave a `filas` de la sección (respetando gráfico 4 +
   tabla 5) y la entrada en `tarjetas` con `componente`, `datos`, `armar`, `fuente`, `nota`, `estado`.
   `armar` solo filtra y da forma; sin dato devuelve `enPreparacion(motivo)` o `requiereBanco(motivo)`.
   Fuentes, grupos, rutas de partición e indicadores salen de `comun.js`; colores, de `tokens.js`; formatos y
   períodos, de `formato.js`; las piezas de series con tabla estándar, de `paginas/_series.js`. Solo
   módulos sin DOM (las herramientas de Node importan las configs).
4. Actualizar el conteo de la página en `herramientas/esqueleto_tarjetas.json`.
5. Verificar: `verificar_f1.py`, `contar_tarjetas.mjs`, `pytest`, y revisar en el sitio publicado con
   fuentes reales, en Presentar, a 1280 / 1440 / 1920 px.

## Agregar una página

1. Proponerla en un canvas y esperar aprobación de Pablo.
2. Registrar la página en `config.js` (`PAGINAS`: clave, ruta, nombre; `oculta: true` si aún no va al menú).
3. Crear `sitio/<ruta>/index.html` como copia exacta de cualquier otro (son todos iguales; Cloudflare Pages
   necesita la carpeta) y `sitio/assets/js/paginas/bN.js` (sin clave, ruta ni nombre).
4. Agregar su conteo a `herramientas/esqueleto_tarjetas.json`. `verificar_f1.py` y `contar_tarjetas.mjs` leen
   las páginas de `config.js`.
5. Si tiene banco, `usaBanco: true` y tarjetas con `banco: true`; si no, `usaBanco: false`.

## Agregar una serie SGS

- Agregar `nombre: código` a `CODIGOS` en `pipeline/sgs.py` (validar antes el código contra el catálogo del
  SGS: una serie inexistente llega como HTML, no como 404). El paso «sgs» de `actualizar.py` la baja con las
  demás a `crudo/bcb_sgs/bancos_sistema/`.
- Leerla con `sgs.serie(sgs.CODIGOS["nombre"])` (o `sgs.serie_mensual` para índice mensual continuo). Si es una
  serie de sistema para el sitio, agregarla a `preparar_gold_bancos_sistema.py` y leerla de `bk_sistema_m/q`.

## Agregar un componente

- Función `nombre(cont, e, { titulo })` en `charts_bancos.js` y su descriptor en `COMPONENTES`:
  `{ dibujar: nombre, entrada: [claves que lee], descripcion }` (`generar_spec.py` los publica). Si es ECharts,
  crear con `iniciar(cont)`, partir la opción de `tema()`, `tooltip()` y `ejeBase()` (charts.js) y devolver la
  instancia. Si es HTML, devolver `null` y ocuparse de su accesibilidad (`cajaDesplazable` para tablas).
  Formatos con las unidades de `formato.js`; colores por categoría en la entrada, no importados. Colores de `C` / `COLOR`; un color nuevo va en `tokens.js` y en
  `tokens.css` con el mismo valor (`verificar_f1.py` lo comprueba).
- Probar en Presentar: la letra se escala ×1,5 recorriendo `fontSize` de la opción; usar `fontSize`
  numérico, no cadenas.

## Después de cualquier cambio

```powershell
python -X utf8 herramientas\generar_spec.py   # mantener spec/generado al día
```
