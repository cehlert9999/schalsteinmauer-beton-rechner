@echo off
REM Schalsteinmauer Betonrechner - Stop Script
echo ========================================
echo  Stoppe Schalsteinmauer Betonrechner
echo ========================================
echo.

echo Suche laufende Streamlit-Prozesse...
tasklist /FI "IMAGENAME eq streamlit.exe" 2>NUL | find /I /N "streamlit.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Streamlit-Prozesse gefunden. Stoppe...
    taskkill /F /IM streamlit.exe
    echo.
    echo [OK] Alle Streamlit-Prozesse wurden beendet.
) else (
    echo [INFO] Keine laufenden Streamlit-Prozesse gefunden.
)

echo.
echo Suche Python-Prozesse mit Streamlit...
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
    netstat -ano | find "8501" | find "%%a" >nul
    if not errorlevel 1 (
        echo Beende Python-Prozess %%a auf Port 8501...
        taskkill /F /PID %%a
    )
)

echo.
echo [FERTIG] Server gestoppt.
echo.
pause


