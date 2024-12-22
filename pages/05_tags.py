import streamlit as st
from motherduck import con
import cached_data
import pandas as pd
from psycopg2 import sql

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

    tags_df = con.sql(f"""SELECT te.team_number, count(ta.tag)
                        FROM tba.teams te
                        LEFT JOIN scouting.tags ta ON
                        (ta.team_number = te.team_number)
                        GROUP BY te.team_number, ta.tag
                        HAVING  tag = '{selected_tag}';""").df()


    st.subheader("Data")



    st.dataframe(tags_df)




my_teams = ['None']
my_teams.extend(team_list)



selected_team = st.selectbox("team", my_teams)


if selected_team != 'None' and selected_tag != 'None':
    
    st.subheader("Data")

    # table_dict = {
    #     "Tag" : [],
    #     "Count" : []
    # }

    # for tag in available_tags:

    #     tag_count = con.sql(f"SELECT COUNT(*) FROM scouting.tags WHERE team_number = {selected_team} AND tag = '{tag}';").fetchall()[0][0]

    #     table_dict["Tag"].append(tag)
    #     table_dict["Count"].append(tag_count)

    # table_df = pd.DataFrame(data=table_dict)
    # st.write(tags_df.iloc[0]["team_number"])
    foundData = False

    for entry in tags_df.iloc:
        if entry["team_number"] == selected_team:
            st.write(entry)
            foundData = True

    if not foundData:
        st.write("Nothing to display :slightly_frowning_face:")
        st.write("Here is a squirrel to make you feel less sad")
        st.image("./static/squirrel.png", width=75)
        st.link_button("https://xkcd.com/1503/", url="https://xkcd.com/1503/")

   ########## # st.dataframe(table_df)

    