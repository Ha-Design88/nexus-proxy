from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta
import time

app = Flask(__name__)

API_KEY = "9e58b2a68c7cd43417ed26e90a8f9cbe"

LIGA_IDS = [
   LIGA_IDS = [
    59, 62,    # Norwegen
    29, 30,    # Schweden
    142,       # Australien
    292, 293   # Südkorea 
]

CACHE = {}  # In-Memory-Cache

def api_get(url, params=None):
    headers = {"x-apisports-key": API_KEY}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=8)
        if r.status_code == 200:
            return r.json()
        return {}
    except:
        return {}

def get_team_stats(team_id, league_id, season):
    url = f"https://v3.football.api-sports.io/teams/statistics"
    params = {"team": team_id, "league": league_id, "season": season}
    return api_get(url, params)

def get_table(league_id, season):
    url = f"https://v3.football.api-sports.io/standings"
    params = {"league": league_id, "season": season}
    data = api_get(url, params)
    try:
        return data["response"][0]["league"]["standings"][0]
    except:
        return []

def get_h2h(team1_id, team2_id):
    url = f"https://v3.football.api-sports.io/fixtures/headtohead"
    params = {"h2h": f"{team1_id}-{team2_id}", "last": 3}
    data = api_get(url, params)
    return [m for m in data.get("response", [])]

def get_odds(fixture_id):
    url = f"https://v3.football.api-sports.io/odds"
    params = {"fixture": fixture_id}
    data = api_get(url, params)
    # Vereinfacht: Alle Quoten als Liste rausgeben (Detailanpassung möglich)
    if data.get("response"): return data["response"]
    return []

def enrich_game(game, league_id, season):
    # Tabellenstand holen
    standings = get_table(league_id, season)
    home_id, away_id = game["teams"]["home"]["id"], game["teams"]["away"]["id"]
    home_tab, away_tab = None, None
    for t in standings:
        if t["team"]["id"] == home_id:
            home_tab = t
        elif t["team"]["id"] == away_id:
            away_tab = t

    # Team-Statistiken holen
    stat_home = get_team_stats(home_id, league_id, season)
    stat_away = get_team_stats(away_id, league_id, season)

    # H2H holen
    h2h = get_h2h(home_id, away_id)

    # Quoten holen
    odds = get_odds(game["fixture"]["id"])

    # Kompaktes Objekt bauen:
    return {
        "datum": game["fixture"]["date"],
        "liga": game["league"]["name"],
        "runde": game["league"].get("round", ""),
        "heim": game["teams"]["home"]["name"],
        "heim_id": home_id,
        "auswaerts": game["teams"]["away"]["name"],
        "auswaerts_id": away_id,
        "tore_heim": game["goals"]["home"],
        "tore_auswaerts": game["goals"]["away"],
        "spiel_id": game["fixture"]["id"],
        "venue": game["fixture"]["venue"].get("name", ""),
        "status": game["fixture"]["status"]["short"],
        "tabellenstand_heim": home_tab,
        "tabellenstand_auswaerts": away_tab,
        "stat_home": stat_home.get("response", {}),
        "stat_away": stat_away.get("response", {}),
        "h2h": h2h,
        "odds": odds,
        # Noch mehr Felder möglich (Verletzungen, Aufstellungen usw.)
    }

def get_all_games():
    spiele = []
    today = datetime.now()
    for offset in range(2):  # heute & morgen
        d = today + timedelta(days=offset)
        date_str = d.strftime('%Y-%m-%d')
        for liga_id in LIGA_IDS:
            url = f"https://v3.football.api-sports.io/fixtures"
            params = {"league": liga_id, "date": date_str}
            data = api_get(url, params)
            if data.get("response"):
                for item in data["response"]:
                    season = item["league"]["season"]
                    try:
                        enriched = enrich_game(item, liga_id, season)
                        spiele.append(enriched)
                        time.sleep(0.7)  # Schont API-Limit!
                    except Exception as e:
                        spiele.append({"error": str(e), "heim": item["teams"]["home"]["name"], "auswaerts": item["teams"]["away"]["name"]})
    # Sortieren nach Datum
    spiele.sort(key=lambda x: x.get("datum", ""))
    return spiele

@app.route('/')
def home():
    return "Nexus Omega ULTRA-API läuft!"

@app.route('/api/spiele')
def api_spiele():
    # CACHE: Nur alle 3h neu holen!
    now = int(time.time() // 10800)
    if CACHE.get("timestamp") != now:
        CACHE["spiele"] = get_all_games()
        CACHE["timestamp"] = now
    return jsonify({"spiele": CACHE["spiele"]})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
