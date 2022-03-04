from dash import Dash, html, dcc, Input, Output
import altair as alt
import pandas as pd
import numpy as np

df = pd.read_csv("processed.csv")

app = Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)
server = app.server

app.layout = html.Div(
    [
        html.H2("Netflix Dash app"),
        html.P("Select Movie/ TV Show genres"),
        dcc.Dropdown(
            id="dropdown",
            options=df.genres.unique().tolist(),
            value=["International"],
            multi=True,
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
    Output("iframe", "srcDoc"), Input("dropdown", "value")  # , Input("radio", "value")
)
def plot_directors(cat):

    click = alt.selection_multi()

    plot_df = (
        df[df["genres"].isin(cat)]
        .query("director != 'Missing'")
        .groupby(["director", "country"])
        .show_id.nunique()
        .reset_index()
        .sort_values(ascending=False, by="show_id")
    )

    chart = (
        alt.Chart(plot_df[0:10], title="Top 10 Directors in terms of number of content")
        .mark_bar(color="#b20710")
        .encode(
            y=alt.Y("director", sort="-x", title=""),
            x=alt.X("sum(show_id)", title="Number of movies + TV shows"),
            opacity=alt.condition(click, alt.value(1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("director", title="Director"),
                alt.Tooltip("sum(show_id)", title="Count"),
            ],
        )
        .add_selection(click)
    )

    return chart.to_html()


if __name__ == "__main__":
    app.run_server(debug=True)
