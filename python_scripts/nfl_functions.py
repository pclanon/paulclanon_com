import pandas as pd


df = pd.read_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL.csv')
df = df[df['WEEK'] == 1]


def this_week_matchups(df):
    this_week_matchups = tuple(zip(df.index.tolist(), df['ROAD TEAM'], df['HOME TEAM']))

    return this_week_matchups


def identify_lone_wolf_pick(row):
    picks = row.tolist()
    lw = False

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
        return [highlight, default, default]
    elif row['MICHELLE'] == row['LONE WOLF']:
        return [default, highlight, default]
    else:
        return [default, default, default]


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


if __name__ == '__main__':
    this_week_matchups(df)