from flask import Flask, render_template, request, redirect
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import flask_wtf
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import datetime
import pandas as pd
from python_scripts import giants_dashboard, almanac_items, nfl_functions


allsky_uploads_path = '/Users/paulclanon/Documents/Python_Scripts/PycharmProjects/paulclanon_com/static/img/allsky/daily_uploads/'

def create_app():
    app = Flask(__name__)
    Bootstrap(app)

    return app

app = create_app()
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '2lospalmos'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/baseball')
def baseball():
    return render_template('baseball/baseball.html')


@app.route('/baseball/nl_rankings')
def nl_rankings():
    teams_rank_styled = giants_dashboard.make_nl_teams_rankings()
    now = datetime.datetime.now()
    now_str = datetime.datetime.strftime(now, ('%a %b %-d %Y %-I:%M %p '))

    return render_template('baseball/nl_rankings.html', teams_rank_styled = teams_rank_styled, now = now_str)


@app.route('/baseball/giants_linescore')
def giants_linescore():
    line_score_styled = giants_dashboard.make_linescore_last_giants_game()
    giants_last_game = giants_dashboard.make_day_of_last_giants_game()
    return render_template('baseball/giants_linescore.html', line_score=line_score_styled,
                           last_game_str=giants_last_game)


@app.route('/baseball/giants_next_game')
def giants_next_game_run_script():
    next_game = giants_dashboard.make_giants_next_game()

    return render_template('baseball/giants_next_game.html', next_game_str=next_game)

@app.route('/baseball/current_standings')
def current_standings_run_script():
    current_standings = giants_dashboard.make_standings_table()
    now = datetime.datetime.now()
    now_str = datetime.datetime.strftime(now, ('%a %b %-d %Y %-I:%M %p '))

    return render_template('baseball/current_standings.html', current_standings_str=current_standings,
                           now=now_str)

@app.route('/almanac')
def almanac():
    return render_template('almanac/almanac.html')

@app.route('/almanac/moon_illumination')
def moon_illumination():
    almanac_items.moon_illumination_chart()
    return render_template('/almanac/moon_illumination.html')

@app.route('/music')
def music():
    return render_template('music/music.html')

@app.route('/allsky')
def allsky():
    return render_template('allsky/allsky.html')

@app.route('/allsky_uploads', methods=['GET', 'POST'])
def allsky_uploads():

    if request.method == 'POST':
        if 'allsky_upload' not in request.files:
            return redirect(request.url)
        file = request.files['allsky_upload']

        if file.filename == '':
            return redirect(request.url)

        if file.filename.lower().endswith(('.jpg', '.mp4')):
            filename = secure_filename(file.filename)
            file.save(f'{allsky_uploads_path}{filename}')
            return redirect(request.url)
    return '''
            <h1>Upload</h1>
            <form method="post" enctpye="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" name="Upload">
        '''
@app.route('/cbcl/mypicks', methods=['GET','POST'])
def mypicks():
    df = pd.read_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL.csv')
    df = df[df['WEEK'] == 17]
    this_week_matchups = nfl_functions.this_week_matchups(df)
    print(request.form)
    print(request.form.get('player'))
    return render_template('cbcl/mypicks.html', this_week_matchups=this_week_matchups)

if __name__ == "__main__":
    app.run()


