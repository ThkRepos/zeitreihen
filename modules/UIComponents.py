import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter import messagebox
import json

from tkcalendar import DateEntry


class UIComponents:
    def __init__(self, master, csv_import_callback, config_callback, end_session_callback):
        self.chart_label = None
        self.alle_anzeigen_button = None
        self.date_range_label = None
        self.timeseries_frame = None
        self.update_plot_button = None
        self.farbschemata = None
        self.metadaten = None
        self.config = None
        self.config_color_schemes = None
        self.master = master
        self.csv_import_callback = csv_import_callback
        self.config_callback = config_callback
        self.end_session_callback = end_session_callback
        self.zeitreihen_checkboxen = {}
        self.aktive_zeitreihen = set()
        self.lade_metadaten()
        self.lade_farbschemata()
        self.lade_config()

    def lade_config(self):
        with open('config/config.json', 'r') as f:
            self.config = json.load(f)
            self.config_color_schemes = self.config['color_scheme']

    def lade_metadaten(self):
        try:
            with open('metadata.json', 'r') as f:
                self.metadaten = json.load(f)
        except FileNotFoundError:
            self.metadaten = {"available_intervals": []}

    def lade_farbschemata(self):
        with open('resources/color_schemes.json', 'r') as f:
            self.farbschemata = json.load(f)

    def erstelle_buttons(self):
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

    def update_plot(self):
        active_series = self.hole_aktive_zeitreihen()
        date_range = self.metadaten['date_range']

        if len(active_series) == 0:
            messagebox.showinfo("Info", "Bitte wählen Sie mindestens eine Zeitreihe aus.")
            return

        start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
        end_date = datetime.strptime(date_range['end'], '%Y-%m-%d')
        date_diff = (end_date - start_date).days

        if date_diff > 5:
            messagebox.showinfo("Info", "Bitte wählen Sie einen Datumsbereich zwischen 1 bis 5 Tagen.")
            return

        print(f"Aktualisiere Plot mit Zeitreihen: {active_series} und Datumsbereich: {date_range}")
        # Hier würden Sie die Plotting-Funktion aufrufen

    def get_date_range_text(self):
        start = self.metadaten['date_range']['start']
        end = self.metadaten['date_range']['end']
        return f"Datumsbereich: {start} - {end}"

    def open_date_picker(self):
        date_window = tk.Toplevel(self.master)
        date_window.title("Datumsauswahl")

        # Fenster zentrieren
        date_window.update_idletasks()
        width = date_window.winfo_width()
        height = date_window.winfo_height()
        x = (date_window.winfo_screenwidth() // 2) - (width // 2)
        y = (date_window.winfo_screenheight() // 2) - (height // 2)
        date_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        # Datumsauswahl
        start_date = datetime.strptime(self.metadaten['date_range']['start'], '%Y-%m-%d').date()
        end_date = datetime.strptime(self.metadaten['date_range']['end'], '%Y-%m-%d').date()
        # Erstelle die Widgets
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
        if self.zeitreihen_checkboxen[intervall][1].get():
            self.aktive_zeitreihen.add(intervall)
        else:
            self.aktive_zeitreihen.remove(intervall)
        print(f"Aktive Zeitreihen: {self.aktive_zeitreihen}")

    def update_date_range(self, start_date, end_date, window):
        self.metadaten['date_range']['start'] = start_date.strftime('%Y-%m-%d')
        self.metadaten['date_range']['end'] = end_date.strftime('%Y-%m-%d')
        self.date_range_label.config(text=self.get_date_range_text(), font=("Arial", 12, "bold"))
        print(f"Neuer Datumsbereich: {self.metadaten['date_range']}")
        window.destroy()

    def zeige_alle(self):
        all_active = all(self.zeitreihen_checkboxen[intervall][1].get() for intervall in self.zeitreihen_checkboxen)

        for intervall, (cb, var, _) in self.zeitreihen_checkboxen.items():
            var.set(not all_active)
            self.aktualisiere_aktive_zeitreihen(intervall)

        print("Alle Zeitreihen aktiviert" if not all_active else "Alle Zeitreihen deaktiviert")

    def hole_aktive_zeitreihen(self):
        return [(zr, self.zeitreihen_checkboxen[zr][2]) for zr in self.aktive_zeitreihen]
