import hashlib
import os
import cufflinks as cf
import plotly.graph_objects as go


class PlotChartLine:
    def __init__(self, plot_dir):
        cf.go_offline()
        cf.set_config_file(offline=True, world_readable=True)
        self.plot_dir = plot_dir

    def create_chart(self, markt_symbol, chart_data_list, date_range, template="plotly_white"):
        fig = go.Figure()
        titel = markt_symbol + '_'
        for df, interval, color in chart_data_list:
            fig.add_trace(go.Scatter(x=df['daytime'], y=df['CLOSE'], mode='lines', name=interval, line=dict(color=color)))
            titel += interval+'_'
        save_path = self.generate_plot_filename(titel, date_range)
        titel += date_range['start'] + '_' + date_range['end']
        fig.update_layout(
            title='Charting: ' + titel,
            xaxis_title='Datum',
            yaxis_title='Schlusskurs',
            legend_title='Intervalle',
            hovermode='x unified',
            template=template
        )
        if not fig.write_html(save_path[0]):
            print(f"Fehler beim Speichern der Datei: {save_path[0]}")
        else:
            print(f"Datei: {save_path[0]} gespeichert!")

        return fig, titel, save_path[1]

    def generate_plot_filename(self, titel, date_range):
        hash_string = f"{titel}{date_range['start']}{date_range['end']}"
        hash_object = hashlib.md5(hash_string.encode())
        hash_value = hash_object.hexdigest()[:8]

        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)

        filename = f"{hash_value}.html"
        full_path = os.path.join(self.plot_dir, filename)

        return full_path, hash_value
