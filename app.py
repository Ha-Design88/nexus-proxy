from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Nexus Proxy läuft!"

@app.route('/api/proxy', methods=['POST'])
def proxy():
    daten = request.json
    # Beispiel: Daten an externe API weiterleiten und Antwort zurückgeben
    # Hier ein Dummy für Testzwecke:
    return jsonify({"status": "ok", "eingabe": daten})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
