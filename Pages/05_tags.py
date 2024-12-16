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
team_list.sort()

# These all need single quotes because sql doesn't like double quotes I think because
# The table is set up as a VARCHAR and not TEXT
available_tags = [
    'Good Driver',  'Bad Driver', 'Unreliable'
]

my_tags = ['None']
my_tags.extend(available_tags)


selected_tag = st.selectbox("tag", my_tags)


tags_df = None



if selected_tag != 'None':


    tags_df = pd.DataFrame(data=con.sql("""SELECT te.team_number, count(ta.tag)
                                            FROM tba.teams te
                                            LEFT JOIN scouting.tags ta ON
                                            (ta.team_number = te.team_number)
                                            GROUP BY te.team_number, ta.tag
                                            HAVING  tag = % s""" % selected_tag))


    st.subheader("Data")



    st.dataframe(tags_df)




my_teams = ['None']
my_teams.extend(team_list)



selected_team = st.selectbox("team", my_teams)


if selected_team != 'None' and selected_tag != 'None':
    
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

    