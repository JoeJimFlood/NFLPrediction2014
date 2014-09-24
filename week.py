import pandas as pd
import matchup
import xlsxwriter
import xlautofit
import xlrd
import sys
import time
import collections
import os

week_timer = time.time()

week_number = 4

matchups = collections.OrderedDict()
matchups['Thursday Night'] = [('WAS', 'NYG')]
matchups['Sunday Morning'] = [('CHI', 'GB'),
                              ('HOU', 'BUF'),
                              ('IND', 'TEN'),
                              ('BAL', 'CAR'),
                              ('NYJ', 'DET'),
                              ('PIT', 'TB'),
                              ('OAK', 'MIA')]
matchups['Sunday Afternoon'] = [('SD', 'JAX'),
                                ('SF', 'PHI'),
                                ('MIN', 'ATL')]
matchups['Sunday Night'] = [('DAL', 'NO')]
matchups['Monday Night'] = [('KC', 'NE')]

location = os.getcwd().replace('\\', '/')
output_file = location + '/Weekly Forecasts/Week' + str(week_number) + '.xlsx'

for read_data in range(2):

    week_book = xlsxwriter.Workbook(output_file)
    header_format = week_book.add_format({'align': 'center', 'bold': True, 'bottom': True})
    index_format = week_book.add_format({'align': 'right', 'bold': True})
    score_format = week_book.add_format({'num_format': '#0', 'align': 'right'})
    percent_format = week_book.add_format({'num_format': '#0%', 'align': 'right'})


    if read_data:
        colwidths = xlautofit.even_widths_single_index(output_file)

    for game_time in matchups:
        if read_data:
            data_book = xlrd.open_workbook(output_file)
            data_sheet = data_book.sheet_by_name(game_time)
        sheet = week_book.add_worksheet(game_time)
        sheet.write_string(1, 0, 'Chance of Winning', index_format)
        sheet.write_string(2, 0, 'Expected Score', index_format)
        sheet.write_string(3, 0, '2.5th Percentile Score', index_format)
        sheet.write_string(4, 0, '10th Percentile Score', index_format)
        sheet.write_string(5, 0, '25th Percentile Score', index_format)
        sheet.write_string(6, 0, '50th Percentile Score', index_format)
        sheet.write_string(7, 0, '75th Percentile Score', index_format)
        sheet.write_string(8, 0, '90th Percentile Score', index_format)
        sheet.write_string(9, 0, '97.5th Percentile score', index_format)
        sheet.freeze_panes(0, 1)
        games = matchups[game_time]
        for i in range(len(games)):
            home = games[i][0]
            away = games[i][1]
            homecol = 3 * i + 1
            awaycol = 3 * i + 2
            sheet.write_string(0, homecol, home, header_format)
            sheet.write_string(0, awaycol, away, header_format)
            if read_data:
                sheet.write_number(1, homecol, data_sheet.cell(1, homecol).value, percent_format)
                sheet.write_number(1, awaycol, data_sheet.cell(1, awaycol).value, percent_format)
                for rownum in range(2, 10):
                    sheet.write_number(rownum, homecol, data_sheet.cell(rownum, homecol).value, score_format)
                    sheet.write_number(rownum, awaycol, data_sheet.cell(rownum, awaycol).value, score_format)
            else:
                results = matchup.matchup(home, away)
                probwin = results['ProbWin']
                sheet.write_number(1, homecol, probwin[home], percent_format)
                sheet.write_number(1, awaycol, probwin[away], percent_format)
                home_dist = results['Scores'][home]
                away_dist = results['Scores'][away]
                sheet.write_number(2, homecol, home_dist['mean'], score_format)
                sheet.write_number(2, awaycol, away_dist['mean'], score_format)
                sheet.write_number(3, homecol, home_dist['2.5%'], score_format)
                sheet.write_number(3, awaycol, away_dist['2.5%'], score_format)
                sheet.write_number(4, homecol, home_dist['10%'], score_format)
                sheet.write_number(4, awaycol, away_dist['10%'], score_format)
                sheet.write_number(5, homecol, home_dist['25%'], score_format)
                sheet.write_number(5, awaycol, away_dist['25%'], score_format)
                sheet.write_number(6, homecol, home_dist['50%'], score_format)
                sheet.write_number(6, awaycol, away_dist['50%'], score_format)
                sheet.write_number(7, homecol, home_dist['75%'], score_format)
                sheet.write_number(7, awaycol, away_dist['75%'], score_format)
                sheet.write_number(8, homecol, home_dist['90%'], score_format)
                sheet.write_number(8, awaycol, away_dist['90%'], score_format)
                sheet.write_number(9, homecol, home_dist['97.5%'], score_format)
                sheet.write_number(9, awaycol, away_dist['97.5%'], score_format)
            if i != len(games) - 1:
                sheet.write_string(0, 3 * i + 3, ' ')
            if read_data:
                for colnum in range(sheet.dim_colmax):
                    sheet.set_column(colnum, colnum, colwidths[sheet.name][colnum])

    week_book.close()

print('Week ' + str(week_number) + ' predictions calculated in ' + str(round((time.time() - week_timer) / 60, 2)) + ' minutes')