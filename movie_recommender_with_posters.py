import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI


# ✅ Must be the FIRST Streamlit command
st.set_page_config(page_title="🎬 Movie Recommender + AI", layout="centered")

# ✅ Load environment variables from .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Validate API keys
if not TMDB_API_KEY or not OPENAI_API_KEY:
    st.error("❌ Missing API keys in .env file. Please set TMDB_API_KEY and OPENAI_API_KEY.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Load movie data
def load_data():
    try:
        df = pd.read_csv("movies_with_genres.csv")
        if df.empty or 'genres' not in df.columns:
            st.error("❌ CSV file is empty or missing 'genres' column.")
            return

        # Ensure language column exists
        if 'language' not in df.columns:
            df['language'] = 'unknown'

        df['language'] = df['language'].fillna('unknown').str.lower()
        df.dropna(subset=['genres'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except FileNotFoundError:
        st.error("❌ movies_with_genres.csv not found in project directory.")
        st.stop()

def compute_similarity(df):
    vectorizer = TfidfVectorizer(stop_words='english')
    features = vectorizer.fit_transform(df['genres'])
    return cosine_similarity(features)

def recommend(movie_title, df, similarity):
    if movie_title not in df['title'].values:
        return []
    index = df[df['title'] == movie_title].index[0]
    if index >= similarity.shape[0]:
        return []  # Prevent out-of-bounds error
    scores = list(enumerate(similarity[index]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:11]
    return [(df.iloc[i]['title'], round(score, 3)) for i, score in sorted_scores]



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

        review_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}"
        review_data = requests.get(review_url).json().get("results", [])
        reviews = [f"**{r['author']}**: {r['content'][:300]}..." for r in review_data[:2]] or ["No reviews available."]
        return poster_url, overview, reviews
    except Exception as e:
        print(f"[Error fetch_movie_details] {e}")
        return None, "TMDB info unavailable.", ["No reviews available."]

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

def chat_with_ai(user_input):
    try:
        prompt = (
            "You are a smart and friendly AI assistant inside a movie and web series recommendation app. "
            "You help users find movies or series based on genres, platforms, moods, actors, or questions like 'what to watch when bored'. "
            "Always explain movie names briefly and list similar movies vertically like:\n"
            "1. Movie One [Netflix]\n2. Movie Two [Amazon Prime]"
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

# ✅ Main Streamlit App
def main():
    st.title("🎬 Movie Recommender")

    df = load_data()
    similarity = compute_similarity(df)

    language_list = sorted(df['language'].unique())
    selected_language = st.selectbox("🌐 Filter by Language", language_list, key="language_selector")

    filtered_df = df[df['language'] == selected_language]
    movie_list = filtered_df['title'].values
    selected_movie = st.selectbox("🎥 Choose a movie:", movie_list, key="movie_selector")

    if st.button("🎯 Recommend"):
        recommendations = recommend(selected_movie, filtered_df, similarity)
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
    user_input = st.sidebar.text_area("Type your question about movies, web series, actors, moods...")
    if st.sidebar.button("Ask AI"):
        with st.spinner("Thinking..."):
            answer = chat_with_ai(user_input)
            st.sidebar.success("Answer:")
            st.sidebar.write(answer)

   
    st.warning("Movie not found in dataset.")

    # 🧠 Sidebar AI Assistant
    st.sidebar.header("💬 Ask the AI")
    user_input = st.sidebar.text_area("Type your question about movies, web series, actors, moods...")
    if st.sidebar.button("Ask AI"):
        with st.spinner("Thinking..."):
            answer = chat_with_ai(user_input)
            st.sidebar.success("Answer:")
            st.sidebar.write(answer)

if __name__ == "__main__":
    main()
    main()
    main() 
