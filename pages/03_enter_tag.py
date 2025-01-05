import streamlit as st
import pandas as pd
from motherduck import con
import cached_data

st.set_page_config(layout="wide")
st.title("Log a Tag ")
st.subheader("Record an observation about a team outside of qualitative data..")
st.caption("""
this is an example of a screen for end users. it allows them to do somethign simply and safely
In this case, simply adding a tag observation as a row in a table, but with guiderails on valid values
""")
team_list = cached_data.get_teams()['team_number'].to_list()
tag_df = con.sql("select tag_name from scouting.allowed_tags where tag_name <> 'null';").df()
available_tags = tag_df['tag_name'].values.tolist()

scouter = st.text_input("scout name")
selected_team = st.selectbox("team Number",team_list)
selected_tag = st.selectbox("tag",available_tags)
description = st.text_area("notes")
confirm = st.button('Save')

if confirm:
    tag_id = con.sql(f"select id from scouting.allowed_tags where tag_name = '{selected_tag}';").df()['id'].values.tolist()[0]
    new_row_df = pd.DataFrame.from_dict({
        'team_number':  [ selected_team ],
        'tag_id': [ tag_id ],
        'scouter_name': [ scouter ],
        'description': [ description ]
    })
    con.sql("INSERT INTO scouting.tags BY NAME SELECT * FROM new_row_df;")
    st.success('Tag Saved!', icon="✅")

st.subheader("Current Data:")
all_data = con.sql("select * from scouting.tags").df()
st.dataframe(all_data )