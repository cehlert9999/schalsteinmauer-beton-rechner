# 🚀 Schnellstart - Schalsteinmauer Betonrechner

Starten Sie in 3 Minuten!

## 📦 Installation

### Windows
```bash
# 1. Terminal öffnen (PowerShell oder CMD)
cd "C:\Users\cehle\Documents\python\schalsteinmauer beton rechner"

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Starten!
streamlit run app.py
```

### macOS/Linux
```bash
# 1. Terminal öffnen
cd "/pfad/zum/schalsteinmauer beton rechner"

# 2. Virtual Environment erstellen (optional aber empfohlen)
python3 -m venv venv
source venv/bin/activate

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Starten!
streamlit run app.py
```

## 🎯 Erste Schritte

### 1. Minimales Beispiel
Die App startet mit sinnvollen Standardwerten:
- **Länge**: 5 m
- **Höhe**: 1 m (ohne Gefälle)
- **Breite**: 36,5 cm
- **Stein**: Standard (Abmessung 1)

Klicken Sie einfach auf "Berechnen" und sehen Sie die Ergebnisse!

### 2. Eigene Mauer berechnen
1. **Sidebar öffnen** (falls geschlossen)
2. **Dimensionen eingeben**:
   - Länge in Metern
   - Höhen (Start = Ende für gerade Mauer)
   - Breite wird automatisch vorgeschlagen
3. **Steintyp wählen** (4 Optionen)
4. **Ergebnisse ansehen** in den Tabs

### 3. Mit Kosten rechnen
1. Sidebar: "Kosten berechnen" aktivieren
2. Preise eingeben (Standard: 5 €/Sack, 50 €/Tonne)
3. Einkaufsliste im Tab "Materialien & Kosten"

## 💡 Beispiele

### Beispiel 1: Gerade Gartenmauer
```
Vorlage: "gerade_gartenmauer" auswählen
→ Automatisch: 10m × 1,5m, Standard-Stein
```

### Beispiel 2: Hangbefestigung mit Gefälle
```
Länge: 8 m
Anfangshöhe: 2,0 m
Endhöhe: 1,0 m
Stein: Standard
→ Berechnet trapezförmige Mauer
```

### Beispiel 3: Niedrige Mauer (Hochbeet)
```
Vorlage: "niedrige_mauer"
→ 5m × 0,5m für kleine Projekte
```

## 🎨 Features ausprobieren

### ✅ Must-Try
1. **3D-Ansicht**: Tab "Visualisierung" → "3D Ansicht"
   - Mit Maus drehen und zoomen
   - Sehen Sie das versetzte Mauerwerk in 3D!

2. **PDF-Export**: Tab "Export" → "PDF erstellen"
   - Professioneller Bericht zum Ausdrucken

3. **Vorlagen**: Sidebar → Dropdown "Vorlage auswählen"
   - Schnellstart für typische Mauern

### 🔧 Admin-Bereich (für Fortgeschrittene)
1. Sidebar: Seite "Admin" öffnen
2. Passwort: `admin123`
3. Steintypen, Preise, Vorlagen anpassen

## ⚠️ Troubleshooting

### App startet nicht?
```bash
# Python-Version prüfen (sollte 3.8+ sein)
python --version

# Dependencies neu installieren
pip install --upgrade -r requirements.txt
```

### "ModuleNotFoundError"?
```bash
# Einzelne Pakete installieren
pip install streamlit plotly pyyaml reportlab pytest numpy
```

### PDF-Export funktioniert nicht?
```bash
# Kaleido für Plotly-Bilder installieren
pip install kaleido

# Falls Probleme: Text-Export nutzen (funktioniert immer)
```

### Port 8501 bereits belegt?
```bash
# Anderen Port verwenden
streamlit run app.py --server.port 8502
```

## 📱 Mobile nutzen

1. **Gleiche Netzwerk**: PC und Handy im selben WLAN
2. **IP finden** (im Terminal nach "Network URL" suchen)
3. **Browser auf Handy**: `http://<ihre-ip>:8501`

Beispiel: `http://192.168.1.100:8501`

## 🔗 Weiterführende Dokumentation

- **Vollständige Anleitung**: `README.md`
- **Mobile-Tipps**: `MOBILE.md`
- **FCN-Daten**: `config.yaml`

## 💬 Häufige Fragen

**Q: Kann ich die Schalstein-Daten ändern?**  
A: Ja! Admin-Interface oder direkt `config.yaml` bearbeiten.

**Q: Sind die Berechnungen genau?**  
A: Ja, basierend auf FCN-Spezifikationen + 15% Puffer. Aber: Keine statische Berechnung!

**Q: Kostet das Tool etwas?**  
A: Nein, komplett kostenlos!

**Q: Kann ich es offline nutzen?**  
A: Ja, nach Installation läuft alles lokal.

## 🎓 Video-Tutorial (Bald verfügbar)

Behalten Sie das Repository im Auge für:
- [ ] Video-Anleitung auf YouTube
- [ ] Schritt-für-Schritt Screenshots
- [ ] Live-Demo

## 🚀 Bereit? Los geht's!

```bash
streamlit run app.py
```

Viel Erfolg mit Ihrem Mauerprojekt! 🧱

---

**Brauchen Sie Hilfe?** Erstellen Sie ein Issue im Repository oder lesen Sie `README.md` für Details.


