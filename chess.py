from chessdotcom import get_player_games_by_month, Client
import datetime
from flask import Flask, redirect, url_for, render_template, request, Blueprint

# stuff for chess

Client.config['headers']['User-Agent'] = (
    "This app is to help players find openings they are weakest in"
    "Contact me at umatt@umich.edu"
)

# code taken from https://stackoverflow.com/questions/10029588/python-implementation-of-the-wilson-score-interval
#Rewritten code from /r2/r2/lib/db/_sorts.pyx
from math import sqrt

def confidence(ups, downs):
    n = ups + downs
    if n == 0:
        return 0
    z = 1.00  #1.44 = 85%, 1.96 = 95%
    phat = float(ups) / n
    return (phat + z*z/(2*n) - z * sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)


def sorterChooser(sort):
    if sort == 'best':
        return reversed_sorter
    else:
        return sorter


def sorter(item):
    wins = item[1][0]
    losses = item[1][1]
    return confidence(losses, wins)


def reversed_sorter(item):
    wins = item[1][0]
    losses = item[1][1]
    return confidence(wins, losses)


def readPGN(pgn):
    pgn = pgn.split("\n")
    for line in pgn:
        if line[0:7] == '[ECOUrl':
            return line[9:-2]
    return "no ECOUrl"

openings_guru = Blueprint('openings_guru', __name__, template_folder='templates')
@openings_guru.route("/", methods=['POST', 'GET'])
def chess_home():
    if request.method == "POST":
        id = request.form["id"]
        color = request.form["color"]
        months = request.form['months']
        sort = request.form['sort']
        return redirect(url_for("openings_guru.chess", id=id, color=color, months=months, sort=sort))
    else:
        return render_template("chess.html")

@openings_guru.route("/<id>/<color>/<months>/<sort>/")
def chess(id, color, months, sort):
    months = int(months)
    if months > 12:
        months = 12
    if color == 'w' or color == 'W':
        color = "white"
    else:
        color = "black"
    if sort == 'b' or sort == 'B':
        sort = 'best'
    else:
        sort = 'worst'
    # get games, process
    current_month = int(datetime.datetime.now().strftime("%m"))
    current_year = 2000 + int(datetime.datetime.now().strftime("%y"))
    openings = {}

    for i in range(int(months)):
        print(current_month, current_year)
        response = get_player_games_by_month(id, current_year, current_month)
        for game in response.json['games']:
            if game[color]['username'] != id:
                continue
            if 'pgn' not in game:
                continue
            URL = readPGN(game['pgn'])
            if URL not in openings:
                openings[URL] = [0,0]
            if game[color]['result'] != 'win':
                openings[URL][1] += 1
            else:
                openings[URL][0] += 1
        if current_month == 1:
            current_month = 12
            current_year -= 1
        else:
            current_month -= 1
    # reshape data
    sorted_openings = reversed(sorted(openings.items(), key=sorterChooser(sort)))
    webpage = ""
    for opening, value in sorted_openings:
        if opening == 'no ECOUrl':
            continue
        webpage += f'<a href="{opening}">{opening[31:]}</a>'
        webpage += f'<p>{value[0]} W - {value[1]} L</p>'
    return webpage

