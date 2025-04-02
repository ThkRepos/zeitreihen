import hashlib
import os
import cufflinks as cf
import plotly.graph_objects as go


class PlotChartLine:
    """
        Eine Klasse zur Erstellung und Speicherung von Liniendiagrammen für Zeitreihendaten.

        Diese Klasse nutzt Plotly und Cufflinks, um interaktive Liniendiagramme zu erstellen.
        Sie ermöglicht die Darstellung mehrerer Zeitreihen in einem Diagramm und speichert
        die Ergebnisse als HTML-Dateien.

        Attribute:
            plot_dir (str): Das Verzeichnis, in dem die generierten Plots gespeichert werden.

        Methoden:
            create_chart(markt_symbol, chart_data_list, date_range, template="plotly_white"):
                Erstellt ein Liniendiagramm basierend auf den gegebenen Daten und Parametern.

            generate_plot_filename(titel, date_range):
                Generiert einen eindeutigen Dateinamen für den Plot basierend auf Titel und Datumsbereich.
        """

    def __init__(self, plot_dir):
        # Initialisierung der Cufflinks-Konfiguration für Offline-Nutzung
        cf.go_offline()
        cf.set_config_file(offline=True, world_readable=True)
        self.plot_dir = plot_dir

    def create_chart(self, markt_symbol, chart_data_list, date_range, template="plotly_white"):
        # Erstellung eines neuen Plotly-Diagramms
        fig = go.Figure()
        titel = markt_symbol + '_'

        # Hinzufügen jeder Zeitreihe zum Diagramm
        for df, interval, color in chart_data_list:
            fig.add_trace(go.Scatter(x=df['daytime'], y=df['CLOSE'], mode='lines', name=interval, line=dict(color=color)))
            titel += interval+'_'

        # Generieren des Dateinamens für den Plot
        save_path = self.generate_plot_filename(titel, date_range)
        titel += date_range['start'] + '_' + date_range['end']

        # Konfiguration des Layouts für das Diagramm
        fig.update_layout(
            title='Charting: ' + titel,
            xaxis_title='Datum',
            yaxis_title='Schlusskurs',
            legend_title='Intervalle',
            hovermode='x unified',
            template=template
        )

        # Speichern des Diagramms als HTML-Datei
        if not fig.write_html(save_path[0]):
            print(f"Fehler beim Speichern der Datei: {save_path[0]}")
        else:
            print(f"Datei: {save_path[0]} gespeichert!")

        return fig, titel, save_path[1]

    def generate_plot_filename(self, titel, date_range):
        # Generieren eines eindeutigen Dateinamens basierend auf Titel und Datumsbereich
        hash_string = f"{titel}{date_range['start']}{date_range['end']}"
        hash_object = hashlib.md5(hash_string.encode())
        hash_value = hash_object.hexdigest()[:8]

        # Sicherstellen, dass das Zielverzeichnis existiert
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)

        # Erstellen des vollständigen Dateipfads
        filename = f"{hash_value}.html"
        full_path = os.path.join(self.plot_dir, filename)

        return full_path, hash_value
