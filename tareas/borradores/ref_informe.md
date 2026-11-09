# Fuente REF (Anexo Estatístico del BCB) → `bk_ref` — informe del 9-nov-2026

Frente 4 (`tareas/04_replica_ref.md`), punto «Construir 1»: la fuente `bcb_ref`. No toca páginas: la página Mora
sigue con sus réplicas propias y las tarjetas nuevas se definen con el rediseño.

**Resumen.**
- `bk_ref` tiene 303.953 puntos de 8 ediciones del REF (abr-23 a oct-26), entre 107 y 140 hojas con datos por
  edición.
- El xlsx es público y se baja solo con `pipeline/ref.py`. No hace falta pasar por `referencias/`, que queda
  reservada al PDF.
- Las dos réplicas que ya publica la página Mora calzan contra el dato del BCB:
  - 1.2.2.16: diferencia media de 0,01 a 0,08 pp por modalidad desde 2025;
  - 1.2.2.15: el total calza (0,03 pp); «mayor riesgo» se aparta hasta 1,7 pp porque la agrupación es nuestra.

## 1. Qué se hizo

| Capa | Qué hay | Dónde |
|---|---|---|
| Crudo | 8 xlsx con manifiesto (URL, sha256), uno por edición: 202304, 202310, 202404, 202410, 202504, 202510, 202605, 202610 | `datos/crudo/bcb_ref/anexo/<edicion>/` |
| Definición | URL, ediciones verificadas, meses candidatos para detectar la siguiente, y los gráficos usados con sus series esperadas | `definiciones/bcb_ref.json` |
| Gold | `bk_ref`: edición × hoja × serie × fila. Columnas `grafico`, `titulo`, `unidad`, `tipo` (serie o categorías), `fecha_ref` (texto «AAAA-MM» o «AAAA»), `categoria` y `valor` | `datos/gold/bk_ref.parquet`, en el contrato |
| Código | Lector genérico por hoja, descarga con sondeo de la edición siguiente, control de los gráficos usados | `pipeline/ref.py`; paso `ref` en `actualizar.py` (con `--descargar`) |
| Tests | 13 pruebas: hojas sintéticas con las formas reales, más integración (gráficos usados presentes, clave única, 1.2.2.16 contra el SCR propio) | `tests/test_ref.py` |
| Sitio | `bk_ref` **no se exporta**: todas las ediciones pesan 81 MB en JSON (12 MB solo la última). Cuando una página lo use, se exportan solo sus gráficos | `pipeline/exportar_web_bancos.py` (`EXCLUIDAS`) |

```powershell
Set-Location C:\dev\bz_banks
.venv\Scripts\python.exe -X utf8 pipeline\ref.py descargar   # baja lo que falte y avisa si hay edición nueva
.venv\Scripts\python.exe -X utf8 pipeline\ref.py gold        # lee todas las ediciones → bk_ref
```

## 2. Trampas del anexo

- **El mes de la edición varía.** No existen 2023-05, 2023-11 ni 2026-04 (la edición es 2026-05). Las ediciones
  van listadas en la definición, y `descargar` sondea los meses 03–06 o 09–12 del semestre siguiente.
- **Cada hoja tiene su forma.** El lector:
  - salta el título, «Fonte» y las notas, y toma la fila de unidad («%», «R$ bilhões»);
  - arrastra hacia la derecha el nivel superior del encabezado, que viene en celdas combinadas («Privado | S1»).
- **Fechas.**
  - Formatos: datetime, «2020-12», «Jun\n2023» seguido de «Jul», «Ago» sin año, y meses en inglés («Dec», «Feb»)
    en 1.2.1.3 y 1.4.1.
  - Hay años sueltos y proyecciones posteriores a hoy (estrés a 2029, brecha de crédito). Por eso la columna es
    `fecha_ref` (texto) y no `fecha`: la regla general del verificador las rechazaría.
- **Hojas sin eje temporal** (distribuciones por tramo de CRI, entidades del FGC, escenarios de estrés, tablas): van
  con `tipo = categorias`, y la primera columna en `categoria`, aunque sea numérica.
- **Celdas vacías a propósito** (el contrafactual de 1.2.2.21 solo existe en la proyección): no generan fila.
- **Sin leer en 202610**: 3 hojas. Son «Grafs 1.2.5.1 a 1.2.5.5» (escenarios con dos columnas de rótulos), Tab 2.2.1
  y Tab 2.6.1. En ediciones viejas, las cascadas de liquidez (1.2.1.12–14) pierden las filas por categoría. Ninguna se
  usa hoy.

## 3. Contraste con lo que ya publica el sitio (edición 202610)

| Gráfico | Serie | Diferencia media desde 2025 | Máxima (mes) | jun-26 REF / propio |
|---|---|---|---|---|
| 1.2.2.16 | Total PF | 0,04 pp | 0,24 (jun-25) | 9,23 / 9,22 |
| | Habitacional | 0,08 | 0,57 (jun-25) | 5,06 / 5,07 |
| | Consignado | 0,01 | 0,07 | 5,04 / 5,01 |
| | Vehículos | 0,02 | 0,08 | 8,48 / 8,46 |
| | No consignado | 0,01 | 0,05 | 14,88 / 14,91 |
| | Rural | 0,06 | 0,22 (ene-26) | 10,27 / 10,23 |
| | Tarjeta | 0,02 | 0,19 | 12,70 / 12,68 |
| 1.2.2.15 | Total | 0,03 (toda la serie) | 0,38 | 10,57 / 10,58 |
| | Menor riesgo | 0,12 | 0,45 | 10,80 / 10,96 |
| | Mayor riesgo | 0,46 | 1,68 (feb-19) | 10,04 / 9,65 |

Rentabilidad por segmento a jun-26, del SFN entero sin Master ni BRB, que el BCB excluye para comparar:

| Segmento | ROE (1.2.3.1) | Costo de provisiones (1.2.3.5) |
|---|---|---|
| SFN | 15,3 % | 4,3 % |
| S1 privados | 19,4 % | 3,9 % |
| Públicos | 10,4 % | 3,2 % |
| Demás IFs | 13,6 % | 4,4 % |
| Digitales | 28,8 % | 18,4 % |
| SNCC | 13,5 % | 4,2 % |

En la réplica del 6-nov, hecha con el panel de 34 bancos, los digitales daban ROE 24 contra ~29 y costo 13,2 contra
~18. Esa brecha era de universo, no de cálculo.

## 4. Decisiones que quedan para Pablo

1. **1.2.2.15 y 1.2.2.16 en la página Mora.** Hoy salen del SCR.data propio, que es mensual y llega a sep-26. El REF
   llega a jun-26 y se actualiza cada seis meses. Recomiendo:
   - seguir con lo propio, porque calza y tiene tres meses más;
   - usar el REF como control: el test de 1.2.2.16 ya lo hace;
   - para 1.2.2.15, si se quiere el «mayor riesgo» exacto del BCB, tomarlo del anexo o ajustar nuestra agrupación.
2. **ROE y provisiones por segmento (1.2.3.x).** El anexo trae el dato del SFN entero, sin la aproximación del panel.
   Recomiendo usar `bk_ref` para esas láminas y dejar el panel para la comparación banco por banco.
3. **Estrés para Capital (B7-03-1):** 1.2.5.6 a 1.2.5.13 están en `bk_ref`. Falta definir qué tarjeta se arma.
4. **Qué exportar al sitio:** cuando el rediseño defina las tarjetas REF, se exporta un `bk_ref_sitio` filtrado a
   esos gráficos y a la última edición.
