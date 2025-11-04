#!/bin/bash
# Schalsteinmauer Betonrechner - Stop Script (Linux/macOS)

echo "========================================"
echo " Stoppe Schalsteinmauer Betonrechner"
echo "========================================"
echo ""

# Stoppe Streamlit-Prozesse
echo "Suche laufende Streamlit-Prozesse..."
STREAMLIT_PIDS=$(pgrep -f "streamlit run")

if [ ! -z "$STREAMLIT_PIDS" ]; then
    echo "Streamlit-Prozesse gefunden. Stoppe..."
    pkill -9 -f "streamlit run"
    echo "[OK] Alle Streamlit-Prozesse wurden beendet."
else
    echo "[INFO] Keine laufenden Streamlit-Prozesse gefunden."
fi

echo ""

# Stoppe Prozesse auf Port 8501
echo "Prüfe Port 8501..."
PORT_PID=$(lsof -ti:8501 2>/dev/null)

if [ ! -z "$PORT_PID" ]; then
    echo "Prozess auf Port 8501 gefunden (PID: $PORT_PID). Stoppe..."
    kill -9 $PORT_PID 2>/dev/null
    echo "[OK] Prozess auf Port 8501 wurde beendet."
else
    echo "[INFO] Kein Prozess auf Port 8501 gefunden."
fi

echo ""
echo "[FERTIG] Server gestoppt."
echo ""


