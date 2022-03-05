import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Output, Input, State
from vega_datasets import data
import altair as alt
import pandas as pd
from altair import datum


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
df = pd.read_csv("data/processed/processed.csv")
genres_df = pd.read_csv('data/processed/df.csv')
raw_data = pd.read_csv("data/raw/netflix_titles.csv")
geocodes = pd.read_csv("data/raw/world_country_latitude_and_longitude_values.csv")
server = app.server


def world_map(year):
    """
    Loads Netflix data and country geocodes, wrangles and merges the two data, 
    and plots a world map containing the number of movies and TV shows produced in a given year.
    
    Parameters
    ----------
    year: int, float
        Filter the data based on year that the movie/TV show is released.
        
    Returns
    -------
    altair.vegalite.v4.api.LayerChart
        A layered Altair chart containing the base world map and the size of number of movies and TV shows produced over the years.
    """
    
    # Load in data and geocodes
    df = pd.read_csv("data/raw/netflix_titles.csv")
    geocodes = pd.read_csv("data/raw/world_country_latitude_and_longitude_values.csv")
    

    # Explode "country" since some shows have multiple countries of production
    movie_exploded = (raw_data.set_index(raw_data.columns.drop("country", 1)
                                        .tolist()).country.str.split(',', expand = True)
                        .stack()
                        .reset_index()
                        .rename(columns = {0:'country'})
                        .loc[:, raw_data.columns]
    )

    # Remove white space
    movie_exploded.country = movie_exploded.country.str.lstrip()
    movie_exploded.country = movie_exploded.country.str.rstrip()
    
    # Get count per country and release year
    count = (pd.DataFrame(movie_exploded.groupby(["country", 
                                                  "release_year"]).size())
        .reset_index()
        .rename(columns = {0 : "count"})
        )
    
    # Merge with geocodes
    count_geocoded = count.merge(geocodes, on = "country")
    count_geocoded = count_geocoded.rename(columns = {"latitude": "lat", 
                                                      "longitude": "lon"})
    
    # Drop unused columns
    count_geocoded = count_geocoded.drop(["usa_state_code", 
                                          "usa_state_latitude", 
                                          "usa_state_longitude", 
                                          "usa_state"], axis = 1)

    
    # Base map layer
    source = alt.topo_feature(data.world_110m.url, 'countries')
    base_map = alt.layer(
        alt.Chart(source).mark_geoshape(
            fill = 'black', 
            stroke = 'grey')
    ).project(
        'equirectangular'
    ).properties(width = 900, 
                 height = 400).configure_view(
                     stroke = None)
    
    # Shows count size layer
    points = alt.Chart(count_geocoded[count_geocoded["release_year"] == year]).mark_point().encode(
    latitude = "lat",
    longitude = "lon",
    fill = alt.value("red"),
    size = alt.Size("count:Q", 
                    scale = alt.Scale(domain = [0, 70]),
                   legend = None),

    stroke = alt.value(None),
    tooltip = [alt.Tooltip("country", title = "Country"), 
               alt.Tooltip("release_year:Q", title = "Release Year"),
               alt.Tooltip("count:Q", title = "Count")]
).properties(
    title = "Number of Movie and TV show Produced Worldwide"
)
    
    chart = (base_map + points).configure_view(
        strokeWidth = 0
        ).configure_mark(
            opacity = 0.8).configure_title(
                            dy = -20
) 
    return chart.to_html()


def plot_hist_duration(type_name, year, cat, bin_num, title, plot_title):
    # filtering data by year and genre
    plot_df = (genres_df[genres_df["genres"].isin(cat)]
               .query(f"release_year <= @year"))
    plot_df = (
        plot_df.groupby(["duration", "type"])
        .show_id.nunique()
        .reset_index(name="count")
    )

    chart = alt.Chart(plot_df, title = plot_title ).mark_bar().encode(
        alt.X("duration", bin =alt.Bin(maxbins = bin_num), title = title),    
        alt.Y('count'),
        color = alt.value("#b20710")
    ).transform_filter(datum.type == type_name).properties(
        width=300,
        height=200
    ).interactive()
    return chart.to_html()


def plot_directors(cat, year):
    click = alt.selection_multi()

    plot_df = (
        df[df["genres"].isin(cat)]
        .query("director != 'Missing'")
        .query(f"release_year <= @year")
        .groupby(["director", "country"])
        .show_id.nunique()
        .reset_index()
        .sort_values(ascending=False, by="show_id")
    )

    chart = (
        alt.Chart(plot_df[0:10], title="Top 10 Directors in Terms of Number of Content")
        .mark_bar(color="#b20710")
        .encode(
            y=alt.Y("director", sort="-x", title=""),
            x=alt.X("sum(show_id)", title="Number of Movies + TV shows"),
            opacity=alt.condition(click, alt.value(1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("director", title="Director"),
                alt.Tooltip("sum(show_id)", title="Count"),
            ],
        )
        .add_selection(click)
    )
    return chart.to_html()



app.layout = dbc.Container([
    dbc.Row(html.Div(
        html.H1("Netflix Explorer")
    )),
    
    dbc.Row([
        dbc.Col([
            html.P("Select Movie/ TV Show genres"),
            dcc.Dropdown(
                    id="dropdown",
                    options=df.genres.unique().tolist(),
                    value=["International"],
                    multi=True,
            )],
        md=4, style={'border': '1px solid #d3d3d3', 'width': '20%', 'border-radius': '10px'}),
        
        
        dbc.Col([
            html.P("Select Year"),
            dcc.Slider(id = 'year_slider', 
                   min = 1942, 
                   max = 2021, 
                   value = 2021,
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
            srcDoc = world_map(year = 2021),
            style={'border-width': '0', 'width': '90%', 'height': '500px'}),

            dbc.Row([
                dbc.Col([
                    html.Iframe(
                        id="plot_directors",
                        srcDoc = plot_directors(["International"], 2021),
                        style={
                            "border-width": "1",
                            "width": "100%",
                            "height": "300px",
                            "top": "20%",
                            "left": "70%",
                        },
                    ),    
                ]),
                dbc.Col([
                    html.Div(
                        children = [
                        dbc.Tabs(
                            id='type_name', 
                            active_tab="Movie",
                            children = [
                                    dbc.Tab(html.Iframe(
                                                id = "movie_duration",
                                                style = {"width": "400px", "height": "320px"} ,
                                                srcDoc=plot_hist_duration(type_name = 'Movie',
                                                                        year = 2021,
                                                                        cat = ["international"],
                                                                        bin_num = 30, title = "Duration of Movies",
                                                                        plot_title= "Duration of Movies")),
                                                                        label='Movie'),
                                    dbc.Tab(html.Iframe(
                                                id = "tv_duration",
                                                style = {"width": "400px", "height": "320px"} ,
                                                srcDoc=plot_hist_duration(type_name = 'TV Show',
                                                                        year = 2021,
                                                                        cat = ["international"],
                                                                        bin_num = 10, title = "Duration of TV Shows",
                                                                        plot_title= "Duration of TV Shows")),
                                                                        label='TV Show')
                            ])
                        ], 
                    style = {"color": "#b20710"}),
                ], style = {"width": "60%"})
            ])             
        ])
    ])
])




# @app.callback(
#         Output('content', 'children'),
#         [Input('type_name', 'value')]
#         )
# # render tabs
# def render_content(tab):
#     if tab == 'Movie':
#         return frame_histogram_movies
#     elif tab == "TV Show": 
#         return frame_histogram_tv_shows



@app.callback(
    [Output("world_map", "srcDoc"),
     Output("plot_directors", "srcDoc"),
     Output("movie_duration", "srcDoc"),
     Output("tv_duration", "srcDoc")],
    [Input("dropdown", "value"),
    Input('year_slider', 'value')])
def update_output(cat, year):
    map = world_map(year)
    directors = plot_directors(cat, year)
    movie_hist = plot_hist_duration("Movie",
                                    year,
                                    cat, 
                                    bin_num = 30, 
                                    title = "Duration of Movies",
                                    plot_title= "Duration of Movies")
    tv_show_hist = plot_hist_duration("TV Show",
                                    year,
                                    cat,
                                    bin_num = 10,
                                    title = "Number of Seasons",
                                    plot_title= "Duration of TV Shows")

    return map, directors, movie_hist, tv_show_hist



if __name__ == '__main__':
    app.run_server(debug = False)

