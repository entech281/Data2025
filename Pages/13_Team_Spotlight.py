import streamlit as st
from motherduck import con
import pandas as pd
from cached_data import get_teams
from opr3 import *


st.title("Team Spotlight")

team_list = sorted(get_teams()['team_number'].values.tolist())

event_list = con.sql("SELECT DISTINCT event_key FROM tba.matches").df()['event_key'].values.tolist()
matches_df = con.sql("SELECT * FROM tba.matches").df()

team = st.selectbox("Team Number", team_list)
events = st.multiselect("Event", event_list)



if team is not None and len(events) > 0:
    st.subheader(f"Team {team}")
    st.caption("This is a demo of a page that shows data about a team")

    # Filter and sort the data using pandas
    team_data = matches_df[
        ((matches_df['red1'] == team) | (matches_df['red2'] == team) | (matches_df['red3'] == team) |
         (matches_df['blue1'] == team) | (matches_df['blue2'] == team) | (matches_df['blue3'] == team)) &
        (matches_df['event_key'].isin(events))
    ]

    st.dataframe(team_data)

    columns = st.columns(3, border=True)

    with columns[0]:
        st.subheader("Coral")

        selected_df = team_data[["blue_auto_amp_note_count", "blue_auto_amp_note_points"]]
        

        chart_df = pd.DataFrame({"Level" : [], "Chart" : []})

        for col_name in selected_df.columns:
            
            # TODO: Add a chart to the chart_df DataFrame
            new_row = pd.DataFrame({"Level" : [col_name], "Chart" : []})
            chart_df = pd.concat([chart_df, new_row], ignore_index=True)


        st.dataframe(chart_df)
        
        
        