import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Output, Input, State
from vega_datasets import data
import altair as alt
import pandas as pd
from altair import datum


app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
df = pd.read_csv("data/processed/processed.csv")
genres_df = pd.read_csv('data/processed/df.csv')
raw_data = pd.read_csv("data/raw/netflix_titles.csv")
geocodes = pd.read_csv("data/raw/world_country_latitude_and_longitude_values.csv")
server = app.server
app.title = 'Netflix Dashboard'


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


def plot_hist_duration(type_name, year, cat, rate, bin_num, title):
    """
    Plots the distribution of movies or TV series.
    
    Parameters
    ----------
    type_name: string
        The name of the required plot category (TV or Movies).
    year: int, float
        Filter the data based on year that the movie/TV show is released.
    cat: list
        List of genres we want to filter out from the dataframe.
    bin_num: int
        Number of bins in the barplot.
    title: string
        The x label of the barplot.
    plot_title: string
        The title of the barplot.
        
    Returns
    -------
    altair.vegalite.v4.api.LayerChart
        A barplot conditioned on the type of content (TV/Movie)
    """
    plot_df = genres_df[genres_df["rating"].isin(rate)]
    plot_df = (plot_df[plot_df["genres"].isin(cat)]
               .query(f"release_year <= @year"))
    plot_df = (
        plot_df.groupby(["duration", "type"])
        .show_id.nunique()
        .reset_index(name="count")
    )

    chart = alt.Chart(plot_df).mark_bar().encode(
        alt.X("duration", bin =alt.Bin(maxbins = bin_num), title = title),    
        alt.Y('count'),
        tooltip='count',
        color = alt.value(color1)
    ).transform_filter(datum.type == type_name).properties(
        width=300,
        height=200
    ).configure(background=transparent
    ).configure_axis(
        labelColor=plot_text_color,
        titleColor=plot_text_color
    ).interactive()
    return chart.to_html()


def plot_directors(cat,rate, year):
    """
    Plots the count of movies or TV series by individual directors.
    
    Parameters
    ----------
    cat: list
        List of genres we want to filter out from the dataframe.\
    year: int, float
        Filter the data based on year that the movie/TV show is released.
        
    Returns
    -------
    altair.vegalite.v4.api.LayerChart
        A barplot showing the number of content directed by individuals
    """
    click = alt.selection_multi()

    plot_df = df[df["rating"].isin(rate)]
    plot_df = (
        plot_df[plot_df["genres"].isin(cat)]
        .query("director != 'Missing'")
        .query(f"release_year <= @year")
        .groupby(["director", "country"])
        .show_id.nunique()
        .reset_index()
        .sort_values(ascending=False, by="show_id")
    )

    chart = (
        alt.Chart(plot_df[0:10])
        .mark_bar(color=color1)
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
    ).configure(background=transparent
    ).configure_axis(
        labelColor=plot_text_color,
        titleColor=plot_text_color
    )
    return chart.to_html()

transparent = "#00000000"        # for transparent backgrounds
color1 = "#9E0600"               # red
color2 = "#993535"               # border colors
plot_text_color = "#ebe8e8"      # plot axis and label color
title_color = "#ebe8e8"          # general title and text color
border_radius = "5px"            # rounded corner radius
border_width = "3px"             # border width


app.layout = dbc.Container([
    dbc.Row(html.Div(
        html.H1("Netflix Explorer"),
    ), style={"color": color1}),
    
    dbc.Row([
        dbc.Col([
            html.P("Select Year",
                style={"background": color1, "color": title_color,
                    'textAlign': 'center', 'border-radius': border_radius}),
            html.Div([
                html.Div(style={'padding': 3}),
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
                        2021: "2021"},
                   )], style={"border": f"{border_width} solid {color2}", 'border-radius': border_radius}),
            html.Div(style={'padding': 10}),

            html.P("Select Genres",
                style={"background": color1, "color": title_color,
                       'textAlign': 'center', 'border-radius': border_radius}),
            html.Div([
                dcc.Dropdown(
                        id="dropdown",
                        options=df.genres.unique().tolist(),
                        value=["International", "Dramas", "Crime TV Shows", "Reality TV", "Comedies"],

                        multi=True,
                        style={"background-color": transparent, "border": "0", "color": "black", "label-color": "black"}
                )], style={"border": f"{border_width} solid {color2}", 'border-radius': border_radius}
            ),
            html.Div(style={'padding': 10}),

            html.P("Select Ratings",
                style={"background": color1, "color": title_color,
                       'textAlign': 'center', 'border-radius': border_radius}),
            html.Div([
                dcc.Dropdown(
                        id="dropdown_ratings",
                        options=df.rating.unique().tolist(),
                        value=   ['PG-13','TV-MA','PG','TV-14','TV-PG','TV-Y','R','TV-G','G','NC-17','NR'], 

                        multi=True,
                        style={"background-color": transparent, "border": "0", "color": "black", "label-color": "black"}
                )], style={"border": f"{border_width} solid {color2}", 'border-radius': border_radius}
            )
                       ],
        md=4, style={'width': '17%'}),   
        
        
        dbc.Col([
            html.H3("Movies and TV shows produced worldwide",
                style={"background": color1,"color": title_color, 
                       'textAlign': 'center', 'border-radius': border_radius, "width": "93%"}),
            html.Div([
                html.Iframe(
                id = "world_map",
                srcDoc = world_map(year = 2021),
                style={'border': '0', 'width': '100%', 'height': '500px'})
            ], style={"border": f"{border_width} solid {color2}", 'border-radius': border_radius, "width": "93%", "height": "470px"}),

            html.Div(style={'padding': 10}),
            dbc.Row([
                dbc.Col([
                    html.H3("Top 10 directors",
                        style={"background": color1, "color": title_color, 
                               'textAlign': 'center', 'border-radius': border_radius}),
                    html.Div([
                        html.P("In terms of number of content",
                               style={"color": title_color, 'textAlign': 'center'}),
                        html.Iframe(
                            id="plot_directors",
                            srcDoc = plot_directors(["International", "Dramas", "Crime TV Shows", "Reality TV", "Comedies"],
                                                    ['PG-13','TV-MA','PG','TV-14','TV-PG','TV-Y','R','TV-G','G','NC-17','NR'], 
                                                          2021),
                            style={
                                "border-width": "1",
                                "width": "100%",
                                "height": "300px",
                                "top": "20%",
                                "left": "70%",
                            },
                        ),   
                    ], style={"border": f"{border_width} solid {color2}", 'border-radius': border_radius, "height": "300px"})
                ], md=4, style={"width": "54%"}),
                dbc.Col([
                    html.H3("Durations",
                        style={"background": color1, "color": title_color, 
                               "textAlign": "center", "border-radius": border_radius, "width": "120%"}),
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
                                                                        cat = ["International", "Dramas", "Crime TV Shows", "Reality TV", "Comedies"],
                                                                        rate =   ['PG-13','TV-MA','PG','TV-14','TV-PG','TV-Y','R','TV-G','G','NC-17','NR'], 
                                                                        bin_num = 30, title = "Duration of Movies"
                                                                        )),
                                                                        label='Movie', tab_id='Movie'),
                                    dbc.Tab(html.Iframe(
                                                id = "tv_duration",
                                                style = {"width": "400px", "height": "320px"} ,
                                                srcDoc=plot_hist_duration(type_name = 'TV Show',
                                                                        year = 2021,
                                                                        cat = ["International", "Dramas", "Crime TV Shows", "Reality TV", "Comedies"],
                                                                        rate =   ['PG-13','TV-MA','PG','TV-14','TV-PG','TV-Y','R','TV-G','G','NC-17','NR'], 
                                                                        bin_num = 10, title = "Duration of TV Shows"
                                                                        )),
                                                                        label='TV Show', tab_id='TV Show')
                            ])
                        ], 
                    style = {"border": f"{border_width} solid {color2}", 'border-radius': border_radius, "width": "120%", "height": "300px"}),
                ], md=4, style = {})
            ])             
        ])
    ])
])


@app.callback(
    [Output("world_map", "srcDoc"),
     Output("plot_directors", "srcDoc"),
     Output("movie_duration", "srcDoc"),
     Output("tv_duration", "srcDoc")],
    [Input("dropdown", "value"),
    Input("dropdown_ratings", "value"),
    Input('year_slider', 'value')])

def update_output(cat, rate, year):
    map = world_map(year)
    directors = plot_directors(cat, rate,  year)
    movie_hist = plot_hist_duration("Movie",
                                    year,
                                    cat, 
                                    rate,
                                    bin_num = 30, 
                                    title = "Duration of Movies"
                                    )
    tv_show_hist = plot_hist_duration("TV Show",
                                    year,
                                    cat,
                                    rate,
                                    bin_num = 10,
                                    title = "Number of Seasons"
                                    )

    return map, directors, movie_hist, tv_show_hist



if __name__ == '__main__':
    app.run_server(debug = True)