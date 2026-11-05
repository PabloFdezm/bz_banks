# 07 · Operación

Todos los comandos desde PowerShell en Windows; la raíz es `C:\Users\pablo\OneDrive\Documentos\bz_banks`.
Siempre `python -X utf8` (los textos tienen tildes y la consola de Windows no es UTF-8 por defecto).

## Instalación (una vez)

```powershell
Set-Location "C:\Users\pablo\OneDrive\Documentos\bz_banks"
python -m pip install -r requirements.txt
python -m playwright install chromium
npm install -g netlify-cli
netlify login
```

## Actualizar datos y publicar

```powershell
Set-Location "C:\Users\pablo\OneDrive\Documentos\bz_banks"
.\actualizar.bat      # gold + JSON (baja solo las series SGS que falten)
.\publicar.bat        # sitio\ → Netlify producción
.\publicar.bat datos  # las dos cosas seguidas
```

Trimestral, cuando el BCB publica un IF.Data nuevo (~60 días después del cierre):

```powershell
python -X utf8 pipeline\ifdata.py colectar --desde 201403 --hasta AAAAMM --escopo prudencial --informe 2 --informe 3 --informe 4
python -X utf8 pipeline\ifdata.py colectar --desde 201403 --hasta AAAAMM --escopo prudencial --informe 11 --informe 13
.\publicar.bat datos
```

(`ifdata.py` no vuelve a bajar lo que ya tiene con menos de `--max-edad-dias` (95), salvo `--refrescar`; ver `python -X utf8 pipeline\ifdata.py colectar -h`.)

## Netlify

- Sitio `banks-bz` (id `992a0e15-6b15-45ea-bc43-ddafa60032b4`), producción https://banks-bz.netlify.app.
- `publicar.bat` arma `deploy_netlify/` (copia espejo de `sitio/` sin `_prueba` ni `.netlify`, más
  `sitio/data`) y corre `netlify deploy --prod --dir deploy_netlify --site <id>`.
- Tras publicar, recargar con Ctrl+F5 la primera vez.
- El sitio lleva `noindex` (no aparece en buscadores) pero es público para quien tenga el link.

## Verificación

| Comando | Qué comprueba |
|---|---|
| `python -X utf8 herramientas\verificar_f1.py --puerto 8080` | Levanta un servidor, abre las 11 páginas (con y sin `?banco=itau`) en Chromium; HTTP 200, 0 errores de consola, conteo de secciones y tarjetas igual al esperado (`ESPERADO`), «en preparación» solo donde no hay `armar()`. `--captura DIR` guarda capturas. |
| `node herramientas\contar_tarjetas.mjs` | Tarjetas declaradas por página contra el esqueleto. |
| `python -X utf8 herramientas\verificar_gold.py --gold` | Estructura, períodos, crédito y validación del gold. |
| `python -m pytest -q` | 115 tests sobre el gold (manifiesto, contratos de columnas, reglas de quiebre, sumas). |
| `python -X utf8 herramientas\generar_spec.py` | Regenera `spec/generado/`. |

Al cambiar el número de tarjetas de una página, actualizar `ESPERADO` en `verificar_f1.py` y en
`contar_tarjetas.mjs`.

**Ojo con las capturas:** `verificar_f1.py` bloquea las fuentes de Google para no depender de la red, así
que las capturas usan una fuente de reemplazo más angosta. Para juzgar cómo se ve de verdad (cortes de
texto, anchos de tabla), revisar el sitio publicado con las fuentes reales y en varios anchos (1280, 1366,
1440, 1920 y ventanas angostas).

## Git

- Repo: https://github.com/PabloFdezm/bz_banks (rama `main`).
- `datos/`, `sitio/data/`, `deploy_netlify/` y `.netlify/` fuera de git.
- `.gitattributes`: LF en el repo, CRLF en los `.bat`.
- Commits en castellano; el código lo commitea Pablo desde Windows.
