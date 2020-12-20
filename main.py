#!/usr/bin/env python3
'''
    small script to create a sankey diagram based on dota2 matches
    (https://github.com/argv1/dota-sankey-diagram-generator/)
    based on https://github.com/argv1/dota2-stats

    Usage: main.py -p PLAYERIDS -o ORDER
    i.e. main.py -p 123456 987654 -o win, mode, hero, lobby, team
    opendota API documentation: https://docs.opendota.com/

    please feel free to improve
'''

import argparse
import os.path
import pandas as pd
from   pathlib import Path
import requests

# Define path and filename
base_path     = Path('H:\OneDrive\Programme\_current\dota-stats')  #adjust
game_modes_f  = base_path / 'data\game_mode.txt'       
heroes_f      = base_path / 'data\hero_lore.txt'
lobby_types_f = base_path / 'data\lobby_type.txt'

def get_matches(player_Ids, order):
    '''
    Load already scrapped matches, 
    check for matches from the provided userid and 
    grab missing ones
    '''

    match_data = player_Ids[0]

    # 0 = including turbo, 1 = without
    url = f"https://api.opendota.com/api/players/{player_Ids[0]}/matches?significant=0"
    if(len(player_Ids) > 1):
        for entry in range(1,len(player_Ids)):
            url += f"&included_account_id={player_Ids[entry]}"
            match_data += '-' + player_Ids[entry]
    match_data = base_path / f'{match_data}.csv'

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

    for entry in data:
        df = df.append(entry, ignore_index=True)
    
    df.drop_duplicates(subset='match_id',inplace=True)

    # decode lobbies, games and heroes
    for column in ["game_mode", "hero_id", "lobby_type"]:
        df[column] = df[column].astype("str")

    with game_modes_f.open("r") as f:
        game_modes = dict(x.rstrip().split(None, 1) for x in f)
    df.game_mode.replace(game_modes, inplace=True)

    with heroes_f.open("r") as f:
        heroes = dict(x.rstrip().split(None, 1) for x in f)
    df.hero_id.replace(heroes, inplace=True)

    with lobby_types_f.open("r") as f:
        lobby_types = dict(x.rstrip().split(None, 1) for x in f)
    df.lobby_type.replace(lobby_types, inplace=True)

    # write new dataframe to csv
    df.to_csv(match_data, index=False)

def main():
    # Initiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--player_Ids', nargs='+', help='Enter opendota user id(s)', required=True)
    parser.add_argument('-o', '--order', help='Enter order of the sankey diagram', type=str)
    args = parser.parse_args()
    player_Ids = args.player_Ids
    order = args.order

    # get all matches
    get_matches(player_Ids, order)

if __name__ == '__main__':
    main()
