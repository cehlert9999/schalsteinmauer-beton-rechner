#!/bin/bash
# Schalsteinmauer Betonrechner - Start Script (Linux/macOS)

echo "========================================"
echo " Schalsteinmauer Betonrechner"
echo "========================================"
echo ""

# Prüfe Python
echo "[1/4] Prüfe Python Installation..."
if ! command -v python3 &> /dev/null; then
    echo "[FEHLER] Python3 ist nicht installiert!"
    echo "Installieren Sie Python3 mit:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi
echo "      Python gefunden: $(python3 --version)"
echo ""

# Stoppe alte Prozesse
echo "[2/4] Stoppe alte Streamlit-Prozesse..."
pkill -f "streamlit run" 2>/dev/null
# Warte kurz
sleep 1

# Prüfe Port 8501
PORT_PID=$(lsof -ti:8501 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo "      Stoppe Prozess auf Port 8501 (PID: $PORT_PID)..."
    kill -9 $PORT_PID 2>/dev/null
    sleep 1
fi
echo "      Alte Prozesse gestoppt."
echo ""

# Prüfe Dependencies
echo "[3/4] Prüfe Dependencies..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "      Dependencies fehlen! Installiere jetzt..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[FEHLER] Installation fehlgeschlagen!"
        exit 1
    fi
    echo "      Installation erfolgreich!"
else
    echo "      Dependencies sind installiert."
fi
echo ""

# Starte Streamlit
echo "[4/4] Starte Server..."
echo ""
echo "========================================"
echo " Server startet..."
echo " Browser öffnet sich automatisch!"
echo ""
echo " Zum Stoppen: Drücken Sie CTRL+C"
echo " oder führen Sie ./stop.sh aus"
echo "========================================"
echo ""

python3 -m streamlit run app.py

# Falls beendet
echo ""
echo "Server wurde beendet."

