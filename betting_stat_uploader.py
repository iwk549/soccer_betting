import betting_stat_functions as bsf
import betting_html_bases as prehtml
from datetime import datetime
from uid_pw import user_id, password


understat_url_base = 'https://understat.com/league/'
league_list = bsf.soccer_league_list
team_list = bsf.team_list
results_file = r'C:\Users\kendalli\PycharmProjects\epl_betting\All Soccer Results.xlsx'

stats_dict = bsf.understat_pull(understat_url_base, league_list, team_list)
updated_date = datetime.now().strftime('%d %B, %Y')

for league in league_list:
    league_name_upper = league[4]
    league_name_short = league[0]
    league_name_under = league[4].lower().replace(' ', '_')
    dump_file = r'C:\Users\kendalli\Desktop\PFiles\dosshouse.us\soccer_betting_'
    print('\n',league_name_under)
    stats_html_tables = bsf.create_stat_table_html(league_name_upper, stats_dict)
    html_stats = prehtml.stats_page_base + stats_html_tables + prehtml.stats_page_after_tables + updated_date + \
        prehtml.stats_page_script
    bsf.dump_and_upload(league_name_under, dump_file + league_name_under + '_stats.html',
                       html_stats, 'stats', user_id, password)

    results_dict = bsf.get_results(league_name_short, results_file)
    archived_odds_table = bsf.create_archived_odds_html(results_dict, league_name_upper)
    html_archived_odds = prehtml.archive_page_base + archived_odds_table + prehtml.archive_page_after_tables + \
        updated_date + prehtml.archive_page_script
    bsf.dump_and_upload(league_name_under, dump_file + league_name_under + '_archived_odds.html',
                        html_archived_odds, 'archived_bets', user_id, password)
