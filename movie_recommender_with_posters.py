import os
print("Current Working Directory:", os.getcwd())
print("Files in current directory:", os.listdir())

import streamlit as st
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TMDB_API_KEY = "b134830ef4bfd4ae256a4046ee695176"

# Load Data
def load_data():
    df = pd.read_csv("movies.csv")
    df.dropna(subset=['genres'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# Compute Similarity Matrix
def compute_similarity(df):
    vectorizer = TfidfVectorizer(stop_words='english')
    feature_vectors = vectorizer.fit_transform(df['genres'])
    similarity = cosine_similarity(feature_vectors)
    return similarity

# Recommend Movies
def recommend(movie_title, df, similarity):
    if movie_title not in df['title'].values:
        return []
    index = df[df['title'] == movie_title].index[0]
    similarity_scores = list(enumerate(similarity[index]))
    sorted_movies = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:11]
    return [(df.iloc[i]['title'], round(score, 3)) for i, score in sorted_movies]

# Fetch movie poster and overview using TMDB
def fetch_movie_details(movie_name):
    movie_name = movie_name.strip().replace(":", "").replace("&", "and")
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    response = requests.get(url)
    data = response.json()
    if data.get('results'):
        poster_path = data['results'][0].get('poster_path')
        overview = data['results'][0].get('overview', 'No description available.')
        full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        return full_poster_url, overview
    return None, "No description available."

# Streamlit UI
def main():
    st.set_page_config(page_title="Movie Recommender", layout="centered")
    st.title("🎬 Movie Recommendation Engine with Posters")

    df = load_data()
    similarity = compute_similarity(df)

    movie_list = df['title'].values
    selected_movie = st.selectbox("Choose a movie to get recommendations:", movie_list)

    if st.button("Recommend"):
        recommendations = recommend(selected_movie, df, similarity)
        if recommendations:
            st.subheader(f"Top 10 movies similar to '{selected_movie}':")
            for title, score in recommendations:
                st.markdown(f"### 🎬 {title} (Score: {score})")
                poster_url, overview = fetch_movie_details(title)
                if poster_url:
                    st.image(poster_url, width=200)
                st.write(overview)
                st.markdown("---")
        else:
            st.warning("Movie not found in dataset.")

if __name__ == '__main__':
    main()
