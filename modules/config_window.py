# modules/config_window.py

import tkinter as tk
from tkinter import filedialog, messagebox
import json


class ConfigWindow:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Konfiguration")
        self.window.geometry("750x450")
        self.create_widgets()

    def create_widgets(self):
        # CSV-Import-Einstellungen
        tk.Label(self.window, text="CSV-Trennzeichen:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.delimiter_entry = tk.Entry(self.window, width=60)  # Breiter
        self.delimiter_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.delimiter_entry.insert(0, ",")

        tk.Label(self.window, text="Spaltennamen:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.columns_entry = tk.Entry(self.window, width=60)  # Breiter
        self.columns_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.columns_entry.insert(0, "Datum,Open,High,Low,Close,Volume")

        tk.Label(self.window, text="Datumsformat:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.date_format_entry = tk.Entry(self.window, width=60)  # Breiter
        self.date_format_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.date_format_entry.insert(0, "%Y-%m-%d %H:%M:%S")

        # Dateiwatcher-Einstellungen
        tk.Label(self.window, text="Überwachter Ordner:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.folder_entry = tk.Entry(self.window, width=60)  # Breiter
        self.folder_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        tk.Button(self.window, text="Durchsuchen", command=self.browse_folder, bg='lightblue').grid(row=3, column=3, padx=5, pady=5)

        tk.Label(self.window, text="Aktualisierungsintervall (s):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.interval_entry = tk.Entry(self.window, width=60)  # Breiter
        self.interval_entry.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.interval_entry.insert(0, "60")

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=5, column=0, columnspan=4, pady=20)

        tk.Button(button_frame, text="Speichern", command=self.save_config, bg='lightgreen').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Laden", command=self.load_config, bg='lightyellow').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Zurücksetzen", command=self.reset_fields, bg='lightpink').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Abbrechen", command=self.close_clicked, bg='salmon').pack(side=tk.LEFT, padx=5)

    def close_clicked(self):
        self.window.destroy()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, folder)

    def save_config(self):
        config = {
            "delimiter": self.delimiter_entry.get(),
            "columns": self.columns_entry.get().split(","),
            "date_format": self.date_format_entry.get(),
            "watch_folder": self.folder_entry.get(),
            "update_interval": int(self.interval_entry.get())
        }

        with open("config/config.json", "w") as f:
            json.dump(config, f, indent=4)

        messagebox.showinfo("Info", "Konfiguration gespeichert!")
        self.window.destroy()

    def load_config(self):
        try:
            with open("config/config.json", "r") as f:
                config = json.load(f)

            self.delimiter_entry.delete(0, tk.END)
            self.delimiter_entry.insert(0, config["delimiter"])

            self.columns_entry.delete(0, tk.END)
            self.columns_entry.insert(0, ",".join(config["columns"]))

            self.date_format_entry.delete(0, tk.END)
            self.date_format_entry.insert(0, config["date_format"])

            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, config["watch_folder"])

            self.interval_entry.delete(0, tk.END)
            self.interval_entry.insert(0, str(config["update_interval"]))

        except FileNotFoundError:
            messagebox.showerror("Fehler", "Keine Konfigurationsdatei gefunden!")

    def reset_fields(self):
        self.delimiter_entry.delete(0, tk.END)
        self.delimiter_entry.insert(0, ",")
        self.columns_entry.delete(0, tk.END)
        self.columns_entry.insert(0, "Datum,Open,High,Low,Close")
        self.date_format_entry.delete(0, tk.END)
        self.date_format_entry.insert(0, "%Y-%m-%d %H:%M:%S")
        self.folder_entry.delete(0, tk.END)
        self.interval_entry.delete(0, tk.END)
        self.interval_entry.insert(0, "60")
