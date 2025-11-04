# 🧱 MauerPlaner

**Betonbedarfsrechner für Schalsteinmauern** | *by LEANOFY*

Ein professionelles Streamlit-basiertes Tool zur Berechnung des Betonbedarfs für Schalsteinmauern basierend auf FCN-Spezifikationen.

## ✨ Features

### Hohe Priorität (Kernfunktionen)
- **🏗️ Mauer-Dimensionen eingeben**: Länge, Anfangshöhe, Endhöhe, Breite mit automatischer Validierung
- **🧱 FCN-Schalstein-Auswahl**: 4 präzise kalibrierte Steintypen mit exakten Füllvolumen
- **📊 Visualisierung**: 2D-Seitenansicht, interaktive 3D-Ansicht und Draufsicht mit versetztem Mauerwerk
- **🧮 Präzise Berechnung**: Betonvolumen mit 15% Puffer für Verluste, aufgeschlüsselt in Zement, Kies und Wasser

### Mittlere Priorität (Usability)
- **💰 Kostenrechner**: Materialpreise eingeben und Gesamtkosten schätzen
- **🛒 Einkaufsliste**: Detaillierte Liste mit benötigten Materialien
- **⚠️ Fehlervalidierung**: Sprechende deutsche Fehlermeldungen und Höhenwarnungen
- **📱 Mobile-optimiert**: Responsive Design für alle Geräte

### Niedrige Priorität (Nice-to-Have)
- **📋 Vorlagen**: Schnellauswahl für typische Mauern (Gartenmauer, Hangbefestigung, etc.)
- **📄 PDF-Export**: Professionelle PDF-Berichte mit allen Berechnungen
- **⚙️ Admin-Interface**: Web-basiertes Interface zur Verwaltung der Konfiguration

## 🚀 Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt 1: Repository klonen oder herunterladen
```bash
git clone <repository-url>
cd "schalsteinmauer beton rechner"
```

Oder laden Sie die Dateien manuell herunter.

### Schritt 2: Dependencies installieren
```bash
pip install -r requirements.txt
```

### Schritt 3: Anwendung starten
```bash
streamlit run app.py
```

Die Anwendung öffnet sich automatisch im Browser unter `http://localhost:8501`

## 📖 Verwendung

### Grundlegende Nutzung

1. **Mauer-Dimensionen eingeben** (Sidebar):
   - Länge in Metern
   - Anfangshöhe und Endhöhe (für Gefälle)
   - Breite/Dicke in Zentimetern

2. **Schalstein-Typ wählen**:
   - 4 FCN-Steintypen zur Auswahl
   - Standard (36,0 × 36,5 × 24,8 cm) ist vorausgewählt
   - Breite wird automatisch vorgeschlagen

3. **Ergebnisse ansehen**:
   - **Übersicht-Tab**: Zusammenfassung, Steinanzahl, Volumen
   - **Visualisierung-Tab**: 2D/3D-Ansichten der Mauer
   - **Materialien-Tab**: Detaillierter Materialbedarf
   - **Export-Tab**: PDF oder Text exportieren

### Erweiterte Features

#### Kostenrechnung aktivieren
1. Sidebar: "Kosten berechnen" aktivieren
2. Preise für Zement und Kies eingeben
3. Automatische Berechnung der Gesamtkosten

#### Vorlagen verwenden
1. Sidebar: Vorlage aus Dropdown auswählen
2. Alle Felder werden automatisch ausgefüllt
3. Nach Bedarf anpassen

#### PDF-Export
1. "Export"-Tab öffnen
2. "PDF erstellen" klicken
3. PDF herunterladen mit allen Berechnungen

#### Admin-Bereich (für Fortgeschrittene)
1. Sidebar: "Admin" Seite öffnen
2. Passwort eingeben (Standard: `admin123`)
3. Schalstein-Daten, Preise, Vorlagen verwalten
4. Änderungen speichern

## 🧮 Berechnungsmethodik

### Volumenberechnung
1. **Mauerfläche**: Länge × Durchschnittshöhe (bei Gefälle)
2. **Steinanzahl**: Fläche × Steine pro m² (aus FCN-Daten)
3. **Füllvolumen**: Steinanzahl × Füllvolumen pro Stein
4. **Puffer**: +15% für Verluste und Verschnitt

### Mischverhältnis (Volumenbasis)
- **1 Teil Zement : 4 Teile Kies : 0,5 Teile Wasser**
- Für 1 m³ Beton: ~300 kg Zement, ~1200 kg Kies, ~150 L Wasser

### Betonempfehlung nach FCN
- **Qualität**: C25/30
- **Korngröße**: max. 16 mm (Rundkies 0-16)
- **Konsistenz**: F3
- **Armierung**: Für Höhen >1 m empfohlen (z.B. 2 Ø 8 mm pro Lage)

## 📁 Projektstruktur

```
schalsteinmauer beton rechner/
├── app.py                      # Haupt-Streamlit-Anwendung
├── calculations.py             # Berechnungslogik
├── visualization.py            # 2D/3D-Visualisierungen
├── pdf_export.py              # PDF-Export-Funktionen
├── config.yaml                # FCN-Daten und Konfiguration
├── requirements.txt           # Python-Dependencies
├── README.md                  # Diese Datei
├── pages/
│   └── 1_⚙️_Admin.py         # Admin-Interface
└── tests/
    └── test_calculations.py   # Unit-Tests
```

## 🧪 Tests ausführen

```bash
pytest tests/ -v
```

Oder nur einen spezifischen Test:
```bash
pytest tests/test_calculations.py::TestWallArea -v
```

## ⚙️ Konfiguration

Die Datei `config.yaml` enthält:
- **stone_types**: FCN-Schalstein-Spezifikationen (4 Typen)
- **defaults**: Standard-Mauermaße
- **concrete_mix**: Mischverhältnis und Umrechnungsfaktoren
- **buffer**: Puffer-Prozentsatz (15%)
- **prices**: Standardpreise für Materialien
- **templates**: Vorlagen für häufige Mauern
- **warnings**: Grenzwerte für Höhenwarnungen

### Konfiguration anpassen

**Option 1: Admin-Interface (empfohlen)**
1. Admin-Seite öffnen
2. Werte anpassen
3. Speichern

**Option 2: Manuell**
1. `config.yaml` in einem Texteditor öffnen
2. Werte ändern (YAML-Syntax beachten!)
3. Speichern
4. Anwendung neu laden

## 🔒 Sicherheitshinweise

### Admin-Passwort
- Standard-Passwort: `admin123`
- **⚠️ Wichtig**: Ändern Sie das Passwort in Produktionsumgebungen!
- Das Passwort ist in `pages/1_⚙️_Admin.py` hardcodiert (Zeile ~23)

### Deployment
Für produktive Nutzung:
1. Passwort-Management verbessern (z.B. Umgebungsvariablen)
2. HTTPS verwenden
3. Backup der `config.yaml` erstellen
4. Zugriffskontrolle einrichten

## 📱 Mobile Nutzung

Die Anwendung ist vollständig responsive:
- Sidebar wird auf mobilen Geräten zu einem ausklappbaren Menü
- Visualisierungen passen sich an Bildschirmgröße an
- Touch-Gesten für 3D-Ansicht (Drehen, Zoomen)

**Tipp**: Auf kleinen Bildschirmen ist die 2D-Ansicht oft übersichtlicher als 3D.

## 🐛 Problembehandlung

### Streamlit startet nicht
```bash
# Prüfen Sie die Python-Version
python --version  # Sollte 3.8+ sein

# Installieren Sie Dependencies neu
pip install --upgrade -r requirements.txt
```

### PDF-Export funktioniert nicht
```bash
# Installieren Sie kaleido für Plotly-Bild-Export
pip install kaleido
```

Falls Probleme mit kaleido auftreten:
- Nutzen Sie den Text-Export als Alternative
- Oder deaktivieren Sie Bilder im PDF (siehe `pdf_export.py`)

### Tests schlagen fehl
```bash
# Stellen Sie sicher, dass Sie im Projekt-Root sind
cd "schalsteinmauer beton rechner"

# Dependencies installieren
pip install pytest

# Tests ausführen
pytest tests/ -v
```

### Config-Datei beschädigt
1. Erstellen Sie ein Backup von `config.yaml` (Admin → "Aktuelle Config herunterladen")
2. Löschen Sie die beschädigte Datei
3. Starten Sie die App neu (erstellt Standard-Config)
4. Oder stellen Sie das Backup wieder her

## 🤝 Beitragen

Verbesserungsvorschläge und Bug-Reports sind willkommen!

### Entwicklung
1. Fork erstellen
2. Feature-Branch erstellen: `git checkout -b feature/neue-funktion`
3. Änderungen committen: `git commit -m 'Neue Funktion hinzufügen'`
4. Branch pushen: `git push origin feature/neue-funktion`
5. Pull Request erstellen

### Tests hinzufügen
Bitte fügen Sie Tests für neue Berechnungsfunktionen hinzu:
```python
# In tests/test_calculations.py
def test_neue_funktion():
    result = neue_funktion(parameter)
    assert result == erwarteter_wert
```

## 📄 Lizenz

Dieses Projekt ist für den persönlichen und kommerziellen Gebrauch frei verfügbar.

## ⚠️ Haftungsausschluss

**Wichtiger Hinweis**: Dieses Tool liefert Schätzungen basierend auf FCN-Spezifikationen und Standardannahmen. Es ersetzt **keine** professionelle statische Berechnung oder Bauplanung.

- Konsultieren Sie einen Fachmann für tragende oder hohe Mauern
- Beachten Sie lokale Bauvorschriften
- Prüfen Sie Statik und Armierung bei Höhen >1 m
- Das Tool berücksichtigt keine spezifischen Bodenverhältnisse oder Lasten

## 📞 Support

Bei Fragen oder Problemen:
1. Lesen Sie diese README-Datei
2. Prüfen Sie die Konfiguration in `config.yaml`
3. Konsultieren Sie die FCN-Dokumentation für Schalsteine
4. Erstellen Sie ein Issue im Repository

## 🙏 Danksagungen

- **FCN (Fels-Werke)** für die Schalstein-Spezifikationen
- **Streamlit** für das fantastische Framework
- **Plotly** für die interaktiven Visualisierungen

## 📊 Technologie-Stack

- **Frontend**: Streamlit (Python)
- **Visualisierung**: Plotly
- **PDF-Export**: ReportLab
- **Konfiguration**: YAML
- **Testing**: pytest

---

**Version**: 1.0.0  
**Erstellt**: 2025  
**Betreiber**: LEANOFY  
**Basiert auf**: FCN-Spezifikationen für Schalsteine  
**Website**: [https://leanofy.de](https://leanofy.de)  

---

**MauerPlaner** - Professionelle Betonbedarfsberechnung by LEANOFY

🧱 **Viel Erfolg mit Ihrem Mauerprojekt!** 🏗️


