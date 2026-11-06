@echo off
rem Recalcula el gold de bancos desde el crudo en datos\ y exporta los JSON del sitio.
rem No baja IF.Data (eso es trimestral, ver README); las series SGS que falten si se bajan.
setlocal
cd /d "%~dp0"
echo [1/9] Balances y resultados por banco (IF.Data)...
python -X utf8 pipeline\preparar_bancos_powerbi.py || goto error
echo [2/9] Metricas por banco...
python -X utf8 pipeline\preparar_metricas_bancos.py || goto error
echo [3/9] Credito por grupo (IF.Data + SGS)...
python -X utf8 pipeline\preparar_credito_paginas_powerbi.py --descargar || goto error
echo [4/9] Gold: sistema, cartera, base, rentabilidad, exposicion...
python -X utf8 pipeline\preparar_gold_bancos.py todo || goto error
echo [5/9] Cambios de cuota...
python -X utf8 pipeline\preparar_gold_bancos_qcambio.py || goto error
echo [6/9] Portada...
python -X utf8 pipeline\preparar_gold_bancos_portada.py || goto error
echo [7/9] Pagina Credito...
python -X utf8 pipeline\preparar_gold_bancos_pag_credito.py || goto error
echo [8/9] Personas y Mora (SCR.data por producto, renta y sector)...
python -X utf8 pipeline\preparar_gold_bancos_scr_productos.py --descargar || goto error
echo [9/9] Manifiesto del gold y JSON del sitio...
python -X utf8 pipeline\preparar_gold_bancos.py base || goto error
python -X utf8 pipeline\exportar_web_bancos.py || goto error
echo.
echo Datos al dia.
exit /b 0
:error
echo.
echo ERROR: fallo el paso anterior.
exit /b 1
