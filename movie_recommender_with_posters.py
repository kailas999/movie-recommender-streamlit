import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def fetch_movies(pages=50):  # 20 movies per page × 50 pages = 1000 movies
    all_movies = []

    for page in range(1, pages + 1):
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get('results', [])
            for movie in results:
                all_movies.append({
                    "title": movie.get("title"),
                    "genres": ", ".join([str(g) for g in movie.get("genre_ids", [])]),
                    "id": movie.get("id")
                })
        else:
            print(f"Error on page {page}: {response.status_code}")
        time.sleep(0.3)  # Avoid hitting rate limits

    df = pd.DataFrame(all_movies)
    df.drop_duplicates(subset='title', inplace=True)
    df.to_csv("movies.csv", index=False)
    print(f"✅ Fetched {len(df)} movies and saved to 'movies.csv'")

if __name__ == "__main__":
    fetch_movies()
