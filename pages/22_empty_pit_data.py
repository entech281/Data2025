import streamlit as st
import pandas as pd
from motherduck import con

st.set_page_config(layout="wide")
st.title("Empty Pit Data")

st.subheader("Missing Data:")

all_data = con.sql("""
                   select team_number, author, notes,created_at  from scouting.pit
where OCTET_LENGTH(auto_route) = 0 or OCTET_LENGTH(robot_picture) = 0
or created_at < NOW() - INTERVAL '7' DAY
order by team_number asc;
                   """
                   ).df()
st.dataframe(all_data )
