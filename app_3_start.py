import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
from modules.UIComponents import UIComponents
from modules.DataImporter import DataImporter
from modules.MetadataManager import MetadataManager
from modules.ConfigWindow import ConfigWindow


class Application:
    def __init__(self, master):
        self.color_schemes_path = os.path.abspath('resources/color_schemes.json')
        self.config_path = os.path.abspath('config/config.json')
        self.metadata_path = os.path.abspath('metadata.json')
        self.window_x = 1200
        self.window_y = 800
        self.config = self.lade_config()
        self.metadata_manager = MetadataManager(self.metadata_path)
        self.master = master
        self.master.title("Zeitreihen-Visualisierungs-App")
        self.master.geometry(f"{self.window_x}x{self.window_y}")
        self.center_window()
        self.data_importer = DataImporter(self.config)
        self.ui_components = UIComponents(self.master, self.csv_import, self.open_config, self.end_session)
        self.create_widgets()

    def lade_config(self):
        with open(self.config_path, 'r') as config_file:
            config = json.load(config_file)
            self.window_x = config['window_x']
            self.window_y = config['window_y']
        return config

    def center_window(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - int(self.window_x)) // 2
        y = (screen_height - int(self.window_y)) // 2
        self.master.geometry(f"{self.window_x}x{self.window_y}+{x}+{y}")

    def create_widgets(self):
        self.ui_components.erstelle_buttons()
        self.ui_components.create_hyperlink_area()
        self.ui_components.update_hyperlinks()

    def csv_import(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        for file_path in file_paths:
            df, symbol, interval, start_date, end_date = self.data_importer.import_csv(file_path)
            if df is not None:
                self.metadata_manager.update_metadata(symbol, interval, start_date, end_date, file_path)
                print(f"Daten importiert für {symbol} {interval}")
                self.aktualisiere_zeitreihen_checkboxen()

        if file_paths:
            print(f"{len(file_paths)} Datei(en) erfolgreich importiert.")

    def aktualisiere_zeitreihen_checkboxen(self):
        intervalle = self.metadata_manager.metadata['available_intervals']
        self.ui_components.aktualisiere_intervalle(intervalle)

    def open_config(self):
        ConfigWindow(self.master, self.aktualisiere_zeitreihen_checkboxen, self.config_path, self.color_schemes_path)

    def end_session(self):
        if messagebox.askyesno("Sitzung beenden", "Möchten Sie die Sitzung wirklich beenden?"):
            self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
