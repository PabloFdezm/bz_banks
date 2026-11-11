# Frente 6 · Lista de limpieza (parte A hecha el 11-nov; parte B pendiente del visto bueno)

11-nov-2026. Cada línea dice qué es, cuánto pesa y por qué se puede borrar o por qué conviene dejarlo.

## A. Caché viejo del SCR en bz_banks (`datos/intermedio/scr_productos/`) — borrado el 11-nov con el visto bueno de Pablo
El cubo se guarda por versión de las reglas de `definiciones/scr_productos.json`; la vigente es la que usa el
pipeline hoy. Las otras dos son de reglas anteriores y nadie las lee.

| Carpeta | Peso | Fecha | Propuesta |
|---|---:|---|---|
| `45fa235300` | 21 MB | 10-nov | borrar (reglas anteriores al frente 13) |
| `e82fb46f9a` | 19 MB | 9-nov | borrar (reglas anteriores) |
| `6e094da528` | 21 MB | 11-nov | **dejar** (versión vigente) |

## B. Archivos de bancos que quedaron en el repo `Dashboard` (`C:\Users\pablo\OneDrive\Documentos\Dashboard`)
Ese repo sigue siendo el dashboard macro; los bancos se mudaron a bz_banks. Nada de esto se toca sin tu visto bueno,
y ojo: el repo Dashboard tiene cambios sin commit propios (borrados de notebooks, `.gitignore`), que no son míos.

| Archivo o carpeta | Peso | ¿Está en bz_banks? | Quién lo usa en Dashboard | Propuesta |
|---|---:|---|---|---|
| `preparar_bancos_powerbi.py` | 28 KB | sí (`pipeline/`) | `preparar_credito_paginas_powerbi.py` | borrar junto con el siguiente |
| `preparar_credito_paginas_powerbi.py` | 52 KB | sí (`pipeline/`) | nadie | borrar |
| `ifdata.py` | 36 KB | sí (`pipeline/`) | `diccionario_ifdata.py`; lo nombran `bajar_documentacion.py`, `exportar_trabajo.py` y `preparar_notebooklm_codigo.py` (listas de archivos) | borrar si esas listas se ajustan |
| `diccionario_ifdata.py` | 40 KB | sí (`pipeline/`) | nadie | borrar |
| `ifdata_diccionario.html` | 248 KB | no | `diccionario_ifdata.py` | borrar con el anterior |
| `ifdata_cache/` | 16 MB | no (bz_banks tiene su propio crudo) | `ifdata.py` | borrar |
| `capturas/` | vacía | — | — | borrar |
| `datos/crudo/bcb_ifdata/` | 3,3 GB | bz_banks tiene 64 MB (parquet); el de Dashboard es CSV viejo | `ifdata.py`, `preparar_bancos_powerbi.py` | borrar con los scripts (libera 3,3 GB) |
| `datos/derivado/bcb_ifdata/` | 163 MB | bz_banks tiene el suyo | los mismos | borrar con los scripts |
| `datos/crudo/bcb_scr/` | 1,9 GB | bz_banks tiene el suyo (2,0 GB) | **sí lo usan scripts macro** (`credito_garantizado.py`, `exportar_credito_pyme_empleo_excel.py`) | **dejar** |

Total que se libera con lo propuesto: ~3,5 GB (Dashboard) + 40 MB (bz_banks).

Para borrar, una vez aprobado (PowerShell):

```powershell
Set-Location C:\dev\bz_banks
Remove-Item -Recurse -Force datos\intermedio\scr_productos\45fa235300, datos\intermedio\scr_productos\e82fb46f9a
```

Lo del repo Dashboard conviene hacerlo con un commit en ese repo, después de ajustar las listas de
`bajar_documentacion.py`, `exportar_trabajo.py` y `preparar_notebooklm_codigo.py`.
