import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# ✅ Load TMDB API key from .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# 🌐 Supported Languages
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu"
}

# ✅ Fetch Genre Mapping
def get_genre_mapping():
    url = f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        genres = response.json().get("genres", [])
        return {g["id"]: g["name"] for g in genres}
    except Exception as e:
        print(f"❌ Failed to fetch genre mapping: {e}")
        return {}

# ✅ Fetch movies by language and pages
def fetch_movies_by_language(lang_code, pages=100):
    movies = []
    for page in range(1, pages + 1):
        url = (
            f"{BASE_URL}/discover/movie"
            f"?api_key={TMDB_API_KEY}&with_original_language={lang_code}"
            f"&sort_by=popularity.desc&page={page}"
        )
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            for movie in response.json().get("results", []):
                movies.append({
                    "title": movie.get("title", ""),
                    "language": LANGUAGES.get(lang_code, lang_code),
                    "genre_ids": movie.get("genre_ids", []),
                    "release_date": movie.get("release_date", ""),
                    "popularity": movie.get("popularity", 0),
                    "id": movie.get("id")
                })
        except Exception as e:
            print(f"❌ Failed on page {page} for {lang_code}: {e}")
        time.sleep(0.3)  # Respect API rate limits
    return movies

# ✅ Main function
def fetch_all_movies():
    genre_map = get_genre_mapping()
    all_movies = []

    for lang in LANGUAGES:
        print(f"🔍 Fetching movies for: {LANGUAGES[lang]} ({lang})")
        lang_movies = fetch_movies_by_language(lang, pages=100)
        all_movies.extend(lang_movies)

    for movie in all_movies:
        genre_names = [genre_map.get(gid, "") for gid in movie["genre_ids"]]
        movie["genres"] = ", ".join(filter(None, genre_names))
        del movie["genre_ids"]

    df = pd.DataFrame(all_movies)
    df.drop_duplicates(subset="title", inplace=True)
    df = df[df["genres"].str.strip() != ""]

    df.to_csv("movies_with_genres.csv", index=False)
    print(f"✅ Saved {len(df)} movies to 'movies_with_genres.csv'")

if __name__ == "__main__":
    fetch_all_movies()
