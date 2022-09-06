# Imports
import json
import os
import shutil

# Variables
player_name = 'Jedı07'
matches_dir = '../data/Jedı07_match_history/matches'
general_dir = '../data/Jedı07_match_history/matches/match_'

# Get list of the player's matches
matches_list = []
with os.scandir(matches_dir) as iter:
    for directory in iter:
        if not (directory.name.startswith('.') and directory.is_file()):
            matches_list.append(directory.name)

for match in matches_list:
    general_dir = '../data/Jedı07_match_history/matches/' + match
    data_directory = general_dir + '/participants'

    # Create directory for the game's players' data to be stored
    if os.path.exists(data_directory):
        shutil.rmtree(data_directory)
    os.mkdir(data_directory)

    # Path of the match data file
    #match_data_path = '../../data/Jedı07_match_history/matches/match_NA1_4276627830/NA1_4276627830.json'
    match_data_path = general_dir + '/' + match[6:] + '.json'

    # Open the json file as a python dictionary
    json_file = json.loads(open(match_data_path, 'r').read())

    # # Extract the players' stats from the match's stats
    for player in json_file['info']['participants']:
        
        # Get player puuid
        player_puuid = player['puuid']

        # Create directory to store that player's statistics
        player_path = data_directory + '/player_' + player_puuid

        if os.path.exists(player_path):
            shutil.rmtree(player_path)
        os.mkdir(player_path)

        # Path of the player's stats file
        player_stats_file_path = player_path + '/player_' + player_puuid + '.json'

        # Save the player's stats file
        player_stats_json_string = json.dumps(player, indent=2)
        match_data_json_file = open(player_stats_file_path, 'w')
        match_data_json_file.write(player_stats_json_string)
        match_data_json_file.close()
