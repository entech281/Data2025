import streamlit as st
from motherduck import con
from pygwalker.api.streamlit import StreamlitRenderer
from cached_data import get_event_list,get_oprs_and_ranks_for_event,get_most_recent_event
st.set_page_config(layout="wide")
# Add Title
st.title("Chart Builder-- TBA OPRs")
CACHE_TIME_SECS=240

event_list = get_event_list()
selected_event = st.pills("Event", event_list, default=get_most_recent_event(), selection_mode="single")
if selected_event is None:
    st.caption("Select an Event")
    st.stop()


@st.cache_resource(ttl=CACHE_TIME_SECS)
def get_pyg_renderer() -> "StreamlitRenderer":
    df =get_oprs_and_ranks_for_event(selected_event)
    df['team_number'] = df['team_number'].astype(str)
    # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
    #df = pd.melt(df, id_vars=['team_id','batch'],var_name='attribute',value_name='weighted_score')
    return StreamlitRenderer(df, spec="./gw2_config.json", spec_io_mode="rw",height=800)

renderer = get_pyg_renderer()

renderer.explorer()