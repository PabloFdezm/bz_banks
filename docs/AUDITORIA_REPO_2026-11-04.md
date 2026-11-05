# Auditoría del repo bz_banks — 4-nov-2026

Revisión general del repositorio: código, datos, tests, sitio y proceso. Hecha con una pasada
completa: lectura de `spec/` y del pipeline, corrida de los tests, verificación de integridad del
crudo y verificación del sitio en Chromium. Todo lo que se afirma abajo se comprobó el mismo día;
los comandos para reproducir cada chequeo van al final.

## Veredicto

Proyecto sólidamente engineered. Documentación excepcional (`spec/` narrativa + inventario
autogenerado), disciplina de datos seria (crudo inmutable con manifiestos sha256, escrituras
atómicas, capas crudo→intermedio→gold), reglas del negocio blindadas en código y verificaciones
reales contra el sitio montado. Se encontró **1 problema grave, 3 medios y 4 menores**, ninguno de
datos incorrectos publicado: el gold en disco está íntegro y el sitio pasa todas las verificaciones.

## Qué se comprobó (y pasó)

| Chequeo | Resultado |
|---|---|
| `pytest` (115 tests) | **113 OK, 2 fallan** — por pandas 3 (ver grave 1) |
| `python -X utf8 pipeline/almacen.py verificar` | `integridad OK` (sha256 de todo el crudo) |
| `herramientas/verificar_f1.py` (Chromium real) | 11 páginas × 2 estados (con y sin `?banco=itau`): 200, 0 errores de consola, conteos del esqueleto OK |
| Exportador vs. dato con licencia | Guardía activa: aborta si una columna contiene `px_`, `pbv`, `pe_`, `bbg`, `bloomberg`, `consenso`, `target` (`exportar_web_bancos.py:61`) |
| `bk_panel.parquet` en disco | 104.396 filas, 0 `valor` nulos, corte 2026-06 (el gold actual está bien; el riesgo es la *próxima* corrida, ver grave 1) |
| Seguridad/higiene del sitio | `noindex` en HTML + `_headers` + `netlify.toml`, `nosniff`, referrer-policy; ECharts vendorizado (sin CDN); sin secretos en el repo |
| Git | `datos/` (5,5 GB), `sitio/data/`, `deploy_netlify/`, `.netlify/` correctamente ignorados; `.gitattributes` con LF en repo / CRLF en `.bat` |
| Frescura de datos | `bk_panel` 2026-06 · `bk_sistema_m` 2026-09 · `bk_scr` 2026-08 · manifiesto del sitio 2026-11-04 19:46 |

Fortalezas de diseño que conviene conservar:

- El crudo no se edita nunca; si un parser falla, se arregla el parser (regla 2 de datos, cumplida).
- Quiebres conocidos (COSIF 2025-03, Res. 4.966, 2024-T4 anómalo) respetados, no suavizados.
- La spec manda: si la narrativa y `spec/generado/` chocan, gana `generado/` (sale del código).
- Verificación del sitio contra un servidor propio con PID propio (no usa uno que ya corría).

---

## Grave

### G1 · pandas 3 rompe tests y —peor— regeneraría el gold con filas nulas

`requirements.txt` exige `pandas>=2.0`, sin tope: permite pandas 3. El equipo de trabajo corre
**Python 3.14.3 + pandas 3.0.1**. Consecuencias comprobadas:

1. **2 tests fallan ya mismo** (`tests/test_gold_bancos_78d.py`):
   - L149 `Q._cambios(wide, set()).stack(dropna=False)` → `ValueError`: `dropna` fue eliminado
     del nuevo `stack` de pandas 3.
   - L133 `sin["sentido"] is None` → falla porque con la nueva inferencia de dtypes llega `NaN`
     (`float`) en vez de `None`.
2. **El riesgo mayor es silencioso** y ya está documentado como pendiente 3b de `spec/08`:
   con pandas 3, `bk_panel` sale con 134.300 filas, incluidas ~29.900 con `valor` nulo
   (con pandas 2.3: 104.396, idénticas entre equipos en las comunes). El gold del disco hoy tiene
   104.396 filas y 0 nulos, pero **la próxima corrida de `actualizar.bat` en este equipo lo
   regeneraría distinto y lo exportaría al sitio sin avisar**.

Arreglo mínimo inmediato: `pip install "pandas<3"` y poner el tope en `requirements.txt`
(`pandas>=2.2,<3`). Arreglo de fondo (cuando toque): adaptar `preparar_gold_bancos.py` (filtrar
nulos explícitamente, como sugiere el propio pendiente 3b) y los dos tests.

## Medios

### M1 · Migración crudo→parquet terminada pero sin commitear

7 archivos modificados (`almacen.py`, `ifdata.py`, `preparar_bancos_powerbi.py`,
`preparar_credito_paginas_powerbi.py`, `preparar_gold_bancos_portada.py`, `spec/03`, `spec/08`)
y 2 sin trackear (`herramientas/comparar_gold.py`, `herramientas/convertir_crudo_parquet.py`).
El trabajo (3,5 GB → 62 MB, recodificación sin pérdida verificada celda a celda, manifiesto con
sha256 del CSV original y del parquet) existe solo en el working tree: un `git checkout .` lo
pierde. Detalle a limpiar antes del commit: quedaron andamios `if True:` en `pipeline/ifdata.py`
(L440 y L524), envoltorios del refactor que ya no aportan nada.

### M2 · Los CSV originales siguen en disco junto a los parquet

`datos/crudo/bcb_ifdata/valores/actual/`: 326 CSV + 326 parquet conviviendo (~3,3 GB + 62 MB);
`cadastro/` igual (52 MB). Es exactamente el pendiente 3 de `spec/08` («falta borrar los CSV
originales, con permiso de Pablo»). Borrarlos libera ~3,2 GB de los 5,5 GB de `datos/`. El
manifiesto conserva sha256 y URL del CSV original, así que la trazabilidad no se pierde.

### M3 · Lo publicado está desactualizado respecto a `sitio/`

`deploy_netlify/` (copia de la última publicación) difiere de `sitio/` en `assets/css/tokens.css`
y `assets/js/charts_bancos.js`: hay cambios locales nunca publicados. Si es intencional, ok; si
no, correr `publicar.bat`.

## Menores

1. `Cache-Control: no-cache` para `/assets/*` (`_headers`, `netlify.toml`): `echarts.min.js`
   se re-baja en cada visita. Con nombres de archivo hasheados se podría usar
   `max-age=31536000, immutable`.
2. Los tests contra datos reales (`skipif` sin `bk_panel`) dependen del disco local: razonable
   para un repo personal, pero es la razón por la que CI (pendiente 7) no es directo.
3. `almacen.glob_crudo`: la línea con el condicional en una sola expresión es difícil de leer.
4. `verificar_f0.py` sigue mencionado como obsoleto en `spec/08` (riesgos técnicos) pero ya no
   existe en el repo; la línea podría borrarse. *(Ya está fuera de git; solo la referencia en la
   spec quedó vieja.)*

---

## Acciones recomendadas (en orden)

1. **Hoy:** `pip install "pandas<3"` + tope `pandas>=2.2,<3` en `requirements.txt` (desactiva la
   trampa del gold corrupto).
2. Arreglar los 2 tests de `test_gold_bancos_78d.py`: `.stack()` a secas (el stack nuevo no
   introduce NA) y `pd.isna(sin["sentido"])` en vez de `is None`.
3. Limpiar los `if True:` de `ifdata.py` y commitear la migración parquet + las 2 herramientas
   nuevas (cierra M1).
4. Decidir el borrado de los 326 CSV + cadastro (cierra M2; libera ~3,2 GB).
5. Publicar si los cambios de CSS/JS deben estar en producción (cierra M3).
6. Después: pendiente 3b de `spec/08` como corresponde (pandas 3 o filtrado explícito), y CI.

## Cómo reproducir los chequeos

```powershell
python -X utf8 -m pytest -q                                   # 113 OK / 2 fallan (G1)
python -X utf8 pipeline/almacen.py verificar                  # integridad OK
python -X utf8 herramientas/verificar_f1.py                   # 11 páginas OK
python -c "import pandas; print(pandas.__version__)"          # 3.0.1 en este equipo
# filas del gold:
python -c "import pandas as pd; p = pd.read_parquet('datos/gold/bk_panel.parquet', columns=['valor']); print(len(p), p['valor'].isna().sum())"
# desfase publicado vs local:
diff -rq sitio deploy_netlify -x data -x .netlify
```
