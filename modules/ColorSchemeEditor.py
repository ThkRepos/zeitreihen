import os
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, scrolledtext
import json


class ColorSchemeEditor:
    def __init__(self, master):
        self.data = None
        self.color_file = './resources/color_schemes.json'
        self.master = master
        self.master.title("Farbschema-Editor")
        self.load_json()
        self.create_widgets()
        self.center_window()

    def load_json(self):
        with open(self.color_file, 'r', encoding='utf-8') as file:
            self.data = json.load(file)

    def create_widgets(self):
        # Schema-Auswahl
        self.schema_var = tk.StringVar()
        self.schema_combo = ttk.Combobox(self.master, textvariable=self.schema_var)
        self.schema_combo['values'] = list(self.data['schemes'].keys())
        self.schema_combo.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        self.schema_combo.bind('<<ComboboxSelected>>', self.load_schema)

        # Name
        tk.Label(self.master, text="Name:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.name_entry = tk.Entry(self.master)
        self.name_entry.grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky='ew')

        # Beschreibung
        tk.Label(self.master, text="Beschreibung:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.desc_text = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, height=3)
        self.desc_text.grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky='ew')

        # Farbtabelle
        self.color_tree = ttk.Treeview(self.master, columns=('Unit', 'Color'), show='headings')
        self.color_tree.heading('Unit', text='Zeiteinheit')
        self.color_tree.heading('Color', text='Farbe')
        self.color_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        self.color_tree.bind('<<TreeviewSelect>>', self.select_color)

        # Farbbearbeitung
        self.color_frame = tk.Frame(self.master)
        self.color_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        tk.Label(self.color_frame, text="Zeit").grid(row=0, column=0)
        tk.Label(self.color_frame, text="Hexcode").grid(row=0, column=1)
        tk.Label(self.color_frame, text="Auswahl").grid(row=0, column=2)

        self.unit_entry = tk.Entry(self.color_frame)
        self.unit_entry.grid(row=1, column=0, padx=2)

        self.color_entry = tk.Entry(self.color_frame)
        self.color_entry.grid(row=1, column=1, padx=2)

        self.color_button = tk.Button(self.color_frame, width=3, command=self.choose_color)
        self.color_button.grid(row=1, column=2, padx=2)

        # Buttons
        self.button_frame = tk.Frame(self.master)
        self.button_frame.grid(row=7, column=0, columnspan=2, pady=20, sticky='ew')
        # Definieren Button-Stile
        button_style = {
            "font": ("Arial", 10),
            "relief": tk.RAISED,
            "borderwidth": 2,
            "cursor": "hand2",
            "width": 10
        }
        tk.Button(self.button_frame, text="Neue Farbe", command=self.add_new_color, bg='lightpink', **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Entfernen", command=self.remove_color, bg='lightblue', **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Speichern", command=self.save_changes, bg='green', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Abbrechen", command=self.abort, bg='red', fg='white', **button_style).pack(side=tk.RIGHT, padx=5)

    def abort(self):
        self.master.destroy()

    def load_schema(self, event):
        schema = self.schema_var.get()
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self.data['schemes'][schema]['name'])
        self.desc_text.delete('1.0', tk.END)
        self.desc_text.insert(tk.END, self.data['schemes'][schema]['description'])

        for item in self.color_tree.get_children():
            self.color_tree.delete(item)
        for unit, color in self.data['schemes'][schema]['colors'].items():
            self.color_tree.insert('', 'end', values=(unit, color))

    def select_color(self, event):
        selection = self.color_tree.selection()
        if selection:
            item = self.color_tree.item(selection[0])
            unit, color = item['values']
            self.unit_entry.delete(0, tk.END)
            self.unit_entry.insert(0, unit)
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, color)
            self.color_button.config(bg=color)

    def choose_color(self):
        color = colorchooser.askcolor(title="Wähle eine Farbe")
        if color[1]:
            self.color_button.config(bg=color[1])
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, color[1])

    def add_new_color(self):
        unit = self.unit_entry.get()
        color = self.color_entry.get()
        if unit and color:
            self.color_tree.insert('', 'end', values=(unit, color))
            schema = self.schema_var.get()
            self.data['schemes'][schema]['colors'][unit] = color

    def remove_color(self):
        selection = self.color_tree.selection()
        if selection:
            item = self.color_tree.item(selection[0])
            unit, _ = item['values']
            self.color_tree.delete(selection[0])
            schema = self.schema_var.get()
            if unit in self.data['schemes'][schema]['colors']:
                del self.data['schemes'][schema]['colors'][unit]
            self.unit_entry.delete(0, tk.END)
            self.color_entry.delete(0, tk.END)
            self.color_button.config(bg='SystemButtonFace')

    def save_changes(self):
        schema = self.schema_var.get()
        self.data['schemes'][schema]['name'] = self.name_entry.get()
        self.data['schemes'][schema]['description'] = self.desc_text.get('1.0', tk.END).strip()
        self.data['schemes'][schema]['colors'] = {}
        for item in self.color_tree.get_children():
            unit, color = self.color_tree.item(item)['values']
            self.data['schemes'][schema]['colors'][unit] = color

        with open(self.color_file, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=2, ensure_ascii=False)
        messagebox.showinfo("Gespeichert", "Änderungen wurden erfolgreich gespeichert.")

    def center_window(self):
        # Zentrieren des Fensters auf dem Bildschirm
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))

if __name__ == '__main__':
    root = tk.Tk()
    app = ColorSchemeEditor(root)
    root.mainloop()
