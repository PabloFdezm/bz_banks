@echo off
rem Recalcula el gold de bancos y exporta los JSON del sitio. Los pasos y su orden estan en pipeline\actualizar.py:
rem   sgs (baja todas las series del catalogo) - focus (IPCA esperado, API Olinda) - balances - metricas - credito - sistema - cartera - base -
rem   rentabilidad - exposicion - qcambio - portada - pag_credito - scr_productos (baja el ZIP del anio) -
rem   scr (con cache por ZIP) - manifiesto - verificacion (pytest + verificar_gold --gold) - exportar.
rem No baja IF.Data (eso es trimestral, ver README). Sin red: actualizar.bat --sin-red
rem Usa el entorno del repo (.venv, versiones de requirements.lock) si existe; si no, el python del sistema.
setlocal
cd /d "%~dp0"
set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
"%PY%" -X utf8 pipeline\actualizar.py %* || goto error
exit /b 0
:error
echo.
echo ERROR: fallo un paso; el sitio no se exporto.
exit /b 1
