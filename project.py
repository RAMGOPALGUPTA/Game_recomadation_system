from flask import Flask, render_template_string, request
import requests
import pygame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# Initialize pygame mixer for background music
pygame.mixer.init()

def play_background_music():
    # Load and play background music
    try:
        pygame.mixer.music.load('background_music.mp3')  # Ensure this file is in the same folder
        pygame.mixer.music.play(loops=-1, start=0.0)
    except Exception as e:
        print(f"Error loading music: {e}")

# Start the music when the app runs
play_background_music()

# Fetch games from GamerPower API
def fetch_games():
    url = "https://www.gamerpower.com/api/giveaways"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching games: {e}")
        return []

games = fetch_games()
titles = [game["title"] for game in games]
descriptions = [game["description"] for game in games]
images = [game["image"] for game in games]
urls = [game["open_giveaway_url"] for game in games]

# Machine Learning setup
vectorizer = TfidfVectorizer(stop_words="english")
vectors = vectorizer.fit_transform(descriptions)
knn = NearestNeighbors(n_neighbors=10, metric="cosine")
knn.fit(vectors)

# Add popular games like GTA, COD, and PUBG for recommendations
popular_games = ["Grand Theft Auto", "Call of Duty", "PUBG", "Apex Legends", "Fortnite", "Battlefield"]

# --- Sexy Dark Theme Template ---
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>🔥 Ultra Dark Game Recommender 🔥</title>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Orbitron', sans-serif;
      background: radial-gradient(circle, rgba(0,0,0,0.7), rgba(0,0,0,1));
      color: #fff;
      overflow-x: hidden;
      padding: 40px;
      position: relative;
      cursor: url('https://cdn.iconscout.com/icon/premium/png-256-thumb/magic-cursor-1438587.png'), auto;
    }
    body::before {
      content: '';
      position: fixed;
      top: 0; left: 0;
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at center, rgba(0,255,255,0.1), transparent),
                  linear-gradient(120deg, #00f2ff33, transparent, #0072ff33);
      z-index: -1;
      animation: animateBG 20s linear infinite;
    }
    @keyframes animateBG {
      0% { transform: translateX(0px); }
      100% { transform: translateX(-1000px); }
    }
    h1, h2 {
      text-align: center;
      margin: 40px 0 20px;
      text-shadow: 0 0 15px #00ffff, 0 0 25px #00ffff;
    }
    .form-box {
      background: rgba(255, 255, 255, 0.1);
      padding: 30px;
      border-radius: 25px;
      max-width: 800px;
      margin: auto;
      box-shadow: 0 0 25px #00ffff;
      margin-bottom: 50px;
      transition: 0.4s;
    }
    .form-box:hover {
      box-shadow: 0 0 50px #00ffff;
    }
    input[type="text"], button {
      width: 100%;
      padding: 14px;
      font-size: 18px;
      border-radius: 10px;
      border: none;
      margin-top: 20px;
      background: #111;
      color: #fff;
    }
    button {
      background: linear-gradient(90deg, #00ffff, #0072ff);
      color: black;
      font-weight: bold;
      margin-top: 25px;
      cursor: pointer;
      box-shadow: 0 0 20px #00ffffaa;
      transition: 0.3s ease;
      border-radius: 15px;
    }
    button:hover {
      transform: scale(1.05);
      background: linear-gradient(90deg, #0072ff, #00ffff);
    }
    .game-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 30px;
      padding: 40px;
    }
    .card {
      background: rgba(255,255,255,0.1);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 0 25px #00ffff;
      transition: 0.3s ease;
      cursor: pointer;
      text-decoration: none;
    }
    .card:hover {
      transform: scale(1.05);
      box-shadow: 0 0 35px #00ffff;
    }
    .card img {
      width: 100%;
      height: 220px;
      object-fit: cover;
      transition: 0.3s ease;
    }
    .card img:hover {
      transform: scale(1.1);
    }
    .card-body {
      padding: 20px;
      text-align: center;
    }
    .card-body h3 {
      margin-bottom: 15px;
      color: #00ffff;
      text-transform: uppercase;
      letter-spacing: 2px;
      font-size: 1.2rem;
      text-shadow: 0 0 15px #00ffff;
    }
    .card-body p {
      font-size: 14px;
      color: #ccc;
      min-height: 60px;
    }
    .form-box label {
      font-size: 18px;
      color: #00ffff;
      margin-bottom: 10px;
    }
    @media(max-width: 600px) {
      .form-box, .card-body { padding: 15px; }
      .game-grid { padding: 20px; }
    }
  </style>
</head>
<body>

  <h1>🔥 Ultra Dark Game Recommender 🔥</h1>

  <div class="form-box">
    <form method="POST">
      <label for="game">Enter a Game Name:</label>
      <input type="text" id="game" name="game" list="gameList" value="{{ selected_game or '' }}">
      <datalist id="gameList">
        {% for title in titles %}
          <option value="{{ title }}">
        {% endfor %}
        {% for p_game in popular_games %}
          <option value="{{ p_game }}">
        {% endfor %}
      </datalist>
      <button type="submit">Find Recommendations</button>
    </form>
  </div>

  {% if recommendations %}
    <h2>Recommended For You</h2>
    <div class="game-grid">
      {% for rec in recommendations %}
      <a href="{{ rec.url }}" target="_blank" class="card">
        <img src="{{ rec.image }}" alt="{{ rec.title }}">
        <div class="card-body">
          <h3>{{ rec.title }}</h3>
          <p>{{ rec.description[:120] }}...</p>
        </div>
      </a>
      {% endfor %}
    </div>
  {% endif %}

</body>
</html>
"""

# Flask route
@app.route("/", methods=["GET", "POST"])
def home():
    selected_game = None
    recommendations = []

    if request.method == "POST":
        selected_game = request.form.get("game")
        all_titles = titles + popular_games
        if selected_game in all_titles:
            selected_game = selected_game if selected_game in titles else popular_games[popular_games.index(selected_game)]
            index = titles.index(selected_game) if selected_game in titles else popular_games.index(selected_game)
            selected_vector = vectors[index] if selected_game in titles else None  # Use vector only for fetched games
            if selected_vector is not None:
                distances, indices = knn.kneighbors(selected_vector)
                indices = [i for i in indices.flatten() if i != index][:8]
                recommendations = [
                    {
                        "title": titles[i],
                        "description": descriptions[i],
                        "image": images[i],
                        "url": urls[i]
                    }
                    for i in indices
                ]
            else:
                recommendations = [{"title": selected_game, "description": "Popular Game", "image": "", "url": ""}]

    return render_template_string(html_template, titles=titles, recommendations=recommendations, selected_game=selected_game, popular_games=popular_games)

if __name__ == "__main__":
    app.run(debug=True)
