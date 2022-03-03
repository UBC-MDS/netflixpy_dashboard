
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

# frame for movies
frame_histogram_movies = html.Iframe(
                        style = {"width": "400px", "height": "320px"} ,
                        srcDoc=plot_hist_duration(type_name = 'Movie',
                         bin_num = 30, title = "Duration of Movies",
                         plot_title= "Histogram of the Duration of Movie"))
#frame for tv shows
frame_histogram_tv_shows = html.Iframe(
                        style = {"width": "400px", "height": "320px"} ,
                        srcDoc=plot_hist_duration(type_name = 'TV Show',
                        bin_num = 10, title = "Duration of TV Shows",
                        plot_title= "Histogram of the Duration of TV Shows"))
#tabs
tabs_items = html.Div(
    children = [
    dbc.Tabs(
        id='type_name', 
        active_tab="Movie",
        children = [
                dbc.Tab(frame_histogram_tv_shows, label='Movie'),
                dbc.Tab(frame_histogram_movies , label='TV Show')
            ]),
            
        html.Div(id="content")
    ], style = {"color": "#b20710"}) 

@app.callback(
        Output('content', 'children'),
        [Input('type_name', 'value')]
        )

# use the tabs
app.layout =  dbc.Row(tabs_items)

if __name__ == "__main__":
    app.run_server()
