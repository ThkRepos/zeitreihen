import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter import messagebox
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
            aktualisiere_intervalle(intervalle): Aktualisiert die Zeitreihen-Checkboxen.
            update_plot(): Aktualisiert das angezeigte Diagramm.
            open_date_picker(): Öffnet den Datumswähler.
            zeige_alle(): Schaltet alle Zeitreihen-Checkboxen um.
        """

    def __init__(self, master, csv_import_callback, config_callback, end_session_callback):
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
        self.metaplot_path = os.path.abspath("./metaplot.json")
        self.farbschemata = None
        self.metadaten = {"available_intervals": []}
        self.config = None
        self.config_color_schemes = None
        self.zeitreihen_checkboxen = {}
        self.aktive_zeitreihen = set()

        # Laden der Konfigurationen und Metadaten
        self.config = lade_json(os.path.abspath('./config/config.json'))
        self.config_color_schemes = self.config['color_scheme']
        self.metadaten = lade_json(os.path.abspath('./metadata.json'))
        self.farbschemata = lade_json(os.path.abspath('./resources/color_schemes.json'))

    def erstelle_buttons(self):
        # Erstellen der Hauptbuttons und UI-Elemente
        button_frame = ttk.Frame(self.master)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        buttons = [
            ("CSV Import", self.csv_import_callback),
            ("Datumsauswahl", self.open_date_picker),
            ("Einstellungen", self.config_callback)
        ]

        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

        # Anzeige des aktuellen Datumsbereichs
        self.date_range_label = ttk.Label(button_frame, text=self.get_date_range_text())
        self.date_range_label.pack(side=tk.LEFT, padx=5)

        # Erstellung des "Sitzung beenden" Buttons
        style = ttk.Style()
        style.configure("Red.TButton", foreground="red", font=("Arial", 10, "bold"))
        end_session_btn = ttk.Button(button_frame, text="Sitzung beenden", command=self.end_session_callback, style="Red.TButton")
        end_session_btn.pack(side=tk.RIGHT, padx=5)

        # Erstellung des Rahmens für Zeitreihen-Checkboxen
        self.timeseries_frame = ttk.Frame(self.master)
        self.timeseries_frame.pack(fill=tk.X, padx=10, pady=5)
        self.alle_anzeigen_button = ttk.Button(self.timeseries_frame, text="Alle anzeigen", command=self.zeige_alle)
        self.alle_anzeigen_button.pack(side=tk.LEFT, padx=5)
        self.update_plot_button = ttk.Button(self.timeseries_frame, text="Chart-Plotten", command=self.update_plot)
        self.update_plot_button.pack(side=tk.LEFT, padx=5)
        self.erstelle_intervall_checkboxen()

    def get_plot_files(self):
        # Abrufen der verfügbaren Plot-Dateien
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)
        return [f for f in os.listdir(self.plot_dir) if f.endswith('.html')]

    def create_hyperlink_area(self):
        # Füge einen Separator oberhalb des hyperlink_frame hinzu
        separator = ttk.Separator(self.master, orient='horizontal')
        separator.pack(fill='x', pady=(5, 0))
        # Erstellen des Bereichs für Hyperlinks zu verfügbaren Plots
        self.hyperlink_frame = ttk.Frame(self.master)
        self.hyperlink_frame.pack(fill=tk.X, padx=10, pady=5)
        self.hyperlink_label = ttk.Label(self.hyperlink_frame, text="Verfügbare Plots:")
        self.hyperlink_label.pack(side=tk.LEFT, padx=5)

    def update_hyperlinks(self):
        # Laden der metaplot.json Daten
        with open(self.metaplot_path, 'r') as f:
            metaplot_data = json.load(f)

        # Aktualisieren der Hyperlinks zu verfügbaren Plots
        plot_files = self.get_plot_files()
        for widget in self.hyperlink_frame.winfo_children()[1:]:
            widget.destroy()

        for plot_file in plot_files:
            hash_value = plot_file.split('.')[0]  # Entfernen der .html Erweiterung
            if hash_value in metaplot_data:
                title = metaplot_data[hash_value]['titel']
            else:
                title = plot_file  # Fallback auf den Dateinamen, falls kein Eintrag gefunden

            link = ttk.Label(self.hyperlink_frame, text=title, foreground="blue", cursor="hand2")
            link.pack(side=tk.LEFT, padx=5)
            link.bind("<Button-1>", lambda e, pf=plot_file: self.open_plot(pf))
            link.bind("<Enter>", lambda e, l=link: l.configure(foreground="orange"))
            link.bind("<Leave>", lambda e, l=link: l.configure(foreground="blue"))

    def open_plot(self, plot_file):
        # Öffnen des ausgewählten Plots im Webbrowser
        self.update_hyperlinks()
        import webbrowser
        webbrowser.open(os.path.join("plots", plot_file))

    def update_plot(self):
        # Aktualisieren des Plots basierend auf ausgewählten Zeitreihen und Datumsbereich
        active_series = self.hole_aktive_zeitreihen()
        date_range = self.metadaten['date_range']
        markt_symbol = self.metadaten['symbols'][0]

        if len(active_series) == 0:
            messagebox.showinfo("Info", f"Bitte wählen Sie mindestens eine Zeitreihe aus.")
            return

        start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
        end_date = datetime.strptime(date_range['end'], '%Y-%m-%d')
        date_diff = (end_date - start_date).days

        if date_diff > 5:
            messagebox.showinfo("Info", "Bitte wählen Sie einen Datumsbereich zwischen 1 bis 5 Tagen.\nAktuell: " + str(date_diff) + " Tage")
            return

        chart_data = self.prepare_chart_data(active_series, date_range, markt_symbol)
        print(f"Aktualisiere Plot {markt_symbol} mit Zeitreihen: {active_series} und Datumsbereich: {date_range}")

        if len(chart_data) > 0:
            chart_creator = PlotChartLine(self.plot_dir)
            result_fig = chart_creator.create_chart(markt_symbol, chart_data, date_range)
            print(f"Daten: {result_fig[1]} / {result_fig[2]}")
            self.update_metaplot(titel=result_fig[1], hash_value=result_fig[2], date_range=date_range)
            self.update_hyperlinks()
        else:
            messagebox.showinfo("Info", "Keine Daten für den ausgewählten Datumsbereich verfügbar.")


    def prepare_chart_data(self, active_series, date_range, symbol):
        # Vorbereiten der Daten für die Charterstellung
        datum_von = pd.to_datetime(date_range['start'], format='%Y-%m-%d')
        datum_bis = pd.to_datetime(date_range['end'], format='%Y-%m-%d')

        chart_data_list = []

        for interval, color in active_series:
            file_name = f"{symbol}_{interval}.parquet"
            print("Verarbeite Datei:", file_name)
            file_path = os.path.join("./cache/data/", file_name)

            if os.path.exists(file_path):
                df = pd.read_parquet(file_path)
                df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d')
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
        start = self.metadaten['date_range']['start']
        end = self.metadaten['date_range']['end']
        return f"Datumsbereich: {start} - {end}"

    def open_date_picker(self):
        # Öffnen des Datumsauswahl-Fensters
        date_window = tk.Toplevel(self.master)
        date_window.title("Datumsauswahl")

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
        start_picker.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(date_window, text="Enddatum:").grid(row=1, column=0, padx=5, pady=5)
        end_picker = DateEntry(date_window, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        end_picker.set_date(end_date)
        end_picker.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(date_window,
                   text="Bestätigen",
                   command=lambda: self.update_date_range(start_picker.get_date(), end_picker.get_date(), date_window)).grid(row=2, column=0, columnspan=2, pady=10)

    def aktualisiere_intervalle(self, intervalle):
        # Aktualisiert die Intervall-Checkboxen durch Löschen und Neuerstellen.
        self.config = lade_json('config/config.json')
        self.config_color_schemes = self.config['color_scheme']
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
        #Erstellt die Intervall-Checkboxen mit aktualisierten Farben
        colors = self.farbschemata['schemes'][self.config_color_schemes]['colors']

        for intervall in self.metadaten['available_intervals']:
            var = tk.BooleanVar()
            farbe = colors.get(intervall, '#000000')
            cb = tk.Checkbutton(self.timeseries_frame,
                                text=intervall,
                                variable=var,
                                command=lambda i=intervall: self.aktualisiere_aktive_zeitreihen(i),
                                bg=farbe)
            cb.pack(side=tk.LEFT, padx=5)
            self.zeitreihen_checkboxen[intervall] = (cb, var, farbe)

        print("Intervall-Checkboxen neu erstellt")

    def aktualisiere_aktive_zeitreihen(self, intervall):
        # Aktualisieren der aktiven Zeitreihen
        if self.zeitreihen_checkboxen[intervall][1].get():
            self.aktive_zeitreihen.add(intervall)
        else:
            self.aktive_zeitreihen.remove(intervall)
        print(f"Aktive Zeitreihen: {self.aktive_zeitreihen}")

    def update_date_range(self, start_date, end_date, window):
        # Aktualisieren des Datumsbereichs und Schließen des Datumsauswahl-Fensters
        self.metadaten['date_range']['start'] = start_date.strftime('%Y-%m-%d')
        self.metadaten['date_range']['end'] = end_date.strftime('%Y-%m-%d')
        self.date_range_label.config(text=self.get_date_range_text(), font=("Arial", 12, "bold"))
        print(f"Neuer Datumsbereich: {self.metadaten['date_range']}")
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
            "end_date": date_range['end']
        }

        with open(self.metaplot_path, "w") as f:
            json.dump(metaplot_data, f, indent=4)
