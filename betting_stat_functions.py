from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time
import ftplib
from datetime import datetime
import xlrd


"""
List of leagues used
    0 - league_short_name
    1 - league_dashed
    2 - num_teams
    3 - league_slashed
    4 - league_name_upper
"""
soccer_league_list = [
    ['epl', 'england-premier-league', 20, 'england/premier-league/results/', 'English Premier League'],
    ['ligue_1', 'france-ligue-1', 20, 'france/ligue-1/results/', 'French Ligue 1'],
    ['bundesliga', 'germany-bundesliga', 18, 'germany/bundesliga/results/', 'German Bundesliga'],
    ['serie_a', 'italy-serie-a', 20, 'italy/serie-a/results/', 'Italian Serie A'],
    ['la_liga', 'spain-la-liga', 20, 'spain/laliga/results/', 'Spanish La Liga'],
        ]


def uncombine_columns(rows, combined_stat_columns, games_played_index=2):
    """to extract data from columns including + or - symbol"""
    for column in combined_stat_columns:
        for row in rows:
            expected_stat = row[column].split("+")
            row[column] = expected_stat[0]
            expected_stat = row[column].split("-")
            row[column] = expected_stat[0]
            row.append(float(row[column]) / float(row[games_played_index]))
    for row in rows:
        row.pop()
    return rows


def get_xlsx_data(file):
    """pull data from .xlsx formatted Excel sheet"""
    workbook = xlrd.open_workbook(file)
    sheet = workbook.sheet_by_index(0)
    columns = sheet.row_values(0)
    rows = []
    for row in range(1, sheet.nrows):
        rows.append(sheet.row_values(row))
    return columns, rows


def get_results(league_short_name, file):
    """get results for a specific league, sort by date DESC"""
    columns, results = get_xlsx_data(file)
    league_name_index = 75
    results_dict = {}
    match_list = []
    for row in results:
        if row[league_name_index] == league_short_name:
            row[0] = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(row[0]) - 2).strftime('%m/%d/%Y')
            match_list.append(row)
    match_list.sort(key=lambda x: datetime.strptime(x[0], '%m/%d/%Y'), reverse=True)
    results_dict[league_short_name] = match_list
    return results_dict


def create_archived_odds_html(results_dict, league):
    archived_odds_html_table = """
                <h1>""" + league + """ Archived Betting Odds</h1>
                <input type="text" id="myInput" onkeyup="searchFunction()" placeholder="Search by team...">
                <table id="stats_table">
                    <tr>
                        <th>Date</th>
                        <th onclick="sortTable(1, 'stats_table')">Home Team</th>
                        <th onclick="sortTable(2, 'stats_table')">Away Team</th>
                        <th>Home Team Spread</h>
                        <th>HT Odds</th>
                        <th>AT Odds</th>
                        <th>Over Under</th>
                        <th>Over Odds</th>
                        <th>Under Odds</th>
                        <th>HT Score</th>
                        <th>AT Score</th>
                        <th style="display: none">Team Search</th>
                    </tr>
                        """
    for value in results_dict.values():
        for match in value:
            match_row = '<tr>'
            for stat in range(0, 6):
                match_row += '<td>' + str(match[stat]) + '</td>'
            for stat in range(8, 11):
                match_row += '<td>' + str(match[stat]) + '</td>'
            for stat in range(73, 75):
                match_row += '<td>' + str(match[stat]) + '</td>'
            match_row += '<td style="display: none;">' + match[1] + '*' + match[2] + '</td>'
            match_row += '</tr>'
            archived_odds_html_table += match_row
    return archived_odds_html_table


def understat_pull(url_base, league_list, team_list):
    """To pull stats for all selected leagues from Understat"""
    stats_dict = {}
    combined_stat_columns = [9, 10, 11]
    stat_filter_decoder = {1: 'Overall', 2: 'Home', 3: 'Away'}
    for league in league_list:
        num_teams = league[2]
        full_url = url_base + league[0]
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(full_url)
        for stat_filter in list(range(1, 4)):
            label = '//label[@for="home-away' + str(stat_filter) + '"]'
            elem = driver.find_element_by_xpath(label)
            time.sleep(1)
            elem.click()
            r = driver.page_source
            soup = BeautifulSoup(r, 'html.parser')
            table = soup.find_all('td')
            a_list = []
            for item in table:
                a_list.append(item.text)
            final_list = []
            x = 0
            while x < num_teams * 12:
                new_list = [item for item in a_list[x:x + 12]]
                final_list.append(new_list)
                x += 12
            uncombine_columns(final_list, combined_stat_columns)
            for item in final_list:
                for team in team_list:
                    if item[1] == team[0]:
                        item[1] = team[1]
            stats_dict[league[4] + '-' + stat_filter_decoder[stat_filter]] = final_list
    return stats_dict


def create_stat_table_html(league, stats_dict):
    """Create html stat tables from pulled stats dictionary"""
    html_header = ''
    html_header = "<h1>" + league + " Current Stats</h1>"
    for key, stats in stats_dict.items():
        ksplit = key.split('-')
        options = ['Overall', 'Home', 'Away']
        if ksplit[0] == league:
            for option in options:
                html_base = """<table id="stats_table_""" + option + """">
                                <tr>
                                    <th onclick="sortTable(0, 'stats_table_""" + option + """')">No</th>
                                    <th onclick="sortTable(1, 'stats_table_""" + option + """')">Team Name</th>
                                    <th onclick="sortTable(2, 'stats_table_""" + option + """')">Matches</th>
                                    <th onclick="sortTable(3, 'stats_table_""" + option + """')">Won</th>
                                    <th onclick="sortTable(4, 'stats_table_""" + option + """')">Drawn</th>
                                    <th onclick="sortTable(5, 'stats_table_""" + option + """')">Lost</th>
                                    <th onclick="sortTable(6, 'stats_table_""" + option + """')">Goals For</th>
                                    <th onclick="sortTable(7, 'stats_table_""" + option + """')">Goals Against</th>
                                    <th onclick="sortTable(8, 'stats_table_""" + option + """')">Points</th>
                                    <th onclick="sortTable(9, 'stats_table_""" + option + """')">xG</th>
                                    <th onclick="sortTable(10, 'stats_table_""" + option + """')">xGA</th>
                                    <th onclick="sortTable(11, 'stats_table_""" + option + """')">xPts</th>
                                    <th onclick="sortTable(12, 'stats_table_""" + option + """')">xG/Match</th>
                                    <th onclick="sortTable(13, 'stats_table_""" + option + """')">xGA/Match</th>
                                </tr>
                    """
                if ksplit[1] == option:
                    html_content = "<h2>" + option + " Stats</h2>" + html_base
                    for team in stats:
                        html_row = "<tr>"
                        for stat in team:
                            if isinstance(stat, float):
                                html_row += "<td>" + str(round(stat, 2)) + "</td>"
                            else:
                                html_row += "<td>" + str(stat) + "</td>"
                        html_row += "</tr>"
                        html_content += html_row
                    html_content += "</table><br />"
                    html_header += html_content
    return html_header


def dump_and_upload(league_name, dump_file, html, page, user_id, password):
    with open(dump_file, 'w') as f:
        f.write(html)

    session = ftplib.FTP('ftp.dosshouse.us', '792e4622@dosshouse.us', '*#8fZ~#8VFe7')
    file = open(dump_file, 'rb')
    session.cwd('public_html/soccer_betting/' + league_name + '/')
    session.storbinary('STOR ' + page.lower() + '.html', file)
    file.close()
    session.quit()
    print(page + ' updated at ' + datetime.now().strftime('%m/%d/%Y %H:%M'))



"""Team list for name conversions:
        0 = Understat Name
        1 = Bovada Name
        2 = Scoreboard Name
    All accents removed
"""
team_list = [
    # English Premier League
    ['Arsenal', 'Arsenal', 'Arsenal'],
    ['Aston Villa', 'Aston Villa', 'Aston Villa'],
    ['Bournemouth', 'Bournemouth', 'Bournemouth'],
    ['Brighton', 'Brighton', 'Brighton'],
    ['Burnley', 'Burnley', 'Burnley'],
    ['Chelsea', 'Chelsea', 'Chelsea'],
    ['Crystal Palace', 'Crystal Palace', 'Crystal Palace'],
    ['Everton', 'Everton', 'Everton'],
    ['Leicester', 'Leicester City', 'Leicester'],
    ['Liverpool', 'Liverpool', 'Liverpool'],
    ['Manchester City', 'Manchester City', 'Manchester City'],
    ['Manchester United', 'Manchester United', 'Manchester United'],
    ['Newcastle United', 'Newcastle United', 'Newcastle'],
    ['Norwich', 'Norwich City', 'Norwich'],
    ['Sheffield United', 'Sheffield United', 'Sheffield Utd'],
    ['Southampton', 'Southampton', 'Southampton'],
    ['Tottenham', 'Tottenham Hotspur', 'Tottenham'],
    ['Watford', 'Watford', 'Watford'],
    ['West Ham', 'West Ham', 'West Ham'],
    ['Wolverhampton Wanderers', 'Wolverhampton Wanderers', 'Wolves'],

    # French Ligue 1
    ['Amiens', 'Amiens', 'Amiens'],
    ['Angers', 'Angers', 'Angers'],
    ['Bordeaux', 'Bordeaux', 'Bordeaux'],
    ['Brest', 'Brest', 'Brest'],
    ['Dijon', 'Dijon', 'Dijon'],
    ['Lille', 'Lille', 'Lille'],
    ['Lyon', 'Lyon', 'Lyon'],
    ['Marseille', 'Marseille', 'Marseille'],
    ['Metz', 'Metz', 'Metz'],
    ['Monaco', 'Monaco', 'Monaco'],
    ['Montpellier', 'Montpellier', 'Montpellier'],
    ['Nantes', 'Nantes', 'Nantes'],
    ['Nice', 'Nice', 'Nice'],
    ['Nimes', 'Nimes', 'Nimes'],
    ['Paris Saint Germain', 'Paris SG', 'Paris SG'],
    ['Reims', 'Reims', 'Reims'],
    ['Rennes', 'Rennes', 'Rennes'],
    ['Saint-Etienne', 'Saint-Etienne', 'Saint-Etienne'],
    ['Strasbourg', 'Strasbourg', 'Strasbourg'],
    ['Toulouse', 'Toulouse', 'Toulouse'],

    # German Bundesliga
    ['Augsburg', 'Augsburg', 'Augsburg'],
    ['Bayer Leverkusen', 'Bayer Leverkusen', 'Bayer Leverkusen'],
    ['Bayern Munich', 'Bayern Munich', 'Bayern Munich'],
    ['Borussia Dortmund', 'Borussia Dortmund', 'Dortmund'],
    ['Borussia M.Gladbach', 'Borussia Monchengladbach', 'B. Monchengladbach'],
    ['Eintracht Frankfurt', 'Eintracht Frankfurt', 'Eintracht Frankfurt'],
    ['FC Cologne', 'FC Koln', 'FC Koln'],
    ['Fortuna Duesseldorf', 'Fortuna Dusseldorf', 'Dusseldorf'],
    ['Freiburg', 'Sport-Club Freiburg', 'Freiburg'],
    ['Hertha Berlin', 'Hertha Berlin', 'Hertha Berlin'],
    ['Hoffenheim', 'Hoffenheim', 'Hoffenheim'],
    ['Mainz 05', 'FSV Mainz', 'Mainz'],
    ['Paderborn', 'Paderborn', 'Paderborn'],
    ['RasenBallsport Leipzig', 'RB Leipzig', 'RB Leipzig'],
    ['Schalke 04', 'FC Schalke 04', 'Schalke'],
    ['Union Berlin', 'Union Berlin', 'Union Berlin'],
    ['Werder Bremen', 'SV Werder Bremen', 'Werder Bremen'],
    ['Wolfsburg', 'Vfl Wolfsburg', 'Wolfsburg'],

    # Italian Serie A
    ['AC Milan', 'AC Milan', 'AC Milan'],
    ['Atalanta', 'Atalanta', 'Atalanta'],
    ['Bologna', 'Bologna', 'Bologna'],
    ['Brescia', 'Brescia', 'Brescia'],
    ['Cagliari', 'Cagliari', 'Cagliari'],
    ['Fiorentina', 'Fiorentina', 'Fiorentina'],
    ['Genoa', 'Genoa', 'Genoa'],
    ['Inter', 'Inter Milan', 'Inter'],
    ['Juventus', 'Juventus', 'Juventus'],
    ['Lazio', 'Lazio', 'Lazio'],
    ['Lecce', 'Lecce', 'Lecce'],
    ['Napoli', 'Napoli', 'Napoli'],
    ['Parma Calcio 1913', 'Parma', 'Parma'],
    ['Roma', 'AS Roma', 'AS Roma'],
    ['SPAL 2013', 'SPAL', 'Spal'],
    ['Sampdoria', 'Sampdoria', 'Sampdoria'],
    ['Sassuolo', 'Sassuolo', 'Sassuolo'],
    ['Torino', 'Torino', 'Torino'],
    ['Udinese', 'Udinese', 'Udinese'],
    ['Verona', 'Verona', 'Verona'],

    # Spanish La Liga
    ['Alaves', 'Alaves', 'Alaves'],
    ['Athletic Club', 'Athletic Bilbao', 'Ath Bilbao'],
    ['Atletico Madrid', 'Atletico Madrid', 'Atl. Madrid'],
    ['Barcelona', 'FC Barcelona', 'Barcelona'],
    ['Celta Vigo', 'Celta de Vigo', 'Celta Vigo'],
    ['Eibar', 'Eibar', 'Eibar'],
    ['Espanyol', 'Espanyol', 'Espanyol'],
    ['Getafe', 'Getafe', 'Getafe'],
    ['Granada', 'Granada', 'Granada CF'],
    ['Leganes', 'Leganes', 'Leganes'],
    ['Levante', 'Levante', 'Levante'],
    ['Mallorca', 'Mallorca', 'Mallorca'],
    ['Osasuna', 'Osasuna', 'Osasuna'],
    ['Real Betis', 'Real Betis', 'Betis'],
    ['Real Madrid', 'Real Madrid', 'Real Madrid'],
    ['Real Sociedad', 'Real Sociedad', 'Real Sociedad'],
    ['Real Valladolid', 'Valladolid', 'Valladolid'],
    ['Sevilla', 'Sevilla', 'Sevilla'],
    ['Valencia', 'Valencia', 'Valencia'],
    ['Villarreal', 'Villarreal', 'Villarreal'],
        ]
