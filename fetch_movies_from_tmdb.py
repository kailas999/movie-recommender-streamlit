<<<<<<< HEAD
import pandas as pd
import requests
import time

TMDB_API_KEY = "b134830ef4bfd4ae256a4046ee695176"  # your TMDB API key

def fetch_genres(title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
        res = requests.get(search_url)
        data = res.json()
        if data['results']:
            movie_id = data['results'][0]['id']
            genre_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
            genre_res = requests.get(genre_url)
            genre_data = genre_res.json()
            genres = [g['name'] for g in genre_data.get("genres", [])]
            return " ".join(genres)
    except Exception as e:
        print(f"Error for {title}: {e}")
    return ""

# Load your movies.csv
df = pd.read_csv("movies.csv")

# Add genres column
df["genres"] = df["title"].apply(fetch_genres)

# Remove rows where no genres were fetched
df = df[df["genres"].str.strip() != ""]

# Save new file
df.to_csv("movies_with_genres.csv", index=False)
print("✅ Done: Saved as movies_with_genres.csv")

=======
import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

# ✅ Load TMDB API key from .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "your_tmdb_api_key")
BASE_URL = "https://api.themoviedb.org/3"

# 🌍 Languages you want to fetch movies for
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu"
}

# ✅ Get genre ID to name mapping from TMDB
def get_genre_mapping():
    url = f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    genres = response.json().get("genres", [])
    return {g["id"]: g["name"] for g in genres}

# ✅ Fetch movies for a given language and number of pages
def fetch_movies_by_language(lang_code, pages=100):
    movies = []
    for page in range(1, pages + 1):
        url = (
            f"{BASE_URL}/discover/movie"
            f"?api_key={TMDB_API_KEY}&with_original_language={lang_code}"
            f"&sort_by=popularity.desc&page={page}"
        )
        try:
            res = requests.get(url)
            if res.status_code == 200:
                results = res.json().get("results", [])
                for movie in results:
                    movies.append({
                        "title": movie.get("title", ""),
                        "language": LANGUAGES.get(lang_code, lang_code),
                        "genre_ids": movie.get("genre_ids", []),
                        "release_date": movie.get("release_date", ""),
                        "popularity": movie.get("popularity", 0),
                        "id": movie.get("id")
                    })
            else:
                print(f"⚠️ Error fetching page {page} for language {lang_code}")
        except Exception as e:
            print(f"❌ Exception on page {page} ({lang_code}): {e}")
        time.sleep(0.25)  # To avoid hitting API rate limits
    return movies

# ✅ Main function to fetch and save all data
def fetch_all_movies():
    genre_map = get_genre_mapping()
    all_movies = []

    for lang_code in LANGUAGES:
        print(f"🔍 Fetching movies for language: {LANGUAGES[lang_code]} ({lang_code})")
        lang_movies = fetch_movies_by_language(lang_code, pages=100)
        all_movies.extend(lang_movies)

    # ✅ Convert genre IDs to names
    for movie in all_movies:
        genres = [genre_map.get(gid, "") for gid in movie.get("genre_ids", [])]
        movie["genres"] = ", ".join(filter(None, genres))
        del movie["genre_ids"]

    # ✅ Load old data if exists and merge
    new_df = pd.DataFrame(all_movies)
    new_df.drop_duplicates(subset="title", inplace=True)

    if os.path.exists("movies.csv"):
        old_df = pd.read_csv("movies.csv")
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
        combined_df.drop_duplicates(subset="title", inplace=True)
        combined_df.to_csv("movies.csv", index=False)
        print(f"✅ Merged: {len(combined_df)} total movies saved to movies.csv")
    else:
        new_df.to_csv("movies.csv", index=False)
        print(f"✅ Saved: {len(new_df)} new movies to movies.csv")

if __name__ == "__main__":
    fetch_all_movies()
>>>>>>> 0b1c7044a9e09cec99fddb0f6b56495a8917297b
