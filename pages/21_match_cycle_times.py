import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages_util.event_selector import event_selector
import log_tools
from log_tools.cycle_times import load_all_folders_in_path
from pathlib import Path
st.set_page_config(layout="wide")
st.title("Match Cycle Times")
selected_event = event_selector()

st.header("What is a Cycle?")
st.markdown("""
A **Cycle** is the time between Intake Coral Sensor transitions from False to True.

Each cycle can be L1, L2, L3, or L4. This is measured by how far up the elevator goes during the cycle.

A Cycle is composed of two parts:
* **travel_time**: the time traveling to and from the reef. Travel time is improved by optimizing intake and alignment
* **deploy_time**: the time to deploy. This is measured by taking the earliest time the elevator first goes up, and the latest time the elevator goes to zero, during a single cycle  
Deploy time is improved by elevator and operator sequence timings.

""")
st.caption("""
The x axis is the match index, with time progressing to the right.
The y axis is total cycle time, in seconds.
The bubble size shows the fraction of the cycle that was deployment time (bigger is more time.
Hover over each point to see the details, including match number
""")
MATCH_LOG_FOLDER = './match_logs'

all_datasets = load_all_folders_in_path(Path(MATCH_LOG_FOLDER),True)


def build_cycle_section(summary_df: pd.DataFrame, section_name:str):
    st.subheader(f"Data for {section_name}")
    df = summary_df.copy()
    df['group'] = section_name
    fig = px.scatter(summary_df,
                     x='match_index',
                     y='duration',
                     color='cycle_type',
                     hover_data='match_key',
                     size='mark_size')

    st.plotly_chart(fig, use_container_width=True, height=600)

    grouped_df = df.groupby(['group','cycle_type']).agg({
        'total_cycle_time': ['min','max','median','mean'],
        'total_travel': ['min','max','median','mean'],
        'deploy_time': ['min','max','median','mean']
    })
    #grouped_df = grouped_df.style.background_gradient(cmap="RdYlGn_r").format("{:.2f}")


    st.dataframe(grouped_df,use_container_width=True)
    return grouped_df

all_dfs = []
for d in all_datasets:
    summary_df = d['analyzed_df']
    name = d['name']
    d = build_cycle_section(summary_df, name)
    all_dfs.append(d)

st.subheader("Combined Data")
all_together = pd.concat(all_dfs)
st.dataframe(all_together,use_container_width=True)
