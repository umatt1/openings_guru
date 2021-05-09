
# flask
from flask import Flask, render_template, Blueprint
from chess import openings_guru
from twitter import synthetic_parrot
from covid_simulator import covid_simulator
from motif_finder import motifer

app = Flask(__name__)
app.register_blueprint(openings_guru, url_prefix="/chess")
app.register_blueprint(synthetic_parrot)
app.register_blueprint(covid_simulator)
app.register_blueprint(motifer, url_prefix="/motif_finder")

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
