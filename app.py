from flask import Flask, render_template, jsonify
import yfinance as yf

app = Flask(__name__)

SYMBOLS = {
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

    for name, ticker in SYMBOLS.items():

        try:
            data = yf.download(ticker, period="3mo", interval="1d", progress=False)

            if data.empty or len(data) < 20:
                continue

            price = float(data["Close"].iloc[-1])

            sma = float(data["Close"].rolling(20).mean().iloc[-1])

            signal = "LONG" if price > sma else "SHORT"

            risk = round(price * 0.01, 2)

            results.append({
                "symbol": name,
                "price": round(price, 2),
                "type": signal,
                "sl": round(price - risk, 2),
                "tp": round(price + (risk * 2), 2),
                "risk": risk,
                "score": round(abs(price - sma), 2)
            })

        except Exception as e:
            print(f"Error {name}: {e}")

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)