import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Output, Input, State
from vega_datasets import data
import altair as alt
import pandas as pd
from altair import datum


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])




def world_map(year):
    
    # Load in data and geocodes
    df = pd.read_csv("data/raw/netflix_titles.csv")
    geocodes = pd.read_csv("data/raw/world_country_latitude_and_longitude_values.csv")
    
    # Explode "country" since some shows have multiple countries of production
    movie_exploded = (df.set_index(df.columns.drop("country", 1)
                                        .tolist()).country.str.split(',', expand = True)
                        .stack()
                        .reset_index()
                        .rename(columns = {0:'country'})
                        .loc[:, df.columns]
    )

    # Remove white space
    movie_exploded.country = movie_exploded.country.str.lstrip()
    movie_exploded.country = movie_exploded.country.str.rstrip()
    
    # Get count per country and release year
    count = (pd.DataFrame(movie_exploded.groupby(["country", "release_year"]).size())
        .reset_index()
        .rename(columns = {0 : "count"})
        )
    
    # Merge with geocodes
    count_geocoded = count.merge(geocodes, on = "country")
    count_geocoded = count_geocoded.rename(columns = {"latitude": "lat", "longitude": "lon"})
    
    # Drop unused columns
    count_geocoded = count_geocoded.drop(["usa_state_code", "usa_state_latitude", "usa_state_longitude", "usa_state"], axis = 1)
    
    # Base map layer
    source = alt.topo_feature(data.world_110m.url, 'countries')
    base_map = alt.layer(
        alt.Chart(source).mark_geoshape(fill = 'black', stroke = 'grey')
    ).project(
        'equirectangular'
    ).properties(width = 900, height = 400).configure_view(stroke = None)
    
    # Shows count size layer
    points = alt.Chart(count_geocoded[count_geocoded["release_year"] == year]).mark_point().encode(
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
    strokeWidth = 0).configure_mark(
    opacity = 0.8)
    
    return chart.to_html()


def plot_hist_duration(type_name, bin_num, title, plot_title):
    genres_df = pd.read_csv('data/processed/df.csv')
    alt.data_transformers.enable('data_server')
    chart = alt.Chart(genres_df, title = plot_title ).mark_bar().encode(
        alt.X("duration", bin =alt.Bin(maxbins = bin_num), title = title),    
        alt.Y('count()'),
        color = alt.value("#b20710")
    ).transform_filter(datum.type == type_name).properties(
        width=300,
        height=200
    ).interactive()
    return chart.to_html()


app.layout = dbc.Container([
    dbc.Row(html.Div(
        html.H1("Netflix")
    )),
    
    dbc.Row([
        dbc.Col(dcc.Dropdown(
                id='genre',
                value='1', 
                options=[{'label': "1", 'value': "1"},
                         {'label': "2", 'value': "2"}]),
        
        md=4, style={'border': '1px solid #d3d3d3', 'width': '20%', 'border-radius': '10px'}),
        dbc.Col([
            html.Div(
                children = [
                dbc.Tabs(
                    id='type_name', 
                    active_tab="Movie",
                    children = [
                            dbc.Tab(html.Iframe(
                                        style = {"width": "400px", "height": "320px"} ,
                                        srcDoc=plot_hist_duration(type_name = 'Movie',
                                                                  bin_num = 30, title = "Duration of Movies",
                                                                  plot_title= "Histogram of the Duration of Movie")),
                                                                  label='Movie'),
                            dbc.Tab(html.Iframe(
                                        style = {"width": "400px", "height": "320px"} ,
                                        srcDoc=plot_hist_duration(type_name = 'TV Show',
                                                                  bin_num = 10, title = "Duration of TV Shows",
                                                                  plot_title= "Histogram of the Duration of TV Shows")),
                                                                  label='TV Show')
                    ]),
                html.Div(id="content")
                ], style = {"color": "#b20710"}),
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
                       2021: "2021"}),
            html.Iframe(
            id = "world_map",
            srcDoc = world_map(year = 1942),
            style={'border-width': '0', 'width': '100%', 'height': '500px'}),
            
        ])
    ])
])




@app.callback(
        Output('content', 'children'),
        [Input('type_name', 'value')]
        )
# render tabs
def render_content(tab):
    if tab == 'Movie':
        return frame_histogram_movies
    elif tab == "TV Show": 
        return frame_histogram_tv_shows


@app.callback(
    Output('world_map', 'srcDoc'),
    Input('year_slider', 'value'))
def update_output(year):
    return world_map(year)



if __name__ == '__main__':
    app.run_server(debug = True)

