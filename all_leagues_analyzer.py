import soccer_data_pull_functions as sf
from time import time
from openpyxl import load_workbook
from datetime import datetime


start_time = time()


# grab variables from functions file
current_week = sf.current_week
stats_file = 'Soccer Betting Sheet - ' + current_week + '.csv'

# grab data from workbook
fields, rows = sf.pull_csv_data(stats_file)

# add new fields
fields.extend(['ht_score', 'at_score', 'league', 'Spread Winner', 'Fav/Dog',
               'Outright Winner', 'Over Under Winner', 'Spread Payout',
               'Outright Payout', 'Over Under Payout', 'ha_Spread Payout',
               'ha_Outright Payout', 'ha_Over Under Payout'])

# append scores to matches
leagues = sf.leagues
teams_list = sf.team_list
all_scores = []
for num in range(0, len(leagues)):
    scoreboard_url = 'https://www.scoreboard.com/en/soccer/' + leagues[num][3]
    scores = sf.pull_scores(scoreboard_url, teams_list)
    for score in scores:
        score.append(leagues[num][0])
        all_scores.append(score)

for row in rows:
    print(row[1], row[2])
    date_string = datetime.strptime(row[0], '%m/%d/%y').date().strftime('%m/%d')
    for game in all_scores:
        if date_string == game[0] and row[1] == game[1] and row[2] == game[2]:
            print(game)
            row.append(game[3])
            row.append(game[4])
            row.append(game[5])

# remove rows of games not yet played
rows = [row for row in rows if len(row) == 76]

# loop through all rows and append winners, picks and payouts
for row in rows:
    spread_winner, outright_winner, over_under_winner, fav_dog = sf.get_winners(row)
    spread_payout, outright_payout, over_under_payout = sf.get_payouts(row, spread_winner,
                                                                       outright_winner,
                                                                       over_under_winner)
    ha_spread_payout, ha_outright_payout, ha_over_under_payout = sf.get_payouts(row, spread_winner,
                                                                                outright_winner,
                                                                                over_under_winner,
                                                                                overall=False)

    row.extend([spread_winner, fav_dog, outright_winner, over_under_winner,
                spread_payout, outright_payout, over_under_payout,
                ha_spread_payout, ha_outright_payout, ha_over_under_payout])


# append data to output file (confirm write to file first)
output_file = sf.knn_training_file
wb = load_workbook(output_file)
sheet = wb.worksheets[0]

# ATTN: only use code below only if you need to add headers to a new sheet
#sheet.append(fields)


for row in rows:
    sheet.append(row)
    print(row)
wb.save(output_file)

# print accuracy scores and payout differential on knn predictions
sf.knn_accuracy_score(rows)


print("\nThe program took " + str(round(time() - start_time, 2)) + " seconds to run.")
