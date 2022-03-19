import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Output, Input, State
from vega_datasets import data
import altair as alt
import pandas as pd
from altair import datum
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import io
import matplotlib
from PIL import Image
import numpy as np
alt.data_transformers.disable_max_rows()

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
df = pd.read_csv("data/processed/processed.csv")
genres_df = pd.read_csv('data/processed/df.csv')
raw_data = pd.read_csv("data/raw/netflix_titles.csv")
geocodes = pd.read_csv("data/raw/world_country_latitude_and_longitude_values.csv")
server = app.server
app.title = 'Netflix Dashboard'


def world_map(cat, rate, year):
    """
    Merges the processed data with country gecodes and
    plots a world map containing the number of movies and TV shows produced in a given year, genre and rating.
    
    Parameters
    ----------
    year: int, float
        Filter the data based on year that the movie/TV show is released.
        
    Returns
    -------
    altair.vegalite.v4.api.LayerChart
        A layered Altair chart containing the base world map and the size of number of movies and TV shows produced over the years.
    """

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
    count = (pd.DataFrame(movie_exploded.groupby(["country", 
                                                  "release_year", "genres", "rating"]).size())
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
    
    
    plot_df = count_geocoded[count_geocoded["rating"].isin(rate)]
    plot_df = (plot_df[plot_df["genres"].isin(cat)]
               .query(f"release_year == @year")
               .groupby(["country", "lat", "lon"])
               .sum()
               .reset_index())           
    
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
    points = alt.Chart(plot_df).mark_point().encode(
    latitude = "lat",
    longitude = "lon",
    fill = alt.value("#E50914"),
    size = alt.Size("count:Q", 
                    scale = alt.Scale(domain = [0, 70]),
                   legend = None),

    stroke = alt.value(None),
    tooltip = [alt.Tooltip("country", title = "Country"), 
               alt.Tooltip("release_year:Q", title = "Release Year"),
               alt.Tooltip("count:Q", title = "Count")]
)
    
    chart = (base_map + points).configure_view(
        strokeWidth = 0
        ).configure_mark(
            opacity = 0.8
        ).configure(background = transparent, style=dict(cell=dict(strokeOpacity=0)))
        
    return chart.to_html()


def plot_hist_duration(type_name, year, cat, rate, title):
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
    plot_df = plot_df[['genres', 'duration', 'show_id', "type"]].copy().drop_duplicates()
   
    chart = alt.Chart(plot_df).mark_boxplot(extent=2.5, color="#752516").encode(
        alt.X("duration", title = title),    
        alt.Y('genres', title=""),
        color = alt.value(color1),
        tooltip = 'genres'
        ).transform_filter(datum.type == type_name).properties(
        width=260,
        height=200
    ).configure(background=transparent
    ).configure_axis(
        labelColor=plot_text_color,
        titleColor=plot_text_color
    ).interactive()
    return chart.to_html()


def plot_directors(cat, rate, year):
    """
    Plots the count of movies or TV series by individual directors.
    
    Parameters
    ----------
    cat: list
        List of genres we want to filter out from the dataframe.
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


def title_cloud(year, cat):
    """
    Add docstring
    """

    plot_df = df
    # prevent error when no genre is selected
    if len(cat) > 0:
        plot_df = df[df["genres"].isin(cat)].query(f'release_year <= @year')
    else:
        plot_df = df.query(f'release_year <= @year')
    
    words = " ".join(plot_df["title"].tolist())
    
    mask = np.array(Image.open("src/assets/netflixN.png"))

    colormap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#824d4d', '#b20710', "#ffeded", "#E50914"])
    word_cloud = WordCloud(collocations = False, 
                           background_color = "#222222", colormap = colormap, mask=mask).generate(words)
    
    buf = io.BytesIO() 
    plt.figure()
    plt.imshow(word_cloud, interpolation = "bilinear");
    plt.axis("off")
    
    plt.savefig(buf, format = "png", dpi = 150, bbox_inches = "tight", pad_inches = 0)
    data = base64.b64encode(buf.getbuffer()).decode("utf8")  
    plt.close()
    return "data:image/png;base64,{}".format(data)






transparent = "#00000000"        # for transparent backgrounds
color1 = "#9E0600"               # red
color2 = "#993535"               # border colors
plot_text_color = "#ebe8e8"      # plot axis and label color
title_color = "#ebe8e8"          # general title and text color
border_radius = "5px"            # rounded corner radius
border_width = "3px"             # border width



app.layout = dbc.Container([ 
    dbc.Row([
        dbc.Col([
            dbc.Col([
                html.Img(
                    id = "image_wc",
                    className = "img-responsive",
                    style = {'width':'100%'}
                )
            ]),




            html.P("Select Year",
                style={"background": color1, "color": title_color,
                    'textAlign': 'center', 'border-radius': border_radius, "margin-top": "15px"}),
            html.Div([
                html.Div(style={'padding': 3}),
                dcc.Slider(id = 'year_slider', 
                    min = 1942, 
                    max = 2021, 
                    value = 2021,
                    step = 1,
                    marks = {
                        1942: "1942",
                        2021: "2021"},
                    tooltip = {"placement": "bottom", "always_visible": False},
                    dots = True
                    
                   )], style={"border": f"{border_width} solid {color2}", 'border-radius': border_radius}),

            html.P("Select Genres",
                style={"background": color1, "color": title_color,
                       'textAlign': 'center', 'border-radius': border_radius,
                       "margin-top": "15px"}),
            html.Div([
                dcc.Dropdown(
                        id="dropdown",
                        options=df.genres.unique().tolist(),
                        value=["International", "Dramas", "Thrillers", "Comedies"],

                        multi=True,
                        style={"background-color": transparent, "border": "0", "color": "black"}
                )], style={"border": f"{border_width} solid {color2}",
                    'border-radius': border_radius}
            ),

            html.P("Select Ratings",
                style={"background": color1, "color": title_color,
                       'textAlign': 'center', 'border-radius': border_radius,
                        "margin-top": "15px"}),
            html.Div([
                dcc.Dropdown(
                        id="dropdown_ratings",
                        options=[i for i in df.rating.unique().tolist() if str(i) not in ['66 min', '84 min', 'nan', '74 min', 'null']],
                        value=['PG-13','TV-MA','PG','TV-14','TV-PG','TV-Y','R','TV-G','G','NC-17','NR'], 

                        multi=True,
                        style={"background-color": transparent, "border": "0", "color": "black"}
                )], style={"border": f"{border_width} solid {color2}", 'border-radius': border_radius}
            )
                       ],
        md=4, style={'width': '17%'}),   
        
        
        dbc.Col([
            dbc.Row([
                dbc.Col([
                html.H1("etflix Explorer", style={"font-weight": "bold", "fontSize":70}),
                ], md=4, style={"color": "#E50914", "width": "43%"}), 
                
                dbc.Col([
                    dbc.Button(
                        "ⓘ",
                        id="popover-target",
                        className="sm",
                        style={"border": color2, "background": f"{color1}95", 'margin-top': "30px"},
                    ),
                    dbc.Popover(
                        [
                            dbc.PopoverHeader("Welcome to Netflix Explorer!"),
                            dbc.PopoverBody([
                                             html.P("This dashboard contains:"), 
                                             html.P("• The map - Number of movies and TV shows produced worldwide"),
                                             html.P("• The directors plot - Top number of movies and TV shows produced by directors"),
                                             html.P("• The durations plots - Durations of movies and TV shows per selected genre")
                            ]),
                            dbc.PopoverBody([
                                html.P("To filter the data displayed:"),
                                html.P("• Select the desired Year, Genre, and Rating from the side bar")
                            
                            ])
                        ],
                        target="popover-target",
                        trigger="legacy",
                        placement="bottom"
                    )
                ]),
            ]),



            html.H3("Movies and TV shows produced worldwide",
                style={"background": color1, "color": title_color, 
                       'textAlign': 'center', 'border-radius': border_radius, "width": "94.5%"}),
            html.Div([
                html.Iframe(
                id = "world_map",
                srcDoc = world_map(["International", "Dramas", "Thrillers", "Comedies"],
                                   ['PG-13','TV-MA','PG','TV-14','TV-PG','TV-Y','R','TV-G','G','NC-17','NR'], 
                                   2021),
                style={'border': '0', 'width': '100%', 'height': '500px', "margin-left": "30px", "margin-top": "20px"})
            ], style={"border": f"{border_width} solid {color2}", 'border-radius': border_radius, 
                "width": "94.5%", "height": "470px"}),

            dbc.Row([
                dbc.Col([
                    html.H3("Top 10 directors",
                        style={"background": color1, "color": title_color, 
                               'textAlign': 'center', 'border-radius': border_radius}),
                    html.Div([
                        html.Iframe(
                            id="plot_directors",
                            srcDoc = plot_directors(["International", "Dramas", "Thrillers", "Comedies"],
                                                    ['PG-13','TV-MA','PG','TV-14','TV-PG','TV-Y','R','TV-G','G','NC-17','NR'], 
                                                    2021),
                            style={
                                "border-width": "1",
                                "width": "100%",
                                "height": "300px",
                                "top": "20%",
                                "left": "70%",
                                "margin-top": "25px"
                            },
                        ),   
                    ], style={"border": f"{border_width} solid {color2}", 'border-radius': border_radius, "height": "300px"})
                ], md=4, style={"width": "55%"}),
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
                                                                        cat = ["International", "Dramas", "Thrillers", "Comedies"],
                                                                        rate =   ['PG-13','TV-MA','PG','TV-14','TV-PG','TV-Y','R','TV-G','G','NC-17','NR'], 
                                                                        title = "Duration of Movies"
                                                                        )),
                                                                        label='Movie', tab_id='Movie'),
                                    dbc.Tab(html.Iframe(
                                                id = "tv_duration",
                                                style = {"width": "400px", "height": "320px"} ,
                                                srcDoc=plot_hist_duration(type_name = 'TV Show',
                                                                        year = 2021,
                                                                        cat = ["International", "Dramas", "Thrillers", "Comedies"],
                                                                        rate =   ['PG-13','TV-MA','PG','TV-14','TV-PG','TV-Y','R','TV-G','G','NC-17','NR'], 
                                                                        title = "Number of Seasons"
                                                                        )),
                                                                        label='TV Show', tab_id='TV Show')
                            ])
                        ], 
                    style = {"border": f"{border_width} solid {color2}", 'border-radius': border_radius, "width": "120%", "height": "300px"}),
                ], md=4, style = {})
            ], style={"margin-top": "20px"}),

            



        ])
    ])
])


@app.callback(
    [Output("world_map", "srcDoc"),
     Output("plot_directors", "srcDoc"),
     Output("movie_duration", "srcDoc"),
     Output("tv_duration", "srcDoc"),
     Output("image_wc", "src")],
    [Input("dropdown", "value"),
    Input("dropdown_ratings", "value"),
    Input('year_slider', 'value')])

def update_output(cat, rate, year):
    map = world_map(cat, rate, year)
    directors = plot_directors(cat, rate, year)
    movie_hist = plot_hist_duration("Movie",
                                    year,
                                    cat, 
                                    rate,
                                    title = "Duration of Movies (minutes)"
                                    )
    tv_show_hist = plot_hist_duration("TV Show",
                                    year,
                                    cat,
                                    rate,
                                    title = "Number of Seasons"
                                    )
    word_cloud = title_cloud(year, cat)

    return map, directors, movie_hist, tv_show_hist, word_cloud



if __name__ == '__main__':
    app.run_server(debug = True)
