# -*- coding: utf-8 -*-

import subprocess
import importlib.util
import sys


def check_modul(modulname):
    """Prüft, ob ein Modul installiert ist."""
    try:
        spec = importlib.util.find_spec(modulname)
        return spec is not None
    except ModuleNotFoundError:
        return False


def hole_basis_modulname(modulname):
    """Extrahiert den Basis-Modulnamen aus der Anforderungsspezifikation."""
    return modulname.split('>=')[0].split('==')[0].split('>')[0].split('<')[0].strip()


def installiere_anforderungen():
    """Prüft und installiert benötigte Module."""
    # Prüfe, ob wir in einer virtuellen Umgebung sind
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

    if not in_venv:
        print("WARNUNG: Dieses Skript wird nicht in einer virtuellen Umgebung ausgeführt.")
        print("Es wird empfohlen, zuerst 'app_1_setup.py' auszuführen, um eine virtuelle Umgebung einzurichten.")
        eingabe = input("Möchten Sie trotzdem fortfahren? (j/N): ")
        if eingabe.lower() != 'j':
            print("Installation abgebrochen. Bitte führen Sie 'setup.py' aus.")
            sys.exit(0)

    anforderungen = []
    with open('requirements.txt', 'r') as datei:
        for zeile in datei:
            zeile = zeile.strip()
            if zeile and not zeile.startswith('#'):
                anforderungen.append(zeile)

    print("Prüfe und installiere benötigte Pakete...")
    fehlende_module = []

    for anf in anforderungen:
        basismodul = hole_basis_modulname(anf)

        if check_modul(basismodul):
            print(f"✓ {basismodul} ist bereits installiert")
        else:
            print(f"✗ {basismodul} wurde nicht gefunden, wird installiert")
            fehlende_module.append(anf)

    if fehlende_module:
        print("\nInstalliere fehlende Pakete...")
        for modul in fehlende_module:
            print(f"Installiere {modul}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", modul])
            print(f"{modul} wurde erfolgreich installiert")
    else:
        print("\nAlle benötigten Pakete sind bereits installiert.")

    # Versuche, tkinter zu importieren, um zu prüfen, ob es verfügbar ist
    try:
        import tkinter
        print("\n✓ tkinter ist verfügbar.")
    except ImportError:
        print("\n⚠️ WARNUNG: tkinter konnte nicht importiert werden!")
        print("tkinter ist Teil der Python-Standardbibliothek, muss aber manchmal separat installiert werden.")
        if sys.platform.startswith('linux'):
            print("Unter Linux: sudo apt-get install python3-tk (Ubuntu/Debian) oder sudo dnf install python3-tkinter (Fedora)")
        elif sys.platform == 'darwin':
            print("Unter macOS: tkinter sollte mit Python installiert sein. Versuchen Sie eine Neuinstallation von Python.")
        print("Bitte installieren Sie tkinter, bevor Sie die Anwendung starten.")

    print("\nEinrichtung abgeschlossen! Sie können die Anwendung jetzt starten.")


if __name__ == "__main__":
    installiere_anforderungen()
