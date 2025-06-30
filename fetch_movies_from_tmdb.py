import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

# ✅ Load TMDB API Key from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"  # <-- Add this line

print("TMDB_API_KEY:", TMDB_API_KEY)  # Should print your key, not None or empty

# ✅ Language codes and labels
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu"
}

# ✅ Get genre mapping (id to name)
def get_genre_mapping():
    try:
        url = f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        genres = response.json().get("genres", [])
        return {g["id"]: g["name"] for g in genres}
    except Exception as e:
        print(f"❌ Failed to fetch genre mapping: {e}")
        return {}

# ✅ Fetch movies by language with retry and increased sleep to avoid rate limit
def fetch_movies_by_language(lang_code, pages=2):  # Start with 2 pages for testing
    movies = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for page in range(1, pages + 1):
        url = (
            f"{BASE_URL}/discover/movie"
            f"?api_key={TMDB_API_KEY}&with_original_language={lang_code}"
            f"&sort_by=popularity.desc&page={page}"
        )
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=10, headers=headers)
                response.raise_for_status()
                results = response.json().get("results", [])
                for movie in results:
                    movies.append({
                        "title": movie.get("title", ""),
                        "language": LANGUAGES.get(lang_code, lang_code),
                        "genre_ids": movie.get("genre_ids", []),
                        "release_date": movie.get("release_date", ""),
                        "popularity": movie.get("popularity", 0),
                        "id": movie.get("id")
                    })
                break  # Success, exit retry loop
            except Exception as e:
                print(f"❌ Failed on page {page} for {lang_code} (attempt {attempt+1}): {e}")
                if attempt < retries - 1:
                    time.sleep(10)  # Wait longer before retrying
                else:
                    print(f"❌ Giving up on page {page} for {lang_code}")
        time.sleep(5)  # Increase sleep to 5 seconds between requests
    return movies

# ✅ Fetch and Save All Movies
def fetch_all_movies():
    genre_map = get_genre_mapping()
    all_movies = []

    for lang_code in LANGUAGES:
        print(f"🔍 Fetching movies for: {LANGUAGES[lang_code]} ({lang_code})")
        movies = fetch_movies_by_language(lang_code, pages=2)  # Start with 2 pages for testing
        all_movies.extend(movies)

    # ✅ Add genres
    for movie in all_movies:
        genre_names = [genre_map.get(gid, "") for gid in movie.get("genre_ids", [])]
        movie["genres"] = ", ".join(genre_names)
        movie.pop("genre_ids", None)

    df = pd.DataFrame(all_movies)
    df.drop_duplicates(subset="title", inplace=True)

    # ✅ Save to movies_with_genres.csv
    try:
        df.to_csv("movies_with_genres.csv", index=False)
        print(f"✅ Saved {len(df)} movies to movies_with_genres.csv")
    except Exception as e:
        print(f"❌ Could not save CSV: {e}")

if __name__ == "__main__":
    print("TMDB_API_KEY:", TMDB_API_KEY)  # Debug: Check if API key is loaded
    fetch_all_movies()