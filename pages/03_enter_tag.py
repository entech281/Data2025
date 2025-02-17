import streamlit as st
import pandas as pd
from motherduck import con
from cached_data import get_event_list,get_most_recent_event,get_team_list
st.set_page_config(layout="wide")
st.title("Log a Tag ")

event_list = get_event_list()
selected_event = st.pills("Event", event_list, default=get_most_recent_event(), selection_mode="single")
if selected_event is None:
    st.caption("Select an Event")
    st.stop()


team_list = get_team_list(selected_event)
available_tags = [
    "Good Driver", "Bad Driver", "Unreliable", "Fast", "Normal-Speed", "Slow", "Pizza Box", "Disable"
]

selected_team = st.selectbox("team Number",team_list)
selected_tag = st.selectbox("tag",available_tags)
confirm = st.button('Save')

if confirm:
    new_row_df = pd.DataFrame.from_dict({
        'team_number':  [ selected_team ],
        'tag': [ selected_tag ]
    })
    con.sql("INSERT INTO scouting.tags BY NAME SELECT * FROM new_row_df")
    st.success('Tag Saved!', icon="✅")

st.subheader("Current Data:")
all_data = con.sql("select * from scouting.tags").df()
st.dataframe(all_data )
