import re
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json


class DataImporter:
    """
        DataImporter-Klasse für die Verarbeitung und Verwaltung von Zeitreihendaten.

        Diese Klasse bietet Funktionen zum Importieren von CSV-Dateien mit Zeitreihendaten,
        zur Verarbeitung dieser Daten und zur Verwaltung eines Caching-Systems für optimierte Leistung.

        Hauptfunktionen:
        - Import von CSV-Dateien mit spezifischem Namensformat
        - Verarbeitung und Konvertierung von Zeitreihendaten
        - Caching von importierten Daten für schnelleren Zugriff
        - Verwaltung von Metadaten für importierte Datensätze

        Die Klasse nutzt Pandas für die Datenverarbeitung und unterstützt verschiedene
        Zeitintervalle und Symbole in den Zeitreihendaten.
        """

    def __init__(self, config):
        # Initialisierung des DataImporter mit Konfiguration
        self.config = config
        self.cache_dir = 'cache'
        self.data_dir = os.path.join(self.cache_dir, 'data')
        self.meta_dir = os.path.join(self.cache_dir, 'meta')
        self.check_cache_directories()

    def check_cache_directories(self):
        # Stellt sicher, dass die erforderlichen Cache-Verzeichnisse existieren
        for directory in [self.cache_dir, self.data_dir, self.meta_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def import_csv(self, file_path):
        try:
            # Extrahiert Informationen aus dem Dateinamen
            file_name = file_path.split('/')[-1]
            symbol, interval, start_date, end_date = self.parse_file_name(file_name)
            cache_file = os.path.join(self.data_dir, f"{symbol}_{interval}.parquet")
            meta_file = os.path.join(self.meta_dir, f"{symbol}_{interval}.json")

            if os.path.exists(cache_file) and os.path.exists(meta_file):
                # Lädt Daten aus dem Cache, wenn vorhanden
                df = pd.read_parquet(cache_file)
                print(f"Daten aus Cache geladen: {file_name}")
            else:
                # Importiert CSV-Daten und verarbeitet sie
                df = pd.read_csv(file_path,
                                 delimiter=self.config['delimiter'].encode().decode('unicode_escape'),
                                 names=self.config['columns'],
                                 skiprows=1)

                # Konvertiert Datum und Zeit
                df['daytime'] = pd.to_datetime(df['DATE'].astype(str) + ' ' + df['TIME'].astype(str))
                df['DATE'] = pd.to_datetime(df['DATE'], format='%Y.%m.%d')

                # Konvertiert numerische Spalten
                for spalte in ['OPEN', 'HIGH', 'LOW', 'CLOSE']:
                    df[spalte] = pd.to_numeric(df[spalte], errors='coerce')

                # Bestimmt die Richtung (long oder short)
                df['direction'] = np.where(df['CLOSE'] >= df['OPEN'], 'green', 'red')

                # Speichert Daten im Cache
                df.to_parquet(cache_file)
                self.update_metadata(meta_file, symbol, interval, start_date, end_date, df)
                print(f"Datei erfolgreich eingelesen und gecached: {file_path} ")

            # Bereitet das Ergebnis-DataFrame vor
            result_df = df[['DATE', 'TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'direction', 'daytime']]
            result_df.columns = ['date', 'time', 'open', 'high', 'low', 'close', 'direction', 'daytime']

            return result_df, symbol, interval, start_date, end_date
        except Exception as e:
            print(f"Fehler beim Importieren der CSV-Datei: {e}")
            return None, None, None, None, None

    def parse_file_name(self, file_name):
        # Extrahiert Informationen aus dem Dateinamen
        match = re.match(r'(\w+)_(M\d+)_(\d{12})_(\d{12})\.csv', file_name)

        if match:
            symbol, interval, start_date, end_date = match.groups()
            start_date = datetime.strptime(start_date, '%Y%m%d%H%M')
            end_date = datetime.strptime(end_date, '%Y%m%d%H%M')
            return symbol, interval, start_date, end_date
        else:
            raise ValueError("Ungültiges Datei-Namen-Format")

    def update_metadata(self, meta_file, symbol, interval, start_date, end_date, df):
        # Aktualisiert die Metadaten für den importierten Datensatz
        metadata = {
            "filename": f"{symbol}_{interval}.parquet",
            "symbol": symbol,
            "timeframe": interval,
            "start_datetime": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_datetime": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "last_accessed": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "stats": {
                "rows": len(df),
                "column": list(df.columns)
            }
        }
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=4)
