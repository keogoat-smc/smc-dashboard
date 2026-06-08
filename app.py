from flask import Flask, render_template, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan")
def scan():

    symbols = {
        "GOLD": "GC=F",
        "GBPJPY": "GBPJPY=X",
        "USDJPY": "USDJPY=X"
    }

    results = []

    for name, ticker in symbols.items():

        try:
            data = yf.download(
                ticker,
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if len(data) < 200:
                continue

            close = float(data["Close"].iloc[-1])

            sma200 = float(
                data["Close"]
                .rolling(200)
                .mean()
                .iloc[-1]
            )

            signal = "LONG" if close > sma200 else "SHORT"

            risk_distance = close * 0.018

            score = 75

            results.append({
                "symbol": name,
                "price": round(close, 2),
                "type": signal,
                "sl": round(close - risk_distance, 2),
                "tp": round(close + (risk_distance * 2), 2),
                "risk": 3.00,
                "score": score
            })

        except Exception as e:
            print(f"{name}: {e}")

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)