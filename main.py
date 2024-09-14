
# flask
from flask import Flask, render_template, Blueprint
from chess import openings_guru

app = Flask(__name__)
app.register_blueprint(openings_guru, url_prefix="/chess")

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
