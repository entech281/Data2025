import streamlit as st
from motherduck import con
from pygwalker.api.streamlit import StreamlitRenderer
import cached_data
st.set_page_config(layout="wide")
# Add Title
st.title("Chart Builder-- TBA OPRs")
CACHE_TIME_SECS=240
# You should cache your pygwalker renderer, if you don't want your memory to explode
@st.cache_resource(ttl=CACHE_TIME_SECS)
def get_pyg_renderer() -> "StreamlitRenderer":
    df =cached_data.get_oprs_and_ranks()
    df['team_number'] = df['team_number'].astype(str)
    # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
    #df = pd.melt(df, id_vars=['team_id','batch'],var_name='attribute',value_name='weighted_score')
    return StreamlitRenderer(df, spec="./gw2_config.json", spec_io_mode="rw",height=800)

renderer = get_pyg_renderer()

renderer.explorer()