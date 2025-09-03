from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enables access from Streamlit, GPT tools, etc.

SLEEPER_BASE_URL = "https://api.sleeper.app/v1"

# --- Utility function to wrap requests ---
def fetch_sleeper_data(endpoint):
    try:
        response = requests.get(f"{SLEEPER_BASE_URL}/{endpoint}")
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": "Sleeper API request failed", "details": str(e)}), 502

# --- Basic test route ---
@app.route("/")
def home():
    return "✅ Sleeper API Bridge is running!"

# --- Standard Sleeper endpoints ---
@app.route("/league/<league_id>")
def get_league(league_id):
    return fetch_sleeper_data(f"league/{league_id}")

@app.route("/roster/<league_id>")
def get_rosters(league_id):
    return fetch_sleeper_data(f"league/{league_id}/rosters")

@app.route("/matchups/<league_id>/<week>")
def get_matchups(league_id, week):
    return fetch_sleeper_data(f"league/{league_id}/matchups/{week}")

@app.route("/league_users/<league_id>")
def get_league_users(league_id):
    return fetch_sleeper_data(f"league/{league_id}/users")

@app.route("/user/<username>")
def get_user(username):
    return fetch_sleeper_data(f"user/{username}")

# --- Player name mapping ---
@app.route("/player_names")
def get_player_names():
    try:
        players = requests.get(f"{SLEEPER_BASE_URL}/players/nfl").json()
        name_map = {
            pid: data["full_name"]
            for pid, data in players.items()
            if "full_name" in data
        }
        return jsonify(name_map)
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch player names", "details": str(e)}), 502

# --- Simplified roster breakdown with names ---
@app.route("/simplified_rosters/<league_id>")
def get_simplified_rosters(league_id):
    try:
        rosters = requests.get(f"{SLEEPER_BASE_URL}/league/{league_id}/rosters").json()
        users = requests.get(f"{SLEEPER_BASE_URL}/league/{league_id}/users").json()
        user_map = {u["user_id"]: u.get("display_name", "Unknown") for u in users}

        simplified = []
        for r in rosters:
            simplified.append({
                "team_name": user_map.get(r["owner_id"], "Unknown"),
                "starters": r.get("starters", []),
                "bench": [p for p in r.get("players", []) if p not in r.get("starters", [])],
                "roster_id": r.get("roster_id")
            })

        return jsonify(simplified)

    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch rosters or users", "details": str(e)}), 502
