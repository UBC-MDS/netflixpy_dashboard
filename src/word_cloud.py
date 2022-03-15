from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import io



genres_df = pd.read_csv('data/processed/df.csv')

def title_cloud(year, cat):
    
    plot_df = (genres_df[genres_df["genres"].isin(cat)]
                .query(f"release_year <= @year"))
    

    words = " ".join(plot_df["title"].tolist())

    word_cloud = WordCloud(collocations = False, background_color = "white").generate(words)

    plt.figure()
    plt.imshow(word_cloud, interpolation = "bilinear");
    plt.axis("off")
    
    buf = io.BytesIO()
    plt.savefig(buf, format = "png", dpi=600, bbox_inches = 'tight', pad_inches = 0)
    
    return base64.b64encode(buf.getbuffer()).decode("utf8")




app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

app.layout = html.Div([
        html.Div(
            html.Img(
                id = "image_wc",
                className = "img-responsive"
                )
        ),

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
                   }
                   ),
        dcc.Dropdown(
                    id = "dropdown",
                    options = genres_df.genres.unique().tolist(),
                    value = ["Dramas"],
                    multi = True,
                    style = {'color': 'black'}
            )
        ]
)

@app.callback(
    Output("image_wc", "src"),
    [Input("dropdown", "value"),
     Input("year_slider", "value")]
)

def update_output(cat, year):
    return title_cloud(year, cat)

if __name__ == '__main__':
    app.run_server(debug = True)