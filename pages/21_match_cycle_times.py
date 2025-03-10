import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages_util.event_selector import event_selector


st.set_page_config(layout="wide")
st.title("Match Cycle Times")
selected_event = event_selector()

st.header("What is a Cycle?")
st.markdown("""
A **Cycle** is the time between when the Intake Coral Sensor transitions from False to True.

Each cycle can be L1, L2, L3, or L4. This is measured by how far up the elevator goes during the cycle.

A Cycle is composed of three parts:
* **travel_time**: the time traveling to and from the reef. Travel time is improved by optimizing intake and alignment
* **deploy_time**: the time to deploy. This is measured by taking the earliest time the elevator first goes up, and the latest time the elevator goes to zero, during a single cycle  
Deploy time is improved by elevator and operator sequence timings.

""")

CACHE_TIME_SECS=1200

df = pd.read_csv("./data/cycle_data.csv")
df = df [ df['event_key'] == selected_event]
df = df [ df['match_type'] != 'Prac']
df = df.dropna()
df['total_travel'] = df['travel_from'] + df['travel_to']
df['match_key'] = df['match_type'] + df['match_number'].astype('str')
df['deploy_time'] = df['deploy']
df['mark_size'] = df['deploy_time'].astype('int')
df.sort_values(by=['cycle_timestamp'],ascending=True)
df.index.name='index'
details_df = df

st.subheader("Total Cycle Times (s)")
st.caption("""
The x axis is the match index, with time progressing to the right.
The y axis is total cycle time, in seconds.
The bubble size shows the fraction of the cycle that was deployment time (bigger is more time.
Hover over each point to see the details, including match number
""")

fig = px.scatter(details_df,
                 x='match_index',
                 y='duration',
                 color='cycle_type',
                 hover_data='match_key',
                 size='mark_size')

st.plotly_chart(fig, use_container_width=True,height=600)


st.subheader("Cycle Deploy Times (s)")
st.caption("""
The x axis is the match index, with time progressing to the right.
The y axis is cycle deploy time, in seconds.
The bubble size shows the fraction of the cycle that was deployment time (bigger is more time.
Hover over each point to see the details, including match number
""")
fig = px.scatter(details_df,
                 x='match_index',
                 y='deploy_time',
                 color='cycle_type',
                 hover_data='match_key')
fig.update_traces(marker=dict(size=15))
st.plotly_chart(fig, use_container_width=True)




#details_df = details_df [ ['start_timestamp','event_key','match_type','match_number','cycle_type','duration','total_travel','deploy']]
st.header("Raw Cycle Times")
st.dataframe(details_df,hide_index=True,height=600)

