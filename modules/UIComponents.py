import hashlib
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import json
import os
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkhtmlview import HTMLLabel

from modules.PlotChartLine import PlotChartLine


class UIComponents:
    def __init__(self, master, csv_import_callback, config_callback, end_session_callback):
        # Main window and callbacks
        self.master = master
        self.csv_import_callback = csv_import_callback
        self.config_callback = config_callback
        self.end_session_callback = end_session_callback

        # UI elements
        self.chart_label = None
        self.alle_anzeigen_button = None
        self.date_range_label = None
        self.timeseries_frame = None
        self.update_plot_button = None
        self.hyperlink_label = None
        self.hyperlink_frame = None

        # Data and configuration
        self.farbschemata = None
        self.metadaten = None
        self.config = None
        self.config_color_schemes = None
        self.zeitreihen_checkboxen = {}
        self.aktive_zeitreihen = set()

        # Initialization
        self.lade_metadaten()
        self.lade_farbschemata()
        self.lade_config()

    def lade_config(self):
        # Load configuration from JSON file
        with open('config/config.json', 'r') as f:
            self.config = json.load(f)
            self.config_color_schemes = self.config['color_scheme']

    def lade_metadaten(self):
        # Load metadata from JSON file
        try:
            with open('metadata.json', 'r') as f:
                self.metadaten = json.load(f)
        except FileNotFoundError:
            self.metadaten = {"available_intervals": []}

    def lade_farbschemata(self):
        # Load color schemes from JSON file
        with open('resources/color_schemes.json', 'r') as f:
            self.farbschemata = json.load(f)

    def erstelle_buttons(self):
        # Create main buttons and UI elements
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

        self.date_range_label = ttk.Label(button_frame, text=self.get_date_range_text())
        self.date_range_label.pack(side=tk.LEFT, padx=5)

        style = ttk.Style()
        style.configure("Red.TButton", foreground="red", font=("Arial", 10, "bold"))
        end_session_btn = ttk.Button(button_frame, text="Sitzung beenden", command=self.end_session_callback, style="Red.TButton")
        end_session_btn.pack(side=tk.RIGHT, padx=5)

        self.timeseries_frame = ttk.Frame(self.master)
        self.timeseries_frame.pack(fill=tk.X, padx=10, pady=5)
        self.alle_anzeigen_button = ttk.Button(self.timeseries_frame, text="Alle anzeigen", command=self.zeige_alle)
        self.alle_anzeigen_button.pack(side=tk.LEFT, padx=5)
        self.update_plot_button = ttk.Button(self.timeseries_frame, text="Chart-Plotten", command=self.update_plot)
        self.update_plot_button.pack(side=tk.LEFT, padx=5)
        self.erstelle_intervall_checkboxen()

    def platzhalter_bild_anzeigen(self):
        # Display placeholder image
        placeholder_image = Image.open("charts_by_ki.jpg")
        placeholder_photo = ImageTk.PhotoImage(placeholder_image)
        placeholder_label = ttk.Label(self.chart_frame, image=placeholder_photo)
        placeholder_label.image = placeholder_photo
        placeholder_label.pack(fill="both", expand=True)

    def get_plot_files(self):
        plot_dir = "./plots"
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        return [f for f in os.listdir(plot_dir) if f.endswith('.html')]

    def create_hyperlink_area(self):
        self.hyperlink_frame = ttk.Frame(self.master)
        self.hyperlink_frame.pack(fill=tk.X, padx=10, pady=5)
        self.hyperlink_label = ttk.Label(self.hyperlink_frame, text="Verfügbare Plots:")
        self.hyperlink_label.pack(side=tk.LEFT, padx=5)

    def update_hyperlinks(self):
        plot_files = self.get_plot_files()
        for widget in self.hyperlink_frame.winfo_children()[1:]:
            widget.destroy()
        for plot_file in plot_files:
            link = ttk.Label(self.hyperlink_frame, text=plot_file, foreground="blue", cursor="hand2")
            link.pack(side=tk.LEFT, padx=5)
            link.bind("<Button-1>", lambda e, pf=plot_file: self.open_plot(pf))

    def open_plot(self, plot_file):
        import webbrowser
        webbrowser.open(os.path.join("plots", plot_file))

    def update_plot(self):
        # Update the plot based on selected time series and date range
        active_series = self.hole_aktive_zeitreihen()
        date_range = self.metadaten['date_range']
        markt_symbol = self.metadaten['symbols'][0]

        if len(active_series) == 0:
            messagebox.showinfo("Info", "Bitte wählen Sie mindestens eine Zeitreihe aus.")
            return

        start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
        end_date = datetime.strptime(date_range['end'], '%Y-%m-%d')
        date_diff = (end_date - start_date).days

        if date_diff > 5:
            messagebox.showinfo("Info", "Bitte wählen Sie einen Datumsbereich zwischen 1 bis 5 Tagen.")
            return

        chart_data = self.prepare_chart_data(active_series, date_range, markt_symbol)
        print(f"Aktualisiere Plot {markt_symbol} mit Zeitreihen: {active_series} und Datumsbereich: {date_range}")

        if len(chart_data) > 0:
            chart_creator = PlotChartLine()
            result_fig = chart_creator.create_chart(chart_data, date_range)
            self.update_metaplot(result_fig[1], result_fig[2], date_range)
            result_fig[0].show()
        else:
            self.platzhalter_bild_anzeigen()

    def prepare_chart_data(self, active_series, date_range, symbol):
        # Prepare data for chart creation
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
        # Get formatted date range text
        start = self.metadaten['date_range']['start']
        end = self.metadaten['date_range']['end']
        return f"Datumsbereich: {start} - {end}"

    def open_date_picker(self):
        # Open date picker window
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
        # Update interval checkboxes
        self.lade_config()
        selected_scheme = self.config_color_schemes
        print(f"Farbschemata neu: {selected_scheme}")
        colors = self.farbschemata['schemes'][selected_scheme]['colors']

        for intervall in intervalle:
            farbe = colors.get(intervall, '#000000')
            style = ttk.Style()
            style.configure(f'{intervall}.TCheckbutton', background=farbe)

            if intervall not in self.zeitreihen_checkboxen:
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(self.timeseries_frame, text=intervall, variable=var,
                                     command=lambda i=intervall: self.aktualisiere_aktive_zeitreihen(i),
                                     style=f'{intervall}.TCheckbutton')
                cb.pack(side=tk.LEFT, padx=5)
                self.zeitreihen_checkboxen[intervall] = (cb, var, farbe)
            else:
                cb, var, _ = self.zeitreihen_checkboxen[intervall]
                cb.configure(style=f'{intervall}.TCheckbutton')
                self.zeitreihen_checkboxen[intervall] = (cb, var, farbe)

    def erstelle_intervall_checkboxen(self):
        # Create interval checkboxes
        self.lade_config()
        selected_scheme = self.config_color_schemes
        print(f"Farbschemata alt: {selected_scheme}")
        colors = self.farbschemata['schemes'][selected_scheme]['colors']

        for intervall in self.metadaten['available_intervals']:
            var = tk.BooleanVar()
            farbe = colors.get(intervall, '#000000')
            style = ttk.Style()
            style.configure(f'{intervall}.TCheckbutton', background=farbe)
            cb = ttk.Checkbutton(self.timeseries_frame, text=intervall, variable=var,
                                 command=lambda i=intervall: self.aktualisiere_aktive_zeitreihen(i),
                                 style=f'{intervall}.TCheckbutton')
            cb.pack(side=tk.LEFT, padx=5)
            self.zeitreihen_checkboxen[intervall] = (cb, var, farbe)

    def aktualisiere_aktive_zeitreihen(self, intervall):
        # Update active time series set
        if self.zeitreihen_checkboxen[intervall][1].get():
            self.aktive_zeitreihen.add(intervall)
        else:
            self.aktive_zeitreihen.remove(intervall)
        print(f"Aktive Zeitreihen: {self.aktive_zeitreihen}")

    def update_date_range(self, start_date, end_date, window):
        # Update date range and close date picker window
        self.metadaten['date_range']['start'] = start_date.strftime('%Y-%m-%d')
        self.metadaten['date_range']['end'] = end_date.strftime('%Y-%m-%d')
        self.date_range_label.config(text=self.get_date_range_text(), font=("Arial", 12, "bold"))
        print(f"Neuer Datumsbereich: {self.metadaten['date_range']}")
        window.destroy()

    def zeige_alle(self):
        # Toggle all time series checkboxes
        all_active = all(self.zeitreihen_checkboxen[intervall][1].get() for intervall in self.zeitreihen_checkboxen)

        for intervall, (cb, var, _) in self.zeitreihen_checkboxen.items():
            var.set(not all_active)
            self.aktualisiere_aktive_zeitreihen(intervall)

        print("Alle Zeitreihen aktiviert" if not all_active else "Alle Zeitreihen deaktiviert")

    def hole_aktive_zeitreihen(self):
        return [(zr, self.zeitreihen_checkboxen[zr][2]) for zr in self.aktive_zeitreihen]

    def update_metaplot(self, hash_value, titel, date_range):
        metaplot_path = "./metaplot.json"
        if os.path.exists(metaplot_path):
            with open(metaplot_path, "r") as f:
                metaplot_data = json.load(f)
        else:
            metaplot_data = {}

        metaplot_data[hash_value] = {
            "titel": titel,
            "start_date": date_range['start'],
            "end_date": date_range['end']
        }

        with open(metaplot_path, "w") as f:
            json.dump(metaplot_data, f, indent=4)
