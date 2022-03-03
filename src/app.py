
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Output, Input, State
from vega_datasets import data
import altair as alt
import pandas as pd
from altair import datum

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

genres_df = pd.read_csv('df.csv')
alt.data_transformers.enable('data_server')

# the charts
def plot_hist_duration(type_name, bin_num, title, plot_title):
    chart = alt.Chart(genres_df, title = plot_title ).mark_bar().encode(
        alt.X("duration", bin =alt.Bin(maxbins = bin_num), title = title),    
        alt.Y('count()'),
        color = alt.value("#b20710")
    ).transform_filter(datum.type == type_name).properties(
        width=300,
        height=200
    ).interactive()
    return chart.to_html()

# use the tabs
app.layout =  dbc.Row(tabs_items)

if __name__ == "__main__":
    app.run_server()
