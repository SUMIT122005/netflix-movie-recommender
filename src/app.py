import streamlit as st
import pickle
import requests

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Netflix Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ---------------------------------------------------
# LOAD CUSTOM CSS
# ---------------------------------------------------

with open("assets/netflix.css") as f:

    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# TMDB API KEY
# ---------------------------------------------------

API_KEY = "4eb66be013b4302a2df866383dba9cfd"

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

movies = pickle.load(
    open("models/movie_list.pkl", "rb")
)

similarity = pickle.load(
    open("models/similarity.pkl", "rb")
)

# ---------------------------------------------------
# FETCH POSTER
# ---------------------------------------------------

@st.cache_data
def fetch_poster(movie_title):

    try:

        url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={API_KEY}"
            f"&query={movie_title}"
        )

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        if (
            "results" in data and
            len(data["results"]) > 0
        ):

            for result in data["results"]:

                poster_path = result.get(
                    "poster_path"
                )

                if poster_path:

                    return (
                        "https://image.tmdb.org/t/p/w500"
                        + poster_path
                    )

    except Exception as e:

        print("Poster Error:", e)

    return (
        "https://via.placeholder.com/"
        "300x450?text=No+Poster"
    )

# ---------------------------------------------------
# FETCH TRAILER
# ---------------------------------------------------

@st.cache_data
def fetch_trailer(movie_title):

    try:

        search_url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={API_KEY}"
            f"&query={movie_title}"
        )

        search_response = requests.get(
            search_url
        )

        search_data = search_response.json()

        movie_id = search_data['results'][0]['id']

        video_url = (
            f"https://api.themoviedb.org/3/movie/"
            f"{movie_id}/videos"
            f"?api_key={API_KEY}"
        )

        video_response = requests.get(
            video_url
        )

        video_data = video_response.json()

        for video in video_data['results']:

            if video['type'] == 'Trailer':

                return (
                    "https://www.youtube.com/watch?v="
                    + video['key']
                )

    except Exception as e:

        print("Trailer Error:", e)

    return None

# ---------------------------------------------------
# TRENDING MOVIES
# ---------------------------------------------------

@st.cache_data
def get_trending_movies():

    try:

        url = (
            "https://api.themoviedb.org/3/trending/movie/day"
            f"?api_key={API_KEY}"
        )

        response = requests.get(url)

        data = response.json()

        trending = []

        for movie in data['results'][:10]:

            trending.append({

                "title": movie['title'],

                "poster": (
                    "https://image.tmdb.org/t/p/w500"
                    + movie['poster_path']
                )
            })

        return trending

    except Exception as e:

        print("Trending Error:", e)

        return []

# ---------------------------------------------------
# RECOMMEND FUNCTION
# ---------------------------------------------------

def recommend(movie):

    movie_index = movies[
        movies['title'] == movie
    ].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []

    recommended_posters = []

    recommended_trailers = []

    for i in movie_list:

        movie_title = movies.iloc[i[0]].title

        recommended_movies.append(
            movie_title
        )

        recommended_posters.append(
            fetch_poster(movie_title)
        )

        recommended_trailers.append(
            fetch_trailer(movie_title)
        )

    return (
        recommended_movies,
        recommended_posters,
        recommended_trailers
    )

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("🎬 Netflix Recommender")

genre = st.sidebar.selectbox(
    "Select Genre",
    [
        "All",
        "Action",
        "Comedy",
        "Drama",
        "Horror",
        "Romance",
        "Sci-Fi"
    ]
)

# ---------------------------------------------------
# HERO SECTION
# ---------------------------------------------------

st.markdown(
    """
    <div class='hero'>
        <h1>NETFLIX MOVIE RECOMMENDER</h1>
        <p>
            Discover movies, trailers and trending content
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# SEARCH BOX
# ---------------------------------------------------

selected_movie = st.selectbox(
    "Search Movie",
    movies['title'].values
)

# ---------------------------------------------------
# RECOMMEND BUTTON
# ---------------------------------------------------

if st.button("Recommend Movies"):

    names, posters, trailers = recommend(
        selected_movie
    )

    st.subheader("Recommended Movies")

    cols = st.columns(5)

    for idx, col in enumerate(cols):

        with col:

            st.image(
                posters[idx],
                use_container_width=True
            )

            st.markdown(
                f"### {names[idx]}"
            )

            if trailers[idx]:

                st.markdown(
                    f"""
                    [▶ Watch Trailer]
                    ({trailers[idx]})
                    """
                )

# ---------------------------------------------------
# TRENDING MOVIES
# ---------------------------------------------------

st.subheader("🔥 Trending Movies")

trending = get_trending_movies()

trend_cols = st.columns(5)

for idx, movie in enumerate(trending[:5]):

    with trend_cols[idx]:

        st.image(
            movie['poster'],
            use_container_width=True
        )

        st.write(movie['title'])