import pandas as pd
import numpy as np

# Create a DataFrame representing the game results
games = pd.DataFrame({
    'Team1': ['A', 'B', 'C'],
    'Team2': ['B', 'C', 'A'],
    'Score': [20, 15, 10]
})
print("games",games)
teams = pd.unique(games[['Team1', 'Team2']].values.ravel('K'))
print("UniqueTeams")
print(teams)
num_teams = len(teams)
num_games = len(games)
print(f"Teams = {num_teams}, games={num_games}")
A = np.zeros((num_games, num_teams))

for i, row in games.iterrows():
    team1_index = np.where(teams == row['Team1'])[0][0]
    team2_index = np.where(teams == row['Team2'])[0][0]
    A[i, team1_index] = 1
    A[i, team2_index] = -1
print(A)
A_plus = np.linalg.pinv(A)

b = games['Score1'] - games['Score2']

# Calculate OPR
opr = A_plus.dot(b)

# Create a DataFrame for OPR
opr_df = pd.DataFrame({'Team': teams, 'OPR': opr})
print(opr_df)