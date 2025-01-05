import streamlit as st
from motherduck import con
import cached_data
import pandas as pd

st.set_page_config(layout="wide")
st.title("Admin Panel")

st.text("Modify allowed tags, changes to 'null' for it to no appear on options but still be able to recover old data.")

tag_id = st.number_input("tag ID")
tag_name = st.text_input("tag name")
confirm = st.button("Confirm")

if confirm:
    new_row_df = pd.DataFrame.from_dict({
        'id': [ tag_id ],
        'tag_name': [ tag_name ]
    })
    con.sql(f"""
        INSERT INTO scouting.allowed_tags 
        BY NAME SELECT *
        FROM new_row_df
        ON CONFLICT (id) DO UPDATE
        SET tag_name = '{tag_name}'
    """)
    st.success('Modification Complete.', icon="✅")

df = con.sql("SELECT * FROM scouting.allowed_tags").df()
st.dataframe(df)