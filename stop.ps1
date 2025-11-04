# Schalsteinmauer Betonrechner - PowerShell Stop Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Stoppe Schalsteinmauer Betonrechner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stoppe Streamlit-Prozesse
Write-Host "Suche laufende Streamlit-Prozesse..." -ForegroundColor Yellow
$streamlitProcesses = Get-Process streamlit -ErrorAction SilentlyContinue

if ($streamlitProcesses) {
    Write-Host "Streamlit-Prozesse gefunden. Stoppe..." -ForegroundColor Yellow
    $streamlitProcesses | Stop-Process -Force
    Write-Host "[OK] Alle Streamlit-Prozesse wurden beendet." -ForegroundColor Green
} else {
    Write-Host "[INFO] Keine laufenden Streamlit-Prozesse gefunden." -ForegroundColor Gray
}

Write-Host ""

# Stoppe Prozesse auf Port 8501
Write-Host "Prüfe Port 8501..." -ForegroundColor Yellow
$port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue

if ($port8501) {
    $pid = $port8501.OwningProcess
    Write-Host "Prozess auf Port 8501 gefunden (PID: $pid). Stoppe..." -ForegroundColor Yellow
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Prozess auf Port 8501 wurde beendet." -ForegroundColor Green
} else {
    Write-Host "[INFO] Kein Prozess auf Port 8501 gefunden." -ForegroundColor Gray
}

Write-Host ""

# Stoppe Python-Prozesse die Streamlit ausführen
Write-Host "Suche Python-Prozesse mit Streamlit..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*streamlit*"
}

if ($pythonProcesses) {
    Write-Host "Python-Streamlit-Prozesse gefunden. Stoppe..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Write-Host "[OK] Python-Streamlit-Prozesse wurden beendet." -ForegroundColor Green
} else {
    Write-Host "[INFO] Keine Python-Streamlit-Prozesse gefunden." -ForegroundColor Gray
}

Write-Host ""
Write-Host "[FERTIG] Server gestoppt." -ForegroundColor Green
Write-Host ""
Read-Host "Drücken Sie Enter zum Schließen"

