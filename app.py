from flask import Flask, render_template, request
import os
import pandas as pd
import requests
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

app = Flask(__name__)
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

df = pd.read_csv("movies_with_genres.csv")
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['genres'])
similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

def recommend(movie_title):
    if movie_title not in df['title'].values:
        return []
    index = df[df['title'] == movie_title].index[0]
    scores = list(enumerate(similarity[index]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]
    return [(df.iloc[i]['title'], df.iloc[i]['language']) for i, score in sorted_scores]

def fetch_movie_overview(movie_name):
    try:
        query = movie_name.strip().replace(":", "").replace("&", "and")
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        res = requests.get(search_url).json()
        movie = res.get("results", [{}])[0]
        return movie.get("overview", "No description available.")
    except:
        return "No overview found."

def chat_with_ai(user_input):
    prompt = (
        "You are a smart AI movie assistant. Suggest great movies, explain genres, moods, etc. "
        "Be concise, human-like, and helpful."
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
        return f"AI Error: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = []
    ai_response = ""
    overview = ""
    selected_movie = ""
    
    if request.method == "POST":
        if "movie" in request.form:
            selected_movie = request.form["movie"]
            recommendations = recommend(selected_movie)
            overview = fetch_movie_overview(selected_movie)

        elif "question" in request.form:
            question = request.form["question"]
            ai_response = chat_with_ai(question)

    return render_template("index.html", 
                           movies=df['title'].values, 
                           recommendations=recommendations,
                           overview=overview,
                           selected_movie=selected_movie,
                           ai_response=ai_response)

if __name__ == "__main__":
    app.run(debug=True)
