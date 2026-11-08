# Registra (o actualiza) la tarea programada de Windows que corre herramientas\actualizar_y_publicar.ps1.
# Lunes a viernes a las 07:30, con la sesion del usuario iniciada (wrangler usa el login del usuario). Si el
# equipo estaba apagado a esa hora, corre apenas se pueda. Hay que volver a correrlo si el repo cambia de carpeta.
# Uso: powershell -ExecutionPolicy Bypass -File herramientas\registrar_tarea.ps1 [-Hora 07:30]
param([string]$Hora = '07:30')
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
$script = Join-Path $PSScriptRoot 'actualizar_y_publicar.ps1'
$accion = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`"" -WorkingDirectory $raiz
$disparo = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday -At $Hora
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'bz_banks actualizar' -Action $accion -Trigger $disparo -Settings $ajustes `
    -Description "Actualiza datos y publica banks-bz.pages.dev ($raiz)" -Force | Out-Null
Get-ScheduledTask -TaskName 'bz_banks actualizar' | Select-Object TaskName, State, @{n='Carpeta'; e={$raiz}}
