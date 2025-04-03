"""
Zeitreihen-Visualisierungs-App

Diese Anwendung ermöglicht die Visualisierung und Analyse von Zeitreihendaten.
Sie bietet Funktionen zum Importieren von CSV-Dateien, Konfigurieren von Einstellungen
und Anzeigen von Diagrammen für verschiedene Zeitintervalle.

Hauptfunktionen:
- CSV-Import
- Konfiguration von Anzeige- und Importeinstellungen
- Interaktive Benutzeroberfläche zur Auswahl von Zeitreihen und Datumsbereichen
- Visualisierung von Zeitreihendaten in Diagrammen

Die Anwendung nutzt Tkinter für die GUI und verschiedene benutzerdefinierte Module
für spezifische Funktionalitäten wie Datenimport und Metadatenverwaltung.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import json
from modules.UIComponents import UIComponents
from modules.DataImporter import DataImporter
from modules.MetadataManager import MetadataManager
from modules.ConfigWindow import ConfigWindow

class StartApplication:
    """
        Diese Klasse initialisiert die Benutzeroberfläche und verwaltet die Hauptfunktionen der Anwendung.

        Attribute:
            color_schemes_path (str): Pfad zur Farbschema-Konfigurationsdatei
            config_path (str): Pfad zur Hauptkonfigurationsdatei
            metadata_path (str): Pfad zur Metadaten-Datei
            metaplot_path (str): Pfad zur Metaplot-Datei
            config (dict): Geladene Konfigurationseinstellungen
            window_x (int): Fensterbreite
            window_y (int): Fensterhöhe
            metadata_manager (MetadataManager): Verwaltet Metadaten
            master (tk.Tk): Hauptfenster der Anwendung
            data_importer (DataImporter): Importiert Daten
            ui_components (UIComponents): Verwaltet UI-Komponenten

        Methoden:
            __init__(self, master): Initialisiert die Anwendung
            erster_init(self): Erstellt initiale Konfigurationsdateien
            lade_config(self): Lädt die Konfiguration
            center_window(self): Zentriert das Hauptfenster auf dem Bildschirm
            show_platzhalter(self): Zeigt ein Platzhalterbild an
            create_widgets(self): Erstellt UI-Widgets
            csv_import(self): Importiert CSV-Dateien
            aktualisiere_zeitreihen_checkboxen(self): Aktualisiert Zeitreihen-Checkboxen
            open_config(self): Öffnet das Konfigurationsfenster
            end_session(self): Beendet die Anwendungssitzung
        """
    def __init__(self, master):
        # Initialisierung der Hauptanwendung
        self.color_schemes_path = os.path.abspath('resources/color_schemes.json')
        self.config_path = os.path.abspath('config/config.json')
        self.metadata_path = os.path.abspath('metadata.json')
        self.metaplot_path = os.path.abspath('metaplot.json')
        self.config = self.lade_config()
        self.window_x = 896
        self.window_y = 700
        self.metadata_manager = MetadataManager(self.metadata_path)
        self.master = master
        self.master.title("Zeitreihen-Visualisierungs-App")
        self.master.geometry(f"{self.window_x}x{self.window_y}")
        self.center_window()
        self.data_importer = DataImporter(self.config)
        self.ui_components = UIComponents(self.master, self.csv_import, self.open_config, self.end_session,self.config_path, self.metaplot_path)
        print(f"Systempfade:\nConfig: {self.config_path}\nMetadaten: {self.metadata_path}\nMetaPlotdaten: {self.metaplot_path}\nerfolgreich initialisiert")
        self.create_widgets()
        self.show_platzhalter()

    def erster_init(self):
        # Erstelle config.json
        if not os.path.exists(self.config_path):
            default_config = {
                "window_x": 896,
                "window_y": 700,
                "color_scheme": "spectrum",
                "delimiter": "\\t",
                "columns": ["DATE", "TIME", "OPEN", "HIGH", "LOW", "CLOSE", "TICKVOL", "VOL", "SPREAD"],
                "date_format": "%Y.%m.%d %H:%M:%S"
            }
            with open(self.config_path, 'w') as config_file:
                json.dump(default_config, config_file, indent=4)

        # Erstelle metadata.json
        if not os.path.exists(self.metadata_path):
            default_metadata = {
                "available_intervals": [],
                "symbols": [],
                "date_range": {"start": None, "end": None},
                "files": {}
            }
            with open(self.metadata_path, 'w') as metadata_file:
                json.dump(default_metadata, metadata_file, indent=4)

        # Erstelle metaplot.json
        if not os.path.exists(self.metaplot_path):
            with open(self.metaplot_path, 'w') as metaplot_file:
                default_metaplot = {}
                json.dump(default_metaplot, metaplot_file)

    def lade_config(self):
        # Testen ob alls notwendigen files vorhanden sind
        self.erster_init()

        with open(self.config_path, 'r') as config_file:
            config = json.load(config_file)
            self.window_x = config.get('window_x', 896)
            self.window_y = config.get('window_y', 700)

        return config

    def center_window(self):
        # Zentrieren des Hauptfensters auf dem Bildschirm
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - int(self.window_x)) // 2
        y = (screen_height - int(self.window_y)) // 2
        self.master.geometry(f"{self.window_x}x{self.window_y}+{x}+{y}")

    def show_platzhalter(self):
        # Anzeigen eines Platzhalterbildes
        placeholder_image = Image.open("charts_by_ki.jpg")
        placeholder_photo = ImageTk.PhotoImage(placeholder_image)
        self.placeholder_label = ttk.Label(self.master, image=placeholder_photo)
        self.placeholder_label.image = placeholder_photo
        self.placeholder_label.pack(side="bottom", fill="x", expand=False)

    def create_widgets(self):
        # Erstellen der UI-Komponenten
        self.ui_components.erstelle_buttons()
        self.ui_components.create_hyperlink_area()
        self.ui_components.update_hyperlinks()

    def csv_import(self):
        # Funktion zum Importieren von CSV-Dateien
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        for file_path in file_paths:
            df, symbol, interval, start_date, end_date = self.data_importer.import_csv(file_path)
            if df is not None:
                self.metadata_manager.update_metadata(symbol, interval, start_date, end_date, file_path)
                self.ui_components.update_date_range(start_date=start_date, end_date=end_date)
                print(f"Daten importiert für {symbol} {interval}")
                self.aktualisiere_zeitreihen_checkboxen()

        if file_paths:
            print(f"{len(file_paths)} Datei(en) erfolgreich importiert.")

    def aktualisiere_zeitreihen_checkboxen(self):
        # Aktualisieren der Zeitreihen-Checkboxen nach dem Import
        intervalle = self.metadata_manager.metadata['available_intervals']
        self.ui_components.aktualisiere_intervalle(intervalle)

    def open_config(self):
        # Öffnen des Konfigurationsfensters
        ConfigWindow(self.master, self.aktualisiere_zeitreihen_checkboxen, self.config_path, self.color_schemes_path)

    def end_session(self):
        # Beenden der Anwendungssitzung
        if messagebox.askyesno("Sitzung beenden", "Möchten Sie die Sitzung wirklich beenden?"):
            self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = StartApplication(root)
    root.mainloop()
