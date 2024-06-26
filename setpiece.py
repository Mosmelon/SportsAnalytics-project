import requests
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


def fetch_matches(competition_id, season_id):
    matches_url = f'https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/{competition_id}/{season_id}.json'
    response = requests.get(matches_url)
    return response.json()


def fetch_match_events(match_id):
    events_url = f'https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{match_id}.json'
    response = requests.get(events_url)
    return response.json()


def fetch_set_pieces(team_name, matches):
    corners = []
    free_kicks = []
    penalties = []
    match_results = []

    for match in matches:
        if team_name in [match['home_team']['home_team_name'], match['away_team']['away_team_name']]:
            match_id = match['match_id']
            events = fetch_match_events(match_id)
            
         
            if match['home_team']['home_team_name'] == team_name:
                opponent_team = match['away_team']['away_team_name']
                goals_for = match['home_score']
                goals_against = match['away_score']
            else:
                opponent_team = match['home_team']['home_team_name']
                goals_for = match['away_score']
                goals_against = match['home_score']

            if goals_for > goals_against:
                result = "Win"
            elif goals_for < goals_against:
                result = "Loss"
            else:
                result = "Draw"
            
            corners_count = 0
            free_kicks_count = 0
            penalties_count = 0
            
            for event in events:
                if event['team']['name'] == team_name and event['period'] in [1, 2, 3, 4]:
                    if event['type']['name'] == "Shot":
                        play_pattern = event.get('play_pattern', {}).get('name')
                        if play_pattern == 'From Corner':
                            corners.append(event['location'])
                            corners_count += 1
                        elif play_pattern == 'From Free Kick':
                            free_kicks.append(event['location'])
                            free_kicks_count += 1
                        elif event['shot'].get('type', {}).get('name') == "Penalty":
                            penalties.append(event['location'])
                            penalties_count += 1
            
            match_results.append({
                "match_id": match_id,
                "opponent_team": opponent_team,
                "result": result,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "corners": corners_count,
                "free_kicks": free_kicks_count,
                "penalties": penalties_count
            })

    return corners, free_kicks, penalties, match_results


def plot_set_pieces_heatmap(team_name, competition_id, season_id, vmax=None):

    matches = fetch_matches(competition_id, season_id)

    corners, free_kicks, penalties, match_results = fetch_set_pieces(team_name, matches)
    
    print(f"Number of corners: {len(corners)}")
    print(f"Number of free kicks: {len(free_kicks)}")
    print(f"Number of penalties: {len(penalties)}")
    
    for match in match_results:
        print(f"Match ID {match['match_id']}: Opponent = {match['opponent_team']}, Result = {match['result']}, Goals For = {match['goals_for']}, Goals Against = {match['goals_against']}, Corners = {match['corners']}, Free Kicks = {match['free_kicks']}, Penalties = {match['penalties']}")
    

    pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black')
    
 
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    def plot_heatmap(ax, locations, color, label):
        pitch.draw(ax=ax)
        if len(locations) > 0:
          
            locations_array = np.array(locations)
            x_coords, y_coords = zip(*locations_array)
            
           
            bin_statistic = pitch.bin_statistic(x_coords, y_coords, statistic='count', bins=(12, 10))
            
           
            norm = Normalize(vmin=0, vmax=vmax)  
            cmap = plt.cm.get_cmap(color)
            
          
            heatmap = pitch.heatmap(bin_statistic, ax=ax, cmap=cmap, edgecolors='black', alpha=0.7, vmin=0, vmax=vmax)
            
        
            for i in range(bin_statistic['statistic'].shape[0]):
                for j in range(bin_statistic['statistic'].shape[1]):
                    bin_count = bin_statistic['statistic'][i, j]
                    bin_center = bin_statistic['cx'][i, j], bin_statistic['cy'][i, j]
                    if bin_count > 0:
                        ax.text(bin_center[0], bin_center[1], str(int(bin_count)),
                                ha='center', va='center', fontsize=10, color='black')
            
        
            sm = ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label(label, fontsize=12)
    

    plot_heatmap(axes[0], corners, 'Blues', 'Corners')
    plot_heatmap(axes[1], free_kicks, 'Greens', 'Free Kicks')
    plot_heatmap(axes[2], penalties, 'Reds', 'Penalties')
    

    axes[0].set_title(f"{team_name} Corners Heat Map", fontsize=15)
    axes[1].set_title(f"{team_name} Free Kicks Heat Map", fontsize=15)
    axes[2].set_title(f"{team_name} Penalties Heat Map", fontsize=15)
    
    plt.tight_layout()
    plt.show()

# Example usage
team_name = "Germany Women's" # example country 
competition_id = 53  # example competition ID
season_id = 106 # example season ID

plot_set_pieces_heatmap(team_name, competition_id, season_id)
