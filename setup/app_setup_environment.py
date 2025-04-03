# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import platform

# Verzeichnisname für die virtuelle Umgebung
VENV_DIR = "./zeitreihen_venv"


def ist_venv():
    """Prüft, ob das Skript in einer virtuellen Umgebung ausgeführt wird."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)


def erstelle_venv():
    """Erstellt eine virtuelle Umgebung, wenn sie nicht existiert."""
    if os.path.exists(VENV_DIR):
        print(f"Virtuelle Umgebung in '{VENV_DIR}' existiert bereits.")
        return

    print(f"Erstelle virtuelle Umgebung in '{VENV_DIR}'...")
    subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    print("Virtuelle Umgebung wurde erfolgreich erstellt.")


def hole_venv_python():
    """Gibt den Pfad zum Python-Interpreter der virtuellen Umgebung zurück."""
    if platform.system() == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "python")


def installiere_anforderungen():
    """Installiert alle Abhängigkeiten in der virtuellen Umgebung."""
    python_interpreter = hole_venv_python()

    print("Aktualisiere pip in der virtuellen Umgebung...")
    subprocess.check_call([python_interpreter, "-m", "pip", "install", "--upgrade", "pip"])

    print("Installiere Anforderungen in der virtuellen Umgebung...")
    subprocess.check_call([python_interpreter, "-m", "pip", "install", "-r", "requirements.txt"])

    print("Alle Abhängigkeiten wurden erfolgreich installiert.")


def erstelle_startskript():
    """Erstellt ein Skript zum einfachen Starten der Anwendung."""
    if platform.system() == "Windows":
        # Windows-Batchdatei
        with open("./start_app.bat", "w") as f:
            f.write(f"@echo off\n")
            f.write(f"echo Starte Zeitreihen-Visualisierungs-App...\n")
            f.write(f"{VENV_DIR}\\Scripts\\python.exe -W ignore StartApplication.py\n")
            f.write(f"pause\n")

        print("Startskript 'start_app.bat' wurde erstellt.")
    else:
        # Unix-Shell-Skript
        with open("./start_app.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("echo \"Starte Zeitreihen-Visualisierungs-App...\"\n")
            f.write(f"{VENV_DIR}/bin/python -W ignore StartApplication.py\n")

        # Führbar machen
        os.chmod("./start_app.sh", 0o755)
        print("Startskript 'start_app.sh' wurde erstellt.")


def teste_tkinter():
    """Prüft, ob tkinter in der virtuellen Umgebung verfügbar ist."""
    python_interpreter = hole_venv_python()
    try:
        subprocess.check_call([python_interpreter, "-c", "import tkinter"])
        print("✓ tkinter ist verfügbar.")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ WARNUNG: tkinter ist nicht verfügbar!")
        print("tkinter ist Teil der Python-Standardbibliothek, muss aber manchmal separat installiert werden.")
        if platform.system() == "Linux":
            print("Unter Linux: sudo apt-get install python3-tk (Ubuntu/Debian) oder sudo dnf install python3-tkinter (Fedora)")
        elif platform.system() == "Darwin":  # macOS
            print("Unter macOS: tkinter sollte mit Python installiert sein. Versuchen Sie eine Neuinstallation von Python.")
        print("Bitte installieren Sie tkinter, bevor Sie die Anwendung starten.")
        return False


def main():
    """Hauptfunktion zum Einrichten des Projekts."""
    if ist_venv():
        print("Dieses Skript sollte nicht innerhalb einer virtuellen Umgebung ausgeführt werden.")
        print("Bitte verwenden Sie Ihre normale Python-Installation.")
        sys.exit(1)

    print("=== Einrichtung der Zeitreihen-Visualisierungs-App ===")

    try:
        erstelle_venv()
        installiere_anforderungen()
        tkinter_ok = teste_tkinter()
        erstelle_startskript()

        print("\n=== Einrichtung erfolgreich abgeschlossen! ===")
        if not tkinter_ok:
            print("\n⚠️ BEACHTEN SIE: tkinter fehlt und muss separat installiert werden.")

        print("Sie können die Anwendung jetzt starten mit:")

        if platform.system() == "Windows":
            print("    start_app.bat")
        else:
            print("    ./start_app.sh")

    except Exception as e:
        print(f"\nFehler bei der Einrichtung: {e}")
        print("Bitte stellen Sie sicher, dass Python 3.8 oder höher installiert ist.")
        sys.exit(1)


if __name__ == "__main__":
    main()
