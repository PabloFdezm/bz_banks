# 10 · Cómo extender

## Agregar una tarjeta a una página existente

1. **Datos primero (Python).** Si la tarjeta necesita un cálculo nuevo, agregarlo al script de gold que
   corresponda (o crear `pipeline/preparar_gold_bancos_<tema>.py`), escribir con `almacen.guardar_derivado`
   + `escribir_atomico` en `datos/gold/bk_<tabla>.parquet`. Si es tabla descriptiva, usar el contrato de la
   tabla estándar (`04_modelo_de_datos.md`). Agregar el script a `actualizar.bat` **antes** del paso 8.
2. Correr el script, luego `preparar_gold_bancos.py base` y `exportar_web_bancos.py`.
3. En `sitio/assets/js/paginas/bN.js`: agregar la clave a `filas` de la sección (respetando gráfico 4 +
   tabla 5) y la entrada en `tarjetas` con `componente`, `datos`, `armar`, `fuente`, `nota`, `estado`.
   `armar` solo filtra y da forma. Sin `import`.
4. Actualizar `ESPERADO` en `herramientas/verificar_f1.py` y `herramientas/contar_tarjetas.mjs`.
5. Verificar: `verificar_f1.py`, `contar_tarjetas.mjs`, `pytest`, y revisar en el sitio publicado con
   fuentes reales, en Presentar, a 1280 / 1440 / 1920 px.

## Agregar una página

1. Proponerla en un canvas y esperar aprobación de Pablo.
2. Crear `sitio/<ruta>/index.html` (copiar uno existente y cambiar el import de la config).
3. Crear `sitio/assets/js/paginas/bN.js` y registrar la página en `config.js` (`PAGINAS`).
4. Agregar la página a `PAGINAS` y `ESPERADO` en `verificar_f1.py` y a `contar_tarjetas.mjs`.
5. Si tiene banco, `usaBanco` y tarjetas con `banco: true`; si no, `usaBanco: false`.

## Agregar una serie SGS

- En los scripts de gold, `serie(codigo)` (`preparar_gold_bancos_portada.py`) busca en cualquier dataset de
  `crudo/bcb_sgs` y si no está la baja con `preparar_gold_bancos_sistema.sgs(codigo, descargar=True)`.
- Documentar el código y su nombre (validado contra el catálogo del SGS) en `03_pipeline_de_datos.md`.

## Agregar un componente

- Función `nombre(cont, e)` en `charts_bancos.js`, con un comentario `/* ---------- nombre (tipo): qué
  dibuja ---------- */` encima (lo lee `generar_spec.py`). Si es ECharts, crear con
  `echarts.init(cont, null, { renderer: 'svg' })`, sin fijar familia de fuente distinta (la fija
  `pagina.js`) y devolver la instancia. Registrar en `COMPONENTES_BANCOS`. Si es HTML, agregar el nombre a la
  lista de componentes HTML en `pagina.js` (no llevan `role=img`).
- Probar en Presentar: la letra se escala ×1,5 recorriendo `fontSize` de la opción; usar `fontSize`
  numérico, no cadenas.

## Después de cualquier cambio

```powershell
python -X utf8 herramientas\generar_spec.py   # mantener spec/generado al día
```
