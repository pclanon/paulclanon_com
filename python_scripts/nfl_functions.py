import random
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator, FixedLocator, FixedFormatter
from python_scripts.nfl_lists_and_dicts import players, color_dict, marker_dict, week_ticks


players = ['BARACK', 'MICHELLE', 'SASHA']
# players = ['PAUL', 'SAM', 'DAVE', 'JEFF', 'DAN', 'SKELLY'] # Later, import variable from nfl_functions
week_to_run = 1

df = pd.read_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL.csv')
df = df[df['WEEK'] == week_to_run]




def this_week_matchups(df):
    this_week_matchups = tuple(zip(df.index.tolist(), df['ROAD TEAM'], df['HOME TEAM']))

    return this_week_matchups


def identify_lone_wolf_pick(row):
    """After at least two people have made picks, look for lone wolf"""
    picks = row.tolist()
    picks_not_nans = [p for p in picks if isinstance(p, str)]
    lw = False

    if len(picks_not_nans) > 2:
        for p in picks:
            if picks.count(p) == 1:
                lw = p
    return lw


def make_lone_wolf_column(df, players):
    lone_wolf_series = df[players].apply(lambda row: identify_lone_wolf_pick(row), axis=1)

    return lone_wolf_series


def color_lone_wolfs(row):
    highlight = 'background-color: green;'
    default = ''
# Have to brute-force each player into this function.
    if row['BARACK'] == row['LONE WOLF']:
        return [highlight, default, default, default]
    elif row['MICHELLE'] == row['LONE WOLF']:
        return [default, highlight, default, default]
    elif row['SASHA'] == row['LONE WOLF']:
        return [default, default, highlight, default]
    else:
        return [default, default, default, default]


def make_df_of_this_weeks_scores():
    """Make a dataframe to use as a lookup table for scores this week,
            indexed by team name. Example: test_df = make_df_of_this_weeks_scores()
            test_df['SCORE'].loc['Broncos']"""

    url = 'https://www.pro-football-reference.com/years/2022/week_1.htm'
    dfs = pd.read_html(url) # Returns a list of dataframes

    team_scores_this_week_df = pd.DataFrame()

    for df in dfs:
        df = df[1:]
        team_scores_this_week_df = pd.concat([df, team_scores_this_week_df], axis=0, ignore_index=True)

    # Give columns descriptive names, drop unneeded columns, drop cities from team names, index by TEAM
    team_scores_this_week_df = (team_scores_this_week_df.rename(columns={0: 'TEAM', 1: 'SCORE'})
                                .filter(['TEAM', 'SCORE']))
    team_scores_this_week_df['TEAM'] = team_scores_this_week_df['TEAM'].apply(lambda t: t.split()[-1])
    team_scores_this_week_df = team_scores_this_week_df.set_index('TEAM')

    return team_scores_this_week_df


def make_dataframe_of_colors(all_games_df, week_to_run, players):
    """For use in styling. Make dataframe in same shape as main dataframe, with each cell
    showing wanted color value. Feed as argument to .set_td_classes"""
    df = all_games_df
    R = df[df['WEEK'] == week_to_run].filter(items=['WEEK', 'ROAD TEAM',
                        'ROAD SCORE', 'HOME SCORE', 'HOME TEAM'] + players)

    R_copy_for_colors = pd.DataFrame(index=R.index, columns=R.columns)

    for player in players:
        conditions = [((R[player] == R['ROAD TEAM']) & (R['ROAD SCORE'] > R['HOME SCORE'])) | (
                    (R[player] == R['HOME TEAM']) & (R['ROAD SCORE'] < R['HOME SCORE'])),
                      ((R[player] == R['ROAD TEAM']) & (R['ROAD SCORE'] < R['HOME SCORE'])) | (
                                  (R[player] == R['HOME TEAM']) & (R['ROAD SCORE'] > R['HOME SCORE'])),
                      ((R[player] == R['ROAD TEAM']) & (R['ROAD SCORE'] == R['HOME SCORE'])) | (
                                  (R[player] == R['HOME TEAM']) & (R['ROAD SCORE'] == R['HOME SCORE']))]

        values = ['white', 'red', 'lightgray']

        R_copy_for_colors[player] = np.select(conditions, values)

    conditions = [(R['ROAD SCORE'] > R['HOME SCORE']), (R['ROAD SCORE'] < R['HOME SCORE']),
                  (R['ROAD SCORE'] == R['HOME SCORE'])]
    values = ['yellow', 'white', 'lightgray']
    R_copy_for_colors['ROAD TEAM'] = np.select(conditions, values)
    values = ['white', 'yellow', 'lightgray']
    R_copy_for_colors['HOME TEAM'] = np.select(conditions, values)
    R_copy_for_colors = R_copy_for_colors.fillna('white')

    return R_copy_for_colors


def plot_leader_board(leader_board_df):
    """Plot Leader Board, save to disc"""
    df_ = leader_board_df

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_ylim(min(df_.min())-1, 1)
    ax.yaxis.set_major_locator(MultipleLocator(2))
    plt.xticks(list(range(1, len(df_) + 1)), week_ticks[0:len(df_)], fontsize=8)

    for player in players:
        df_.reset_index().plot(kind='line', x='WEEK', y=f'{player} GAMES BACK', marker=marker_dict[player],
                                   linewidth=4, color=color_dict[player], label=player.capitalize(), ax=ax)

    plt.title('Games Behind Leader', fontsize=20)

    fig.savefig(f'/Users/paulclanon/Downloads/leaderboard_week{week_to_run}.png', dpi=300)
    plt.show()
    plt.close()


def random_scores(all_games_dataframe):
    """Generate random scores for testing, all games in df"""
    df = all_games_dataframe
    score = []
    for i in range(0, len(df.index)):
        x = random.randint(0, 50)
        score.append(x)
    df['ROAD SCORE'] = score

    score = []
    for i in range(0, len(df.index)):
        x = random.randint(0, 50)
        score.append(x)
    df['HOME SCORE'] = score

    return df


def random_picker_for_tests(all_games_dataframe, players):
    """Generate random picks for testing, all players and all games in df"""
    df = all_games_dataframe

    def picker(row):
        if random.randint(0, 100) < 50:
            return row['ROAD TEAM']
        else:
            return row['HOME TEAM']

    for player in players:
        df[player] = df.apply(lambda row: picker(row), axis=1)

    return df


def this_weeks_picks_table(df, players):
    """Produce the table showing players' picks for the week, and lone-wolf picks"""
    this_weeks_picks_df = pd.read_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL.csv')
    # this_weeks_picks_df = sheep_scores(this_weeks_picks_df, players)

    this_weeks_picks_df_styled = (this_weeks_picks_df.style
                         # .applymap(lambda v: 'background-color: yellow' if v == 'Giants' else '')
                         .hide(axis=0)
                         # .set_properties(**{'background-color': 'green'}, subset=players)
                         # .highlight_max(color='palegreen', axis=0, subset='R')
                         .set_properties(**{'text-align': 'center'})
                         # .set_properties(**{'text-align': 'left'}, subset='Final')
                         .set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
                         )

    # Convert styled line score df to html
    this_weeks_picks_df_styled = this_weeks_picks_df_styled.to_html()

    return this_weeks_picks_df_styled


def sheep_scores(all_games_dataframe, players):
    df = all_games_dataframe

    def sheepy(row, player):
        return row.tolist().count(row[player]) - 1  # The -1 corrects for your own pick

    for player in players:
        df[player + ' SHEEP SCORE'] = df[players].apply(lambda row: sheepy(row, player), axis=1)

    return df


def winner_and_winning_margin(all_games_dataframe):
    """Add 'WINNER' column to display winning team or 'TIE'. Add 'WINNING MARGIN' column."""
    df = all_games_dataframe
    conditions = [(df['ROAD SCORE'] > df['HOME SCORE']),
                  (df['ROAD SCORE'] < df['HOME SCORE']),
                  (df['ROAD SCORE'] == df['HOME SCORE'])]

    values = [df['ROAD TEAM'], df['HOME TEAM'], 'TIE']

    df['WINNER'] = np.select(conditions, values)
    df['WINNING MARGIN'] = abs(df['ROAD SCORE'] - df['HOME SCORE'])

    return df


def player_win_loss_tie(all_games_dataframe, players):
    """Define win, loss, tie, and display each game's results in column for each player as W, L, T"""
    df = all_games_dataframe

    for player in players:
        conditions = [((df[player] == df['ROAD TEAM']) & (df['ROAD SCORE'] > df['HOME SCORE'])) | (
                    (df[player] == df['HOME TEAM']) & (df['ROAD SCORE'] < df['HOME SCORE'])),
                      ((df[player] == df['ROAD TEAM']) & (df['ROAD SCORE'] < df['HOME SCORE'])) | (
                                  (df[player] == df['HOME TEAM']) & (df['ROAD SCORE'] > df['HOME SCORE'])),
                      ((df[player] == df['ROAD TEAM']) & (df['ROAD SCORE'] == df['HOME SCORE'])) | (
                                  (df[player] == df['HOME TEAM']) & (df['ROAD SCORE'] == df['HOME SCORE']))]
        # Show win, loss, tie
        values = ['W', 'L', 'T']

        df[player + ' RESULTS'] = np.select(conditions, values)

    return df


def player_point_differential(all_games_dataframe, players):
    """ Calculate Point differentials by game, by player. Add column to display for each player-game """
    df = all_games_dataframe
    for player in players:
        conditions = [((df[player] == df['ROAD TEAM']) & (df['ROAD SCORE'] > df['HOME SCORE'])),
                      ((df[player] == df['HOME TEAM']) & (df['ROAD SCORE'] < df['HOME SCORE'])),
                      ((df[player] == df['ROAD TEAM']) & (df['ROAD SCORE'] < df['HOME SCORE'])),
                      ((df[player] == df['HOME TEAM']) & (df['ROAD SCORE'] > df['HOME SCORE'])),
                      ((df[player] == df['ROAD TEAM']) & (df['ROAD SCORE'] == df['HOME SCORE'])) |
                      ((df[player] == df['HOME TEAM']) & (df['ROAD SCORE'] == df['HOME SCORE']))]

        values = [df['ROAD SCORE'] - df['HOME SCORE'], df['HOME SCORE'] - df['ROAD SCORE'],
                  df['ROAD SCORE'] - df['HOME SCORE'],
                  df['HOME SCORE'] - df['ROAD SCORE'], 0]

        df[player + ' POINT DIFF'] = np.select(conditions, values)

    return df


def all_players_win_loss_record(all_games_dataframe, players):
    """For leader board. Player W-L record by week and year to date"""
    df = all_games_dataframe
    win_loss_record_df_ = pd.DataFrame()

    for player in players:
        df_ = df.groupby(by='WEEK')[f'{player} RESULTS'].value_counts().unstack().astype('Int64').fillna(0)

        for result in ['W', 'L', 'T']:
            if result not in df_.columns: # Was failing if no Tie that week
                df_[result] = 0
            win_loss_record_df_[f'{player} {result}'] = df_[result]

    win_loss_record_df_.loc['YTD'] = win_loss_record_df_.sum()

    return win_loss_record_df_


def make_leader_board_df(win_loss_record_df, players):
    """Calculate games back for each player, all weeks in supplied df"""
    df_ = pd.DataFrame()
    win_loss_record_df = win_loss_record_df[:-1] # Drop the YTD row

    for player in players:
        df_[f'{player} CUM WINS'] = win_loss_record_df[f'{player} W'].cumsum()

    df_['MAX CUM WINS'] = df_.max(axis=1)

    for player in players:
        df_[f'{player.upper()} GAMES BACK'] = df_[f'{player} CUM WINS'] - df_['MAX CUM WINS']

    return df_


# def plot_leader_board(leader_board_df):
#     """Plot Leader Board, save to disc"""
#     df_ = leader_board_df
#
#     fig = plt.figure()
#     ax = fig.add_subplot()
#     ax.set_ylim(min(df_.min())-1, 1)
#     ax.yaxis.set_major_locator(MultipleLocator(2))
#     plt.xticks(list(range(1, len(df_) + 1)), week_ticks[0:len(df_)], fontsize=8)
#
#     for player in players:
#         df_.reset_index().plot(kind='line', x='WEEK', y=f'{player} GAMES BACK', marker=marker_dict[player],
#                                    linewidth=4, color=color_dict[player], label=player.capitalize(), ax=ax)
#
#     plt.title('Games Behind Leader', fontsize=20)
#
#     # fig.savefig(f'/Users/paulclanon/Downloads/leaderboard_week{week_to_run}.png', dpi=300)
#     plt.show()
#     plt.close()


def team_results_all_games(all_games_df, teams_to_run):
    """Make dataframe showing results for teams, as opposed to players"""
    team_results_df_temp = pd.DataFrame()

    for team in teams_to_run:
        conditions = [((team == all_games_df['ROAD TEAM']) & (all_games_df['ROAD SCORE'] > \
                                                              all_games_df['HOME SCORE'])) | (
                                  (team == all_games_df['HOME TEAM']) & \
                                  (all_games_df['ROAD SCORE'] < all_games_df['HOME SCORE'])), \
                      ((team == all_games_df['ROAD TEAM']) & (all_games_df['ROAD SCORE'] < \
                                                              all_games_df['HOME SCORE'])) | (
                                  (team == all_games_df['HOME TEAM']) & \
                                  (all_games_df['ROAD SCORE'] > all_games_df['HOME SCORE'])),
                      ((team == all_games_df['ROAD TEAM']) & (all_games_df['ROAD SCORE'] == \
                                                              all_games_df['HOME SCORE'])) | (
                                  (team == all_games_df['HOME TEAM']) & \
                                  (all_games_df['ROAD SCORE'] == all_games_df['HOME SCORE']))]

        values = ['W', 'L', 'T']

        team_results_df_temp[f'{team.upper()} RESULTS'] = np.select(conditions, values)

    for team in teams_to_run:
        team_results_df_temp.loc[team_results_df_temp[f'{team.upper()} RESULTS'] == 'W', f'{team.upper()} WINS'] = 1
        team_results_df_temp.loc[team_results_df_temp[f'{team.upper()} RESULTS'] == 'L', f'{team.upper()} LOSSES'] = 1
        team_results_df_temp.loc[team_results_df_temp[f'{team.upper()} RESULTS'] == 'T', f'{team.upper()} TIES'] = 1

    team_results_df_temp['WEEK'] = all_games_df['WEEK']
    team_results_df_temp.fillna(value=0, inplace=True)

    return team_results_df_temp


def team_records_by_week_and_season_to_date(team_results_df_all_games):
    """Using the big DF of all games, returns a weekly DF of that week's
    results and season to date"""
    team_records_df_temp = pd.DataFrame()
    summed_df_temp = team_results_df_all_games.groupby(['WEEK']).sum()  # For weekly results
    cum_summed_df_temp = summed_df_temp.cumsum()  # For season to date

    for team in nfl_teams:
        # This week
        team_records_df_temp[f'{team.upper()} WINS THIS WEEK'] = summed_df_temp[f'{team.upper()} WINS']
        team_records_df_temp[f'{team.upper()} LOSSES THIS WEEK'] = summed_df_temp[f'{team.upper()} LOSSES']
        team_records_df_temp[f'{team.upper()} TIES THIS WEEK'] = summed_df_temp[f'{team.upper()} TIES']

        # Season to date
        team_records_df_temp[f'{team.upper()} YTD WINS'] = cum_summed_df_temp[f'{team.upper()} WINS']
        team_records_df_temp[f'{team.upper()} YTD LOSSES'] = cum_summed_df_temp[f'{team.upper()} LOSSES']
        team_records_df_temp[f'{team.upper()} YTD TIES'] = cum_summed_df_temp[f'{team.upper()} TIES']

    team_records_df_temp.astype(int)

    return team_records_df_temp


"""Have to have this look from LAST WEEK, not this week"""


def rolling_team_wins(weekly_records_df, rolling_window, teams_to_run):
    """Takes the weekly team records DF and returns a DF of teams_to_runs'
    wins in last rolling_window weeks. Byes count as weeks."""
    rolling_df_temp = pd.DataFrame()

    for team in teams_to_run:
        rolling_df_temp[f'{team.upper()} WINS LAST {rolling_window} WEEKS'] = \
            weekly_records_df[f'{team.upper()} WINS THIS WEEK'].rolling(rolling_window).sum()

    return rolling_df_temp


if __name__ == '__main__':
    # this_week_matchups(df)
    df = random_scores(df)
    df = random_picker_for_tests(df, players)
    df.to_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL_test_year.csv', index=False)
    df = sheep_scores(df, players)
    df = winner_and_winning_margin(df)
    df = player_win_loss_tie(df, players)
    df = player_point_differential(df, players)
    win_loss_record_df = all_players_win_loss_record(df, players)
    leader_board_df = make_leader_board_df(win_loss_record_df, players)
    plot_leader_board(leader_board_df)