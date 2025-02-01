import streamlit as st
import pandas as pd
from motherduck import con

st.set_page_config(layout="wide")

st.title("Camera Test")

cam_input = st.camera_input(label="Camera Test")

if cam_input:
    st.image(cam_input)
    binary_data = cam_input.read()
    st.image(binary_data)