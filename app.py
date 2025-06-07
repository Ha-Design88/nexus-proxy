from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Nexus Proxy läuft!"

@app.route('/api/proxy', methods=['POST'])
def proxy():
    daten = request.json
    return jsonify({"status": "ok", "eingabe": daten})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
