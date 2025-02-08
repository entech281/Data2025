import streamlit as st
from motherduck import con
import cached_data
import pandas as pd
#Is this import needed...I'm leaving it cause all
#I'm doing right now is resolving merge conflicts
#But we should probably check this...
# from psycopg2 import sql


st.title("This is a tags page")
st.subheader("It will do stuff")
st.caption("""
caption
""") 

team_list = cached_data.get_teams()['team_number'].to_list()
team_list.sort()


available_tags = [
    'Good Driver',  'Bad Driver', 'Unreliable'
]

my_tags = ['None']
my_tags.extend(available_tags)


selected_tag = st.selectbox("tag", my_tags)


tags_df = None


if selected_tag != 'None' and selected_tag in available_tags:

    tags_df = con.sql(f"""SELECT te.team_number, count(ta.tag), ta.tag
                        FROM tba.teams te
                        LEFT JOIN scouting.tags ta ON
                        (ta.team_number = te.team_number)
                        GROUP BY te.team_number, ta.tag;""").df()
    
    
    my_df = tags_df[(tags_df['tag'] == selected_tag)]

    my_df = my_df[['team_number', 'count(ta.tag)']]

    st.subheader("Data")

    st.dataframe(my_df)




my_teams = ['None']
my_teams.extend(team_list)



selected_team = st.selectbox("team", my_teams)


if selected_team != 'None' and selected_tag != 'None':
    
    st.subheader("Data")

    my_df = tags_df[(tags_df['team_number'] == selected_team)]
    my_df = my_df['']

    st.dataframe(my_df)

    if my_df.empty:
        st.write("Nothing to display :slightly_frowning_face:")
        st.write("Here is a squirrel to make you feel less sad")
        st.image("./static/squirrel.png", width=75)
        st.link_button("https://xkcd.com/1503/", url="https://xkcd.com/1503/")

   ########## # st.dataframe(table_df)

    