import tkinter as tk
from tkinter import ttk
import json

class UIComponents:
    def __init__(self, master, csv_import_callback, config_callback, end_session_callback):
        self.metadata = None
        self.master = master
        self.csv_import_callback = csv_import_callback
        self.config_callback = config_callback
        self.end_session_callback = end_session_callback
        self.timeseries_buttons = {}
        self.load_metadata()

    def load_metadata(self):
        try:
            with open('metadata.json', 'r') as f:
                self.metadata = json.load(f)
        except FileNotFoundError:
            self.metadata = {"available_intervals": []}

    def create_buttons(self):
        button_frame = ttk.Frame(self.master)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        buttons = [
            ("CSV Import", self.csv_import_callback),
            ("Datumsauswahl", self.date_selection),
            ("Dateiwatcher", self.file_watcher),
            ("Einstellungen", self.config_callback),
            ("Sitzung beenden", self.end_session_callback)
        ]

        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

        self.timeseries_frame = ttk.Frame(self.master)
        self.timeseries_frame.pack(fill=tk.X, padx=10, pady=5)

        self.all_button = ttk.Button(self.timeseries_frame, text="Alle anzeigen", command=self.show_all)
        self.all_button.pack(side=tk.LEFT, padx=5)

        self.create_interval_buttons()

    def create_interval_buttons(self):
        for interval in self.metadata['available_intervals']:
            self.update_timeseries_buttons(interval)

    def update_timeseries_buttons(self, new_timeseries):
        if new_timeseries not in self.timeseries_buttons:
            btn = ttk.Button(self.timeseries_frame, text=new_timeseries, command=lambda ts=new_timeseries: self.show_timeseries(ts))
            btn.pack(side=tk.LEFT, padx=5)
            self.timeseries_buttons[new_timeseries] = btn

    def show_all(self):
        print("Zeige alle Zeitreihen")

    def show_timeseries(self, timeseries):
        print(f"Zeige Zeitreihe: {timeseries}")

    def csv_import(self):
        print("CSV Import clicked")

    def date_selection(self):
        print("Datumsauswahl clicked")

    def file_watcher(self):
        print("Dateiwatcher clicked")

    def open_config(self):
        print("Einstellungen clicked")

    def end_session(self):
        print("Sitzung beenden clicked")
