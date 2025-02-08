import streamlit as st
import cached_data
st.set_page_config(layout="wide")

display_config = {
    'id': st.column_config.NumberColumn(  "Id", format="%d" ),
    'start': st.column_config.DatetimeColumn( 'Start', format="D MMM YYYY, h:mm a"),
    'end': st.column_config.DatetimeColumn('End', format="D MMM YYYY, h:mm a"),
    'started': st.column_config.DatetimeColumn('End', format="D MMM YYYY, h:mm a"),
    "updated_at": st.column_config.DatetimeColumn('End', format="D MMM YYYY, h:mm a"),
    'event_id':st.column_config.NumberColumn(  "Id", format="%d" ),
}
#getting these from cache-- so that we can save database resources
# in production, we'd cache things that dont change often

events = cached_data.get_teams()  # get from cache this will hardly ever change
matches= cached_data.get_matches()  #this one is not executed each page refresh.
rankings = cached_data.get_rankings()


st.title("Raw Data")
st.header(f"Events ({len(events)})")
st.dataframe(events,column_config=display_config)

st.header(f"Matches  ({len(matches)})")
st.dataframe(matches,column_config=display_config)

st.header(f"Rankings ({len(rankings)})")
st.dataframe(rankings,column_config=display_config)