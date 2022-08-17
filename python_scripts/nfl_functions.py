import pandas as pd
import numpy as np


df = pd.read_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL.csv')
df = df[df['WEEK'] == 1]


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


    # if row['PAUL'] == row['LONE WOLF']:
    #     return [highlight, default, default, default, default, default, default]
    # elif row['SAM'] == row['LONE WOLF']:
    #     return [default, highlight, default, default, default, default, default]
    # elif row['DAVE'] == row['LONE WOLF']:
    #     return [default, default, highlight, default, default, default, default]
    # elif row['DAN'] == row['LONE WOLF']:
    #     return [default, default, default, highlight, default, default, default]
    # elif row['JEFF'] == row['LONE WOLF']:
    #     return [default, default, default, default, highlight, default, default]
    # elif row['SKELLY'] == row['LONE WOLF']:
    #     return [default, default, default, default, default, highlight, default]
    # else:
    #     return [default, default, default, default, default, default, default]


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


if __name__ == '__main__':
    this_week_matchups(df)