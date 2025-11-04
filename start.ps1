# Schalsteinmauer Betonrechner - PowerShell Start Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Schalsteinmauer Betonrechner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Prüfe Python
Write-Host "[1/4] Prüfe Python Installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "      Python gefunden: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[FEHLER] Python nicht gefunden!" -ForegroundColor Red
    Write-Host "Bitte installieren Sie Python von https://www.python.org" -ForegroundColor Red
    Read-Host "Drücken Sie Enter zum Beenden"
    exit 1
}
Write-Host ""

# Stoppe alte Prozesse
Write-Host "[2/4] Stoppe alte Streamlit-Prozesse..." -ForegroundColor Yellow
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Prüfe auch Port 8501
$port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if ($port8501) {
    $pid = $port8501.OwningProcess
    Write-Host "      Stoppe Prozess auf Port 8501 (PID: $pid)..." -ForegroundColor Yellow
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}
Write-Host "      Alte Prozesse gestoppt." -ForegroundColor Green
Write-Host ""

# Prüfe Dependencies
Write-Host "[3/4] Prüfe Dependencies..." -ForegroundColor Yellow
$streamlitInstalled = python -c "import streamlit; print('OK')" 2>&1
if ($streamlitInstalled -notlike "*OK*") {
    Write-Host "      Streamlit nicht gefunden! Installiere Dependencies..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FEHLER] Installation fehlgeschlagen!" -ForegroundColor Red
        Write-Host "Versuchen Sie manuell: python -m pip install streamlit plotly pyyaml reportlab numpy" -ForegroundColor Yellow
        Read-Host "Drücken Sie Enter zum Beenden"
        exit 1
    }
    Write-Host "      Installation erfolgreich!" -ForegroundColor Green
} else {
    Write-Host "      Dependencies sind installiert." -ForegroundColor Green
}
Write-Host ""

# Starte Streamlit
Write-Host "[4/4] Starte Server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Server startet..." -ForegroundColor Green
Write-Host " Browser öffnet sich automatisch!" -ForegroundColor Green
Write-Host "" 
Write-Host " Zum Stoppen: Drücken Sie CTRL+C" -ForegroundColor Yellow
Write-Host " oder führen Sie stop.ps1 aus" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Starte Streamlit (mit python -m für bessere Kompatibilität)
python -m streamlit run app.py

# Falls beendet
Write-Host ""
Write-Host "Server wurde beendet." -ForegroundColor Yellow
Read-Host "Drücken Sie Enter zum Schließen"

