from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Sleeper API Bridge is running!"

@app.route("/league/<league_id>")
def get_league(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}"
    return jsonify(requests.get(url).json())
