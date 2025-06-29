import pandas as pd
import requests
import time

TMDB_API_KEY = "your_tmdb_api_key_here"  # Replace this with your actual TMDB API key

def fetch_language(title):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
        res = requests.get(url).json()
        return res['results'][0].get('original_language', 'unknown')
    except:
        return 'unknown'

df = pd.read_csv("movies_with_genres.csv")
df['language'] = df['title'].apply(fetch_language)

# Optional: Map language codes to full names
lang_map = {'en': 'english', 'hi': 'hindi', 'mr': 'marathi', 'te': 'telugu', 'ta': 'tamil'}
df['language'] = df['language'].map(lang_map).fillna('unknown')

df.to_csv("movies_with_genres.csv", index=False)
print("✅ language column added using TMDB API.")
