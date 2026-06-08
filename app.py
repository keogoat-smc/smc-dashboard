from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
import math

app = Flask(__name__)

def clean(val):
    """Convert NaN/Inf to None so jsonify never breaks."""
    if val is None:
        return None
    try:
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    except (TypeError, ValueError):
        return val

def clean_list(lst):
    return [clean(v) for v in lst]

SYMBOLS = {
    "GOLD":   "GC=F",
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

            # --- prices ---
            close  = data["Close"].squeeze()
            high   = data["High"].squeeze()
            low    = data["Low"].squeeze()
            open_  = data["Open"].squeeze()
            dates  = data.index.strftime("%Y-%m-%d").tolist()

            price  = float(close.iloc[-1])
            sma20  = float(close.rolling(20).mean().iloc[-1])
            sma50  = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else sma20

            # --- signal ---
            signal = "LONG" if price > sma20 else "SHORT"

            # --- SL / TP based on recent swing ---
            recent_high = float(high.iloc[-10:].max())
            recent_low  = float(low.iloc[-10:].min())
            atr_approx  = float((high - low).rolling(14).mean().iloc[-1])

            if signal == "LONG":
                sl = round(price - atr_approx * 1.5, 3)
                tp = round(price + atr_approx * 3.0, 3)
            else:
                sl = round(price + atr_approx * 1.5, 3)
                tp = round(price - atr_approx * 3.0, 3)

            # --- score: distance from SMA as % ---
            score = round(abs(price - sma20) / sma20 * 100, 2)

            # --- momentum: last 5 closes direction ---
            last5 = close.iloc[-5:].tolist()
            momentum = round(
                (last5[-1] - last5[0]) / last5[0] * 100, 2
            )

            # --- candle data (last 60 bars) ---
            n = min(60, len(data))
            candles = {
                "dates":  dates[-n:],
                "open":   clean_list([round(float(x), 3) for x in open_.iloc[-n:]]),
                "high":   clean_list([round(float(x), 3) for x in high.iloc[-n:]]),
                "low":    clean_list([round(float(x), 3) for x in low.iloc[-n:]]),
                "close":  clean_list([round(float(x), 3) for x in close.iloc[-n:]]),
                "sma20":  clean_list([round(float(x), 3) for x in
                           close.rolling(20).mean().iloc[-n:]]),
                "sma50":  clean_list([round(float(x), 3) for x in
                           close.rolling(50).mean().iloc[-n:]]),
            }

            results.append({
                "symbol":   name,
                "price":    clean(round(price, 3)),
                "sma20":    clean(round(sma20, 3)),
                "sma50":    clean(round(sma50, 3)),
                "type":     signal,
                "sl":       clean(sl),
                "tp":       clean(tp),
                "atr":      clean(round(atr_approx, 3)),
                "score":    clean(score),
                "momentum": clean(momentum),
                "candles":  candles,
            })

        except Exception as e:
            print(f"Error {name}: {e}")

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)