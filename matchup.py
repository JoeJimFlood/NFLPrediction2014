import os
import sys
import pandas as pd
import numpy as np
from numpy.random import poisson, uniform
from numpy import mean
import time
import math

po = True

teamsheetpath = sys.path[0] + '/teamcsvs/'

compstat = {'TDF': 'TDA', 'TDA': 'TDF', #Dictionary to use to compare team stats with opponent stats
            'FGF': 'FGA', 'FGA': 'FGF',
            'SFF': 'SFA', 'SFA': 'SFF',
            'PAT1%F': 'PAT1%A', 'PAT1%A': 'PAT1%F',
            'PAT2%F': 'PAT2%A', 'PAT2%A': 'PAT2%F'}

def get_opponent_stats(opponent): #Gets summaries of statistics for opponent each week
    opponent_stats = {}
    global teamsheetpath
    opp_stats = pd.DataFrame.from_csv(teamsheetpath + opponent + '.csv')
    for stat in opp_stats.columns:
        if stat in ['TDF', 'FGF', 'SFF', 'TDA', 'FGA', 'SFA']:
            opponent_stats.update({stat: opp_stats[stat].mean()})
    try:
        opponent_stats.update({'PAT1%F': float(opp_stats['PAT1FS'].sum()) / opp_stats['PAT1FA'].sum()})
    except ZeroDivisionError:
        opponent_stats.update({'PAT1%F': .99})
    try:
        opponent_stats.update({'PAT2%F': float(opp_stats['PAT2FS'].sum()) / opp_stats['PAT2FA'].sum()})
    except ZeroDivisionError:
        opponent_stats.update({'PAT2%F': .5})
    try:
        opponent_stats.update({'PAT1%A': float(opp_stats['PAT1AS'].sum()) / opp_stats['PAT1AA'].sum()})
    except ZeroDivisionError:
        opponent_stats.update({'PAT1%A': .99})
    try:
        opponent_stats.update({'PAT2%A': float(opp_stats['PAT2AS'].sum()) / opp_stats['PAT2AA'].sum()})
    except ZeroDivisionError:
        opponent_stats.update({'PAT2%A': .5})
    return opponent_stats

def get_residual_performance(team): #Get how each team has done compared to the average performance of their opponents
    global teamsheetpath
    score_df = pd.DataFrame.from_csv(teamsheetpath + team + '.csv')
    residual_stats = {}
    score_df['PAT1%F'] = np.nan
    score_df['PAT2%F'] = np.nan
    score_df['PAT1%A'] = np.nan
    score_df['PAT2%A'] = np.nan
    for week in score_df.index:
        try:
            score_df['PAT1%F'][week] = float(score_df['PAT1FS'][week]) / score_df['PAT1FA'][week]
        except ZeroDivisionError:
            score_df['PAT1%F'][week] = 0.99
        #print ('For: ' + str(score_df['PAT1%F'][week]))
        try:
            score_df['PAT2%F'][week] = float(score_df['PAT2FS'][week]) / score_df['PAT2FA'][week]
        except ZeroDivisionError:
            score_df['PAT2%F'][week] = 0.5
        try:
            score_df['PAT1%A'][week] = float(score_df['PAT1AS'][week]) / score_df['PAT1AA'][week]
        except ZeroDivisionError:
            score_df['PAT1%A'][week] = 0.99
        #print ('Against: ' + str(score_df['PAT1%F'][week]))
        try:
            score_df['PAT2%A'][week] = float(score_df['PAT2AS'][week]) / score_df['PAT2AA'][week]
        except ZeroDivisionError:
            score_df['PAT2%A'][week] = 0.5
        opponent_stats = get_opponent_stats(score_df['OPP'][week])
        for stat in opponent_stats:
            if week == 1:
                score_df['OPP_' + stat] = np.nan       
            score_df['OPP_' + stat][week] = opponent_stats[stat]           
    for stat in opponent_stats:
        score_df['R_' + stat] = score_df[stat] - score_df['OPP_' + compstat[stat]]
        if stat in ['TDF', 'FGF', 'SFF', 'TDA', 'FGA', 'SFA']:
            residual_stats.update({stat: score_df['R_' + stat].mean()})
        elif stat == 'PAT1%F':
            residual_stats.update({stat: (score_df['R_PAT1%F'].multiply(score_df['PAT1FA'])).sum() / score_df['PAT1FA'].sum()})
        elif stat == 'PAT2%F':
            residual_stats.update({stat: (score_df['R_PAT2%F'].multiply(score_df['PAT2FA'])).sum() / score_df['PAT2FA'].sum()})
        elif stat == 'PAT1%A':
            residual_stats.update({stat: (score_df['R_PAT1%A'].multiply(score_df['PAT1AA'])).sum() / score_df['PAT1AA'].sum()})
        elif stat == 'PAT2%A':
            residual_stats.update({stat: (score_df['R_PAT2%A'].multiply(score_df['PAT2AA'])).sum() / score_df['PAT2AA'].sum()})
        try:
            residual_stats.update({'GOFOR2': float(score_df['PAT2FA'].sum()) / score_df['TDF'].sum()})
        except ZeroDivisionError:
            residual_stats.update({'GOFOR2': .1})
    #print team
    #print residual_stats
    return residual_stats

def get_score(expected_scores): #Get the score for a team based on expected scores
    score = 0
    if expected_scores['TD'] > 0:
        tds = poisson(expected_scores['TD'])
    else:
        tds = poisson(0.01)
    score = score + 6 * tds
    if expected_scores['FG'] > 0:
        fgs = poisson(expected_scores['FG'])
    else:
        fgs = poisson(0.01)
    score = score + 3 * fgs
    if expected_scores['S'] > 0:
        sfs = poisson(expected_scores['S'])
    else:
        sfs = poisson(0.01)
    score = score + 2 * sfs
    for td in range(tds):
        go_for_2_determinant = uniform(0, 1)
        if go_for_2_determinant <= expected_scores['GOFOR2']: #Going for 2
            successful_pat_determinant = uniform(0, 1)
            if successful_pat_determinant <= expected_scores['PAT2PROB']:
                score = score + 2
            else:
                continue
        else: #Going for 1
            #print(expected_scores['PAT1PROB'])
            successful_pat_determinant = uniform(0, 1)
            if successful_pat_determinant <= expected_scores['PAT1PROB']:
                score = score + 1
            else:
                continue
    return score

def game(team_1, team_2,
         expected_scores_1, expected_scores_2,
         playoff): #Get two scores and determine a winner
    score_1 = get_score(expected_scores_1)
    score_2 = get_score(expected_scores_2)
    if score_1 > score_2:
        win_1 = 1
        win_2 = 0
        draw_1 = 0
        draw_2 = 0
    elif score_2 > score_1:
        win_1 = 0
        win_2 = 1
        draw_1 = 0
        draw_2 = 0
    else:
        if playoff:
            win_1 = 0.5
            win_2 = 0.5
            draw_1 = 0
            draw_2 = 0
        else:
            win_1 = 0
            win_2 = 0
            draw_1 = 1
            draw_2 = 1
    summary = {team_1: [win_1, draw_1, score_1]}
    summary.update({team_2: [win_2, draw_2, score_2]})
    return summary

def get_expected_scores(team_1_stats, team_2_stats, team_1_df, team_2_df): #Get the expected scores for a matchup based on the previous teams' performances
    expected_scores = {}
    for stat in team_1_stats:
        expected_scores.update({'TD': mean([team_1_stats['TDF'] + team_2_df['TDA'].mean(),
                                            team_2_stats['TDA'] + team_1_df['TDF'].mean()])})
        expected_scores.update({'FG': mean([team_1_stats['FGF'] + team_2_df['FGA'].mean(),
                                            team_2_stats['FGA'] + team_1_df['FGF'].mean()])})
        expected_scores.update({'S': mean([team_1_stats['SFF'] + team_2_df['SFA'].mean(),
                                            team_2_stats['SFA'] + team_1_df['SFF'].mean()])})
        #print mean([team_1_stats['PAT1%F'] + team_2_df['PAT1AS'].astype('float').sum() / team_2_df['PAT1AA'].sum(),
        #       team_2_stats['PAT1%A'] + team_1_df['PAT1FS'].astype('float').sum() / team_1_df['PAT1FA'].sum()])
        expected_scores.update({'GOFOR2': team_1_stats['GOFOR2']})
        pat1prob = mean([team_1_stats['PAT1%F'] + team_2_df['PAT1AS'].astype('float').sum() / team_2_df['PAT1AA'].sum(),
                         team_2_stats['PAT1%A'] + team_1_df['PAT1FS'].astype('float').sum() / team_1_df['PAT1FA'].sum()])
        if not math.isnan(pat1prob):
            expected_scores.update({'PAT1PROB': pat1prob})
        else:
            expected_scores.update({'PAT1PROB': 0.99})
        #print(expected_scores['PAT1PROB'])
        pat2prob = mean([team_1_stats['PAT2%F'] + team_2_df['PAT2AS'].astype('float').sum() / team_2_df['PAT2AA'].sum(),
                         team_2_stats['PAT2%A'] + team_1_df['PAT2FS'].astype('float').sum() / team_1_df['PAT2FA'].sum()])
        if not math.isnan(pat2prob):
            expected_scores.update({'PAT2PROB': pat2prob})
        else:
            expected_scores.update({'PAT2PROB': 0.5})
    #print(expected_scores)
    return expected_scores
            
def matchup(team_1, team_2):
    ts = time.time()
    team_1_season = pd.DataFrame.from_csv(teamsheetpath + team_1 + '.csv')
    team_2_season = pd.DataFrame.from_csv(teamsheetpath + team_2 + '.csv')
    stats_1 = get_residual_performance(team_1)
    stats_2 = get_residual_performance(team_2)
    expected_scores_1 = get_expected_scores(stats_1, stats_2, team_1_season, team_2_season)
    expected_scores_2 = get_expected_scores(stats_2, stats_1, team_2_season, team_1_season)
    team_1_wins = 0
    team_2_wins = 0
    team_1_draws = 0
    team_2_draws = 0
    team_1_scores = []
    team_2_scores = []
    i = 0
    error = 1
    while error > 0.000001 or i < 5000000: #Run until convergence after 100,000 iterations
        summary = game(team_1, team_2,
                       expected_scores_1, expected_scores_2,
                       po)
        team_1_prev_wins = team_1_wins
        team_1_wins += summary[team_1][0]
        team_2_wins += summary[team_2][0]
        team_1_draws += summary[team_1][1]
        team_2_draws += summary[team_2][1]
        team_1_scores.append(summary[team_1][2])
        team_2_scores.append(summary[team_2][2])
        team_1_prob = float(team_1_wins) / len(team_1_scores)
        team_2_prob = float(team_2_wins) / len(team_2_scores)
        if i > 0:
            team_1_prev_prob = float(team_1_prev_wins) / i
            error = team_1_prob - team_1_prev_prob
        i = i + 1
    if i == 5000000:
        print('Probability converged within 5 million iterations')
    else:
        print('Probability converged after ' + str(i) + ' iterations')
    games = pd.DataFrame.from_items([(team_1, team_1_scores), (team_2, team_2_scores)])
    summaries = games.describe(percentiles = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975])
    output = {'ProbWin': {team_1: team_1_prob, team_2: team_2_prob}, 'Scores': summaries}

    print(team_1 + '/' + team_2 + ' score distributions computed in ' + str(round(time.time() - ts, 1)) + ' seconds')

    return output