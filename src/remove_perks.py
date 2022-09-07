# Imports
import json
import os
import shutil

def remove_perks(name):
    # Variables
    player_name = name
    matches_dir = '../data/' + name + '_match_history/matches'
    general_dir = matches_dir + '/match_'

    # Get list of the player's matches
    matches_list = []
    with os.scandir(matches_dir) as iter:
        for directory in iter:
            if not (directory.name.startswith('.') and directory.is_file()):
                matches_list.append(directory.name)

    # Cycle through all matches
    for match in matches_list:
        general_dir = matches_dir + '/' + match
        
        # Obtain participants' directories of current match
        participants_list = []
        participants_dir = general_dir + '/participants'

        with os.scandir(participants_dir) as iter:
            for directory in iter:
                if not (directory.name.startswith('.') and directory.is_file()):
                    participants_list.append(directory.name)
        
        # Cycle through participants
        for participant in participants_list:
            general_dir = participants_dir + '/' + participant + '/' + participant + '.json'
            json_string = None
            
            # Open the player's json file
            with open(general_dir, 'r+') as json_file:
                data = json.load(json_file)
                del data['perks']
                json_string = json.dumps(data, indent=2)
                json_file.close()

            with open(general_dir, 'w') as json_file:
                json_file.write(json_string)
                json_file.close()
