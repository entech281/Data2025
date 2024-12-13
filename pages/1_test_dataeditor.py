import streamlit as st
from motherduck import con

TEST_TABLE = "scouting.test"
st.title("Demo Table Editor")
st.subheader("edit contents of table scouting.test in motherduck database")

st.caption("""This is a demo of editing the rows in a table.
not for end users, this builds a way to edit stuff for admins or developers
""")

