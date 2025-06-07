from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "9e58b2a68c7cd43417ed26e90a8f9cbe"

@app.route("/")
def home():
    return "Nexus Proxy läuft!"

@app.route("/api/spiele", methods=["GET"])
def spiele():
    league = request.args.get("league", "78")      # Standard: Bundesliga (ID 78)
    season = request.args.get("season", "2023")    # Standard: Saison 2023

    url = f"https://v3.football.api-sports.io/fixtures?league={league}&season={season}"

    headers = {
        "x-apisports-key": API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Optional: Nur die wichtigsten Infos ausgeben (z.B. Teams, Ergebnis, Datum)
        spiele_liste = []
        for eintrag in data.get("response", []):
            fixture = eintrag.get("fixture", {})
            league_data = eintrag.get("league", {})
            teams = eintrag.get("teams", {})
            goals = eintrag.get("goals", {})

            spiel = {
                "datum": fixture.get("date"),
                "liga": league_data.get("name"),
                "runde": league_data.get("round"),
                "heim": teams.get("home", {}).get("name"),
                "auswärts": teams.get("away", {}).get("name"),
                "tore_heim": goals.get("home"),
                "tore_auswärts": goals.get("away")
            }
            spiele_liste.append(spiel)

        return jsonify({"spiele": spiele_liste})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
