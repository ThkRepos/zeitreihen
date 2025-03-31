import json
from datetime import datetime


class MetadataManager:
    def __init__(self, metadata_file):
        self.metadata_file = metadata_file
        self.metadata = self.load_metadata()

    def load_metadata(self):
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
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=4)

    def update_metadata(self, symbol, interval, start_date, end_date, file_path):
        self.metadata['available_intervals'] = sorted(list(set(self.metadata['available_intervals'] + [interval])), key=interval_sort_key)
        self.metadata['symbols'] = list(set(self.metadata['symbols'] + [symbol]))

        if self.metadata['date_range']['start'] is None or start_date < datetime.strptime(self.metadata['date_range']['start'], '%Y-%m-%d'):
            self.metadata['date_range']['start'] = start_date.strftime('%Y-%m-%d')

        if self.metadata['date_range']['end'] is None or end_date > datetime.strptime(self.metadata['date_range']['end'], '%Y-%m-%d'):
            self.metadata['date_range']['end'] = end_date.strftime('%Y-%m-%d')

        self.metadata['files'][f"{symbol}_{interval}"] = file_path

        self.save_metadata()


def interval_sort_key(interval):
    return int(interval[1:])
