import json
from datetime import datetime


class MetadataManager:
    """
     Verwaltet Metadaten für die Zeitreihen-Visualisierungs-Anwendung.

     Diese Klasse ist verantwortlich für das Laden, Aktualisieren und Speichern von Metadaten,
     die für die Verwaltung von Zeitreihen und deren Eigenschaften verwendet werden.

     Attribute:
         metadata_file (str): Pfad zur JSON-Datei, in der die Metadaten gespeichert werden.
         metadata (dict): Ein Dictionary, das die aktuellen Metadaten enthält.

     Methoden:
         load_metadata(): Lädt Metadaten aus der Datei oder erstellt eine neue Struktur.
         save_metadata(): Speichert die aktuellen Metadaten in die Datei.
         update_metadata(symbol, interval, start_date, end_date, file_path): Aktualisiert die Metadaten mit neuen Informationen.

     Die Klasse verwaltet Informationen über verfügbare Intervalle, Symbole, Datumsbereiche
     und Dateipfade für verschiedene Zeitreihen-Kombinationen.
     """

    def __init__(self, metadata_file):
        # Initialisierung des MetadataManagers mit dem Pfad zur Metadaten-Datei
        self.metadata_file = metadata_file
        self.metadata = self.load_metadata()

    def load_metadata(self):
        # Laden der Metadaten aus der Datei oder Erstellen einer neuen Struktur, falls die Datei nicht existiert
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "available_intervals": [],
                "symbols": [],
                "date_range": {"start": None, "end": None},
                "files": {}
            }

    def save_metadata(self):
        # Speichern der aktuellen Metadaten in die Datei
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=4)

    def update_metadata(self, symbol, interval, start_date, end_date, file_path):
        # Aktualisieren der Metadaten mit neuen Informationen
        # Hinzufügen des neuen Intervalls zur Liste der verfügbaren Intervalle
        self.metadata['available_intervals'] = sorted(list(set(self.metadata['available_intervals'] + [interval])), key=interval_sort_key)
        # Hinzufügen des neuen Symbols zur Liste der Symbole
        self.metadata['symbols'] = list(set(self.metadata['symbols'] + [symbol]))

        # Aktualisieren des Startdatums, falls es das früheste ist
        if self.metadata['date_range']['start'] is None or start_date < datetime.strptime(self.metadata['date_range']['start'], '%Y-%m-%d'):
            self.metadata['date_range']['start'] = start_date.strftime('%Y-%m-%d')

        # Aktualisieren des Enddatums, falls es das späteste ist
        if self.metadata['date_range']['end'] is None or end_date > datetime.strptime(self.metadata['date_range']['end'], '%Y-%m-%d'):
            self.metadata['date_range']['end'] = end_date.strftime('%Y-%m-%d')

        # Speichern des Dateipfads für die Kombination aus Symbol und Intervall
        self.metadata['files'][f"{symbol}_{interval}"] = file_path

        # Speichern der aktualisierten Metadaten
        self.save_metadata()


def interval_sort_key(interval):
    # Hilfsfunktion zum Sortieren der Intervalle
    # Extrahiert die Zahl aus dem Intervall-String (z.B. 'M5' -> 5) für die Sortierung
    return int(interval[1:])
