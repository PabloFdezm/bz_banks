@echo off
rem Publica el sitio en Cloudflare Pages (produccion: https://banks-bz.pages.dev).
rem   publicar.bat         publica lo que hay en sitio\ (paginas + data)
rem   publicar.bat datos   antes corre actualizar.bat (gold + JSON)
rem Requisito (una vez): Node.js y "npx wrangler login".
setlocal
cd /d "%~dp0"
set "PROYECTO=banks-bz"
if /i "%~1"=="datos" (call actualizar.bat || goto error)
echo [0/3] Construyendo el sitio v2 (hojas del canvas)...
python -X utf8 herramientas\construir_v2.py || goto error
echo [1/3] Copiando el sitio...
robocopy "sitio" "deploy_web" /MIR /XJ /XD data /NFL /NDL /NJH /NJS /NP
if %ERRORLEVEL% GEQ 8 goto error
echo [2/3] Copiando los datos...
robocopy "sitio\data" "deploy_web\data" /MIR /XF *.bak* /NFL /NDL /NJH /NJS /NP
if %ERRORLEVEL% GEQ 8 goto error
echo [3/3] Subiendo a Cloudflare Pages...
call npx -y wrangler@4.158.0 pages deploy deploy_web --project-name %PROYECTO% --branch main --commit-dirty=true
if errorlevel 1 goto error
echo.
echo Listo: https://banks-bz.pages.dev (recarga con Ctrl+F5).
pause
exit /b 0
:error
echo.
echo ERROR: no se pudo publicar. Revisa el mensaje de arriba.
pause
exit /b 1
