import pandas as pd
import sys
import os

def reorder_index(team_csv):
    location = sys.path[0] + '\\teamcsvs'
    team_df = pd.DataFrame.from_csv(location + '\\' + team_csv)
    cols_df = pd.DataFrame.from_csv(location + '\\ARI.csv')
    cols = cols_df.columns
    team_df = team_df[cols]
    team_df.to_csv(location + '\\' + team_csv)

files = os.listdir(sys.path[0] + '\\teamcsvs')
for f in files:
    reorder_index(f)
