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
  281, 342, 343, 1051, 1102, 1287, 1319, 1758, 2815, 3489, 3490, 4451, 4533, 4864, 5130, 6167, 6366, 7085, 8137, 8575, 9315, 9571, 10231, 10367, 10388, 10591, 10599, 10619
)
                   """
                     ).df()
st.dataframe(all_data)


