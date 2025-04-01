import hashlib
import os

import cufflinks as cf
import plotly.graph_objects as go


class PlotChartLine:
    def __init__(self):
        cf.go_offline()
        cf.set_config_file(offline=True, world_readable=True)

    def create_chart(self, chart_data_list, date_range):
        fig = go.Figure()
        titel = "Chart_"
        for df, interval, color in chart_data_list:
            fig.add_trace(go.Scatter(x=df['daytime'], y=df['CLOSE'], mode='lines', name=interval, line=dict(color=color)))
            titel += interval+'_'
        save_path = self.generate_plot_filename(titel, date_range)

        fig.update_layout(
            title='Zeitreihen Visualisierung: '+ titel,
            xaxis_title='Datum',
            yaxis_title='Schlusskurs',
            legend_title='Intervalle',
            hovermode='x unified',
            template="plotly_white"
        )
        if fig.write_html(save_path[0]):
            print(f"Datei: {save_path[0]} gespeichert!")
        else:
            print(f"Fehler beim Speichern der Datei: {save_path[0]}")

        return fig, titel, save_path[1]

    def generate_plot_filename(self, titel, date_range):
        hash_string = f"{titel}{date_range['start']}{date_range['end']}"
        hash_object = hashlib.md5(hash_string.encode())
        hash_value = hash_object.hexdigest()[:8]

        plot_dir = "./plots"
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        filename = f"{hash_value}.html"
        full_path = os.path.join(plot_dir, filename)

        return full_path, hash_value
