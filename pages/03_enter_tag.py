import streamlit as st
import pandas as pd
from motherduck import con

st.set_page_config(layout="wide")
st.title("Log a Tag ")
st.subheader("add a row into table scouting.tags in motherduck database")
st.caption("""
this is an example of a screen for end users. it allows them to do somethign simply and safely
In this case, simply adding a tag observation as a row in a table, but with guiderails on valid values
""")
df = con.sql("select team_number from tba.teams").df()
team_list = df['team_number'].values.tolist()
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
