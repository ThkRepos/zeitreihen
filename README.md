# Zeitreihen-Visualisierungs-App

Eine interaktive Anwendung zur Visualisierung und Analyse von Zeitreihen-Finanzdaten mit Unterstützung für mehrere Zeiteinheiten und optionaler Live-Daten-Integration.

![Zeitreihen-Visualisierungs-App](C:\AlfaKurse\Python\App\charts_by_ki.jpg)
++ Quelle: Bild mit Microsoft Ki-Bildgenerator ++

## Inhaltsverzeichnis
- [Übersicht](#übersicht)
- [Funktionen](#funktionen)
- [Installation](#installation)
  - [Voraussetzungen](#voraussetzungen)
  - [Setup mit virtueller Umgebung](#setup-mit-virtueller-umgebung)
  - [Manuelle Installation](#manuelle-installation)
  - [Hinweis zu tkinter](#hinweis-zu-tkinter)
- [Verwendung](#verwendung)
- [Datenformat](#datenformat)
  - [Eingabedaten (CSV)](#eingabedaten-csv)
  - [Datenstruktur](#datenstruktur)
- [UI-Komponenten](#ui-komponenten)
  - [Hauptfenster](#hauptfenster)
  - [Steuerungspanel](#steuerungspanel)
  - [Zeiteinheiten-Panel](#zeiteinheiten-panel)
  - [Chart-Bereich](#chart-bereich)
  - [Statusleiste](#statusleiste)
- [Farbschemata](#farbschemata)
- [Live-Daten-Integration](#live-daten-integration)
- [Projektstruktur](#projektstruktur)
- [Entwicklungsplan](#entwicklungsplan)
- [Fehlerbehebung und FAQ](#fehlerbehebung-und-faq)

## Übersicht

Diese App ermöglicht die Visualisierung von Finanz-Zeitreihen (M1 bis M30) in einem interaktiven Liniendiagramm. Daten werden aus tab-getrennten CSV-Dateien eingelesen, transformiert und in einem konfigurierbaren Cache gespeichert. Mit der optionalen Live-Daten-Funktionalität können auch Echtzeit-Updates angezeigt werden.

## Funktionen

- **Visualisierung mehrerer Zeiteinheiten**: Gleichzeitige Darstellung von M1, M2, M3, M4, M5, M6, M10, M12, M15, M20 und M30 Zeitreihen in einem Chart
- **Interaktive Charts**: Zoomen, Schwenken und Hover-Informationen mittels Plotly
- **Flexible Datumsfilterung**: Auswahl beliebiger Zeiträume innerhalb der Datenverfügbarkeit
- **Anpassbare Farbschemata**: Drei vordefinierte Farbschemata zur visuellen Unterscheidung der Zeitreihen
- **Intelligentes Caching**: Speicherung transformierter Daten mit automatischer Bereinigung
- **Live-Daten-Option**: Erweiterbarkeit für Echtzeit-Datenstreams aus verschiedenen Quellen
- **Exportfunktionen**: Export der Diagramme als Bild oder interaktives HTML

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- Betriebssystem: Windows, macOS oder Linux

### Setup mit virtueller Umgebung (empfohlen)

Die einfachste Methode zur Installation ist die Verwendung unseres Setup-Skripts, das automatisch eine virtuelle Umgebung erstellt und alle Abhängigkeiten installiert:

1. Klonen oder laden Sie das Repository herunter
2. Öffnen Sie ein Terminal/Kommandozeile im Projektverzeichnis
3. Führen Sie folgenden Befehl aus:

```bash
python app_1_setup.py
```

4. Nach Abschluss der Installation können Sie die Anwendung mit einem der generierten Startskripte starten:

- **Windows**: Doppelklick auf `start_app.bat` oder im Terminal: `start_app.bat`
- **macOS/Linux**: Im Terminal: `./start_app.sh`

### Manuelle Installation

Falls Sie die Abhängigkeiten manuell installieren möchten:

```bash
pip install -r requirements.txt
```
**oder:**
```bash
python app_2_install_dependencies.py
```

Danach können Sie die Anwendung direkt starten:

```bash
python app_3_start.py
```

### Hinweis zu tkinter

Diese Anwendung verwendet tkinter, das Standard-GUI-Toolkit für Python. Tkinter ist normalerweise Teil der Python-Standardinstallation, in einigen Fällen muss es jedoch separat installiert werden.

#### Fehlerbehebung für tkinter

Wenn Sie eine Fehlermeldung wie `ModuleNotFoundError: No module named 'tkinter'` erhalten, müssen Sie tkinter für Ihr Betriebssystem installieren:

**Windows**  
Auf Windows ist tkinter normalerweise in der Standard-Python-Installation enthalten. Wenn es fehlt:
1. Deinstallieren Sie Python
2. Laden Sie Python erneut herunter und installieren Sie es
3. Stellen Sie sicher, dass Sie während der Installation "Alle Optionalen Features" auswählen

**Ubuntu/Debian Linux**
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**Fedora Linux**
```bash
sudo dnf install python3-tkinter
```

**macOS mit Homebrew**
```bash
brew install python-tk
```

Um zu prüfen, ob tkinter korrekt installiert ist, führen Sie in Ihrer Kommandozeile aus:
```bash
python -c "import tkinter; tkinter._test()"
```

## Verwendung

Nach dem Start der Anwendung:

1. Laden Sie über den Datei-Upload ihre Zeitreihen-Daten hoch - Schema weiter unten beachten
2. Setzen Sie nach dem Upload Ihrer Daten den gewünschten Zeitraum mit dem Datumsfilter
3. Aktivieren Sie die Zeiteinheiten, die Sie visualisieren möchten (M1-M30)
4. Wählen Sie ein Farbschema für die Darstellung
5. Nutzen Sie die interaktiven Funktionen des Charts (Zoomen, Schwenken, Hover)
6. Optional: Nur Live-Daten verwenden für Echtzeit-Updates zeitversetzt um 1 Minute
7. Bei Bedarf exportieren Sie das Diagramm als Bild oder HTML

## Datenformat

### Eingabedaten (CSV)

Die App verarbeitet tab-getrennte CSV-Dateien mit folgendem Namensformat:
`Symbol_Zeiteinheit_Startdatum_Enddatum.csv`

**Beispiel-Dateiname**: `DE40_M1_202410010102_202503272358.csv`
- Symbol: DE40 (Deutscher Aktienindex)
- Zeiteinheit: M1 (1-Minuten-Intervall)
- Startdatum/-zeit: 2024-10-01 01:02
- Enddatum/-zeit: 2025-03-27 23:58

### Datenstruktur

#### Originalspalten der CSV-Datei (tab-getrennt)
- `DATE`: Datumsinformation
- `TIME`: Zeitinformation
- `OPEN`: Eröffnungskurs
- `HIGH`: Höchstkurs im Intervall
- `LOW`: Tiefstkurs im Intervall
- `CLOSE`: Schlusskurs
- `TICKVOL`: Tick-Volumen
- `VOL`: Handelsvolumen
- `SPREAD`: Spread

#### Transformierte Spalten nach der Verarbeitung
- `date`: Datum (entspricht DATE)
- `time`: Zeit (entspricht TIME)
- `open`: Eröffnungskurs
- `high`: Höchstkurs
- `low`: Tiefstkurs
- `close`: Schlusskurs
- `direction`: Richtungsindikator (buy=grün, sell=rot)
  - Berechnet aus Vergleich von 'open' und 'close'
  - buy (grün): wenn close > open
  - sell (rot): wenn close < open
- `daytime`: Kombiniertes Datums-/Zeitfeld aus DATE und TIME

## UI-Komponenten

### Hauptfenster
- Größe: 1200x800 Pixel (skalierbar)
- Layout: Grid-System mit 4 Hauptbereichen

### Steuerungspanel
- Dateiauswahl-Upload
- Datumsauswahl mit Zeitfiltern
- Farbschema-Auswahl
- Live-Daten-Aktivierung
- Export-Optionen

### Zeiteinheiten-Panel
- Checkboxen für M1, M2, M3, M4, M5, M6, M10, M12, M15, M20, M30 Zeiteinheiten
- Farblich kodierte Labels
- Auswahl/Abwahl-alle Optionen

### Chart-Bereich
- Interaktives Plotly-Liniendiagramm
- Mehrere Zeitreihen mit farblicher Unterscheidung
- Dynamische Legende

### Statusleiste
- Aktuelle Datei und Zeitraum
- Cache-Status
- Verbindungsstatus (für Live-Daten)

## Farbschemata

Die App bietet drei verschiedene Farbschemata zur klaren Unterscheidung der Zeitreihen:

### Spektrales Farbschema
- M1: Dunkelrot (#8B0000)
- M2: Rotbraun (#A52A2A)
- M3: Lachsrot (#CD5C5C)
- M4: Rot (#FF0000)
- M5: Orange-Rot (#FF4500)
- M6: Tomatenrot (#FF6347)
- M10: Orange (#FFA500)
- M12: Goldgelb (#FFD700)
- M15: Grün (#00A000)
- M20: Blau (#0000FF)
- M30: Violett (#800080)

### Monochrom mit Intensitätsabstufung
- M1: Hellstes Blau (#E6F3FF)
- M2: Sehr helles Blau (#CCE7FF)
- M3: Helles Blau (#B3DBFF)
- M4: Mittleres helles Blau (#99CFFF)
- M5: Mittleres Blau (#80C3FF)
- M6: Kräftiges Blau (#66B7FF)
- M10: Königsblau (#4169E1)
- M12: Dunkelblau (#0000CD)
- M15: Hellgrün (#90EE90)
- M20: Mittelgrün (#2E8B57)
- M30: Dunkelgrün (#006400)

### Komplementärfarben
- M1: Sehr helles Türkis (#E0FFFF)
- M2: Helles Türkis (#AFEEEE)
- M3: Mittleres Türkis (#40E0D0)
- M4: Türkis (#00CED1)
- M5: Mitteldunkles Türkis (#20B2AA)
- M6: Dunkles Türkis (#008B8B)
- M10: Koralle (#FF7F50)
- M12: Tomatenrot (#FF6347)
- M15: Karmesinrot (#DC143C)
- M20: Indischrot (#CD5C5C)
- M30: Burgunderrot (#800000)

Die Farbschemata sind in der Datei `resources/color_schemes.json` definiert und können bei Bedarf angepasst werden.

## Live-Daten-Integration - zukünftige Entwicklung

Die App unterstützt die Integration von Live-Daten, wodurch Echtzeit-Updates zu den visualisierten Zeitreihen möglich sind.

### Unterstützte Datenquellen
- Lokaler Dateiwatcher
- Websocket-Verbindung zukünftige Entwicklung
- REST API-Polling zukünftige Entwicklung

### Konfigurationsoptionen
- Verbindungstyp
- Aktualisierungsrate (1s, 5s, 10s, 30s, 60s) zukünftige Entwicklung
- Quellspezifische Einstellungen zukünftige Entwicklung

### Visualisierung
- Statistische Daten 
- Live-Daten zukünftige Entwicklung
- Automatisches Scrolling für neueste Daten - (Dateiwatcher als erste Entwicklungsstufe)

## Cache-System

Für eine effiziente Datenverarbeitung implementiert die App ein intelligentes Cache-System:

### Metadaten-JSON-Struktur
Für jede CSV-Datei wird eine entsprechende JSON-Metadatendatei erstellt:

```json
{
  "filename": "DE40_M1_202410010102_202503272358.csv",
  "symbol": "DE40",
  "timeframe": "M1",
  "start_datetime": "2024-10-01T01:02:00",
  "end_datetime": "2025-03-27T23:58:00",
  "last_accessed": "2023-11-20T15:30:00",
  "cache_expiry": "2023-12-20T15:30:00",
  "stats": {
    "min_value": 15678.5,
    "max_value": 16982.3,
    "avg_value": 16245.7,
    "buy_count": 3542,
    "sell_count": 3245
  },
  "color_settings": {
    "line_color": "#FF0000",
    "scheme_name": "spectrum"
  }
}
```

## Projektstruktur

```
zeitreihen-app/
├── app_3_start.py                    # Hauptanwendungsdatei
├── README.md                         # Diese Dokumentation
├── requirements.txt                  # Abhängigkeiten
├── app_1_setup.py                    # Einrichtungsskript (virtuelle Umgebung)
├── app_2_install_dependencies.py     # Hilfsskript zur Installation von Abhängigkeiten
├── start_app.bat                     # Startskript für Windows (generiert)
├── start_app.sh                      # Startskript für macOS/Linux (generiert)
├── config/
│   └── settings.json                 # Allgemeine App-Einstellungen
├── modules/
│   ├── data_manager.py               # CSV-Einlesung, Caching, Datentransformation
│   ├── plotly_visualizer.py          # Plotly-Integration, Chart-Erstellung
│   ├── live_data_handler.py          # Handling von Live-Daten-Streams
│   └── ui_components.py              # Tkinter-UI-Komponenten
├── cache/
│   ├── data/                         # Gespeicherte CSV-Dateien
│   └── meta/                         # Metadaten-JSON-Dateien
└── resources/
    └── color_schemes.json            # Vordefinierte Farbschemata
```

## Entwicklungsplan

### Phase 1: Grundlagen
- Projektstruktur aufsetzen
- Daten-Einlesungs-Funktionen implementieren (CSV-Einlesung, Caching)
- Bestenfalls Ordner auswahl und Liste der CSV Dateien verarbeiten (Batch)
- Basis-UI mit Tkinter erstellen

### Phase 2: Plotly-Integration
- Plotly-Visualisierungsmodul implementieren
- Integration in Tkinter-Oberfläche
- Interaktivität und Farbschemata

### Phase 3: Kernfunktionalität
- Datenverarbeitungs-Pipeline implementieren
- Datumsfilterung und -auswahl
- Cache-Management

### Phase 4: Live-Daten-Erweiterung zukünftige Entwicklung
- Live-Daten-Handler-Modul implementieren
- Verbindungseinstellungen-Dialog
- Integration in die Hauptanwendung

### Phase 5: Fertigstellung
- Fehlerbehandlung und Robustheit
- Performance-Optimierungen
- Benutzerfreundlichkeit und Dokumentation

## Fehlerbehebung und FAQ

### Allgemeine Probleme

**F: Die Anwendung startet nicht und zeigt einen ImportError**  
A: Stellen Sie sicher, dass alle Abhängigkeiten korrekt installiert sind. 
Führen Sie `python app_2_install_dependencies.py` aus oder verwenden Sie das Setup-Skript erneut.

**F: Die Charts werden nicht angezeigt**  
A: Prüfen Sie, ob die ausgewählte CSV-Datei dem erwarteten Format entspricht und gültige Daten enthält.

**F: Änderungen der Farbschemata werden nicht angewendet**  
A: Nachdem Sie Änderungen an `color_schemes.json` vorgenommen haben, starten Sie die Anwendung neu.

### Probleme mit der virtuellen Umgebung

**F: Das Setup-Skript schlägt fehl**  
A: Stellen Sie sicher, dass Sie Python 3.8 oder höher installiert haben und ausreichende Berechtigungen für die Installation besitzen.

**F: Wie aktiviere ich die virtuelle Umgebung manuell?**  
A: 
- Windows: `zeitreihen_venv\Scripts\activate`
- macOS/Linux: `source zeitreihen_venv/bin/activate`

### Datenformat-Probleme

**F: Meine CSV-Dateien werden nicht erkannt**  
A: Überprüfen Sie, ob der Dateiname dem Format `Symbol_Zeiteinheit_Startdatum_Enddatum.csv` entspricht und die Datei tab-getrennt ist.

**F: Wie erstelle ich kompatible CSV-Dateien?**  
A: Stellen Sie sicher, dass Ihre Datei mindestens die Spalten DATE, TIME, OPEN, HIGH, LOW, CLOSE enthält und tab-getrennt ist.

### Leistungsprobleme

**F: Die Anwendung wird bei großen Datensätzen langsam**  
A: 
- Reduzieren Sie den ausgewählten Zeitraum
- Deaktivieren Sie nicht benötigte Zeiteinheiten
- Stellen Sie sicher, dass die optionalen Leistungs-Abhängigkeiten (orjson, pyarrow) installiert sind

---

**Hinweis:** Dieses Projekt wird aktiv weiterentwickelt. Bei Fragen oder Problemen erstellen Sie bitte ein Issue im Repository oder kontaktieren Sie das Entwicklungsteam.

