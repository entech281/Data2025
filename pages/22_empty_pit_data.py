import streamlit as st
import pandas as pd
from motherduck import con

st.set_page_config(layout="wide")
st.title("Empty Pit Data")

st.subheader("Missing Picture:")

all_data = con.sql("""
                   select team_number, author, notes,created_at  from scouting.pit
where OCTET_LENGTH(auto_route) is NULL or OCTET_LENGTH(robot_picture) is NULL
order by team_number asc;
                   """
                   ).df()
st.dataframe(all_data )

st.subheader("Not Updated Recently:")

all_data = con.sql("""
                     SELECT team_number, created_at
FROM scouting.pit
WHERE created_at < NOW() - INTERVAL '3 days'
and team_number in (
  select distinct team_number
  from tba.oprs where event_key='2025sccmp'
)
                   """
                     ).df()
st.dataframe(all_data)


