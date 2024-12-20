import streamlit as st
from motherduck import con
import cached_data
import pandas as pd

team_list = cached_data.get_teams()["team_number"].to_list()

team_list.sort()

selected_team = st.selectbox("team", team_list)

opr_data = con.sql("SELECT event_key, oprs FROM tba.oprs WHERE team_number = % s" % selected_team).df()


first_col1, first_col2 = st.columns(2)

with first_col1:

    with st.container(border=True):
        st.line_chart(opr_data, x="event_key", y="oprs")


with first_col2:

    with st.container(border=True):
        pass
    





match_data = cached_data.get_matches()

event_list = match_data["event_key"].to_list()

temp_list = []

for event in event_list:
    if not event in temp_list:
        temp_list.append(event)

event_list = temp_list

selected_event = st.selectbox("event", event_list)



row_num = opr_data[opr_data['event_key'] == selected_event].index 


second_col1, second_col2, second_col3 = st.columns(3)

#Opr at Event
with second_col1:

    with st.container(border=True):
        try:
            st.write(f"OPR: {opr_data.iloc[row_num, 1][0]}")

        except:
            st.write("Sorry, something went wrong, double check that the selected team participated at the selected event")


with second_col2:

    with st.container(border=True):
        pass


#Opr vs event ranking
with second_col3:

    with st.container(border=True):
        pass
        


