import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

# ✅ Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Load movie data
def load_data():
    df = pd.read_csv("C:/Users/kailas/OneDrive/Documents/movie_recom/movies_with_genres.csv")
    df.dropna(subset=['genres'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# ✅ TF-IDF similarity
def compute_similarity(df):
    vectorizer = TfidfVectorizer(stop_words='english')
    features = vectorizer.fit_transform(df['genres'])
    return cosine_similarity(features)

# ✅ Recommend similar movies
def recommend(movie_title, df, similarity):
    if movie_title not in df['title'].values:
        return []
    index = df[df['title'] == movie_title].index[0]
    scores = list(enumerate(similarity[index]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:11]
    return [(df.iloc[i]['title'], round(score, 3)) for i, score in sorted_scores]

# ✅ Fetch poster, overview, reviews
def fetch_movie_details(movie_name):
    try:
        query = movie_name.strip().replace(":", "").replace("&", "and")
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        res = requests.get(search_url).json()
        movie = res.get("results", [{}])[0]
        movie_id = movie.get("id")
        poster_path = movie.get("poster_path")
        overview = movie.get("overview", "No description available.")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        # Reviews
        review_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}"
        review_data = requests.get(review_url).json().get("results", [])
        reviews = [f"**{r['author']}**: {r['content'][:300]}..." for r in review_data[:2]] or ["No reviews available."]
        return poster_url, overview, reviews
    except Exception as e:
        print(f"[Error fetch_movie_details] {e}")
        return None, "TMDB info unavailable.", ["No reviews available."]

# ✅ Trailer from YouTube via TMDB
def fetch_trailer_url(movie_name):
    try:
        query = movie_name.strip().replace(":", "").replace("&", "and")
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        movie_id = requests.get(search_url).json().get("results", [{}])[0].get("id")
        video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
        video_data = requests.get(video_url).json().get("results", [])
        for video in video_data:
            if video["site"] == "YouTube" and video["type"] == "Trailer":
                return f"https://www.youtube.com/watch?v={video['key']}"
    except Exception as e:
        print(f"[Error fetch_trailer_url] {e}")
    return None

# ✅ AI Assistant with custom prompt
def chat_with_ai(user_input):
    try:
        prompt = (
            "You are a smart and friendly AI assistant inside a movie and web series recommendation app. "
            "You specialize in helping users with movie and series suggestions, genres, streaming platforms, and anything related to films or TV. "
            "When someone asks about a specific movie or series, tell them what it’s about in simple language, "
            "mention similar titles in vertical list format with platform info (e.g., [Netflix], [Prime Video]). "
            "Also answer questions about genres (e.g., thriller, romantic), actor-based suggestions, moods (e.g., bored, sad), and upcoming releases. "
            "Be helpful, human-like, and friendly. Never say 'I don't know' — always suggest something useful."
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI response failed: {str(e)}"

# ✅ Streamlit App
def main():
    st.set_page_config(page_title="Movie Recommender + AI", layout="centered")
    st.title("🎬 Movie Recommendation Engine with Posters, Reviews, Trailers & AI")

    df = load_data()
    similarity = compute_similarity(df)

    movie_list = df['title'].values
    selected_movie = st.selectbox("🎥 Choose a movie to get recommendations:", movie_list)

    if st.button("🎯 Recommend"):
        recommendations = recommend(selected_movie, df, similarity)
        if recommendations:
            st.subheader(f"Top 10 similar movies to '{selected_movie}':")
            for title, score in recommendations:
                st.markdown(f"### 🎬 {title} ({score*100:.1f}%)")
                poster, overview, reviews = fetch_movie_details(title)
                if poster:
                    st.image(poster, width=220)
                st.write(f"📖 {overview}")

                trailer_url = fetch_trailer_url(title)
                if trailer_url:
                    st.video(trailer_url)

                st.markdown("📝 **Reviews:**")
                for review in reviews:
                    st.markdown(f"- {review}")
                st.markdown("---")
        else:
            st.warning("Movie not found in dataset.")

    # 🧠 Sidebar AI Assistant
    st.sidebar.header("💬 Ask the AI")
    user_input = st.sidebar.text_area("Type your question here (about movies, web series, genres, moods...)")
    if st.sidebar.button("Ask AI"):
        with st.spinner("Thinking..."):
            answer = chat_with_ai(user_input)
            st.sidebar.success("Answer:")
            st.sidebar.write(answer)

if __name__ == "__main__":
    main()
