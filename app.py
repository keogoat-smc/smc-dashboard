from flask import Flask, render_template, jsonify
import yfinance as yf

app = Flask(__name__)

symbols = {
    "GOLD": "GC=F",
    "GBPJPY": "GBPJPY=X",
    "USDJPY": "USDJPY=X"
}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan")
def scan():

    results = []

    for name, ticker in symbols.items():

        try:
            data = yf.download(
                ticker,
                period="6mo",
                interval="1d",
                progress=False
            )

            if len(data) < 50:
                continue

            close = float(data["Close"].iloc[-1])

            sma = float(data["Close"].rolling(50).mean().iloc[-1])

            signal = "LONG" if close > sma else "SHORT"

            risk = close * 0.015

            results.append({
                "symbol": name,
                "price": round(close, 2),
                "type": signal,
                "sl": round(close - risk, 2),
                "tp": round(close + (risk * 2), 2),
                "risk": round(risk, 2),
                "score": round(abs(close - sma) / sma * 100, 2)
            })

        except Exception as e:
            print(f"{name} error:", e)

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)