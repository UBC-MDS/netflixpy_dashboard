from dash import Dash, html, dcc, Input, Output
import altair as alt
import pandas as pd
import numpy as np


app = Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)
server = app.server

app.layout = html.Div(
    [
        html.H2("Netflix Dash app"),
        # html.H3("Checklist"),
        html.P("Select Movie/ TV Show"),
        dcc.Checklist(
            id="check", options=["Movie", "TV Show"], value=["Movie", "TV Show"]
        ),
        html.Iframe(
            id="iframe",
            style={
                "border-width": "1",
                "width": "36%",
                "height": "300px",
                "top": "20%",
                "left": "70%",
            },
        ),
    ]
)

# Set up callbacks/backend
@app.callback(
    Output("iframe", "srcDoc"), Input("check", "value")  # , Input("radio", "value")
)
def plot_altair(cat):

    df = pd.read_csv("netflix_titles.csv")
    df["director"] = df["director"].astype("string")
    dir_df = df.dropna(subset=["director"]).copy()
    genres_series = [str.split(",") for str in dir_df.director.values]
    dir_df["director"] = genres_series
    dir_df = dir_df.explode("director")
    dir_df["director"] = dir_df.director.str.strip()

    plot_df = (
        dir_df[dir_df["type"].isin(cat)]
        .groupby(["director", "country"])
        .show_id.count()
        .reset_index()
        .sort_values(ascending=False, by="show_id")
    )

    chart = (
        alt.Chart(plot_df[0:10], title="Top 10 Directors in terms of number of content")
        .mark_bar(color="#b20710")
        .encode(
            y=alt.Y("director", sort="-x", title=""),
            x=alt.X("sum(show_id)", title="Number of movies + TV shows"),
        )
        .properties(width=250)
    )

    return chart.to_html()


if __name__ == "__main__":
    app.run_server(debug=True)
