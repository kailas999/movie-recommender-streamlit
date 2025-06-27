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

