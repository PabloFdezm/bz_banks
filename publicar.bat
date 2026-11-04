@echo off
rem Publica el sitio en Netlify (produccion: https://banks-bz.netlify.app).
rem   publicar.bat         publica lo que hay en sitio\ (paginas + data)
rem   publicar.bat datos   antes corre actualizar.bat (gold + JSON)
rem Requisito (una vez): npm install -g netlify-cli y "netlify login".
setlocal
cd /d "%~dp0"
set "SITIO=992a0e15-6b15-45ea-bc43-ddafa60032b4"
if /i "%~1"=="datos" (call actualizar.bat || goto error)
echo [1/3] Copiando el sitio...
robocopy "sitio" "deploy_netlify" /MIR /XJ /XD data .netlify /NFL /NDL /NJH /NJS /NP
if %ERRORLEVEL% GEQ 8 goto error
echo [2/3] Copiando los datos...
robocopy "sitio\data" "deploy_netlify\data" /MIR /XF *.bak* /NFL /NDL /NJH /NJS /NP
if %ERRORLEVEL% GEQ 8 goto error
echo [3/3] Subiendo a Netlify...
call netlify deploy --prod --dir deploy_netlify --site %SITIO%
if errorlevel 1 goto error
echo.
echo Listo: https://banks-bz.netlify.app (recarga con Ctrl+F5).
pause
exit /b 0
:error
echo.
echo ERROR: no se pudo publicar. Revisa el mensaje de arriba.
pause
exit /b 1
