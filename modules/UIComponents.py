import tkinter as tk
from tkinter import ttk
import json


class UIComponents:
    def __init__(self, master, csv_import_callback, config_callback, end_session_callback):
        self.farbschemata = None
        self.metadaten = None
        self.config = None
        self.config_color_schemes = None
        self.master = master
        self.csv_import_callback = csv_import_callback
        self.config_callback = config_callback
        self.end_session_callback = end_session_callback
        self.zeitreihen_checkboxen = {}
        self.aktive_zeitreihen = []
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
            ("Datumsauswahl", self.datumsauswahl),
            # ("Dateiwatcher", self.dateiwatcher),
            ("Einstellungen", self.config_callback),
            ("Sitzung beenden", self.end_session_callback)
        ]

        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

        self.timeseries_frame = ttk.Frame(self.master)
        self.timeseries_frame.pack(fill=tk.X, padx=10, pady=5)

        self.alle_anzeigen_button = ttk.Button(self.timeseries_frame, text="Alle anzeigen", command=self.zeige_alle)
        self.alle_anzeigen_button.pack(side=tk.LEFT, padx=5)

        self.erstelle_intervall_checkboxen()

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
            self.aktive_zeitreihen.append(intervall)
        else:
            self.aktive_zeitreihen.remove(intervall)
        print(f"Aktive Zeitreihen: {self.aktive_zeitreihen}")

    def zeige_alle(self):
        print("Zeige alle Zeitreihen")

    def zeige_zeitreihe(self, zeitreihe):
        print(f"Zeige Zeitreihe: {zeitreihe}")

    def datumsauswahl(self):
        print("Datumsauswahl angeklickt")

    def dateiwatcher(self):
        print("Dateiwatcher angeklickt")

    def hole_aktive_zeitreihen(self):
        return [(zr, self.zeitreihen_checkboxen[zr][2]) for zr in self.aktive_zeitreihen]
