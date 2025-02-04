import streamlit as st
import pandas as pd
from cached_data import get_matches, get_rankings, get_teams
st.set_page_config(layout="wide")

st.title("281 Scouting")

st.subheader("Open the page list if this looks totally blank")

st.caption("""
This is a demo landing page. put stuff you want users to see on here. 
A good example might be links, very important data, 
or branding information
""" )

st.image("./static/281.png", width=200)


