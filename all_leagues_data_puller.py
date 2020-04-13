import soccer_data_pull_functions as esf
import epl_analyzer_functions as eaf
import csv
import os.path
import sys
from time import time
from unidecode import unidecode


start_time = time()

# set static variables
expected_stat_columns = [9, 10, 11]
odds_range = [4, 5, 6, 7, 9, 10]
current_week = esf.current_week
leagues = esf.leagues


# check for existing gameweek file, exit if true
output_file = 'Soccer Betting Sheet - ' + current_week + '.csv'
if os.path.exists(output_file):
    sys.exit("This week's betting file already exists")

all_league_game_lines = []
for num in range(0, len(leagues)):
    league = leagues[num][0]
    bovada_league = leagues[num][1]
    num_teams = leagues[num][2]
    print(league, bovada_league)

    # use this one for pulling directly from understat.com
    usurl = 'https://understat.com/league/' + league
    rows = esf.understat_pull(usurl, filter='1', combined_stat_columns=expected_stat_columns,
                              num_teams=num_teams)
    home_rows = esf.understat_pull(usurl, filter='2', combined_stat_columns=expected_stat_columns,
                                   num_teams=num_teams)
    away_rows = esf.understat_pull(usurl, filter='3', combined_stat_columns=expected_stat_columns,
                                   num_teams=num_teams)

    # use this one to pull data directly from the web
    url = 'https://www.bovada.lv/sports/soccer/' + bovada_league
    game_lines = esf.improved_bovada_pull(url, esf.team_list)
    """
    # use this one to pull data from csv file
    fields, game_lines = esf.pull_csv_data('bovada_odds.csv')
    """

    # convert all odds to fractionals
    for row in game_lines:
        if len(row) != 11:
            game_lines.remove(row)

    for row in game_lines:
        for column in odds_range:
            fractional = esf.convert_odds_to_fractional(float(row[column]))
            row.append(fractional)

    # loop through each row in bovada odds and append fractionals and payout potentials
    for row in game_lines:
        avg_stat_columns = [12, 13, 14]
        row[1] = home_team = unidecode(row[1])
        row[2] = away_team = unidecode(row[2])
        ht_spread_fract = row[11]
        at_spread_fract = row[12]
        ht_out_fract = row[13]
        at_out_fract = row[14]
        over_fract = row[15]
        under_fract = row[16]

        # find expected goals in this match for each team
        print(home_team, away_team)
        xs_home_team, xs_away_team = esf.get_xg_stats(rows, rows,
                                                      home_team, away_team, avg_stat_columns)
        ha_xs_home_team, ha_xs_away_team = esf.get_xg_stats(home_rows, away_rows,
                                                            home_team, away_team, avg_stat_columns)

        # create poisson distributions for xG
        home_team_poisson = esf.poissonate(xs_home_team)
        away_team_poisson = esf.poissonate(xs_away_team)
        ha_home_team_poisson = esf.poissonate(ha_xs_home_team)
        ha_away_team_poisson = esf.poissonate(ha_xs_away_team)

        # zip poisson results into list of possible scores, calculate result and total goals
        results_dict, total_goals_dict = esf.zip_scores(home_team_poisson, away_team_poisson)
        ha_results_dict, ha_total_goals_dict = esf.zip_scores(ha_home_team_poisson, ha_away_team_poisson)

        # get game line variable from bovada stats
        home_team_line, over_under_line = esf.get_bovada_info(game_lines, home_team, away_team)

        # find probability of spread result
        spread_home_win_prob, spread_away_win_prob, spread_push_prob = \
            esf.get_spread_result_probabilities(results_dict, home_team_line)
        ha_spread_home_win_prob, ha_spread_away_win_prob, ha_spread_push_prob = \
            esf.get_spread_result_probabilities(ha_results_dict, home_team_line)

        # find probability of outright result
        home_win_prob, away_win_prob, draw_prob = \
            esf.get_outright_result_probabilities(results_dict)
        ha_home_win_prob, ha_away_win_prob, ha_draw_prob = \
            esf.get_outright_result_probabilities(ha_results_dict)

        # find probability of total goals beating over/under line
        over_prob, under_prob, push_prob = \
            esf.get_over_under_probabilities(total_goals_dict, over_under_line)
        ha_over_prob, ha_under_prob, ha_push_prob = \
            esf.get_over_under_probabilities(ha_total_goals_dict, over_under_line)

        # find payout potential and optimal bet as percentage of bankroll for each result
        # overall
        spread_home_pp, spread_home_kelly = esf.calculate_payout_potential(spread_home_win_prob,
                                                                           spread_away_win_prob,
                                                                           ht_spread_fract)
        spread_away_pp, spread_away_kelly = esf.calculate_payout_potential(spread_away_win_prob,
                                                                           spread_home_win_prob,
                                                                           at_spread_fract)
        out_home_pp, out_home_kelly = esf.calculate_payout_potential(home_win_prob, away_win_prob,
                                                                     ht_out_fract, push_prob=draw_prob,
                                                                     push_possible=False)
        out_away_pp, out_away_kelly = esf.calculate_payout_potential(away_win_prob, home_win_prob,
                                                                     at_out_fract, push_prob=draw_prob,
                                                                     push_possible=False)
        over_pp, over_kelly = esf.calculate_payout_potential(over_prob, under_prob, over_fract)
        under_pp, under_kelly = esf.calculate_payout_potential(under_prob, over_prob, under_fract)

        # home/away
        ha_spread_home_pp, ha_spread_home_kelly = esf.calculate_payout_potential(ha_spread_home_win_prob,
                                                                                 ha_spread_away_win_prob,
                                                                                 ht_spread_fract)
        ha_spread_away_pp, ha_spread_away_kelly = esf.calculate_payout_potential(ha_spread_away_win_prob,
                                                                                 ha_spread_home_win_prob,
                                                                                 at_spread_fract)
        ha_out_home_pp, ha_out_home_kelly = esf.calculate_payout_potential(ha_home_win_prob,
                                                                           ha_away_win_prob,
                                                                           ht_out_fract, push_prob=draw_prob,
                                                                           push_possible=False)
        ha_out_away_pp, ha_out_away_kelly = esf.calculate_payout_potential(ha_away_win_prob,
                                                                           ha_home_win_prob,
                                                                           at_out_fract, push_prob=draw_prob,
                                                                           push_possible=False)
        ha_over_pp, ha_over_kelly = esf.calculate_payout_potential(ha_over_prob, ha_under_prob, over_fract)
        ha_under_pp, ha_under_kelly = esf.calculate_payout_potential(ha_under_prob, ha_over_prob, under_fract)

        # append overall columns
        row.extend([xs_home_team, xs_away_team, spread_home_win_prob, spread_away_win_prob,
                    spread_push_prob, home_win_prob, away_win_prob, draw_prob, over_prob, under_prob,
                    push_prob, spread_home_pp, spread_away_pp, out_home_pp, out_away_pp, over_pp, under_pp,
                    spread_home_kelly, spread_away_kelly, out_home_kelly, out_away_kelly,
                    over_kelly, under_kelly])

        # get picks for overall stats, append to row
        spread_pick, outright_pick, over_under_pick = eaf.get_picks(row)
        row.extend([spread_pick, outright_pick, over_under_pick])

        # append home/away columns
        row.extend([ha_xs_home_team, ha_xs_away_team, ha_spread_home_win_prob, ha_spread_away_win_prob,
                    ha_spread_push_prob, ha_home_win_prob, ha_away_win_prob, ha_draw_prob, ha_over_prob,
                    ha_under_prob, ha_push_prob, ha_spread_home_pp, ha_spread_away_pp, ha_out_home_pp,
                    ha_out_away_pp, ha_over_pp, ha_under_pp, ha_spread_home_kelly, ha_spread_away_kelly,
                    ha_out_home_kelly, ha_out_away_kelly, ha_over_kelly, ha_under_kelly])

        # get picks for home/away stats, append to row
        ha_spread_pick, ha_outright_pick, ha_over_under_pick = eaf.get_picks(row, overall=False)
        row.extend([ha_spread_pick, ha_outright_pick, ha_over_under_pick])

        # append row to main sheet
        all_league_game_lines.append(row)


# create extra header lists
fields1 = ['Date', 'Home Team', 'Away Team', 'HT Spread', 'HT Spread Odds', 'AT Spread Odds',
           'HT Outright Odds', 'AT Outright Odds', 'Over Under', 'Over Odds', 'Under Odds']
fractional_headers = ['HT Spread Fract', 'AT Spread Fract',
                      'HT Out Fract', 'AT Out Fract',
                      'Over Fract', 'Under Fract']
stats_headers = ['HT xs', 'AT xs',
                 'HT Spread Prob', 'AT Spread Prob', 'Spread Push Prob',
                 'HT Out Prob', 'AT Out Prob', 'Draw Prob',
                 'Over Prob', 'Under Prob', 'OU Push Prob']
bet_options = ['Spread Home Win', 'Spread Away Win',
               'Outright Home Win', 'Outright Away Win',
               'Over', 'Under',
               'kc Spread Home', 'kc Spread Away',
               'kc Out Home', 'kc Out Away',
               'kc Over', 'kc Under',
               'Spread Pick', 'Outright Pick', 'Over Under Pick']

# create header list for home/away stats
ha_stats_headers = []
for item in stats_headers:
    item = 'ha_' + item
    ha_stats_headers.append(item)
ha_bet_options = []
for item in bet_options:
    item = 'ha_' + item
    ha_bet_options.append(item)

# append lists to fields1
for item in fractional_headers:
    fields1.append(item)
for item in stats_headers:
    fields1.append(item)
for item in bet_options:
    fields1.append(item)
for item in ha_stats_headers:
    fields1.append(item)
for item in ha_bet_options:
    fields1.append(item)

# append knn results to game lines
ovr_spread_pred, ha_spread_pred, ovr_ou_pred, ha_ou_pred = \
    esf.knn_predictions(esf.knn_training_file, all_league_game_lines, fields1)
zip_predictions = list(zip(ovr_spread_pred, ha_spread_pred, ovr_ou_pred, ha_ou_pred))
x = 0
while x < len(zip_predictions):
    for row in all_league_game_lines:
        row.extend([zip_predictions[x][0], zip_predictions[x][1],
                   zip_predictions[x][2], zip_predictions[x][3]])
        x += 1

# append prediction headers to fields1
fields1.extend(['ovr_spread_pred', 'ha_spread_pred', 'ovr_ou_pred', 'ha_ou_pred'])

# add field names to game_lines
all_league_game_lines.insert(0, fields1)

# output game_lines to csv for betting and import by epl_analyzer
with open(output_file, 'w',  newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(all_league_game_lines)

print('\nThe script took ' + str(round(time() - start_time, 2)) + ' seconds to run.')
