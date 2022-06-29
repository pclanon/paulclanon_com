from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import datetime
from python_scripts import giants_dashboard, almanac_items


def create_app():
    app = Flask(__name__)
    Bootstrap(app)

    return app


# app = Flask(__name__)
app = create_app()

@app.route('/')
def index():
    return render_template('index.html')


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

@app.route('/almanac')
def almanac():
    return render_template('almanac/almanac.html')

@app.route('/almanac/moon_illumination')
def moon_illumination():
    almanac_items.moon_illumination_chart()
    return render_template('/almanac/moon_illumination.html')


if __name__ == "__main__":
    app.run()


