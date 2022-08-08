import pandas as pd


df = pd.read_csv('/Users/paulclanon/Documents/NFL_2022/2022_NFL_CBCL.csv')
df = df[df['WEEK'] == 1]


def this_week_matchups(df):
    this_week_matchups = tuple(zip(df.index.tolist(), df['ROAD TEAM'], df['HOME TEAM']))

    return this_week_matchups



if __name__ == '__main__':
    this_week_matchups(df)