import csv
import numpy as np
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from unidecode import unidecode
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV


current_week = '2020-02-20'
iterations = 10000
knn_training_file = 'All Soccer Results.xlsx'
team_list = [['AC Milan', 'AC Milan'], ['AS Roma', 'AS Roma'], ['Alaves', 'Alaves'], ['Amiens', 'Amiens'],
             ['Angers', 'Angers'], ['Arsenal', 'Arsenal'], ['Aston Villa', 'Aston Villa'], ['Atalanta', 'Atalanta'],
             ['Athletic Bilbao', 'Ath Bilbao'], ['Atletico Madrid', 'Atl. Madrid'], ['Augsburg', 'Augsburg'],
             ['Bayer Leverkusen', 'Bayer Leverkusen'], ['Bayern Munich', 'Bayern Munich'], ['Bologna', 'Bologna'],
             ['Bordeaux', 'Bordeaux'], ['Borussia Dortmund', 'Dortmund'],
             ['Borussia Monchengladbach', 'B. Monchengladbach'], ['Bournemouth', 'Bournemouth'],
             ['Brescia', 'Brescia'], ['Brest', 'Brest'], ['Brighton', 'Brighton'], ['Burnley', 'Burnley'],
             ['Cagliari', 'Cagliari'], ['Celta de Vigo', 'Celta Vigo'], ['Chelsea', 'Chelsea'],
             ['Crystal Palace', 'Crystal Palace'], ['Dijon', 'Dijon'], ['Eibar', 'Eibar'],
             ['Eintracht Frankfurt', 'Eintracht Frankfurt'], ['Espanyol', 'Espanyol'], ['Everton', 'Everton'],
             ['FC Barcelona', 'Barcelona'], ['1. FC Koln', 'FC Koln'], ['FC Schalke 04', 'Schalke'],
             ['FSV Mainz', 'Mainz'], ['Fiorentina', 'Fiorentina'], ['Fortuna Dusseldorf', 'Dusseldorf'],
             ['Genoa', 'Genoa'], ['Getafe', 'Getafe'], ['Granada', 'Granada CF'], ['Hertha Berlin', 'Hertha Berlin'],
             ['Hoffenheim', 'Hoffenheim'], ['Inter Milan', 'Inter'], ['Juventus', 'Juventus'], ['Lazio', 'Lazio'],
             ['Lecce', 'Lecce'], ['Leganes', 'Leganes'], ['Leicester City', 'Leicester'], ['Levante', 'Levante'],
             ['Lille', 'Lille'], ['Liverpool', 'Liverpool'], ['Lyon', 'Lyon'], ['FC Koln', 'FC Koln'],
             ['Mallorca', 'Mallorca'], ['Manchester City', 'Manchester City'], ['Manchester United', 'Manchester Utd'],
             ['Olympique Marseille', 'Marseille'], ['Metz', 'Metz'], ['Monaco', 'Monaco'], ['Montpellier', 'Montpellier'],
             ['Nantes', 'Nantes'], ['Napoli', 'Napoli'], ['Newcastle United', 'Newcastle'], ['Nice', 'Nice'],
             ['Nimes', 'Nimes'], ['Norwich City', 'Norwich'], ['Osasuna', 'Osasuna'], ['Paderborn', 'Paderborn'],
             ['Paris SG', 'Paris SG'], ['Parma', 'Parma'], ['RB Leipzig', 'RB Leipzig'],
             ['Racing Strasburg', 'Strasbourg'], ['Real Betis', 'Betis'], ['Real Madrid', 'Real Madrid'],
             ['Real Sociedad', 'Real Sociedad'], ['Rennes', 'Rennes'], ['SPAL', 'Spal'],
             ['SV Werder Bremen', 'Werder Bremen'], ['Saint-Etienne', 'St Etienne'], ['Sampdoria', 'Sampdoria'],
             ['Sassuolo', 'Sassuolo'], ['Sevilla', 'Sevilla'], ['Sheffield United', 'Sheffield Utd'],
             ['Southampton', 'Southampton'], ['Sport-Club Freiburg', 'Freiburg'], ['Stade Reims', 'Reims'],
             ['Torino', 'Torino'], ['Tottenham Hotspur', 'Tottenham'], ['Toulouse', 'Toulouse'],
             ['Udinese', 'Udinese'], ['Union Berlin', 'Union Berlin'], ['Valencia', 'Valencia'],
             ['Valladolid', 'Valladolid'], ['Verona', 'Verona'], ['VfL Wolfsburg', 'Wolfsburg'],
             ['Villarreal', 'Villarreal'], ['Watford', 'Watford'], ['West Ham', 'West Ham'],
             ['Wolverhampton Wanderers', 'Wolves']]

leagues = [
    ['epl', 'england-premier-league', 20, 'england/premier-league/results/'],
    ['la_liga', 'spain-la-liga', 20, 'spain/laliga/results/'],
    ['bundesliga', 'germany-bundesliga', 18, 'germany/bundesliga/results/'],
    ['serie_a', 'italy-serie-a', 20, 'italy/serie-a/results/'],
    ['ligue_1', 'france-ligue-1', 20, 'france/ligue-1/results/'],
           ]


def render_page(url):
    """to pull html from page which takes a few secs to load"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)
    r = driver.page_source
    return r


def improved_bovada_pull(url, team_list):
    """pull betting data from bovada"""
    # grab raw data from bovada.lv
    r = render_page(url)
    soup = BeautifulSoup(r, 'html.parser')
    table = soup.find_all('sp-multi-markets', class_='coupon multi3')

    # turn soup into usable table
    my_list = []
    for item in table:
        my_list.append(item.text)
    split_list = []
    for item in my_list:
        split_list.append(item.split(" "))

    # remove leading info from first match
    for item in split_list:
        if item[3][-5:].lower() == 'total':
            for col in item[0:3]:
                item.remove(col)
        elif item[4][-5:].lower() == 'total':
            for col in item[0:4]:
                item.remove(col)

    # remove unwanted and blank columns
    pop_indices = list(range(11, -1, -1))
    pop_indices.pop(3)
    for item in split_list:
        for num in pop_indices:
            item.pop(num)
    for item in split_list:
        for col in item:
            if col == '':
                item.remove(col)

    # create team dict with and without spaces
    team_dict = {}
    team_dict_rev = {}
    for team in team_list:
        team_dict[team[0]] = team[0].replace(' ', '')
    for team in team_list:
        team_dict_rev[team[0].replace(' ', '')] = team[0]

    # split up team names correctly
    # remove 'Draw' and split items by capital letter
    for item in split_list:
        if len(item) < 14:
            split_list.remove(item)
            continue

        for num in range(1, 5):
            if item[num].find('Draw') != -1:
                item[num] = item[num][0:item[num].find('Draw')]

        # place team names with no space in item[1]
        if item[4][0].isupper():
            item[1] = item[1] + item[2] + item[3] + item[4]
            item.remove(item[4])
            item.remove(item[3])
            item.remove(item[2])
        elif item[3][0].isupper():
            item[1] = item[1] + item[2] + item[3]
            item.remove(item[3])
            item.remove(item[2])
        elif item[2][0].isupper():
            item[1] = item[1] + item[2]
            item.remove(item[2])

        # decode accents fro team names
        item[1] = unidecode(item[1])

        # separate teams into home and away
        for team in team_dict.values():
            if team in item[1]:
                if item[1][0:len(team)] == team:
                    item.insert(1, team)
                    item[2] = item[2].replace(team, '')

        # FC Schalke 04 special case as away team
        if item[2] == 'FCSchalke':
            item[2] = item[2] + '04'
            item.remove(item[3])
        elif item[1] == 'FCSchalke':
            item[1] = item[1] + '04'
            item[2] = item[2][2:]
        print(item)
        # convert team names into correct format
        item[1] = team_dict_rev[item[1]]
        item[2] = team_dict_rev[item[2]]

        if len(item) != 15:
            split_list.remove(item)
            continue

        # remove unneeded columns
        pop_indices2 = [13, 10, 6, 3]
        for index in pop_indices2:
            item.pop(index)
        replace_indices = list(range(3, 11))
        for index in replace_indices:
            item[index] = item[index].replace('(',
                                              '').replace(')',
                                                          '').replace('+',
                                                                      '').replace('O',
                                                                                  '').replace('EVEN', '100')

    return split_list


def uncombine_columns(rows, combined_stat_columns, games_played_index=2):
    """to extract data from columns including + or - symbol"""
    for column in combined_stat_columns:
        for row in rows:
            expected_stat = row[column].split("+")
            row[column] = expected_stat[0]
            expected_stat = row[column].split("-")
            row[column] = expected_stat[0]
            row.append(float(row[column]) / float(row[games_played_index]))
    return rows


def understat_pull(url, filter='1', combined_stat_columns=None, num_teams=20):
    """pull in data from understat.com (use filter to pull home/away stats (1=Overall, 2=Home, 3=Away"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=chrome_options)
    #driver = webdriver.Chrome(r'c:\\Users\\iwk54\\PycharmProjects\\chromedriver.exe')
    driver.get(url)
    label = '//label[@for="home-away' + filter + '"]'
    elem = driver.find_element_by_xpath(label)
    time.sleep(1)
    elem.click()
    r = driver.page_source
    soup = BeautifulSoup(r, 'html.parser')
    table = soup.find_all('td')
    driver.close()

    alist = []
    for item in table[0:240]:
        alist.append(item.text)

    # replace team names to match bovada.lv (be thankful they don't offer bets on RFPL yet)
    blist = [item.replace('Leicester', 'Leicester City') for item in alist]
    blist = [item.replace('Tottenham', 'Tottenham Hotspur') for item in blist]
    blist = [item.replace('Norwich', 'Norwich City') for item in blist]
    blist = [item.replace('Barcelona', 'FC Barcelona') for item in blist]
    #blist = [item.replace('Atletico Madrid', 'Atle' + u'\u0301' + 'tico Madrid') for item in blist]
    #blist = [item.replace('Leganes', 'Legane' + u'\u0301' + 's') for item in blist]
    #blist = [item.replace('Alaves', 'Alave' + u'\u0301' + 's') for item in blist]
    blist = [item.replace('Celta Vigo', 'Celta de Vigo') for item in blist]
    blist = [item.replace('Real Valladolid', 'Valladolid') for item in blist]
    blist = [item.replace('Athletic Club', 'Athletic Bilbao') for item in blist]
    blist = [item.replace('Freiburg', 'Sport-Club Freiburg') for item in blist]
    blist = [item.replace('Fortuna Duesseldorf', 'Fortuna Dusseldorf') for item in blist]
    blist = [item.replace('Mainz 05', 'FSV Mainz') for item in blist]
    blist = [item.replace('RasenBallsport Leipzig', 'RB Leipzig') for item in blist]
    blist = [item.replace('Wolfsburg', 'VfL Wolfsburg') for item in blist]
    blist = [item.replace('Werder Bremen', 'SV Werder Bremen') for item in blist]
    blist = [item.replace('Borussia M.Gladbach', 'Borussia Monchengladbach') for item in blist]
    blist = [item.replace('FC Cologne', 'FC Koln') for item in blist]
    blist = [item.replace('Schalke 04', 'FC Schalke 04') for item in blist]
    blist = [item.replace('Inter', 'Inter Milan') for item in blist]
    blist = [item.replace('SPAL 2013', 'SPAL') for item in blist]
    blist = [item.replace('Roma', 'AS Roma') for item in blist]
    blist = [item.replace('Parma Calcio 1913', 'Parma') for item in blist]
    blist = [item.replace('Paris Saint Germain', 'Paris SG') for item in blist]
    blist = [item.replace('Reims', 'Stade Reims') for item in blist]
    #blist = [item.replace('Saint-Etienne', 'Saint-E' + u'\u0301' + 'tienne') for item in blist]
    blist = [item.replace('Strasbourg', 'Racing Strasburg') for item in blist]
    blist = [item.replace('Marseille', 'Olympique Marseille') for item in blist]
    blist = [item.replace('FC Koln', '1. FC Koln') for item in blist]
    x = 0
    final_list = []
    while x < num_teams * 12:
        new_list = [item for item in blist[x:x + 12]]
        final_list.append(new_list)
        x += 12
    if combined_stat_columns is not None:
        uncombine_columns(final_list, combined_stat_columns)

    return final_list


def pull_csv_data(filename, combined_stat_columns=None, expected_lines=0):
    """to pull in data stored in csv format into list of fields and rows"""
    rows = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            rows.append(row)
        if expected_lines != 0:
            # verify correct number of rows is in file
            if csvreader.line_num - 1 != expected_lines:
                print("Error! " + filename + " is incomplete.")
    if combined_stat_columns is not None:
        uncombine_columns(rows, combined_stat_columns)
    return [fields, rows]


def get_bovada_info(rows, home_team, away_team):
    for row in rows:
        if unidecode(row[1]) == home_team and unidecode(row[2]) == away_team:
            home_team_line = float(row[3])
            over_under_line = float(row[8])
    return [home_team_line, over_under_line]


def get_xg_stats(ht_rows, at_rows, home_team, away_team, avg_stat_columns, team_index=1):
    """to make average expected goal stats for the match based on home team and away team stats"""
    for row in ht_rows:
        if row[team_index] == home_team:
            xg_home_team = float(row[avg_stat_columns[0]])
            xga_home_team = float(row[avg_stat_columns[1]])
    for row in at_rows:
        if row[team_index] == away_team:
            xg_away_team = float(row[avg_stat_columns[0]])
            xga_away_team = float(row[avg_stat_columns[1]])
    xs_home_team = (xg_home_team + xga_away_team) / 2
    xs_away_team = (xg_away_team + xga_home_team) / 2
    return [xs_home_team, xs_away_team]


def poissonate(stat, number_of_iterations=iterations):
    """create poisson distribution for average goals"""
    poisson = np.random.poisson(stat, number_of_iterations)
    return poisson


def zip_scores(home_poisson, away_poisson):
    """"zip poisson distributions into list of possible game results,
    return expected game result probabilities and total goal probabilities"""
    scores = list(zip(home_poisson, away_poisson))
    score_diff_list = []
    total_goals_list = []
    for item in scores:
        score_diff_list.append(item[0] - item[1])
    results_dict = Counter(score_diff_list)
    for item in scores:
        total_goals_list.append(item[0] + item[1])
    total_goals_dict = Counter(total_goals_list)
    return [results_dict, total_goals_dict]


def get_outright_result_probabilities(results_dict, number_of_iterations=iterations):
    """get probabilities of outright results (positive = home win, negative = away win, 0 = draw)"""
    home_win_prob = 0
    away_win_prob = 0
    draw_prob = 0
    for result, prob in results_dict.items():
        if result > 0:
            home_win_prob += prob / number_of_iterations
        elif result < 0:
            away_win_prob += prob / number_of_iterations
        elif result == 0:
            draw_prob += prob / number_of_iterations
    return [home_win_prob, away_win_prob, draw_prob]


def get_spread_result_probabilities(results_dict, home_line, number_of_iterations=iterations):
    """get probabilities of results based on home team spread
    (positive = home win, negative = away win, 0 = draw)"""
    spread_home_win_prob = 0
    spread_away_win_prob = 0
    spread_push_prob = 0
    for result, prob in results_dict.items():
        if result + home_line > 0:
            spread_home_win_prob += prob / number_of_iterations
        elif result + home_line < 0:
            spread_away_win_prob += prob / number_of_iterations
        elif result + home_line == 0:
            spread_push_prob += prob / number_of_iterations
    return [spread_home_win_prob, spread_away_win_prob, spread_push_prob]


def get_over_under_probabilities(total_goals_dict, over_under_line, number_of_iterations=iterations):
    """get probabilities of total goals beating the over under line"""
    over_prob = 0
    under_prob = 0
    push_prob = 0
    for goals, prob in total_goals_dict.items():
        if goals > over_under_line:
            over_prob += prob / number_of_iterations
        elif goals < over_under_line:
            under_prob += prob / number_of_iterations
        elif goals == over_under_line:
            push_prob += prob / number_of_iterations
    return [over_prob, under_prob, push_prob]


def convert_odds_to_fractional(odds):
    """convert American odds to fractional/decimal odds"""
    if float(odds) >= 0:
        fractional = odds/100
    elif float(odds) < 0:
        fractional = abs(100/odds)
    return fractional


def calculate_payout_potential(win_prob, loss_prob, win_odds, push_prob=None, push_possible=True):
    """calculate the likely payout based on probability of win and odds offered
    also return Kelly Criterion (optimal bet size as percentage of bankroll)"""
    if push_possible:
        payout_potential = (win_prob * win_odds) - loss_prob
        kelly = payout_potential / win_odds
    elif not push_possible:
        payout_potential = (win_prob * win_odds) - (loss_prob + push_prob)
        kelly = payout_potential / win_odds
    return [payout_potential, kelly]


def knn_predictions(training_file, test_data, test_columns):
    """get Known Nearest Neighbor predictions for all results"""
    # pull training and test data, convert headers to lower case and spaces to underscores
    training_data = pd.read_excel(training_file)
    test_data = pd.DataFrame(test_data, columns=test_columns)
    training_data.columns = [c.lower().replace(' ', '_') for c in training_data.columns]
    test_data.columns = [c.lower().replace(' ', '_') for c in test_data.columns]

    # set other reused variables
    gscv_param_grid = {'n_neighbors': np.arange(1, 25)}

    # FOR SPREAD RESULTS

    # convert payout to Win/Loss/Push
    training_data.loc[training_data.spread_payout > 0, 'spread_payout_wl'] = 'Win'
    training_data.loc[training_data.spread_payout < 0, 'spread_payout_wl'] = 'Loss'
    training_data.loc[training_data.ha_spread_payout > 0, 'ha_spread_payout_wl'] = 'Win'
    training_data.loc[training_data.ha_spread_payout < 0, 'ha_spread_payout_wl'] = 'Loss'

    # set columns to be used for predictions
    ovr_spread_prediction_columns = ['ht_spread', 'ht_xs', 'at_xs',
                                     'ht_spread_fract', 'at_spread_fract',
                                     'ht_spread_prob', 'at_spread_prob',
                                     'spread_home_win', 'spread_away_win',
                                     'kc_spread_home', 'kc_spread_away']
    ha_spread_prediction_columns = ['ht_spread', 'ht_xs', 'at_xs',
                                    'ht_spread_fract', 'at_spread_fract',
                                    'ha_ht_spread_prob', 'ha_at_spread_prob',
                                    'ha_spread_home_win', 'ha_spread_away_win',
                                    'ha_kc_spread_home', 'ha_kc_spread_away']

    # drop NaN rows separately from each set (ovr & ha)
    ovr_spread_training_data = training_data.drop(['ha_spread_payout_wl'], axis=1)
    ovr_spread_training_data.dropna(subset=['spread_payout_wl'], inplace=True)
    ha_spread_training_data = training_data.drop(['spread_payout_wl'], axis=1)
    ha_spread_training_data.dropna(subset=['ha_spread_payout_wl'], inplace=True)

    # preprocessing, scale values
    scaler = MinMaxScaler()
    scaled_ovr_spread_training_data = \
        scaler.fit_transform(ovr_spread_training_data[ovr_spread_prediction_columns])
    scaled_ha_spread_training_data = \
        scaler.fit_transform(ha_spread_training_data[ha_spread_prediction_columns])

    # split training data into x and y (x columns: HT Spread, HT Spread Prob, AT Spread Prob)
    spread_train_x_ovr = scaled_ovr_spread_training_data
    spread_train_y_ovr = ovr_spread_training_data['spread_payout_wl']
    spread_train_x_ha = scaled_ha_spread_training_data
    spread_train_y_ha = ha_spread_training_data['ha_spread_payout_wl']

    # find optimal k value
    ovr_spread_knn_gscv = GridSearchCV(KNeighborsClassifier(), gscv_param_grid, cv=5, iid=True)
    ovr_spread_knn_gscv.fit(spread_train_x_ovr, spread_train_y_ovr)
    ovr_spread_k = next(iter(ovr_spread_knn_gscv.best_params_.values()))
    ha_spread_knn_gscv = GridSearchCV(KNeighborsClassifier(), gscv_param_grid, cv=5, iid=True)
    ha_spread_knn_gscv.fit(spread_train_x_ha, spread_train_y_ha)
    ha_spread_k = next(iter(ha_spread_knn_gscv.best_params_.values()))

    # fit KNeighbors to training data
    knn_spread_ovr = KNeighborsClassifier(n_neighbors=ovr_spread_k)
    knn_spread_ovr.fit(spread_train_x_ovr, spread_train_y_ovr)
    knn_spread_ha = KNeighborsClassifier(n_neighbors=ha_spread_k)
    knn_spread_ha.fit(spread_train_x_ha, spread_train_y_ha)

    # print stats on wins/losses in training data
    print('\nDistribution of Spread Results in Overall Training Set, Optimal k=', ovr_spread_k)
    print(training_data.spread_payout_wl.value_counts()/training_data.spread_payout_wl.count())

    print('\nDistribution of Spread Results in Home/Away Training Set, Optimal k=', ha_spread_k)
    print(training_data.ha_spread_payout_wl.value_counts()/training_data.ha_spread_payout_wl.count())

    # get predictions for test set
    ovr_spread_pred = knn_spread_ovr.predict(test_data[ovr_spread_prediction_columns])
    ha_spread_pred = knn_spread_ha.predict(test_data[ha_spread_prediction_columns])

    # append predictions to test data
    test_data['ovr_spread_pred'] = ovr_spread_pred
    test_data['ha_spread_pred'] = ha_spread_pred

    # test data against itself using cross-validation - for output purposes only
    ovr_spread_cv_scores = cross_val_score(KNeighborsClassifier(n_neighbors=ovr_spread_k),
                                           spread_train_x_ovr, spread_train_y_ovr, cv=5)
    ha_spread_cv_scores = cross_val_score(KNeighborsClassifier(n_neighbors=ha_spread_k),
                                          spread_train_x_ha, spread_train_y_ha, cv=5)
    print('\nSpread Overall Mean Cross Validation Score: {}'.format(np.mean(ovr_spread_cv_scores)))
    print('\nSpread Home/Away Mean Cross Validation Score: {}'.format(np.mean(ha_spread_cv_scores)))

    # FOR OVER UNDER RESULTS

    # convert payout to Win/Loss/Push
    training_data.loc[training_data.over_under_payout > 0, 'over_under_payout_wl'] = 'Win'
    training_data.loc[training_data.over_under_payout < 0, 'over_under_payout_wl'] = 'Loss'
    training_data.loc[training_data.ha_over_under_payout > 0, 'ha_over_under_payout_wl'] = 'Win'
    training_data.loc[training_data.ha_over_under_payout < 0, 'ha_over_under_payout_wl'] = 'Loss'

    # set columns to be used for predictions
    ovr_ou_prediction_columns = ['over_under', 'ht_xs', 'at_xs',
                                 'over_fract', 'under_fract',
                                 'over_prob', 'under_prob',
                                 'over', 'under', 'kc_over', 'kc_under']
    ha_ou_prediction_columns = ['over_under', 'ht_xs', 'at_xs',
                                'over_fract', 'under_fract',
                                'ha_over_prob', 'ha_under_prob',
                                'ha_over', 'ha_under', 'ha_kc_over', 'ha_kc_under']

    # drop NaN rows separately from each set (ovr & ha)
    ovr_ou_training_data = training_data.drop(['ha_over_under_payout_wl'], axis=1)
    ovr_ou_training_data.dropna(subset=['over_under_payout_wl'], inplace=True)
    ha_ou_training_data = training_data.drop(['over_under_payout_wl'], axis=1)
    ha_ou_training_data.dropna(subset=['ha_over_under_payout_wl'], inplace=True)

    # preprocessing, scale values
    scaled_ovr_ou_training_data = \
        scaler.fit_transform(ovr_ou_training_data[ovr_spread_prediction_columns])
    scaled_ha_ou_training_data = \
        scaler.fit_transform(ha_ou_training_data[ha_spread_prediction_columns])

    # split training data into x and y (x columns: HT Spread, HT Over Prob, AT Under Prob)
    ou_train_x_ovr = scaled_ovr_ou_training_data
    ou_train_y_ovr = ovr_ou_training_data['over_under_payout_wl']
    ou_train_x_ha = scaled_ha_ou_training_data
    ou_train_y_ha = ha_ou_training_data['ha_over_under_payout_wl']

    # find optimal k value
    ovr_ou_knn_gscv = GridSearchCV(KNeighborsClassifier(), gscv_param_grid, cv=5, iid=True)
    ovr_ou_knn_gscv.fit(ou_train_x_ovr, ou_train_y_ovr)
    ovr_ou_k = next(iter(ovr_spread_knn_gscv.best_params_.values()))
    ha_ou_knn_gscv = GridSearchCV(KNeighborsClassifier(), gscv_param_grid, cv=5, iid=True)
    ha_ou_knn_gscv.fit(ou_train_x_ha, ou_train_y_ha)
    ha_ou_k = next(iter(ha_ou_knn_gscv.best_params_.values()))

    # fit KNeighbors to training data
    knn_ou_ovr = KNeighborsClassifier(n_neighbors=ovr_ou_k)
    knn_ou_ovr.fit(ou_train_x_ovr, ou_train_y_ovr)
    knn_ou_ha = KNeighborsClassifier(n_neighbors=ha_ou_k)
    knn_ou_ha.fit(ou_train_x_ha, ou_train_y_ha)

    # print stats on wins/losses in training data
    print('\nDistribution of Over Under Results in Overall Training Set, Optimal k=', ovr_ou_k)
    print(training_data.over_under_payout_wl.value_counts() /
          training_data.over_under_payout_wl.count())

    print('\nDistribution of Over Under Results in Home/Away Training Set, Optimal k=', ha_ou_k)
    print(training_data.ha_over_under_payout_wl.value_counts() /
          training_data.ha_over_under_payout_wl.count())

    # get predictions for test set
    ovr_ou_pred = knn_ou_ovr.predict(test_data[ovr_ou_prediction_columns])
    ha_ou_pred = knn_ou_ha.predict(test_data[ha_ou_prediction_columns])

    # test data against itself using cross-validation - for output purposes only
    ovr_ou_cv_scores = cross_val_score(KNeighborsClassifier(n_neighbors=ovr_ou_k),
                                       ou_train_x_ovr, ou_train_y_ovr, cv=5)
    ha_ou_cv_scores = cross_val_score(KNeighborsClassifier(n_neighbors=ha_ou_k),
                                      ou_train_x_ha, ou_train_y_ha, cv=5)
    print('\nOver/Under Overall Mean Cross Validation Score: {}'.format(np.mean(ovr_ou_cv_scores)))
    print('\nOver/Under Home/Away Mean Cross Validation Score: {}'.format(np.mean(ha_ou_cv_scores)))

    return [ovr_spread_pred, ha_spread_pred, ovr_ou_pred, ha_ou_pred]


"""Begin Analyzer Functions"""


def pull_scores(url, teams_list):
    r = render_page(url)
    soup = BeautifulSoup(r, 'html.parser')
    table = soup.find_all('div', id=lambda x: x and x.startswith('g_1_'))

    my_list = []
    for item in table:
        my_list.append(item.text)

    split_list = []
    for item in my_list:
        item = item.replace(u'\xa0', u' ')
        split_list.append(item.split(' '))

    team_dict = {}
    team_dict_rev = {}
    reg_team_dict = {}
    for team in teams_list:
        team_dict[team[1]] = team[1].replace(' ', '')
        team_dict_rev[team[1].replace(' ', '')] = team[1]
        reg_team_dict[team[1]] = team[0]

    for item in split_list:
        item[1] = item[1][5:]

        if len(item) == 8:
            item[1] = item[1] + item[2]
            item[4] = item[4] + item[5]
            item.remove(item[5])
            item.remove(item[2])
        elif len(item) == 7:
            if item[4][0].isupper():
                item[3] = item[3] + item[4]
                item.remove(item[4])
            else:
                item[1] = item[1] + item[2]
                item.remove(item[2])
        item.remove(item[2])

        for team in team_dict.values():
            if team in item[1]:
                if item[1][0:len(team)] == team:
                    item.insert(1, team)
                    item[2] = item[2].replace(team, '')
        for team in team_dict.values():
            if team in item[3]:
                if item[3][1:len(team) + 1] == team:
                    item.insert(3, item[3][0])
                else:
                    item.insert(3, item[3][0:2])
                item.insert(2, team)
        item.remove(item[7])
        item.remove(item[6])
        item.remove(item[5])

        item[1] = team_dict_rev[item[1]]
        item[1] = reg_team_dict[item[1]]
        item[2] = team_dict_rev[item[2]]
        item[2] = reg_team_dict[item[2]]
        item[0] = item[0][3:5] + '/' + item[0][0:2]

    return split_list


# set column indices
ht_line = 3
over_under_line = 8
ht_spread_fract = 11
at_spread_fract = 12
ht_out_fract = 13
at_out_fract = 14
over_fract = 15
under_fract = 16
ht_score = 73
at_score = 74
kc_spread_home = 34
kc_spread_away = 35
kc_outright_home = 36
kc_outright_away = 37
kc_over = 38
kc_under = 39
spread_pick = 40
outright_pick = 41
over_under_pick = 42


def get_winners(row):
    """return winner of each bet (spread, outright, over/under"""
    # spread winner
    if float(row[ht_score]) + float(row[ht_line]) > float(row[at_score]):
        spread_winner = 'HT'
        if float(row[ht_line]) < 0:
            fav_dog = 'Fav'
        elif float(row[ht_line]) > 0:
            fav_dog = 'Dog'
        else:
            fav_dog = 'No Line'
    elif float(row[ht_score]) + float(row[ht_line]) < float(row[at_score]):
        spread_winner = 'AT'
        if float(row[ht_line]) < 0:
            fav_dog = 'Dog'
        elif float(row[ht_line]) > 0:
            fav_dog = 'Fav'
        else:
            fav_dog = 'No Line'
    else:
        spread_winner = 'Push'
        fav_dog = 'Push'

    # outright winner
    if float(row[ht_score]) > float(row[at_score]):
        outright_winner = 'HT'
    elif float(row[ht_score]) < float(row[at_score]):
        outright_winner = 'AT'
    else:
        outright_winner = 'Draw'

    # over/under winner
    if float(row[ht_score]) + float(row[at_score]) > float(row[over_under_line]):
        over_under_winner = 'Over'
    elif float(row[ht_score]) + float(row[at_score]) < float(row[over_under_line]):
        over_under_winner = 'Under'
    else:
        over_under_winner = 'Push'

    return [spread_winner, outright_winner, over_under_winner, fav_dog]


def get_spread_pick(row, x=0):
    if float(row[kc_spread_home + x]) <= 0 and float(row[kc_spread_away + x]) <= 0:
        spread_pick = 'No Pick'
    elif float(row[kc_spread_home + x]) > float(row[kc_spread_away + x]):
        spread_pick = 'HT'
    elif float(row[kc_spread_home + x]) < float(row[kc_spread_away + x]):
        spread_pick = 'AT'
    else:
        spread_pick = 'Pick Both'
    return spread_pick


def get_outright_pick(row, x=0):
    if float(row[kc_outright_home + x]) <=0 and float(row[kc_outright_away + x]) <= 0:
        outright_pick = 'No Pick'
    elif float(row[kc_outright_home + x]) > float(row[kc_outright_away + x]):
        outright_pick = 'HT'
    elif float(row[kc_outright_home + x]) < float(row[kc_outright_away + x]):
        outright_pick = 'AT'
    else:
        outright_pick = 'Pick Both'
    return outright_pick


def get_over_under_pick(row, x=0):
    if float(row[kc_over + x]) <= 0 and float(row[kc_under + x]) <= 0:
        over_under_pick = 'No Pick'
    elif float(row[kc_over + x]) > float(row[kc_under + x]):
        over_under_pick = 'Over'
    elif float(row[kc_over + x]) < float(row[kc_under + x]):
        over_under_pick = 'Under'
    else:
        over_under_pick = 'Pick Both'
    return over_under_pick


def get_picks(row, overall=True):
    """return picks based on highest kelly coefficient"""
    if overall:
        spread_pick = get_spread_pick(row)
        outright_pick = get_outright_pick(row)
        over_under_pick = get_over_under_pick(row)
    else:
        spread_pick = get_spread_pick(row, x=26)
        outright_pick = get_outright_pick(row, x=26)
        over_under_pick = get_over_under_pick(row, x=26)

    return [spread_pick, outright_pick, over_under_pick]


def get_spread_payout(row, spread_winner, x=0):
    if row[spread_pick + x] == 'No Pick' or row[spread_pick + x] == 'Pick Both':
        spread_payout = ''
    elif spread_winner == 'Push':
        spread_payout = 0
    elif spread_winner == row[spread_pick + x]:
        if spread_winner == 'HT':
            spread_payout = round(float(row[ht_spread_fract]), 2)
        elif spread_winner == 'AT':
            spread_payout = round(float(row[at_spread_fract]), 2)
    else:
        spread_payout = -1
    return spread_payout


def get_outright_payout(row, outright_winner, x=0):
    if row[outright_pick + x] == 'No Pick' or row[spread_pick + x] == 'Pick Both':
        outright_payout = ''
    elif outright_winner == row[outright_pick + x]:
        if outright_winner == 'HT':
            outright_payout = round(float(row[ht_out_fract]), 2)
        elif outright_winner == 'AT':
            outright_payout = round(float(row[at_out_fract]), 2)
    else:
        outright_payout = -1
    return outright_payout


def get_over_under_payout(row, over_under_winner, x=0):
    if row[over_under_pick + x] == 'No Pick' or row[over_under_pick + x] == 'Pick Both':
        over_under_payout = ''
    elif over_under_winner == 'Push':
        over_under_payout = 0
    elif over_under_winner == row[over_under_pick + x]:
        if over_under_winner == 'Over':
            over_under_payout = round(float(row[over_fract]), 2)
        elif over_under_winner == 'Under':
            over_under_payout = round(float(row[under_fract]), 2)
    else:
        over_under_payout = -1
    return over_under_payout


def get_payouts(row, spread_winner, outright_winner, over_under_winner, overall=True):
    if overall:
        spread_payout = get_spread_payout(row, spread_winner)
        outright_payout = get_outright_payout(row, outright_winner)
        over_under_payout = get_over_under_payout(row, over_under_winner)
    else:
        spread_payout = get_spread_payout(row, spread_winner, x=26)
        outright_payout = get_outright_payout(row, outright_winner, x=26)
        over_under_payout = get_over_under_payout(row, over_under_winner, x=26)

    return [spread_payout, outright_payout, over_under_payout]


def knn_accuracy_score(test_data_with_results):
    """return an accuracy percentage based on predictions vs results"""
    # copy data and manipulate to match columns and remove unneeded outright columns
    test_data_test = test_data_with_results[:]
    for row in test_data_test:
        del row[84]
        del row[81]
        row.insert(81, row[82])
        del row[83]
    for row in test_data_test:
        wl_columns = [80, 81, 82, 83]
        for col in wl_columns:
            if row[col] != '':
                row[col] = float(row[col])
            if row[col] == '' or row[col] == 0:
                row.append('n/a')
            elif row[col] > 0:
                row.append('Win')
            elif row[col] < 0:
                row.append('Loss')

    # get accuracy percentage for each prediction
    columns = [[84, 'ovr_spr'], [85, 'ha_spr'], [86, 'ovr_ou'], [87, 'ha_ou']]
    for column in columns:
        correct_pred = 0
        total = 0
        for row in test_data_test:
            if row[column[0]] != 'n/a':
                if row[column[0]] == row[column[0] - 15]:
                    correct_pred += 1
                total += 1
        column.append(correct_pred / total)

    # get payout differential if only betting predicted wins
    for column in columns:
        predicted_payout = 0
        actual_payout = 0
        for row in test_data_test:
            if row[column[0] - 4] != '':
                if row[column[0] - 15] == "Win":
                    predicted_payout += row[column[0] - 4]
                actual_payout += row[column[0] - 4]
        column.append(predicted_payout - actual_payout)

    # append accuracy scores and predicted payout differentials to dictionary
    scores_list = {}
    for column in columns:
        scores_list[column[1]] = [column[2], column[3]]

    for key, value in scores_list.items():
        print('\n' + key + ' accuracy score = ' + str(round(value[0] * 100, 2)) + '%')
        print('\tPayout Differential = ' + str(value[1]))
