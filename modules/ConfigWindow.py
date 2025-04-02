# modules/ConfigWindow.py
import tkinter as tk
from tkinter import messagebox, ttk
import json


class ConfigWindow:
    def __init__(self, master, update_callback, config_path, color_schemes_path):
        # Initialisierung des Konfigurationsfensters
        self.config_path = config_path
        self.color_schemes_path = color_schemes_path
        self.window_y_entry = None
        self.window_x_entry = None
        self.color_scheme_dropdown = None
        self.date_format_entry = None
        self.columns_entry = None
        self.delimiter_entry = None
        self.color_scheme_var = None
        self.master = master
        self.update_callback = update_callback
        self.window = tk.Toplevel(master)
        self.window.title("Konfiguration")
        self.window.geometry("750x450")
        self.color_schemes = self.load_color_schemes()
        self.create_widgets()
        self.create_color_scheme_dropdown()
        self.center_window()

    def load_color_schemes(self):
        # Laden der Farbschemata aus einer JSON-Datei
        with open(self.color_schemes_path, 'r') as f:
            return json.load(f)

    def create_widgets(self):
        # Erstellen der Eingabefelder und Labels für die Konfiguration

        # CSV-Import-Einstellungen
        tk.Label(self.window, text="CSV-Trennzeichen:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.delimiter_entry = tk.Entry(self.window, width=60)
        self.delimiter_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.delimiter_entry.insert(0, "\t")

        tk.Label(self.window, text="Spaltennamen:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.columns_entry = tk.Entry(self.window, width=60)
        self.columns_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.columns_entry.insert(0, "DATE,TIME,OPEN,HIGH,LOW,CLOSE,TICKVOL,VOL,SPREAD")

        tk.Label(self.window, text="Datumsformat:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.date_format_entry = tk.Entry(self.window, width=60)
        self.date_format_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.date_format_entry.insert(0, "%Y.%m.%d %H:%M:%S")

        # Startfenster-Größe
        tk.Label(self.window, text="Startfenster Breite / Länge:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.window_x_entry = tk.Entry(self.window, width=20)
        self.window_x_entry.grid(row=3, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        self.window_x_entry.insert(0, "1200")

        self.window_y_entry = tk.Entry(self.window, width=20)
        self.window_y_entry.grid(row=3, column=2, columnspan=1, padx=5, pady=5, sticky="ew")
        self.window_y_entry.insert(0, "800")

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=6, column=0, columnspan=4, pady=20)

        tk.Button(button_frame, text="Speichern", command=self.save_config, bg='green').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Laden", command=self.load_config, bg='lightyellow').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Zurücksetzen", command=self.reset_fields, bg='lightpink').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Abbrechen", command=self.close_clicked, bg='red').pack(side=tk.LEFT, padx=5)

    def create_color_scheme_dropdown(self):
        # Erstellen des Dropdown-Menüs für Farbschemata
        tk.Label(self.window, text="Farbschema:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.color_scheme_var = tk.StringVar()
        self.color_scheme_dropdown = ttk.Combobox(self.window, textvariable=self.color_scheme_var, state="readonly")
        self.color_scheme_dropdown['values'] = list(self.color_schemes['schemes'].keys())
        self.color_scheme_dropdown.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.color_scheme_dropdown.bind("<<ComboboxSelected>>", self.update_color_preview)
        self.color_scheme_var.set(self.color_schemes['default'])
        self.update_color_preview()

    def update_color_preview(self, event=None):
        # Aktualisieren der Farbvorschau basierend auf dem ausgewählten Farbschema
        selected_scheme = self.color_scheme_var.get()
        colors = self.color_schemes['schemes'][selected_scheme]['colors']
        color_frame = tk.Frame(self.window)
        color_frame.grid(row=8, column=1, columnspan=3, sticky='nsew')

        for i, (interval, color) in enumerate(colors.items()):
            label = tk.Label(color_frame, text=interval, bg=color, width=10, wraplength=60, justify='center')
            label.grid(row=i // 6, column=i % 6, padx=2, pady=2, sticky='nsew')

    def close_clicked(self):
        # Schließen des Konfigurationsfensters
        self.window.destroy()

    def save_config(self):
        # Speichern der Konfiguration in eine JSON-Datei
        config = {
            "delimiter": self.delimiter_entry.get(),
            "columns": self.columns_entry.get().split(","),
            "date_format": self.date_format_entry.get(),
            "color_scheme": self.color_scheme_var.get(),
            "window_y": self.window_y_entry.get(),
            "window_x": self.window_x_entry.get()
        }

        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)

        self.update_callback()
        messagebox.showinfo("Info", "Konfiguration gespeichert!")
        self.window.destroy()

    def load_config(self):
        # Laden der Konfiguration aus einer JSON-Datei
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)

            self.delimiter_entry.delete(0, tk.END)
            self.delimiter_entry.insert(0, config["delimiter"])

            self.columns_entry.delete(0, tk.END)
            self.columns_entry.insert(0, ",".join(config["columns"]))

            self.date_format_entry.delete(0, tk.END)
            self.date_format_entry.insert(0, config["date_format"])

            self.window_x_entry.delete(0, tk.END)
            self.window_x_entry.insert(0, config["window_x"])

            self.window_y_entry.delete(0, tk.END)
            self.window_y_entry.insert(0, config["window_y"])

            if "color_scheme" in config:
                self.color_scheme_var.set(config["color_scheme"])
                self.update_color_preview()

        except FileNotFoundError:
            messagebox.showerror("Fehler", "Keine Konfigurationsdatei gefunden!")

    def reset_fields(self):
        # Zurücksetzen aller Eingabefelder auf Standardwerte
        self.delimiter_entry.delete(0, tk.END)
        self.delimiter_entry.insert(0, "\\t")
        self.columns_entry.delete(0, tk.END)
        self.columns_entry.insert(0, "DATE,TIME,OPEN,HIGH,LOW,CLOSE,TICKVOL,VOL,SPREAD")
        self.date_format_entry.delete(0, tk.END)
        self.date_format_entry.insert(0, "%Y.%m.%d %H:%M:%S")
        self.window_x_entry.delete(0, tk.END)
        self.window_x_entry.insert(0, "1000")
        self.window_y_entry.delete(0, tk.END)
        self.window_y_entry.insert(0, "600")

    def center_window(self):
        # Zentrieren des Konfigurationsfensters auf dem Bildschirm
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
