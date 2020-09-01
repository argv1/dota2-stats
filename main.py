#!/usr/bin/env python3
'''
    small script to scrap all dota2 stats
    (including turbo matches, which are usually not included)
    (https://github.com/argv1/dota2-stats/)

    Usage: main.py -p PLAYERID 
    i.e. main.py -p 221666230
    opendota API documentation: https://docs.opendota.com/

    please feel free to improve
'''

import argparse
import os.path
import pandas as pd
from   pathlib import Path
import requests

# Define path and filename
base_path  = Path('H:\OneDrive\Programme\_current\dota-stats')  #adjust
match_data = base_path / 'data.csv'            


def get_matches(player_Id):
    '''
    Load already scrapped matches, 
    check for matches from the provided userid and 
    grab missing ones
    '''

    # 0 = including turbo, 1 = without
    url = f"https://api.opendota.com/api/players/{player_Id}/matches?significant=0" 

    # check if match_data already exists, else create it
    if not os.path.isfile(match_data):
        df = pd.DataFrame(columns=["match_id", "player_slot", "radiant_win", "duration", "game_mode", "lobby_type", "hero_id", "start_time", "version", "kills", "deaths", "assists", "skill", "leaver_status", "party_size"])
        df.to_csv(match_data, index=False)

    # load existing matches
    df = pd.read_csv(match_data)
    match_ids = pd.Series(df.match_id)
    
    # start request
    resp = requests.get(url=url)
    data = resp.json()
    
    # store every new match in the dataframe
    skip_entry = False
    for entry in data:
        df = df.append(entry, ignore_index=True)
        df.drop_duplicates(inplace=True)
    
    # write new dataframe to csv
    df.to_csv(match_data, index=False)

def main():
    # Initiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--playerid', help='Enter a opendota user id', type=str, required=True)
    args = parser.parse_args()
    player_Id = args.playerid
    
    # get all matches
    get_matches(player_Id)

if __name__ == '__main__':
    main()