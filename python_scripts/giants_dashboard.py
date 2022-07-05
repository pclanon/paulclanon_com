# giantsdashboard4.py
# June 13, 2022. Refactor into functions for import into website ops
# Email daily MLB standings, linescore of Giants' last game,
#       next game info, Giants' rank in NL on various stats
# Have to pass data to the functions that need it
import datetime
import itertools
import logging
import smtplib
from datetime import timedelta, timezone
from email.mime.text import MIMEText
import pandas as pd
import statsapi
from pybaseball import team_batting, team_pitching


def highlight(value, string_to_test_for):
    string_present = (value == string_to_test_for)

    return ['background-color: yellow' if string_present else '']


def dict_to_dataframe(dataset, division_number):
    """Convert mlb-API's dictionary to a dataframe"""
    standings_df = pd.DataFrame(dataset[division_number])
    division_standings_df = standings_df['teams'].apply(pd.Series)

    return division_standings_df


def streak(dict_team_records, team_name):
    return dict_team_records[team_name]['streak']['streakCode']


def last_ten(dict_team_records, team_name):
    wins = dict_team_records[team_name]['records']['splitRecords'][8]['wins']
    losses = dict_team_records[team_name]['records']['splitRecords'][8]['losses']

    return f'{wins}-{losses}'


def rank_calculator(df_, team):
    team_rank = df_[df_['Team'] == team].index[0] + 1

    return team_rank

def make_standings_table():
    # Housekeeping
    divisions = [203, 205, 204, 201, 202, 200]  # Sets the order of display later, NL West first

    # Get the standings from MLB
    data = statsapi.standings_data()

    # Make a dataframe to house the standings in desired order of divisions
    standings_df = pd.DataFrame()

    for division in divisions:
        division_df = dict_to_dataframe(data, division)
        division_df['div_name'] = data[division]['div_name']
        standings_df = pd.concat([standings_df, division_df], ignore_index=True, sort=False)

    standings_table_df = standings_df.filter(['name', 'w', 'l', 'gb'])

    # Fill in pretty Division labels for standings df

    standings_table_df['Division'] = ['NL West','','','','',
                                      'NL Central','','','','',
                                      'NL East','','','','',
                                      'AL East','','','','',
                                      'AL Central','','','','',
                                      'AL West','','','','',]

    standings_table_df = (standings_table_df[['Division', 'name', 'w', 'l', 'gb']]
                          .rename(columns={'name': 'Team', 'w': 'W', 'l': 'L', 'gb': 'GB'}))

    # Make grand list of teamRecords, one dict per team
    # NL
    standings_NL = statsapi.get('standings', {'leagueId': 104})['records']
    records_NL_ = []

    for division in standings_NL:
        records_NL_.append(division['teamRecords'])

    records_NL = list(itertools.chain(*records_NL_))  # flatten list of lists

    # AL
    standings_AL = statsapi.get('standings', {'leagueId': 103})['records']
    records_AL_ = []

    for division in standings_AL:
        records_AL_.append(division['teamRecords'])

    records_AL = list(itertools.chain(*records_AL_))

    # Combine NL and AL
    records_NL_AL = records_NL + records_AL  # List of dictionaries, one per team

    # Recast list as dictionary with team name as key, 30 teams
    team_records_dict = {}

    for item in records_NL_AL:
        team_records_dict[item['team']['name']] = item

    # Make Streak and Last 10 Columns
    standings_table_df['Str'] = standings_table_df['Team'].apply(lambda x: streak(team_records_dict, x))
    standings_table_df['L10'] = standings_table_df['Team'].apply(lambda x: last_ten(team_records_dict, x))

    # Style standings table df
    standings_table_styled = \
        (standings_table_df.style.applymap(lambda v: 'background-color: yellow' if v == 'San Francisco Giants' else '')
         .hide(axis=0)
         .set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
         )

    standings_table_styled = standings_table_styled.to_html()

    return standings_table_styled

def make_linescore_last_giants_game():
    # Make line score df of last Giants game
    line_score_df = pd.DataFrame()

    # Get line score data
    most_recent_game_id = statsapi.last_game(137)  # 137=Giants team ID
    line_score = statsapi.linescore(most_recent_game_id)
    line_score = line_score.replace('White Sox', 'WhiteSox').replace('Red Sox',
                                         'RedSox').replace('Blue Jays', 'BlueJays')

    for line in range(0, 3):
        l_df = pd.DataFrame(line_score.split('\n')[line].split()).T
        line_score_df = pd.concat([line_score_df, l_df], ignore_index=True, sort=False)

    # Build header from first row of line score df
    new_header = line_score_df.iloc[0]  # grab the first row for the header
    line_score_df = line_score_df[1:]  # take the data less the header row
    line_score_df.columns = new_header  # set the header row as the df header

    # Style line score df
    line_score_df['R'] = line_score_df['R'].astype(int)  # String otherwise, no good.
    line_score_styled = (line_score_df.style
                         .applymap(lambda v: 'background-color: yellow' if v == 'Giants' else '')
                         .hide(axis=0)
                         .set_properties(**{'background-color': 'gainsboro'}, subset='R')
                         .highlight_max(color='palegreen', axis=0, subset='R')
                         .set_properties(**{'text-align': 'center'})
                         .set_properties(**{'text-align': 'left'}, subset='Final')
                         .set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
                         )

    # Convert styled line score df to html
    line_score_styled = line_score_styled.to_html() #doctype_html=True, exclude_styles=True

    return line_score_styled


def make_day_of_last_giants_game():
    last_game_id = statsapi.last_game(137)
    last_game_date = statsapi.boxscore_data(last_game_id, timecode=None)['gameId'][:10]
    last_game_datetime = datetime.datetime.strptime(last_game_date, '%Y/%m/%d')
    giants_last_game_day = datetime.datetime.strftime(last_game_datetime,
                                                      '%a, %B %-d')

    return giants_last_game_day

def make_giants_next_game():
    # Next Game -- Opponent, location, day, time in Pacific Time (ex: Padres @ Giants, Wed 12:45 PM PDT)

    next_game_id = statsapi.next_game(137)
    giants_next_game_dict = statsapi.schedule(game_id=next_game_id)[0]

    giants_next_game_day_time = datetime.datetime.strptime(giants_next_game_dict['game_datetime'],
                                                           '%Y-%m-%dT%H:%M:00Z')
    giants_next_game_day_time = giants_next_game_day_time.replace(tzinfo=timezone.utc).astimezone(tz=None)
    giants_next_game_day_time = datetime.datetime.strftime(giants_next_game_day_time,
                                                           '%a %-I:%M %p')
    next_game_str = (
        f"{giants_next_game_dict['away_name'].split()[-1]} @ {giants_next_game_dict['home_name'].split()[-1]}, "
        f'{giants_next_game_day_time} PDT')

    return next_game_str


def make_nl_teams_rankings():
    # NL teams' rank in various stats
    nl_teams = ['SFG', 'ARI', 'ATL', 'CHC', 'CIN', 'COL', 'LAD', 'MIA', 'MIL',
                'NYM', 'PHI', 'PIT', 'SDP', 'STL', 'WSN']

    batting_stats_of_interest = ['OPS', ' HR', ' R']
    pitching_stats_of_interest = ['ERA', 'HR-Op', 'R-Op']

    batting_df = team_batting(2022, league="nl")[['Team', 'OPS', 'HR', 'R']]
    pitching_df = team_pitching(2022, league="nl")[['Team', 'ERA', 'HR', 'R']]

    df = (pd.merge(batting_df, pitching_df, on='Team')
          .rename(columns={'HR_x': ' HR', 'HR_y': 'HR-Op', 'R_x': ' R', 'R_y': 'R-Op'})
          )

    teams_rank_df = pd.DataFrame(index=nl_teams, columns=batting_stats_of_interest + pitching_stats_of_interest)

    for stat in batting_stats_of_interest:
        col_ = []
        for team in nl_teams:
            df_sorted = df.sort_values(by=[stat], ignore_index=True, ascending=False)
            col_.append(rank_calculator(df_sorted, team))
        teams_rank_df[stat] = col_

    for stat in pitching_stats_of_interest:
        col_ = []
        for team in nl_teams:
            df_sorted = df.sort_values(by=[stat], ignore_index=True)
            col_.append(rank_calculator(df_sorted, team))
        teams_rank_df[stat] = col_

    teams_rank_df = teams_rank_df.reset_index().rename(columns={'index': ''})
    teams_rank_df['Overall'] = ((teams_rank_df['OPS'] + teams_rank_df['R-Op'])/2).astype('int')

    # Style the rank dataframe
    teams_rank_styled = (teams_rank_df
                         .style
                         .hide(axis=0)
                         .set_table_styles([{"selector": "td", "props": [("text-align", "right")]}])
                         .applymap(lambda v: 'background-color: palegreen' if v == 1 else '')
                         .applymap(lambda v: 'background-color: yellow' if v == 'SFG' else '', subset=[''])
                         )
    # Convert styled teams rank df to html
    teams_rank_styled = teams_rank_styled.to_html()

    return teams_rank_styled

def email_giants_dashboard(line_score_styled, next_game_str,
                           teams_rank_styled, standings_table_styled):
    # Day and date housekeeping
    most_recent_game_id = statsapi.last_game(137)  # 137=Giants team ID
    date_of_last_game = statsapi.boxscore_data(most_recent_game_id, timecode=None)['gameId'][0:10]
    date_of_last_game = datetime.datetime.strptime(date_of_last_game, '%Y/%m/%d')
    date_of_last_game = datetime.datetime.strftime(date_of_last_game, ('%A, %b %-d %Y'))
    today = datetime.datetime.now()
    yesterday = (today - timedelta(days=1)).strftime('%A, %b %-d %Y')

    # Create the container email message.
    msg = MIMEText(f"<b>* Giants' Last Game -- {date_of_last_game}</b><br><br>{line_score_styled}"
                   f"<br><br><b>* Giants' Next Game -- {next_game_str}</b>"
                   f"<br><br><br><b>* NL Teams' Rank on Key Stats</b><br><br>{teams_rank_styled}"
                   f'<br><br><b>* MLB Standings After {yesterday}</b><br><br>{standings_table_styled}',
                   'html')
    msg['Subject'] = "Giants Dashboard"
    msg['From'] = '***********'
    msg['To'] = '********, ********'
    msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # Open an SMTP session on server
    session = smtplib.SMTP(host='*******.com')

    # Send Email & Exit
    session.send_message(msg)
    session.quit

def main():

    standings_table_styled = make_standings_table()
    line_score_styled = make_linescore_last_giants_game()
    next_game_str = make_giants_next_game()
    teams_rank_styled = make_nl_teams_rankings()
    email_giants_dashboard(line_score_styled, next_game_str,
                               teams_rank_styled, standings_table_styled)


if __name__ == '__main__':
    # Log begin
    logging.basicConfig(filename='dizzy.log', format='%(asctime)s %(message)s',
                        datefmt='%m-%d-%Y %I:%M:%S %p', encoding='utf-8',
                        level=logging.INFO)
    logging.info('Clanon giantsdashboard.py started')

    main()

    # Log end
    logging.info('Clanon giantsdashboard.py finished')