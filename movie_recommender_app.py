
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

# Streamlit UI
def main():
    st.set_page_config(page_title="Movie Recommender", layout="centered")
    st.title("🎬 Movie Recommendation Engine")

    df = load_data()
    similarity = compute_similarity(df)

    movie_list = df['title'].values
    selected_movie = st.selectbox("Choose a movie to get recommendations:", movie_list)

    if st.button("Recommend"):
        recommendations = recommend(selected_movie, df, similarity)
        if recommendations:
            st.subheader(f"Top 10 movies similar to '{selected_movie}':")
            for title, score in recommendations:
                st.write(f"- {title} (Similarity: {score})")
        else:
            st.warning("Movie not found in dataset.")

if __name__ == '__main__':
    main()
