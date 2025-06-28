import os, time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# Languages you want to include
LANGUAGES = {
    "en": "English", "hi": "Hindi", "mr": "Marathi",
    "ta": "Tamil", "te": "Telugu"
}

def get_genre_mapping():
    url = f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    res = requests.get(url).json()
    return {g["id"]: g["name"] for g in res.get("genres", [])}

def fetch_by_lang(lang_code, pages=100):
    all_movies = []
    for page in range(1, pages+1):
        url = (
            f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}"
            f"&with_original_language={lang_code}"
            f"&sort_by=popularity.desc&page={page}"
        )
        r = requests.get(url)
        if r.status_code!=200:
            print(f"▶️ Error lang={lang_code}, page={page}")
            break
        all_movies += r.json().get("results", [])
        time.sleep(0.25)
    return all_movies

def fetch_all_movies():
    genres_map = get_genre_mapping()
    rows = []
    for code, lang in LANGUAGES.items():
        print(f"Fetching {lang} movies...")
        movies = fetch_by_lang(code, pages=100)  # 100 pages ~2000 movies per language
        for m in movies:
            rows.append({
                "title": m.get("title"),
                "language": lang,
                "genres": ", ".join(genres_map.get(g, "") for g in m.get("genre_ids", [])),
                "release_date": m.get("release_date"),
                "popularity": m.get("popularity"),
                "tmdb_id": m.get("id")
            })
    df = pd.DataFrame(rows).drop_duplicates(subset=["title", "language"])
    df.to_csv("movies.csv", index=False)
    print(f"✅ Saved {len(df)} movies to movies.csv")

if __name__=="__main__":
    fetch_all_movies()
