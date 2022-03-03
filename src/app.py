import altair as alt
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from vega_datasets import data
import pandas as pd

map_df = pd.read_csv("../data/processed/world_map_data.csv")

def world_map(year):

    # Base map layer
    source = alt.topo_feature(data.world_110m.url, 'countries')
    base_map = alt.layer(
        alt.Chart(source).mark_geoshape(fill = 'black', stroke = 'grey')
    ).project(
        'equirectangular'
    ).properties(width = 900, height = 400).configure_view(stroke = None)
    
    # Count size layer
    points = alt.Chart(map_df[map_df["release_year"] == year]).mark_point().encode(
    latitude = "lat",
    longitude = "lon",
    fill = alt.value("red"),
    size = alt.Size("count:Q", 
                    scale = alt.Scale(domain = [0, 70]),
                   legend = None),

    stroke = alt.value(None),
    tooltip = ["country", "release_year:Q" ,"count:Q"]
)
    
    chart = (base_map + points).configure_view(
    strokeWidth=0).configure_mark(
    opacity = 0.8)
    
    return chart.to_html()


app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])


app.layout = html.Div([
        html.Iframe(
            id = "world_map",
            srcDoc = world_map(year = 1942),
            style={'border-width': '0', 'width': '100%', 'height': '400px'}),
        dcc.Slider(id = 'year_slider', 
                   min = 1942, 
                   max = 2021, 
                   step = 5,
                   marks = {
                       1942: "1942",
                       1947: "1947",
                       1952: "1952",
                       1957: "1957",
                       1962: "1962",
                       1967: "1967",
                       1972: "1972",
                       1977: "1977",
                       1982: "1982",
                       1987: "1987",
                       1992: "1992",
                       1997: "1997",
                       2002: "2002",
                       2007: "2007",
                       2012: "2012",
                       2017: "2017",
                       2021: "2021"  
                   })])

@app.callback(
    Output('world_map', 'srcDoc'),
    Input('year_slider', 'value'))

def update_output(year):
    return world_map(year)

if __name__ == '__main__':
    app.run_server(debug = True)