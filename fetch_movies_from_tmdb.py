import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

# ✅ Load TMDB API key from .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "b134830ef4bfd4ae256a4046ee695176")
BASE_URL = "https://api.themoviedb.org/3"

# 🌍 Supported Languages (you can add more)
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu"
}

# ✅ Fetch genre mappings
def get_genre_mapping():
    url = f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    genres = response.json().get("genres", [])
    return {g["id"]: g["name"] for g in genres}

# ✅ Fetch movies by language
def fetch_movies_by_language(lang_code, pages=100):
    all_movies = []
    for page in range(1, pages + 1):
        url = (
            f"{BASE_URL}/discover/movie"
            f"?api_key={TMDB_API_KEY}&with_original_language={lang_code}"
            f"&sort_by=popularity.desc&page={page}"
        )
        try:
            res = requests.get(url)
            if res.status_code == 200:
                for movie in res.json().get("results", []):
                    all_movies.append({
                        "title": movie.get("title"),
                        "language": LANGUAGES.get(lang_code, lang_code),
                        "genre_ids": movie.get("genre_ids", []),
                        "release_date": movie.get("release_date", ""),
                        "popularity": movie.get("popularity", 0),
                        "id": movie.get("id")
                    })
            else:
                print(f"Error page {page} for {lang_code}")
        except Exception as e:
            print(f"Failed on page {page} ({lang_code}): {e}")
        time.sleep(0.25)
    return all_movies

# ✅ Main fetch function
def fetch_all_movies():
    genre_map = get_genre_mapping()
    all_movies = []

    for lang in LANGUAGES:
        print(f"📥 Fetching {LANGUAGES[lang]} movies...")
        movies = fetch_movies_by_language(lang, pages=100)
        all_movies.extend(movies)

    # ✅ Map genre_ids to genre names
    for movie in all_movies:
        genre_names = [genre_map.get(genre_id, "") for genre_id in movie["genre_ids"]]
        movie["genres"] = ", ".join(filter(None, genre_names))
        del movie["genre_ids"]  # remove raw ids

    # ✅ Save to CSV
    df = pd.DataFrame(all_movies)
    df.drop_duplicates(subset="title", inplace=True)
    df.to_csv("movies.csv", index=False)
    print(f"✅ {len(df)} movies saved to movies.csv")

if __name__ == "__main__":
    fetch_all_movies()
