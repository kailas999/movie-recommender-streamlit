import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

# ✅ Load TMDB API key from .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "b134830ef4bfd4ae256a4046ee695176")
BASE_URL = "https://api.themoviedb.org/3"

# 🌍 Languages to fetch movies from
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu"
}

# ✅ Get TMDB genre ID to name mapping
def get_genre_mapping():
    url = f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    genres = response.json().get("genres", [])
    return {g["id"]: g["name"] for g in genres}

# ✅ Fetch movies by language and number of pages (each page = ~20 movies)
def fetch_movies_by_language(lang_code, pages=100):
    movies = []
    for page in range(1, pages + 1):
        url = (
            f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}"
            f"&with_original_language={lang_code}&sort_by=popularity.desc&page={page}"
        )
        try:
            response = requests.get(url)
            if response.status_code == 200:
                for movie in response.json().get("results", []):
                    movies.append({
                        "title": movie.get("title"),
                        "language": LANGUAGES.get(lang_code, lang_code),
                        "genre_ids": movie.get("genre_ids", []),
                        "release_date": movie.get("release_date", ""),
                        "popularity": movie.get("popularity", 0),
                        "id": movie.get("id")
                    })
            else:
                print(f"⚠️ Error page {page} for {lang_code}")
        except Exception as e:
            print(f"❌ Failed on page {page} ({lang_code}): {e}")
        time.sleep(0.2)
    return movies

# ✅ Main function to fetch all data and save
def fetch_all_movies():
    genre_map = get_genre_mapping()
    all_movies = []

    for lang_code in LANGUAGES:
        print(f"📥 Fetching {LANGUAGES[lang_code]} movies...")
        lang_movies = fetch_movies_by_language(lang_code, pages=100)  # 100 pages * 20 = 2000+ movies per language
        all_movies.extend(lang_movies)

    # Map genre_ids to genre names
    for movie in all_movies:
        genre_names = [genre_map.get(gid, "") for gid in movie["genre_ids"]]
        movie["genres"] = ", ".join(genre_names)
        movie.pop("genre_ids", None)

    # Save to CSV
    df = pd.DataFrame(all_movies)
    df.drop_duplicates(subset="title", inplace=True)
    df.to_csv("movies_with_genres.csv", index=False)
    print(f"✅ Done! Saved {len(df)} movies to movies_with_genres.csv")

if __name__ == "__main__":
    fetch_all_movies()
