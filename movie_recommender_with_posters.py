import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

# ✅ Load API keys from .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Load movie data (updated with cast/keywords)
@st.cache_resource
def load_data():
    df = pd.read_csv("movies_with_cast_keywords.csv")  # Ensure this file exists!
    df.dropna(subset=['genres', 'cast', 'keywords'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# ✅ Compute hybrid similarity (genres + cast + keywords)
@st.cache_data
def compute_similarity(df):
    # Combine all textual features into one string per movie
    df["combined_features"] = (
        df["genres"].fillna("") + " " +
        df["cast"].fillna("") + " " +
        df["keywords"].fillna("")
    )
    
    # TF-IDF on combined features
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df["combined_features"])
    
    # Cosine similarity
    return cosine_similarity(tfidf_matrix, tfidf_matrix)

# ✅ Recommend similar movies (uses hybrid similarity)
def recommend(movie_title, df, similarity):
    try:
        filtered_df = df.reset_index(drop=True)
        index = filtered_df[filtered_df['title'] == movie_title].index[0]
        scores = list(enumerate(similarity[index]))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:11]
        return [(filtered_df.iloc[i]['title'], round(score, 3)) for i, score in sorted_scores]
    except Exception as e:
        print(f"[ERROR in recommend] {e}")
        return []

# ✅ Fetch enhanced movie details (includes cast/keywords)
def fetch_enhanced_movie_details(movie_name):
    try:
        query = movie_name.strip().replace(":", "").replace("&", "and")
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        res = requests.get(search_url).json()
        movie = res.get("results", [{}])[0]
        movie_id = movie.get("id")
        
        # Fetch cast (top 5 actors)
        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
        credits = requests.get(credits_url).json()
        cast = ", ".join([actor["name"] for actor in credits.get("cast", [])[:5]])
        
        # Fetch keywords (themes like "superhero", "time travel")
        keywords_url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={TMDB_API_KEY}"
        keywords = ", ".join([kw["name"] for kw in requests.get(keywords_url).json().get("keywords", [])])
        
        # Existing poster/overview
        poster_path = movie.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w342{poster_path}" if poster_path else "https://via.placeholder.com/220x330?text=No+Poster"
        overview = movie.get("overview", "No description available.")
        
        return {
            "poster_url": poster_url,
            "overview": overview,
            "cast": cast,
            "keywords": keywords
        }
    except Exception as e:
        print(f"[Error fetch_enhanced_movie_details] {e}")
        return {
            "poster_url": "https://via.placeholder.com/220x330?text=No+Poster",
            "overview": "No description available.",
            "cast": "",
            "keywords": ""
        }

# ✅ Fetch YouTube trailer
def fetch_trailer_url(movie_name):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        movie_id = requests.get(search_url).json().get("results", [{}])[0].get("id")
        video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
        video_data = requests.get(video_url).json().get("results", [])
        for video in video_data:
            if video["site"] == "YouTube" and video["type"] == "Trailer":
                return f"https://www.youtube.com/watch?v={video['key']}"
    except Exception as e:
        print(f"[Error fetch_trailer_url] {e}")
    return None

# ✅ AI Assistant using OpenAI
def chat_with_ai(user_input):
    prompt = (
        "You are a smart and friendly AI assistant inside a movie and web series recommendation app. "
        "You specialize in helping users with movie and series suggestions, genres, streaming platforms, and anything related to films or TV. "
        "When someone asks about a specific movie or series, tell them what it’s about in simple language, "
        "mention similar titles in vertical list format with platform info (e.g., [Netflix], [Amazon Prime]). "
        "Be helpful, human-like, and friendly."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI response failed: {str(e)}"

# ✅ Main Streamlit App
def main():
    st.set_page_config(page_title="Movie Recommender + AI", layout="centered")
    st.title("🎬 Movie Recommendation Engine with Posters, Reviews, Trailers & AI")
    df_full = load_data()
    
    # Language filter (optional, keep if you have language data)
    language_list = ['all'] + sorted(df_full['language'].dropna().unique())
    selected_language = st.selectbox("🌐 Filter by Language", language_list, key="language_filter")
    df = df_full if selected_language == 'all' else df_full[df_full['language'] == selected_language]
    if df.empty:
        st.warning("No movies found for this language.")
        return
    
    similarity = compute_similarity(df)
    movie_list = df['title'].values
    selected_movie = st.selectbox("🎥 Choose a movie to get recommendations:", movie_list)
    
    if st.button("🎯 Recommend"):
        recommendations = recommend(selected_movie, df, similarity)
        if recommendations:
            st.subheader(f"Top 10 similar movies to '{selected_movie}':")
            for idx, (title, score) in enumerate(recommendations):
                st.markdown(f"### 🎬 {title} ({score*100:.1f}%)")
                enhanced_details = fetch_enhanced_movie_details(title)
                
                # Display poster and overview
                st.image(enhanced_details["poster_url"], width=220)
                st.write(f"📖 {enhanced_details['overview']}")
                
                # NEW: Show cast and keywords
                st.write(f"🎭 Cast: {enhanced_details['cast']}")
                st.write(f"🔑 Keywords: {enhanced_details['keywords']}")
                
                # Trailer and reviews (unchanged)
                trailer_url = fetch_trailer_url(title)
                if trailer_url:
                    st.video(trailer_url)
                reviews = fetch_reviews(title)  # Assume you have a fetch_reviews function
                st.markdown("📝 **Reviews:**")
                for review in reviews:
                    st.markdown(f"- {review}")
                st.markdown("---")
        else:
            st.warning("No recommendations found.")

    st.sidebar.header("💬 Ask AI")
    user_input = st.sidebar.text_area("Type your movie/web series question...")
    if st.sidebar.button("Ask AI"):
        with st.spinner("Thinking..."):
            answer = chat_with_ai(user_input)
            st.sidebar.success("Answer:")
            st.sidebar.write(answer)

if __name__ == '__main__':
    main()
