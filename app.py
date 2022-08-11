import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import flask_monitoringdashboard as dashboard
import datetime
import pandas as pd
import numpy as np
from python_scripts import giants_dashboard, almanac_items, nfl_functions

players = ['BARACK', 'MICHELLE'] # Later, import variable from nfl_functions

allsky_uploads_path = '/Users/paulclanon/Documents/Python_Scripts/PycharmProjects/paulclanon_com/static/img/allsky/daily_uploads/'

def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    dashboard.bind(app)

    return app

app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '2lospalmos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt_obj = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],
                           render_kw={'placeholder': "Password"})
    submit = SubmitField('Login')

class ChangePasswordForm(FlaskForm):

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],
                           render_kw={'placeholder': "New one (8-20 chars)."})
    confirm = PasswordField(render_kw={'placeholder': "Type it again."})
    submit = SubmitField('Register')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # print(f'Coming from {request.referrer}')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt_obj.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('login_dashboard'))

    return render_template('login.html', form=form)


@app.route('/login_dashboard', methods=['GET', 'POST'])
@login_required
def login_dashboard():
    return render_template('login_dashboard.html')


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if form.password.data == form.confirm.data:
            hashed_password = bcrypt_obj.generate_password_hash(form.password.data)
            db.session.query(User).filter(User.username == current_user.username). \
                update({"password": hashed_password}, synchronize_session="fetch")
            db.session.commit()
            return redirect(url_for('login_dashboard'))
        else:
            return redirect(url_for('change_password'))

    return render_template('change_password.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt_obj.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


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

# @app.route('/allsky_uploads', methods=['GET', 'POST'])
# def allsky_uploads():
#
#     if request.method == 'POST':
#         if 'allsky_upload' not in request.files:
#             return redirect(request.url)
#         file = request.files['allsky_upload']
#
#         if file.filename == '':
#             return redirect(request.url)
#
#         if file.filename.lower().endswith(('.jpg', '.mp4')):
#             filename = secure_filename(file.filename)
#             file.save(f'{allsky_uploads_path}{filename}')
#             return redirect(request.url)
#     return '''
#             <h1>Upload</h1>
#             <form method="post" enctpye="multipart/form-data">
#             <input type="file" name="file">
#             <input type="submit" name="Upload">
#         '''

@app.route('/cbcl/mypicks', methods=['GET','POST'])
@login_required
def mypicks():
    df = pd.read_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL.csv')
    df_this_week = df[df['WEEK'] == 1]
    this_week_matchups = nfl_functions.this_week_matchups(df_this_week)

    picks = request.form
    if picks:
        for gameid in picks:
            df.loc[int(gameid), current_user.username.upper()] = picks[gameid]

        df.to_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL.csv', index=False)

        return redirect(url_for('this_weeks_picks'))

    return render_template('cbcl/mypicks.html', this_week_matchups=this_week_matchups)


@app.route('/cbcl/this_weeks_picks', methods=['GET','POST'])
@login_required
def this_weeks_picks():
    df = pd.read_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL.csv')
    this_weeks_picks_df = df[df['WEEK'] == 1]
    this_weeks_picks_df = this_weeks_picks_df.filter(['WEEK', 'ROAD TEAM', 'HOME TEAM'] + players)
    this_weeks_picks_df = this_weeks_picks_df.rename(columns={'ROAD TEAM': 'Road', 'HOME TEAM': 'Home'})
    this_weeks_picks_df['LONE WOLF'] = nfl_functions.make_lone_wolf_column(this_weeks_picks_df, players)
    this_weeks_picks_df_styled = (this_weeks_picks_df.style
                                  .apply(nfl_functions.color_lone_wolfs, subset=players + ['LONE WOLF'], axis=1)

                                  .hide(axis=0)
                                  .set_properties(**{'background-color': 'gainsboro'},
                                                  subset=['Road', 'Home'])
                                  .set_properties(**{'text-align': 'center'})

                                  .set_table_styles([dict(selector='th', props=[('text-align', 'center')])])

                                  .hide_columns('LONE WOLF')
                                  .to_html())

    return render_template('cbcl/this_weeks_picks_table.html', this_weeks_picks=this_weeks_picks_df_styled)


if __name__ == "__main__":
    app.run()


