from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan")
def scan():
    return jsonify([
        {
            "symbol": "GOLD",
            "price": 2350,
            "type": "LONG",
            "sl": 2330,
            "tp": 2390,
            "risk": 5.0,
            "score": 75
        }
    ])

if __name__ == "__main__":
    app.run(debug=True)