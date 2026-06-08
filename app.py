from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan")
def scan():
    return jsonify({"status": "SMC dashboard working 🚀"})

if __name__ == "__main__":
    app.run(debug=True)