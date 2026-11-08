# Actualizacion desatendida: baja datos, recalcula el gold, verifica y publica (publicar.bat datos auto).
# La corre la tarea programada "bz_banks actualizar" (ver herramientas/registrar_tarea.ps1).
# - Log por corrida en datos/logs/AAAA-MM-DD_HHMM.log (se guardan los ultimos 60).
# - Si un paso falla, publicar.bat no sube nada (actualizar.bat corta antes de exportar) y se avisa con una
#   notificacion de Windows y con datos/logs/ULTIMO_ERROR.txt (se borra en la siguiente corrida buena).
# Uso manual: powershell -ExecutionPolicy Bypass -File herramientas\actualizar_y_publicar.ps1
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz
$logs = Join-Path $raiz 'datos\logs'
New-Item -ItemType Directory -Force $logs | Out-Null
$log = Join-Path $logs ((Get-Date -Format 'yyyy-MM-dd_HHmm') + '.log')
$marca = Join-Path $logs 'ULTIMO_ERROR.txt'

function Avisar([string]$titulo, [string]$texto) {
    try {
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $nodos = $xml.GetElementsByTagName('text')
        $nodos.Item(0).AppendChild($xml.CreateTextNode($titulo)) | Out-Null
        $nodos.Item(1).AppendChild($xml.CreateTextNode($texto)) | Out-Null
        $app = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app).Show([Windows.UI.Notifications.ToastNotification]::new($xml))
    } catch { }   # sin sesion interactiva no hay notificacion; queda ULTIMO_ERROR.txt
}

$inicio = Get-Date
"[$($inicio.ToString('s'))] inicio en $raiz" | Out-File $log -Encoding utf8
$env:PYTHONUTF8 = '1'
# cmd escribe el log directo: si PowerShell 5.1 recibe el stderr de un programa externo (el pipeline informa
# su avance por stderr), con ErrorActionPreference = Stop lo toma como error y corta el script.
cmd /c "publicar.bat datos auto >> `"$log`" 2>&1"
$codigo = $LASTEXITCODE
$fin = Get-Date
"[$($fin.ToString('s'))] fin, codigo $codigo, $([int]($fin - $inicio).TotalMinutes) min" | Out-File $log -Append -Encoding utf8

if ($codigo -ne 0) {
    "Fallo la actualizacion del $($inicio.ToString('s')) (codigo $codigo). Log: $log" | Out-File $marca -Encoding utf8
    Avisar 'bz_banks: fallo la actualizacion' "No se publico nada. Log: $log"
} elseif (Test-Path $marca) {
    Remove-Item $marca
}

Get-ChildItem $logs -Filter '*.log' | Sort-Object Name -Descending | Select-Object -Skip 60 | Remove-Item
exit $codigo
