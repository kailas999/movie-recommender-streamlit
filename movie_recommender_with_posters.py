import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

# Load API Keys from .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "b134830ef4bfd4ae256a4046ee695176")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def load_data():
    df = pd.read_csv("movies.csv")
    df.dropna(subset=['genres'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def compute_similarity(df):
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

def fetch_movie_details(movie_name):
    try:
        query = movie_name.strip().replace(":", "").replace("&", "and")
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('results'):
            movie = data['results'][0]
            movie_id = movie['id']
            poster_path = movie.get('poster_path')
            overview = movie.get('overview', 'No description available.')
            full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

            reviews_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}"
            reviews_response = requests.get(reviews_url).json()
            if reviews_response.get('results'):
                reviews = [f"**{r['author']}**: {r['content'][:250]}..." for r in reviews_response['results'][:2]]
            else:
                reviews = ["No reviews available."]
            return full_poster_url, overview, reviews
    except Exception as e:
        print(f"[fetch_movie_details Error] {e}")
    return None, "TMDB info unavailable.", ["No reviews available."]

def fetch_trailer_url(movie_name):
    try:
        query = movie_name.strip().replace(":", "").replace("&", "and")
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        res = requests.get(url).json()
        if res.get('results'):
            movie_id = res['results'][0]['id']
            video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
            video_response = requests.get(video_url).json()
            for video in video_response['results']:
                if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                    return f"https://www.youtube.com/watch?v={video['key']}"
    except Exception as e:
        print(f"[fetch_trailer_url Error] {e}")
    return None

def chat_with_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI response failed: {str(e)}"

def main():
    st.set_page_config(page_title="Movie Recommender", layout="centered")
    st.title("🎬 Movie Recommendation Engine with Posters, Trailers, Reviews & AI Chat")

    df = load_data()
    similarity = compute_similarity(df)

    movie_list = df['title'].values
    selected_movie = st.selectbox("🎥 Choose a movie:", movie_list)

    if st.button("🎯 Recommend"):
        recommendations = recommend(selected_movie, df, similarity)
        if recommendations:
            st.subheader(f"Top 10 movies similar to '{selected_movie}':")
            for title, score in recommendations:
                st.markdown(f"### 🎬 {title} (Score: {100 * score:.1f})")
                poster_url, overview, reviews = fetch_movie_details(title)

                if poster_url:
                    st.image(poster_url, width=200)
                st.write(overview)

                trailer_url = fetch_trailer_url(title)
                if trailer_url:
                    st.video(trailer_url)

                st.markdown("#### 🗨️ Reviews:")
                for review in reviews:
                    st.markdown(f"- {review}")
                st.markdown("---")
        else:
            st.warning("❌ Movie not found in dataset.")

    # AI Chat Assistant
    st.sidebar.header("🧠 AI Movie Assistant")
    user_question = st.sidebar.text_area("Ask something about movies or the app:")
    if st.sidebar.button("Ask AI"):
        with st.spinner("Thinking..."):
            answer = chat_with_ai(user_question)
            st.sidebar.success("Answer:")
            st.sidebar.write(answer)

if __name__ == '__main__':
    main()
