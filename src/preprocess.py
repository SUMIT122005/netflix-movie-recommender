import pandas as pd
import ast
import pickle
import os

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------
# CREATE MODELS FOLDER
# ---------------------------------------------------

os.makedirs("models", exist_ok=True)

# ---------------------------------------------------
# LOAD DATASETS
# ---------------------------------------------------

movies = pd.read_csv(
    "data/tmdb_5000_movies.csv"
)

credits = pd.read_csv(
    "data/tmdb_5000_credits.csv"
)

# ---------------------------------------------------
# MERGE DATASETS
# ---------------------------------------------------

movies = movies.merge(
    credits,
    on='title'
)

# ---------------------------------------------------
# SELECT REQUIRED COLUMNS
# ---------------------------------------------------

movies = movies[
    [
        'movie_id',
        'title',
        'overview',
        'genres',
        'keywords',
        'cast',
        'crew'
    ]
]

# ---------------------------------------------------
# REMOVE NULL VALUES
# ---------------------------------------------------

movies.dropna(inplace=True)

# ---------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------

def convert(text):

    result = []

    for i in ast.literal_eval(text):

        result.append(i['name'])

    return result

def convert_cast(text):

    result = []

    counter = 0

    for i in ast.literal_eval(text):

        if counter != 3:

            result.append(i['name'])

            counter += 1

        else:
            break

    return result

def fetch_director(text):

    result = []

    for i in ast.literal_eval(text):

        if i['job'] == 'Director':

            result.append(i['name'])

            break

    return result

# ---------------------------------------------------
# APPLY TRANSFORMATIONS
# ---------------------------------------------------

movies['genres'] = movies['genres'].apply(
    convert
)

movies['keywords'] = movies['keywords'].apply(
    convert
)

movies['cast'] = movies['cast'].apply(
    convert_cast
)

movies['crew'] = movies['crew'].apply(
    fetch_director
)

movies['overview'] = movies['overview'].apply(
    lambda x: x.split()
)

# ---------------------------------------------------
# REMOVE SPACES
# ---------------------------------------------------

movies['genres'] = movies['genres'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

movies['keywords'] = movies['keywords'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

movies['cast'] = movies['cast'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

movies['crew'] = movies['crew'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

# ---------------------------------------------------
# CREATE TAGS
# ---------------------------------------------------

movies['tags'] = (
    movies['overview'] +
    movies['genres'] +
    movies['keywords'] +
    movies['cast'] +
    movies['crew']
)

# ---------------------------------------------------
# NEW DATAFRAME
# ---------------------------------------------------

new_df = movies[
    ['movie_id', 'title', 'tags']
]

# ---------------------------------------------------
# CONVERT LIST TO STRING
# ---------------------------------------------------

new_df['tags'] = new_df['tags'].apply(
    lambda x: " ".join(x)
)

new_df['tags'] = new_df['tags'].apply(
    lambda x: x.lower()
)

# ---------------------------------------------------
# VECTORIZATION
# ---------------------------------------------------

cv = CountVectorizer(
    max_features=5000,
    stop_words='english'
)

vectors = cv.fit_transform(
    new_df['tags']
).toarray()

# ---------------------------------------------------
# SIMILARITY MATRIX
# ---------------------------------------------------

similarity = cosine_similarity(vectors)

# ---------------------------------------------------
# SAVE FILES
# ---------------------------------------------------

pickle.dump(
    new_df,
    open(
        'models/movie_list.pkl',
        'wb'
    )
)

pickle.dump(
    similarity,
    open(
        'models/similarity.pkl',
        'wb'
    )
)

print("Preprocessing completed successfully!")