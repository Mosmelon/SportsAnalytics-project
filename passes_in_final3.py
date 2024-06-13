import requests
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# Function to fetch match IDs for a given competition and season
def fetch_match_ids(competition_id, season_id):
    matches_url = f'https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/{competition_id}/{season_id}.json'
    response = requests.get(matches_url)
    matches = response.json()
    return [match['match_id'] for match in matches]

# Function to fetch passes into the penalty area for a team across specified matches
def fetch_penalty_area_passes(team_name, match_ids):
    penalty_area_passes = []
    
    for match_id in match_ids:
        events_url = f'https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{match_id}.json'
        response = requests.get(events_url)
        match_events = response.json()
        
        for event in match_events:
            if event['team']['name'] == team_name and event['type']['name'] == "Pass":
                end_location = event['pass']['end_location']
                if end_location:
                    end_x, end_y = end_location
                    
                    # Define penalty area criteria
                    if end_x >= 102 and 18 <= end_y <= 62:  # assuming pitch length is 120 and width is 80
                        event_location = event['location']
                        if event_location:
                            penalty_area_passes.append(event_location)
                    
    return penalty_area_passes

# Function to plot the passes into the penalty area for multiple teams
def plot_penalty_area_passes_for_teams(teams, competition_id, season_id):
    # Fetch match IDs for the competition and season
    match_ids = fetch_match_ids(competition_id, season_id)
    
    # Calculate the number of rows and columns for the grid layout
    num_teams = len(teams)
    cols = 2  # Number of columns
    rows = (num_teams + 1) // cols  # Number of rows

    # Create a figure with subplots
    fig, axes = plt.subplots(rows, cols, figsize=(15, 10 * rows))
    axes = axes.flatten()

    for idx, team_name in enumerate(teams):
        ax = axes[idx]
        pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black')
        pitch.draw(ax=ax)
        
        # Fetch passes into the penalty area for the team
        penalty_area_passes = fetch_penalty_area_passes(team_name, match_ids)
        
        # Convert pass locations to numpy array for plotting
        locations = np.array(penalty_area_passes)
        
        if locations.size > 0:
            # Unpack x and y coordinates
            x_coords, y_coords = zip(*locations)
            
            # Calculate the number of events in each bin
            bin_statistic = pitch.bin_statistic(x_coords, y_coords, statistic='count', bins=(6, 5))
            
            # Normalize the data for coloring
            norm = Normalize(vmin=0, vmax=100)
            cmap = plt.cm.Oranges
            
            # Plot the colored squares
            pc = pitch.heatmap(bin_statistic, ax=ax, cmap=cmap, edgecolors='black', alpha=0.7, vmin=0, vmax=100)
            
            # Add text annotations for each bin
            for i in range(bin_statistic['statistic'].shape[0]):
                for j in range(bin_statistic['statistic'].shape[1]):
                    bin_count = bin_statistic['statistic'][i, j]
                    bin_center = bin_statistic['cx'][i, j], bin_statistic['cy'][i, j]
                    ax.text(bin_center[0], bin_center[1], str(int(bin_count)),
                            ha='center', va='center', fontsize=12, color='black')
            
            # Add a color scale using matplotlib directly
            sm = ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label(f'Number of passes into penalty area', fontsize=12)
        
        # Calculate and display the total number of passes into the penalty area for the team
        total_passes = len(penalty_area_passes)
        ax.text(0.5, 1.0, f"Total passes: {total_passes}", ha='center', va='center', transform=ax.transAxes, fontsize=12, color='black')
        
        # Set title
        ax.set_title(f"{team_name} Passes into the box Map", fontsize=15)

    # Remove any unused subplots
    for i in range(len(teams), len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    plt.show()

# Parameters
teams = ["Spain Women's", "Sweden Women's", "England Women's"]
competition_id = 72  # competition ID
season_id = 107  # season ID

# Plot passes into the penalty area for the teams
plot_penalty_area_passes_for_teams(teams, competition_id, season_id)
