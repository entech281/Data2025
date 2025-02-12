import streamlit as st
from motherduck import con
from pygwalker.api.streamlit import StreamlitRenderer

st.set_page_config(layout="wide")
# Add Title
st.title("Chart Builder-- TBA OPRs")
CACHE_TIME_SECS=240
# You should cache your pygwalker renderer, if you don't want your memory to explode
@st.cache_resource(ttl=CACHE_TIME_SECS)
def get_pyg_renderer() -> "StreamlitRenderer":
    df =con.sql("""
            select er.team_number, er.event_key,er.wins, er.losses, er.ties,er.rank,er.dq, op.oprs, op.ccwms, op.dprs
            from frc_2025.tba.event_rankings er
            join frc_2025.tba.oprs op on er.team_number = op.team_number and er.event_key = op.event_key
            order by er.rank asc;
    """).df()
    df['team_number'] = df['team_number'].astype(str)
    # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
    #df = pd.melt(df, id_vars=['team_id','batch'],var_name='attribute',value_name='weighted_score')
    return StreamlitRenderer(df, spec="./gw2_config.json", spec_io_mode="rw",height=800)

renderer = get_pyg_renderer()

renderer.explorer()