import pandas as pd
import pygwalker as pyg
import streamlit as st
import opr3
from pygwalker.api.streamlit import StreamlitRenderer

st.set_page_config(layout="wide")
# Add Title
st.title("chart Kitchen")


# You should cache your pygwalker renderer, if you don't want your memory to explode
@st.cache_resource
def get_pyg_renderer() -> "StreamlitRenderer":
    df =opr3.fake_analyze()
    # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
    return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")


renderer = get_pyg_renderer()

renderer.explorer()


