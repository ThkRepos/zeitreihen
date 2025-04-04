import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import pandas as pd
import json
import os
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from modules.PlotChartLine import PlotChartLine

# Hilfsfunktion zum Laden von JSON-Dateien
def lade_json(datei_name):
    with open(datei_name, 'r') as json_file:
        return json.load(json_file)

class UIComponents:
    """
        Verwaltet die Benutzeroberflächen-Komponenten für die Zeitreihen-Visualisierungs-Anwendung.

        Diese Klasse ist verantwortlich für die Erstellung und Verwaltung aller UI-Elemente,
        einschließlich Buttons, Checkboxen für Zeitreihen, Datumswähler und Diagrammanzeige.
        Sie handhabt auch die Interaktionen mit dem Benutzer und aktualisiert die Anzeige
        basierend auf Benutzeraktionen und Datenänderungen.

        Attribute:
            master (tk.Tk): Das Hauptfenster der Anwendung.
            csv_import_callback (function): Callback für CSV-Import.
            config_callback (function): Callback für Konfigurationseinstellungen.
            end_session_callback (function): Callback zum Beenden der Sitzung.

        Methoden:
            erstelle_buttons(): Erstellt die Hauptbuttons der Anwendung.
            get_plot_files(): Gibt eine Liste der verfügbaren Plot-Dateien zurück.
            create_hyperlink_area(): Erstellt den Bereich für Hyperlinks.
            update_hyperlinks(): Aktualisiert die Hyperlinks basierend auf vorhandenen Plots.
            open_plot(dateiname): Öffnet einen bestimmten Plot.
            update_plot(): Aktualisiert das angezeigte Diagramm.
            prepare_chart_data(): Vorbereitet die Daten für den Plot.
            get_date_range_text(): Gibt den Datumsbereich als Text zurück.
            open_date_picker(): Öffnet den Datumswähler.
            aktualisiere_intervalle(intervalle): Aktualisiert die Zeitreihen-Checkboxen.
            erstelle_intervall_checkboxen(intervalle): Erstellt Checkboxen für Zeitreihen-Intervalle.
            aktuallisiere_aktive_zeitreihen(intervall): Aktualisiert die Zeitreihen-Checkboxen.
            update_date_range(): Aktualisiert den Datumsbereich basierend auf den ausgewählten Zeitreihen.
            zeige_alle(): Schaltet alle Zeitreihen-Checkboxen um.
            hole_aktive_zeitreihen(): Gibt die aktiven Zeitreihen zurück.
            update_metaplot(): Aktualisiert das Metaplot basierend auf den ausgewählten Zeitreihen.
        """

    def __init__(self, master, csv_import_callback, config_callback, end_session_callback, config_path, metaplot_path):
        # Initialisierung der Hauptkomponenten und Callbacks
        self.master = master
        self.csv_import_callback = csv_import_callback
        self.config_callback = config_callback
        self.end_session_callback = end_session_callback

        # UI-Elemente
        self.chart_frame = None
        self.chart_label = None
        self.alle_anzeigen_button = None
        self.date_range_label = None
        self.timeseries_frame = None
        self.update_plot_button = None
        self.hyperlink_label = None
        self.hyperlink_frame = None

        # Daten und Konfiguration
        self.plot_dir = os.path.abspath("./plots")
        self.metaplot_path = metaplot_path
        self.farbschemata = None
        self.metadaten = {"available_intervals": []}
        self.config = None
        self.config_color_schemes = None
        self.zeitreihen_checkboxen = {}
        self.aktive_zeitreihen = set()

        # Laden der Konfigurationen und Metadaten
        self.config = lade_json(config_path)
        self.config_color_schemes = self.config['color_scheme']
        self.metadaten = lade_json(os.path.abspath('./config/metadata.json'))
        self.farbschemata = lade_json(os.path.abspath('./resources/color_schemes.json'))
        self.color_schema_old = self.config_color_schemes
        self.markt_symbol = 'DE40'

    def erstelle_buttons(self):
        # Erstellen der Hauptbuttons und UI-Elemente
        button_frame = tk.Frame(self.master)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        # Definieren der Button-Stile
        button_style = {
            "font": ("Arial", 10),
            "relief": tk.RAISED,
            "borderwidth": 2,
            "cursor": "hand2",
            "width": 13
        }

        # CSV Import Button
        csv_import_btn = tk.Button(button_frame, text="CSV Import", command=self.csv_import_callback, bg="lightblue", **button_style)
        csv_import_btn.pack(side=tk.LEFT, padx=5)

        # Datumsauswahl Button
        date_picker_btn = tk.Button(button_frame, text="Datumsauswahl", command=self.open_date_picker, bg="lightgreen", **button_style)
        date_picker_btn.pack(side=tk.LEFT, padx=5)

        # Einstellungen Button
        config_btn = tk.Button(button_frame, text="Einstellungen", command=self.config_callback, bg="lightyellow", **button_style)
        config_btn.pack(side=tk.LEFT, padx=5)

        # Anzeige des aktuellen Datumsbereichs
        self.date_range_label = tk.Label(button_frame, text=self.get_date_range_text(), font=("Arial", 10))
        self.date_range_label.pack(side=tk.LEFT, padx=5)

        # Erstellung des "Sitzung beenden" Buttons
        end_session_btn = tk.Button(button_frame, text="Sitzung beenden", command=self.end_session_callback, bg="red", fg="white", **button_style)
        end_session_btn.pack(side=tk.RIGHT, padx=5)

        # Erstellung des Rahmens für Zeitreihen-Checkboxen
        self.timeseries_frame = tk.Frame(self.master)
        self.timeseries_frame.pack(fill=tk.X, padx=10, pady=5)

        # Alle Zeitreihen aktivieren/ deaktivieren Button
        self.alle_anzeigen_button = tk.Button(self.timeseries_frame, text="Alle anzeigen", command=self.zeige_alle, bg="lightgray", **button_style)
        self.alle_anzeigen_button.pack(side=tk.LEFT, padx=5)

        # Chart-Plotten Button
        self.update_plot_button = tk.Button(self.timeseries_frame, text="Chart-Plotten", command=self.update_plot, bg="lightpink", **button_style)
        self.update_plot_button.pack(side=tk.LEFT, padx=5)

        # Erstellung Checkboxen für Zeitreihen
        self.erstelle_intervall_checkboxen()


    def get_plot_files(self):
        # Abrufen der verfügbaren Plot-Dateien
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)
        return [f for f in os.listdir(self.plot_dir) if f.endswith('.html')]

    def create_hyperlink_area(self):
        separator = ttk.Separator(self.master, orient='horizontal')
        separator.pack(fill='x', pady=(5, 0))

        self.hyperlink_frame = ttk.Frame(self.master)
        self.hyperlink_frame.pack(fill=tk.X, padx=10, pady=5)

        self.hyperlink_label = ttk.Label(self.hyperlink_frame, text="Verfügbare Plots / Aktueller:", font=("Arial", 12, "bold"))
        self.hyperlink_label.grid(row=0, column=0, sticky='w', padx=5, pady=(0, 5))

        self.latest_plot_link = ttk.Label(self.hyperlink_frame, text="", foreground="blue", cursor="hand2")
        self.latest_plot_link.grid(row=0, column=1, sticky='w', padx=5, pady=(0, 5))

        self.links_frame = ttk.Frame(self.hyperlink_frame)
        self.links_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')

    def update_hyperlinks(self):
        with open(self.metaplot_path, 'r') as f:
            metaplot_data = json.load(f)

        plot_files = self.get_plot_files()
        # Finde den aktuellsten Plot
        latest_plot = max(metaplot_data.values(), key=lambda x: x['erstellt_am'], default=None)
        if latest_plot:
            latest_title = latest_plot['titel']
            latest_hash = next(hash for hash, data in metaplot_data.items() if data == latest_plot)
            self.latest_plot_link.config(text=f"{latest_title}", foreground="brown", font=("Arial", 10, "bold"), cursor="hand2")
            self.latest_plot_link.bind("<Button-1>", lambda e, pf=f"{latest_hash}.html": self.open_plot(pf))
            self.latest_plot_link.bind("<Enter>", lambda e: self.latest_plot_link.configure(foreground="orange"))
            self.latest_plot_link.bind("<Leave>", lambda e: self.latest_plot_link.configure(foreground="blue"))
        else:
            self.latest_plot_link.config(text="(Keine Plots verfügbar)", font=('Arial', 10, 'bold'), foreground="red")

        for widget in self.links_frame.winfo_children():
            widget.destroy()

        for i, plot_file in enumerate(plot_files):
            hash_value = plot_file.split('.')[0]
            title = metaplot_data.get(hash_value, {}).get('titel', plot_file)

            link = ttk.Label(self.links_frame, text=title, foreground="blue", cursor="hand2")
            link.grid(row=i // 2, column=i % 2, padx=5, pady=2, sticky='w')
            link.bind("<Button-1>", lambda e, pf=plot_file: self.open_plot(pf))
            link.bind("<Enter>", lambda e, l=link: l.configure(foreground="orange"))
            link.bind("<Leave>", lambda e, l=link: l.configure(foreground="blue"))

    def open_plot(self, plot_file):
        # Öffnen des ausgewählten Plots im Webbrowser
        self.update_hyperlinks()
        import webbrowser
        webbrowser.open(os.path.join("plots", plot_file))

    def update_plot(self):
        # Anzeigen wenn Daten fehlen
        if not self.metadaten['date_range']['start'] or not self.metadaten['date_range']['end']:
            messagebox.showinfo("Info", "Kein Datumsbereich verfügbar. Bitte importieren Sie zuerst Daten.")
            return

        # Aktualisieren des Plots basierend auf ausgewählten Zeitreihen und Datumsbereich
        active_series = self.hole_aktive_zeitreihen()
        date_range = self.metadaten['date_range']

        if len(active_series) == 0:
            messagebox.showinfo("Info", f"Bitte wählen Sie mindestens eine Zeitreihe aus.")
            return

        start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
        end_date = datetime.strptime(date_range['end'], '%Y-%m-%d')
        date_diff = (end_date - start_date).days

        if date_diff > 5:
            messagebox.showinfo("Info", "Bitte wählen Sie einen Datumsbereich zwischen 1 bis 5 Tagen.\nAktuell: " + str(date_diff) + " Tage")
            return
        # Aktualisieren des Plots basierend auf ausgewählten Zeitreihen und Datumsbereich
        chart_data = self.prepare_chart_data(active_series, date_range, self.markt_symbol)
        print(f"Aktualisiere Plot {self.markt_symbol} mit Zeitreihen: {active_series} und Datumsbereich: {date_range}")

        if len(chart_data) > 0:
            chart_creator = PlotChartLine(self.plot_dir)
            result_fig = chart_creator.create_chart(self.markt_symbol, chart_data, date_range)
            print(f"Daten: {result_fig[1]} / {result_fig[2]}")
            self.update_metaplot(titel=result_fig[1], hash_value=result_fig[2], date_range=date_range)
            self.update_hyperlinks()
        else:
            messagebox.showinfo("Info", "Keine Daten für den ausgewählten Datumsbereich verfügbar.")

    def prepare_chart_data(self, active_series, date_range, symbol):
        # Vorbereiten der Daten für die Charterstellung
        datum_von = datetime.strptime(date_range['start'], '%Y-%m-%d')
        datum_bis = datetime.strptime(date_range['end'], '%Y-%m-%d')

        chart_data_list = []

        for interval, color in active_series:
            file_name = f"{symbol}_{interval}.parquet"
            print("Verarbeite Datei:", file_name)
            file_path = os.path.join("./cache/data/", file_name)

            if os.path.exists(file_path):
                df = pd.read_parquet(file_path)
                result_df = df[
                    (df['DATE'].dt.strftime('%Y-%m-%d') >= datum_von.strftime('%Y-%m-%d')) &
                    (df['DATE'].dt.strftime('%Y-%m-%d') <= datum_bis.strftime('%Y-%m-%d'))
                    ]
                df_subset = result_df[['daytime', 'CLOSE']]
                chart_data_list.append((df_subset, interval, color))
            else:
                print(f"Datei: {file_path} nicht gefunden.")

        return chart_data_list

    def get_date_range_text(self):
        # Formatieren des Datumsbereich-Texts
        if not self.metadaten['date_range']['start'] or not self.metadaten['date_range']['end']:
            return "Kein Datumsbereich verfügbar"

        start = self.metadaten['date_range']['start']
        end = self.metadaten['date_range']['end']
        return f"Datumsbereich: {start} - {end}"

    def open_date_picker(self):
        # Hiniweis das Daten zum Anzeigen fehlen
        if not self.metadaten['date_range']['start'] or not self.metadaten['date_range']['end']:
            messagebox.showinfo("Info", "Kein Datumsbereich verfügbar. Bitte importieren Sie zuerst Daten.")
            return
        # Öffnen des Datumsauswahl-Fensters
        date_window = tk.Toplevel(self.master)
        date_window.title("Datumsauswahl")
        date_window.geometry("270x120")
        date_window.update_idletasks()
        width = date_window.winfo_width()
        height = date_window.winfo_height()
        x = (date_window.winfo_screenwidth() // 2) - (width // 2)
        y = (date_window.winfo_screenheight() // 2) - (height // 2)
        date_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        start_date = datetime.strptime(self.metadaten['date_range']['start'], '%Y-%m-%d').date()
        end_date = datetime.strptime(self.metadaten['date_range']['end'], '%Y-%m-%d').date()

        ttk.Label(date_window, text="Startdatum:").grid(row=0, column=0, padx=5, pady=5)
        start_picker = DateEntry(date_window, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        start_picker.set_date(start_date)
        start_picker.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        ttk.Label(date_window, text="Enddatum:").grid(row=1, column=0, padx=5, pady=5)
        end_picker = DateEntry(date_window, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        end_picker.set_date(end_date)
        end_picker.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        # Buttons
        tk.Button(date_window, text="Bestätigen", bg="green", fg="white", cursor="hand2",
                  command=lambda: self.update_date_range(start_picker.get_date(), end_picker.get_date(), date_window)).grid(row=2, column=1, padx=10)
        tk.Button(date_window, text="Abbrechen", bg="red", fg="white", cursor="hand2", command=date_window.destroy).grid(row=2, column=2, pady=10)

    def aktualisiere_intervalle(self, intervalle):
        # Aktualisiert die Intervall-Checkboxen durch Löschen und Neuerstellen.
        self.config = lade_json(os.path.abspath('./config/config.json'))
        self.config_color_schemes = self.config['color_scheme']
        self.farbschemata = lade_json(os.path.abspath('./resources/color_schemes.json'))

        if self.color_schema_old != self.config_color_schemes:
            print(f"Farbschemata neu: {self.config_color_schemes}")

        self.metadaten['available_intervals'] = intervalle
        # Lösche alle bestehenden Checkboxen
        for cb, _, _ in self.zeitreihen_checkboxen.values():
            cb.destroy()
        self.zeitreihen_checkboxen.clear()
        # Erstelle die Checkboxen neu
        self.erstelle_intervall_checkboxen()
        # Aktualisiere die Anzeige
        self.master.update()

    def erstelle_intervall_checkboxen(self):
        # Erstellt die Intervall-Checkboxen mit aktualisierten Farben
        colors = self.farbschemata['schemes'][self.config_color_schemes]['colors']
        if not self.metadaten['available_intervals']:
            return
        for intervall in self.metadaten['available_intervals']:
            var = tk.BooleanVar()
            farbe = colors.get(intervall, '#000000')
            cb = tk.Checkbutton(self.timeseries_frame, cursor='hand2', text=intervall, variable=var, command=lambda i=intervall: self.aktualisiere_aktive_zeitreihen(i), bg=farbe)
            cb.pack(side=tk.LEFT, padx=5)
            self.zeitreihen_checkboxen[intervall] = (cb, var, farbe)
        self.date_range_label.config(text=self.get_date_range_text(), font=("Arial", 12, "bold"))
        print("Intervall-Checkboxen neu erstellt")

    def aktualisiere_aktive_zeitreihen(self, intervall):
        # Aktualisieren der aktiven Zeitreihen
        if self.zeitreihen_checkboxen[intervall][1].get():
            self.aktive_zeitreihen.add(intervall)
        else:
            self.aktive_zeitreihen.remove(intervall)
        print(f"Aktive Zeitreihen: {self.aktive_zeitreihen}")

    def update_date_range(self, start_date, end_date, window=None):
        # Aktualisieren des Datumsbereichs und Schließen des Datumsauswahl-Fensters
        self.metadaten['date_range']['start'] = start_date.strftime('%Y-%m-%d')
        self.metadaten['date_range']['end'] = end_date.strftime('%Y-%m-%d')
        self.date_range_label.config(text=self.get_date_range_text(), font=("Arial", 12, "bold"))
        print(f"Neuer Datumsbereich:{self.markt_symbol} - {self.metadaten['date_range']}")
        if window is not None:
            window.destroy()

    def zeige_alle(self):
        # Umschalten aller Zeitreihen-Checkboxen
        all_active = all(self.zeitreihen_checkboxen[intervall][1].get() for intervall in self.zeitreihen_checkboxen)

        for intervall, (cb, var, _) in self.zeitreihen_checkboxen.items():
            var.set(not all_active)
            self.aktualisiere_aktive_zeitreihen(intervall)

        print("Alle Zeitreihen aktiviert" if not all_active else "Alle Zeitreihen deaktiviert")

    def hole_aktive_zeitreihen(self):
        # Gibt die Liste der aktiven Zeitreihen mit ihren Farben zurück
        return [(zr, self.zeitreihen_checkboxen[zr][2]) for zr in self.aktive_zeitreihen]

    def update_metaplot(self, hash_value, titel, date_range):
        # Aktualisiert die Metaplot-Daten in einer JSON-Datei
        if os.path.exists(self.metaplot_path):
            with open(self.metaplot_path, "r") as f:
                metaplot_data = json.load(f)
        else:
            metaplot_data = {}

        metaplot_data[hash_value] = {
            "titel": titel,
            "start_date": date_range['start'],
            "end_date": date_range['end'],
            "erstellt_am": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(self.metaplot_path, "w") as f:
            json.dump(metaplot_data, f, indent=4)
