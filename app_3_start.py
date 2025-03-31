# app_1.start.py

import tkinter as tk
import os
import json
from modules.config_window import ConfigWindow


def check_config(root):
    if not os.path.exists("config/config.json"):
        ConfigWindow(root)
    else:
        # Hier können Sie die Konfiguration laden und verwenden
        with open("config/config.json", "r") as f:
            config = json.load(f)
        print("Konfiguration geladen:", config)


class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("Zeitreihen-Visualisierungs-App")
        self.master.geometry("1200x800")

        self.create_widgets()
        check_config(self.master)

    def create_widgets(self):
        # Hier fügen Sie die Hauptelemente Ihrer Anwendung hinzu
        tk.Button(self.master, text="Konfiguration öffnen", command=self.open_config).pack()

    def open_config(self):
        ConfigWindow(self.master)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
