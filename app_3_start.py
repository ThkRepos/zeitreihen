import tkinter as tk
import os
from tkinter import ttk, filedialog, messagebox
import json
from modules.ConfigWindow import ConfigWindow
from modules.UIComponents import UIComponents
from modules.DataImporter import DataImporter
from modules.MetadataManager import MetadataManager


class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("Zeitreihen-Visualisierungs-App")
        self.master.geometry("1200x800")
        self.center_window()
        self.config = self.load_config()
        self.metadata_manager = MetadataManager('metadata.json')
        self.data_importer = DataImporter(self.config)
        self.ui_components = UIComponents(self.master, self.csv_import, self.open_config, self.end_session)
        self.create_widgets()
        self.existing_data = self.load_existing_data()
        self.update_ui_with_existing_data()

    def update_ui_with_existing_data(self):
        for symbol, interval in self.existing_data:
            timeseries_name = f"{interval}"
            self.ui_components.update_timeseries_buttons(timeseries_name)

    def center_window(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2
        self.master.geometry(f"1200x800+{x}+{y}")

    def create_widgets(self):
        self.ui_components.create_buttons()

    def load_config(self):
        with open('config/config.json', 'r') as f:
            return json.load(f)

    def open_config(self):
        ConfigWindow(self.master)
        print("Konfigurationsfenster wird geöffnet")

    def end_session(self):
        if tk.messagebox.askyesno("Sitzung beenden", "Möchten Sie die Sitzung wirklich beenden?"):
            self.master.quit()

    def load_existing_data(self):
        existing_data = []
        for file in os.listdir(self.data_importer.data_dir):
            if file.endswith('.parquet'):
                symbol, interval = file.split('_')
                interval = interval.split('.')[0]
                existing_data.append((symbol, interval))
        return sorted(existing_data)

    def csv_import(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        for file_path in file_paths:
            df, symbol, interval, start_date, end_date = self.data_importer.import_csv(file_path)
            # print(f"Daten importiert für {symbol} {interval} \n Startdatum: {start_date}, Enddatum: {end_date}\ndf: {df}")
            if df is not None:
                self.metadata_manager.update_metadata(symbol, interval, start_date, end_date, file_path)
                print(f"Daten importiert für {symbol} {interval}")

                timeseries_name = f"{interval}"
                self.ui_components.update_timeseries_buttons(timeseries_name)

        if file_paths:
            print(f"{len(file_paths)} Datei(en) erfolgreich importiert.")


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
