from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "9e58b2a68c7cd43417ed26e90a8f9cbe" # <-- Trage hier deinen API-Key von api-football ein

@app.route('/')
def home():
    return "Nexus Proxy läuft!"

@app.route('/api/spiele', methods=['GET'])
def spiele():
    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "league": "78",      # z.B. Bundesliga = 78, Premier League = 39, usw.
        "season": "2023",    # Saison anpassen (z.B. 2023)
        # "date": "2024-06-07" # Optional: Konkretes Datum (Format: JJJJ-MM-TT)
    }
    headers = {
        "x-apisports-key": API_KEY
    }
    response = requests.get(url, headers=headers, params=params)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
