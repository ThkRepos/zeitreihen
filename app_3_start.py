import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
from modules.UIComponents import UIComponents
from modules.DataImporter import DataImporter
from modules.MetadataManager import MetadataManager
from modules.ConfigWindow import ConfigWindow


class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("Zeitreihen-Visualisierungs-App")
        self.master.geometry("1200x800")
        self.center_window()
        self.config = self.lade_config()
        self.metadata_manager = MetadataManager('metadata.json')
        self.data_importer = DataImporter(self.config)

        self.ui_components = UIComponents(self.master, self.csv_import, self.open_config, self.end_session)
        self.create_widgets()

    def center_window(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2
        self.master.geometry(f"1200x800+{x}+{y}")

    def create_widgets(self):
        self.ui_components.erstelle_buttons()
        self.ui_components.chart_label = tk.Label(self.master)
        self.ui_components.chart_label.pack(expand=True, fill=tk.BOTH)
        self.platzhalter_bild_anzeigen()

    def lade_config(self):
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        config['delimiter'] = config['delimiter']
        return config

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
        ConfigWindow(self.master, self.aktualisiere_zeitreihen_checkboxen)

    def end_session(self):
        if messagebox.askyesno("Sitzung beenden", "Möchten Sie die Sitzung wirklich beenden?"):
            self.master.quit()

    def platzhalter_bild_anzeigen(self):
        placeholder_image = Image.open("charts_by_ki.jpg")
        placeholder_photo = ImageTk.PhotoImage(placeholder_image)
        self.ui_components.chart_label.config(image=placeholder_photo)
        self.ui_components.chart_label.image = placeholder_photo

    def update_chart(self):
        # Ihre bestehende Logik zur Diagrammerstellung hier
        chart_erstellt = False  # Diese Variable sollte auf True gesetzt werden, wenn ein Diagramm erstellt wurde
        if chart_erstellt:
            # Zeigen Sie das erstellte Diagramm an
            pass
        else:
            self.platzhalter_bild_anzeigen()


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
