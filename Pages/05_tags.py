import streamlit as st
from motherduck import con
import cached_data
import pandas as pd

st.title("This is a tags page")
st.subheader("It will do stuff")
st.caption("""
caption
""")

team_list = cached_data.get_teams()['team_number'].to_list()
available_tags = [
    "Good Driver", "Bad Driver", "Unreliable"
]

selected_tag = st.selectbox("tag", available_tags)

confirm1 = st.button('Get tag count')


if confirm1:
    st.subheader("Data")
    #change this sql to actually get the right column
    # tag_data = con.sql("SELECT tag FROM scouting.tags").df()
    # st.dataframe(tag_data)

    table_dict = {
        "Team" : [],
        "Number of Tags" : []
        }

    for team in team_list:


        tag_count = con.sql(f"SELECT COUNT(*) FROM scouting.tags WHERE team_number = {team} AND tag = '{selected_tag}';").fetchall()[0][0]

        table_dict["Team"].append(team)
        table_dict["Number of Tags"].append(tag_count)

    table_df = pd.DataFrame(data=table_dict)
    
    st.dataframe(table_df)






selected_team = st.selectbox("team", team_list)

confirm2 = st.button("Get tags for this team")

if confirm2:
    
    st.subheader("Data")

    table_dict = {
        "Tag" : [],
        "Count" : []
    }

    for tag in available_tags:

        tag_count = con.sql(f"SELECT COUNT(*) FROM scouting.tags WHERE team_number = {selected_team} AND tag = '{tag}';").fetchall()[0][0]

        table_dict["Tag"].append(tag)
        table_dict["Count"].append(tag_count)

    table_df = pd.DataFrame(data=table_dict)

    st.dataframe(table_df)

    