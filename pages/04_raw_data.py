import streamlit as st
import cached_data
from motherduck import con
from PIL import Image
import base64

st.set_page_config(layout="wide")

def bytes_to_base64(byte_array):
    if byte_array is None:
        return ""
    return base64.b64encode(byte_array).decode("utf-8")

def image_formatter(byte_array):
    base64_str = bytes_to_base64(byte_array)
    return f'<img src="data:image/png;base64,{base64_str}" width="200">'

display_config = {
    'id': st.column_config.NumberColumn("Id", format="%d"),
    'start': st.column_config.DatetimeColumn('Start', format="D MMM YYYY, h:mm a"),
    'end': st.column_config.DatetimeColumn('End', format="D MMM YYYY, h:mm a"),
    'started': st.column_config.DatetimeColumn('End', format="D MMM YYYY, h:mm a"),
    'updated_at': st.column_config.DatetimeColumn('End', format="D MMM YYYY, h:mm a"),
    'event_id': st.column_config.NumberColumn("Id", format="%d"),
    'auto_route': st.column_config.Column("Auto Route")
}

#getting these from cache-- so that we can save database resources
# in production, we'd cache things that dont change often

events = cached_data.get_teams()  # get from cache this will hardly ever change
matches= cached_data.get_matches()  #this one is not executed each page refresh.
rankings = cached_data.get_rankings()
pit = con.sql("SELECT * FROM scouting.pit").df()

# Format images in pit data
if 'auto_route' in pit.columns:
    pit['auto_route'] = pit['auto_route'].apply(image_formatter)

st.title("Raw Data")
st.header(f"Events ({len(events)})")
st.dataframe(events,column_config=display_config)

st.header(f"Matches  ({len(matches)})")
st.dataframe(matches,column_config=display_config)

st.header(f"Rankings ({len(rankings)})")
st.dataframe(rankings,column_config=display_config)

st.header(f"Pit ({len(pit)})")
st.markdown(pit.to_html(escape=False), unsafe_allow_html=True)