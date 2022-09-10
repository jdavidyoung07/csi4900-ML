import json
import os
import sys
import shutil

#TEST_FILE = '../data/Jedı07_match_history/matches/match_NA1_4034399637/NA1_4034399637.json'
participants_key_subset = [
    'win',
    'teamId',
    'championName',
    'championId',
    'goldEarned',
    'goldSpent',
    'kills',
    'baronKills',
    'dragonKills',
    'inhibitorKills',
    'champExperience',
    'deaths',
    'totalDamageDealtToChampions',
    'totalDamageTaken',
    'visionScore',
    'wardsPlaced',
    'totalMinionsKilled',
    'damageDealtToObjectives'
    ]

TEAMS = [100,200]

def get_players_list()-> list:
    players_directory = 'data'
    players_list = []
    with os.scandir(players_directory) as iter:
        for directory in iter:
            if not (directory.name.startswith('.') and directory.isfile()):
                directory_name = directory.name.removesuffix('_match_history')
                players_list.append(directory_name)
    return players_list


def get_matches(player_name:str)-> list:
    player_directory = 'data/' + player_name + '_match_history/matches' 
    match_list = []
    with os.scandir(player_directory) as iter:
        for directory in iter:
            if not (directory.name.startswith('.') and directory.isfile()):
                directory_name = directory.name.removeprefix('match_')
                match_list.append(directory_name)
    return match_list


def get_winner(participants:list)-> bool :
    for p in participants :
        if p['win'] :
            return p['teamId']


def compute_team_match_performance(teams_data,team_id,participants) -> None :
    max_dmg,dmg_carry = float('-inf'),''
    max_obj_carry,obj_carry = float('-inf'),''
    for p in participants :
        if p['teamId'] == team_id :
            teams_data['per_team'][team_id]['total_gold_earned'] += p['goldEarned']
            teams_data['per_team'][team_id]['total_gold_spent'] += p['goldSpent']
            teams_data['per_team'][team_id]['team_comp'].append({'champName':p['championName'],'champId':p['championId']})
            teams_data['per_team'][team_id]['total_baron_kills'] += p['baronKills']
            teams_data['per_team'][team_id]['total_dragon_kills'] += p['dragonKills']
            teams_data['per_team'][team_id]['total_kills'] += p['kills']
            teams_data['per_team'][team_id]['total_inhibitor_kils'] += p['inhibitorKills']
            teams_data['per_team'][team_id]['total_deaths'] += p['deaths']
            teams_data['per_team'][team_id]['total_damage_dealt_to_champions'] += p['totalDamageDealtToChampions']
            teams_data['per_team'][team_id]['total_damage_dealt_to_objectives'] += p['damageDealtToObjectives']
            teams_data['per_team'][team_id]['total_damage_taken'] += p['totalDamageTaken']
            teams_data['per_team'][team_id]['average_vision_score'] += p['visionScore']
            teams_data['per_team'][team_id]['total_wards_placed'] += p['wardsPlaced']
            teams_data['per_team'][team_id]['average_creep_score'] += p['totalMinionsKilled']
            teams_data['per_team'][team_id]['average_champion_experience'] += p['champExperience']

            if p['totalDamageDealtToChampions'] > max_dmg :
                max_dmg = p['totalDamageDealtToChampions']
                dmg_carry = p['championName']
            
            if p['damageDealtToObjectives'] > max_obj_carry :
                max_obj_carry = p['totalDamageDealtToChampions']
                obj_carry = p['championName']
        
    team_size = len(teams_data['per_team'][team_id]['team_comp'])
    
    try:
        teams_data['per_team'][team_id]['average_champion_experience'] //=  team_size
    except:
        print(teams_data)
        sys.exit()
    teams_data['per_team'][team_id]['average_creep_score'] //= team_size
    teams_data['per_team'][team_id]['average_vision_score'] //=  team_size
    teams_data['per_team'][team_id]['dmg_carry'] = dmg_carry
    teams_data['per_team'][team_id]['obj_carry'] = obj_carry

    if 'dmg_to_champs_winner' not in teams_data['general'] or teams_data['per_team'][teams_data['general']['dmg_to_champs_winner']]['total_damage_dealt_to_champions'] < teams_data['per_team'][team_id]['total_damage_dealt_to_champions']:
        teams_data['general']['dmg_to_champs_winner'] = team_id
    
    if 'dmg_to_obj_winner' not in teams_data['general'] or teams_data['per_team'][teams_data['general']['dmg_to_obj_winner']]['total_damage_dealt_to_objectives'] < teams_data['per_team'][team_id]['total_damage_dealt_to_objectives']:
        teams_data['general']['dmg_to_obj_winner'] = team_id
    
    if 'vision_winner' not in teams_data['general'] or teams_data['per_team'][teams_data['general']['vision_winner']]['average_vision_score'] < teams_data['per_team'][team_id]['average_vision_score']:
        teams_data['general']['vision_winner'] = team_id

    if 'cs_winner' not in teams_data['general'] or teams_data['per_team'][teams_data['general']['cs_winner']]['average_creep_score'] < teams_data['per_team'][team_id]['average_creep_score']:
        teams_data['general']['cs_winner'] = team_id
    
    if 'champ_experience_winner' not in teams_data['general'] or teams_data['per_team'][teams_data['general']['champ_experience_winner']]['average_champion_experience'] < teams_data['per_team'][team_id]['average_champion_experience']:
        teams_data['general']['champ_experience_winner'] = team_id
    
    if 'wards_placed_winner' not in teams_data['general'] or teams_data['per_team'][teams_data['general']['wards_placed_winner']]['total_wards_placed'] < teams_data['per_team'][team_id]['total_wards_placed']:
        teams_data['general']['wards_placed_winner'] = team_id

    if 'gold_spender_winner' not in teams_data['general'] or teams_data['per_team'][teams_data['general']['gold_spender_winner']]['total_gold_spent'] < teams_data['per_team'][team_id]['total_gold_spent']:
        teams_data['general']['gold_spender_winner'] = team_id
    
    
def clean_json_match_data(match:dict) -> dict :

    participants = match['info']['participants']
    match_duration_in_millis = match['info']['gameDuration']
    match_duration_in_minutes = match_duration_in_millis/(1000*60)%60
    match_id = match['metadata']['matchId']

    for i in range(len(participants)) :
        participants[i] = dict((k,participants[i][k]) for k in participants_key_subset if k in participants[i])

    data_per_team = {'general':{},'per_team':{}}

    data_per_team['general']['gameLengthMin'] = int(match_duration_in_minutes)

    for team in TEAMS :
        data_per_team['per_team'][team] = {
            'total_gold_earned':0,
            'total_gold_spent':0,
            'team_comp':[],
            'total_baron_kills':0,
            'total_dragon_kills':0,
            'total_inhibitor_kils':0,
            'total_kills':0,
            'total_deaths':0,
            'total_damage_dealt_to_champions':0,
            'total_damage_dealt_to_objectives':0,
            'total_damage_taken':0,
            'average_vision_score':0,
            'total_wards_placed':0,
            'average_creep_score':0,
            'average_champion_experience':0,
            'dmg_carry':"",
            'obj_carry':"",
            'match_id': match_id
        }
        compute_team_match_performance(data_per_team,team,participants)
    
    data_per_team['general']['final_match_winner'] = get_winner(participants)

    return data_per_team


def run() :
    players_list = get_players_list()

    for p_index in range(len(players_list)):
        matches_list = get_matches(players_list[p_index])
        for m_index in range(len(matches_list)):
            match_directory = 'data/' + players_list[p_index] + '_match_history/matches/match_' + matches_list[m_index] + '/' + matches_list[m_index] + '.json'
            match_data_file_path = 'data/' + players_list[p_index] + '_match_history/matches/match_' + matches_list[m_index] + '/data_per_team.json'
            with open(match_directory, 'r') as file:
                data = json.load(file)
                if data['info']['gameDuration'] == 0:
                    file.close()
                    shutil.rmtree('data/' + players_list[p_index] + '_match_history/matches/match_' + matches_list[m_index])
                else:
                    match_data_per_team = clean_json_match_data(data)
                    match_data_json_string = json.dumps(match_data_per_team, indent=2)
                    match_data_json_file = open(match_data_file_path, 'w')
                    match_data_json_file.write(match_data_json_string)
                    match_data_json_file.close()
    #with open(TEST_FILE, 'r') as f:
    #    data = json.load(f)
    #match_data_per_team = clean_json_match_data(data)
    #print(match_data_per_team)


if __name__ == '__main__' :
    run() 