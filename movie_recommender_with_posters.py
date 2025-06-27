import os
import streamlit as st
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TMDB_API_KEY = "b134830ef4bfd4ae256a4046ee695176"

def load_data():
    df = pd.read_csv("movies.csv")
    
    # Ensure 'genres' column exists
    if 'genres' not in df.columns:
        st.error("❌ 'genres' column not found in movies.csv. Please check your dataset.")
        return None

    # Fill missing genres and drop rows with empty genres
    df['genres'] = df['genres'].fillna("")
    df = df[df['genres'].str.strip() != ""]

    if df.empty:
        st.error("❌ DataFrame is empty after filtering. Check 'genres' column values.")
        return None

    df.reset_index(drop=True, inplace=True)
    return df

def compute_similarity(df):
    print("Checking genres column sample:", df['genres'].head())
    vectorizer = TfidfVectorizer(stop_words='english')
    feature_vectors = vectorizer.fit_transform(df['genres'])
    similarity = cosine_similarity(feature_vectors)
    return similarity

def recommend(movie_title, df, similarity):
    if movie_title not in df['title'].values:
        return []
    index = df[df['title'] == movie_title].index[0]
    similarity_scores = list(enumerate(similarity[index]))
    sorted_movies = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:11]
    return [(df.iloc[i]['title'], round(score, 3)) for i, score in sorted_movies]

# Safe API call for poster & description
def fetch_movie_details(movie_name):
    try:
        movie_name = movie_name.strip().replace(":", "").replace("&", "and")
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('results'):
            poster_path = data['results'][0].get('poster_path')
            overview = data['results'][0].get('overview', 'No description available.')
            full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            return full_poster_url, overview
    except requests.exceptions.RequestException as e:
        print(f"[Poster API Error] {e}")
    return None, "TMDB info unavailable."

# Safe API call for trailer
def fetch_trailer_url(movie_name):
    try:
        movie_name = movie_name.strip().replace(":", "").replace("&", "and")
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        search_response = requests.get(search_url, timeout=10).json()
        if search_response.get('results'):
            movie_id = search_response['results'][0]['id']
            video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
            video_response = requests.get(video_url, timeout=10).json()
            for video in video_response['results']:
                if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                    return f"https://www.youtube.com/watch?v={video['key']}"
    except requests.exceptions.RequestException as e:
        print(f"[Trailer API Error] {e}")
    return None

def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(page_title="Movie Recommender", layout="centered")
    st.title("🎬 Movie Recommendation Engine with Posters")

    df = load_data()
    if df is None:
        st.stop()  # ⛔ Stop app execution if df is invalid

    similarity = compute_similarity(df)

    movie_list = df['title'].values
    selected_movie = st.selectbox("Choose a movie to get recommendations:", movie_list)

    if st.button("Recommend"):
        recommendations = recommend(selected_movie, df, similarity)
        if recommendations:
            st.subheader(f"Top 10 movies similar to '{selected_movie}':")
            for title, score in recommendations:
                st.markdown(f"### 🎬 {title} (Score: {100* score})")
                poster_url, overview = fetch_movie_details(title)
                if poster_url:
                    st.image(poster_url, width=200)
                st.write(overview)

                trailer_url = fetch_trailer_url(title)
                if trailer_url:
                    st.video(trailer_url)

                st.markdown("---")
        else:
            st.warning("Movie not found in dataset.")

if __name__ == '__main__':
    main()
