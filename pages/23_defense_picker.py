import streamlit as st
from pages_util.event_selector import event_selector
from cached_data import get_defense
import duckdb
from motherduck import con

# Event Selector
selected_event = event_selector()
st.title("Defense Picker")

st.subheader("Good Defense")

# Query to get all data

all_data = get_defense()


# Initialize session state to track hidden teams
if "hidden_teams" not in st.session_state:
    st.session_state.hidden_teams = set()

# Step 1: Prepare data for the pill control (display team numbers)
all_teams = all_data['team_number'].unique().tolist()

# Step 2: Display the pill control for selecting teams
selected_teams = st.pills(
    "Select Teams to Remove",
    options=[str(team) for team in all_teams],
    default=[str(team) for team in st.session_state.hidden_teams],  # Pre-select hidden teams
    selection_mode="multi"
)

# Step 3: Update the session state with the selected teams
# When teams are selected via the pills, we'll add those to the hidden_teams list
if selected_teams:
    st.session_state.hidden_teams = set(map(int, selected_teams))  # Convert to integer if needed

# Step 4: Filter out the hidden teams for display
visible_data = all_data[~all_data['team_number'].isin(st.session_state.hidden_teams)]

# Step 5: Display the filtered DataFrame (visible teams only)
st.write("### Visible Teams (Filtered)")
st.dataframe(visible_data)

# Step 6: Allow users to "Re-add All Teams" at the bottom
if st.button("Re-add All Teams"):
    st.session_state.hidden_teams.clear()  # Clear hidden teams, restoring all teams
