# 07 · Operación

Todos los comandos desde PowerShell en Windows; la raíz es `C:\dev\bz_banks`.
Siempre `python -X utf8` (los textos tienen tildes y la consola de Windows no es UTF-8 por defecto).

## Instalación (una vez)

```powershell
Set-Location "C:\dev\bz_banks"
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.lock
.venv\Scripts\python -m playwright install chromium
npx wrangler login
powershell -ExecutionPolicy Bypass -File herramientas\registrar_tarea.ps1
```

`actualizar.bat` y `publicar.bat` usan `.venv\Scripts\python.exe` si existe (si no, el `python` del sistema).
`requirements.lock` fija las versiones exactas con las que corre el pipeline; `requirements.txt`, los rangos.
Para subir una versión: instalarla en `.venv`, correr `actualizar.bat` completo y regenerar el lock con
`.venv\Scripts\python -m pip freeze`.

El repo vivió en OneDrive hasta el 8-nov-2026. Se sacó porque OneDrive bloquea archivos mientras sincroniza
(el pipeline escribe por temporal + rename), puede corromper `.git` y sincronizaba 2 GB de datos que se pueden
volver a bajar. `referencias/` (reportes de terceros, no se pueden volver a bajar) conviene respaldarla aparte.

## Actualizar datos y publicar

```powershell
Set-Location "C:\dev\bz_banks"
.\actualizar.bat      # baja SGS y el ZIP SCR del año, recalcula, verifica (pytest + verificar_gold) y exporta
.\actualizar.bat --sin-red   # lo mismo sin descargas (un dato que falte hace fallar el paso)
.\publicar.bat        # sitio\ → Cloudflare Pages producción
.\publicar.bat datos  # las dos cosas seguidas
.\publicar.bat datos auto   # igual, sin pausas (lo usa la tarea programada)
```

## Actualización automática

- Tarea programada de Windows **«bz_banks actualizar»**, lunes a viernes 07:30 (si el equipo estaba apagado,
  corre apenas puede). La registra `herramientas\registrar_tarea.ps1` (`-Hora HH:MM` para cambiarla); hay que
  volver a registrarla si el repo cambia de carpeta.
- Corre `herramientas\actualizar_y_publicar.ps1` → `publicar.bat datos auto`. Log por corrida en
  `datos\logs\AAAA-MM-DD_HHMM.log` (guarda los últimos 60).
- Si un paso falla no se publica nada (actualizar.bat corta antes de exportar), aparece una notificación de
  Windows y queda `datos\logs\ULTIMO_ERROR.txt` hasta la siguiente corrida buena.
- IF.Data sigue siendo manual y trimestral (abajo).
- CI: `.github/workflows/tests.yml` corre `pytest` en GitHub en cada push con las versiones del lock (sin
  `datos/`: solo las pruebas unitarias; las de integración corren aquí en `actualizar.bat`).

Trimestral, cuando el BCB publica un IF.Data nuevo (~60 días después del cierre):

```powershell
python -X utf8 pipeline\ifdata.py colectar --desde 201403 --hasta AAAAMM --escopo prudencial --informe 2 --informe 3 --informe 4
python -X utf8 pipeline\ifdata.py colectar --desde 201403 --hasta AAAAMM --escopo prudencial --informe 11 --informe 13
.\publicar.bat datos
```

(`ifdata.py` no vuelve a bajar lo que ya tiene con menos de `--max-edad-dias` (95), salvo `--refrescar`; ver `python -X utf8 pipeline\ifdata.py colectar -h`.)

## Cloudflare Pages

- Proyecto `banks-bz` (creado el 6-nov; Pages clásico, no Workers), producción https://banks-bz.pages.dev.
  Netlify (`banks-bz.netlify.app`) quedó en desuso y ya no se actualiza.
- `publicar.bat` arma `deploy_web/` (copia espejo de `sitio/`, más `sitio/data`) y corre
  `npx wrangler@4.158.0 pages deploy deploy_web --project-name banks-bz --branch main`.
- Límites de Pages: 20.000 archivos y 25 MB por archivo (hoy 253 archivos, ninguno cerca).
- Tras publicar, recargar con Ctrl+F5 la primera vez.
- El sitio lleva `noindex` (no aparece en buscadores) pero es público para quien tenga el link.

## Verificación

| Comando | Qué comprueba |
|---|---|
| `python -X utf8 herramientas\verificar_f1.py --puerto 8080` | Levanta un servidor, abre las páginas de `config.js` (con y sin `?banco=itau`) en Chromium; HTTP 200, 0 errores de consola, conteo de secciones y tarjetas igual al de `herramientas/esqueleto_tarjetas.json`, «en preparación» solo donde no hay `armar()`. `--captura DIR` guarda capturas. |
| `python -X utf8 herramientas\verificar_f1.py --url https://banks-bz.pages.dev --anchos 1920,1280,390` | Lo mismo sobre el sitio publicado, con las fuentes reales (reporta cuáles cargaron) y sin scroll horizontal en cada ancho. Es la verificación después de publicar. |
| `node herramientas\contar_tarjetas.mjs` | Tarjetas declaradas por página contra el esqueleto. |
| `python -X utf8 herramientas\verificar_gold.py` | Intermedio (`metricas_bancos`, `cre_panorama`, `cre_calidad`): estructura, períodos y validación contra los informes. `--comparar <parquet>` contrasta un candidato. |
| `python -X utf8 herramientas\verificar_gold.py --gold` | Tablas gold `bk_*`: columnas y clave según `definiciones/contrato_gold.json`, fechas, licencias y las reglas de cada tabla (sumas de grupo, árbol ROE, cartera, SCR, manifiesto). |
| `python -m pytest -q` | Tests del verificador y del gold. Los marcados `integracion` leen `datos/` y se omiten si no está. |
| `python -X utf8 herramientas\generar_spec.py` | Regenera `spec/generado/`. |

Al cambiar el número de tarjetas de una página, actualizar `herramientas/esqueleto_tarjetas.json` (lo leen
`verificar_f1.py` y `contar_tarjetas.mjs`).

**Ojo con las capturas:** `verificar_f1.py` bloquea las fuentes de Google para no depender de la red, así
que las capturas usan una fuente de reemplazo más angosta. Para juzgar cómo se ve de verdad (cortes de
texto, anchos de tabla), revisar el sitio publicado con las fuentes reales y en varios anchos (1280, 1366,
1440, 1920 y ventanas angostas), o con `--url` (ver la tabla de arriba).

## Git

- Repo: https://github.com/PabloFdezm/bz_banks (rama `main`).
- `datos/`, `sitio/data/`, `deploy_web/` y `.wrangler/` fuera de git.
- `.gitattributes`: LF en el repo, CRLF en los `.bat`.
- Commits en castellano; el código lo commitea Pablo desde Windows.
