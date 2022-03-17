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
mod_df["genres_old"] = genres_series
mod_df = mod_df.explode("genres_old")
mod_df["genres_old"] = mod_df.genres_old.str.strip()

mod_df['genres'] = mod_df.genres_old.str.replace('TV', '', regex=True).str.replace('Shows', '', regex=True).str.replace('Movies', '', regex=True).str.strip()

# Genres with less than 250 entries is put under Others category
genres_dict = {
    'International ': 'International ',
    'Dramas': 'Dramas',
    'Comedies': 'Comedies',
    'Action & Adventure': 'Action',
    'Documentaries': 'Documentaries',
    'Romantic': 'Romantic',
    'Children & Family': 'Kids',
    'Thrillers': 'Thrillers',
    'Crime': 'Thrillers',
    'Horror': 'Thrillers',
     "Kids'": 'Kids',
    'Music & Musicals': 'Musicals',
    'Docuseries': 'Documentaries',
    'Stand-Up Comedy': 'Comedies ',
    'Sci-Fi & Fantasy': 'Sci-Fi & Fantasy',
    'British': 'International',
    'Reality': 'Reality',
     "Sports": 'Sports',
    'Spanish-Language': 'International',
    'Anime Series': 'Anime',
    'Mysteries': 'Thrillers',
    'Stand-Up Comedy & Talk': 'Comedies',
    'Anime Features': 'Anime',
    'Korean': 'International',
    'Reality': 'RealityTV',
    'Classic': 'Others',
    'LGBTQ': 'Others',
    '': 'Others',
    'Science & Nature': 'Others',
    'Cult': 'Others',
    'Faith & Spirituality': 'Others',
    'Teen': 'Others',
    'Classic & Cult': 'Others'
}

mod_df['genres'] = mod_df['genres'].replace(genres_dict)
mod_df['genres'].unique()
mod_df.to_csv("data/processed/processed.csv", index=False)