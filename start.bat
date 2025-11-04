@echo off
REM Schalsteinmauer Betonrechner - Start Script
echo ========================================
echo  Schalsteinmauer Betonrechner
echo ========================================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH!
    echo Bitte installieren Sie Python von https://www.python.org
    pause
    exit /b 1
)

echo [1/4] Python gefunden: 
python --version
echo.

REM Stoppe eventuell laufende Streamlit-Prozesse
echo [2/4] Stoppe alte Streamlit-Prozesse...
taskkill /F /IM streamlit.exe >nul 2>&1
timeout /t 1 /nobreak >nul
echo      Alte Prozesse gestoppt.
echo.

REM Prüfe ob Dependencies installiert sind
echo [3/4] Pruefen der Dependencies...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo      Dependencies fehlen! Installiere jetzt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [FEHLER] Installation fehlgeschlagen!
        pause
        exit /b 1
    )
    echo      Installation erfolgreich!
) else (
    echo      Dependencies sind installiert.
)
echo.

REM Starte Streamlit
echo [4/4] Starte Server...
echo.
echo ========================================
echo  Server startet...
echo  Browser oeffnet sich automatisch!
echo  
echo  Zum Stoppen: Druecken Sie CTRL+C
echo  oder schliessen Sie dieses Fenster
echo ========================================
echo.

python -m streamlit run app.py

REM Falls Streamlit beendet wird
echo.
echo Server wurde beendet.
pause

