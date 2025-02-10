import duckdb
import pandas as pd
import numpy as np
from motherduck import con
# Connect to DuckDB and load match data
con = duckdb.connect("frc_matches.db")  # Change to your actual DB file
match_data = con.execute("SELECT * FROM matches").fetch_df()

# Extract team names
team_columns = ["red1", "red2", "red3", "blue1", "blue2", "blue3"]
teams = set(match_data[team_columns].values.flatten())

# Extract match attributes (everything except identifiers)
excluded_columns = ["match_number"] + team_columns  # Adjust based on your schema
attributes = [col for col in match_data.columns if col not in excluded_columns]

# Initialize team contributions (mean = 0, high uncertainty)
team_estimates = {team: {attr: {"mu": 0, "sigma": 100} for attr in attributes} for team in teams}

# Bayesian update parameters
BETA = 50  # Controls update magnitude
DECAY = 0.95  # Reduces uncertainty over time

# Store historical estimates per match
history = []

def update_team_contributions(row):
    """
    Bayesian update for each team's contribution to match attributes.
    """
    global team_estimates

    # Split teams
    red_alliance = [row["red1"], row["red2"], row["red3"]]
    blue_alliance = [row["blue1"], row["blue2"], row["blue3"]]

    for attr in attributes:
        # Get actual match outcome for this attribute
        red_score = row[attr]
        blue_score = row[attr]  # Adjust if needed (e.g., different columns for each alliance)

        # Compute prior estimates for alliances
        red_mu = np.mean([team_estimates[t][attr]["mu"] for t in red_alliance])
        blue_mu = np.mean([team_estimates[t][attr]["mu"] for t in blue_alliance])

        # Compute uncertainties
        red_sigma2 = np.mean([team_estimates[t][attr]["sigma"]**2 for t in red_alliance])
        blue_sigma2 = np.mean([team_estimates[t][attr]["sigma"]**2 for t in blue_alliance])

        # Compute expected outcome
        p_red = 1 / (1 + np.exp(-(red_mu - blue_mu) / BETA))

        # Compute actual outcome (normalize score difference)
        actual_outcome = (red_score - blue_score) / max(abs(red_score - blue_score), 1)

        # Bayesian update factor
        update_factor = (actual_outcome - p_red) * BETA

        # Update means
        for team in red_alliance:
            team_estimates[team][attr]["mu"] += update_factor * (team_estimates[team][attr]["sigma"]**2 / (team_estimates[team][attr]["sigma"]**2 + red_sigma2))
        for team in blue_alliance:
            team_estimates[team][attr]["mu"] -= update_factor * (team_estimates[team][attr]["sigma"]**2 / (team_estimates[team][attr]["sigma"]**2 + blue_sigma2))

        # Reduce uncertainty over time
        for team in red_alliance + blue_alliance:
            team_estimates[team][attr]["sigma"] = max(team_estimates[team][attr]["sigma"] * DECAY, 10)

# Loop through matches and update estimates
for index, match in match_data.iterrows():
    update_team_contributions(match)

    # Store snapshot of current estimates
    df_snapshot = pd.DataFrame({team: {attr: team_estimates[team][attr]["mu"] for attr in attributes} for team in teams}).T
    history.append(df_snapshot)

# Final estimate after all matches
final_estimate = history[-1]

# Save final rankings to CSV
final_estimate.to_csv("final_team_contributions.csv")

# Print final rankings
print("Final Team Contributions:")
print(final_estimate)
