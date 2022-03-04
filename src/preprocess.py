# author: Rohit Rawat
# date: 2022-03-03

import pandas as pd
import numpy as np

df = pd.read_csv("data/raw/netflix_titles.csv")

# Indivudal directors in seperate rows
df["director"] = df["director"].astype("string")
mod_df = df.copy()
mod_df.director = mod_df.director.replace(np.nan, "Missing", regex=True)
director_series = [str.split(",") for str in mod_df.director.values]
mod_df["director"] = director_series
mod_df = mod_df.explode("director")
mod_df["director"] = mod_df.director.str.strip()

# Categorising genres
genres_series = [str.split(",") for str in mod_df.listed_in.values]
mod_df["genres"] = genres_series
mod_df = mod_df.explode("genres")
mod_df["genres"] = mod_df.genres.str.strip()

cond1 = (mod_df.genres == "Anime Features") | (mod_df.genres == "Anime Series")
mod_df.loc[cond1, "genres"] = "Anime"
cond2 = (mod_df.genres == "Comedies") | (mod_df.genres == "TV Comedies")
mod_df.loc[cond2, "genres"] = "Comedies"
cond3 = (mod_df.genres == "Thrillers") | (mod_df.genres == "TV Thrillers")
mod_df.loc[cond3, "genres"] = "Thrillers"
cond4 = (mod_df.genres == "TV Horror") | (mod_df.genres == "Horror Movies")
mod_df.loc[cond4, "genres"] = "Horror"
cond5 = (mod_df.genres == "Dramas") | (mod_df.genres == "TV Dramas")
mod_df.loc[cond5, "genres"] = "Dramas"
cond6 = (mod_df.genres == "Action & Adventure") | (
    mod_df.genres == "TV Action & Adventure"
)
mod_df.loc[cond6, "genres"] = "Action & Adventure"
cond7 = (mod_df.genres == "International TV Shows") | (
    mod_df.genres == "International Movies"
)
mod_df.loc[cond7, "genres"] = "International"
cond8 = (mod_df.genres == "Romantic TV Shows") | (mod_df.genres == "Romantic Movies")
mod_df.loc[cond8, "genres"] = "Romantic"
cond9 = (
    (mod_df.genres == "Classic & Cult TV")
    | (mod_df.genres == "Classic Movies")
    | (mod_df.genres == "Cult Movies")
)
mod_df.loc[cond9, "genres"] = "Classic & Cult"
cond10 = (mod_df.genres == "Docuseries") | (mod_df.genres == "Documentaries")
mod_df.loc[cond10, "genres"] = "Documentaries"


mod_df.to_csv("data/processed/processed.csv", index=False)
