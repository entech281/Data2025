import streamlit as st
from motherduck import con
import pandas as pd
from cached_data import get_teams
from opr3 import *
import altair as alt
from pages_util.team_stats import get_team_stats

st.title("Team Comparison")

# Get data
team_list = sorted(get_teams()['team_number'].fillna(0).astype(int).values.tolist())
event_list = con.sql("SELECT DISTINCT event_key FROM tba.matches ORDER BY event_key").df()['event_key'].values.tolist()

# Team selection
col1, col2 = st.columns(2)
with col1:
    team1 = st.selectbox("Team 1", team_list, key="team1")
with col2:
    team2 = st.selectbox("Team 2", team_list, key="team2")

events = st.pills("Events", event_list, selection_mode="multi")

if team1 and team2 and len(events) > 0:
    # Get rankings data
    ranking_df = con.execute("""
        SELECT er.team_number, er.rank, o.oprs, er.event_key
        FROM tba.event_rankings er
        JOIN tba.oprs o ON er.team_number = o.team_number 
        AND er.event_key = o.event_key
        WHERE er.team_number IN (?, ?) AND er.event_key IN ({})
    """.format(','.join([f"'{e}'" for e in events])), 
    [team1, team2]).df()
    
    # Rankings comparison
    st.subheader("Rankings Comparison")
    for event in events:
        event_rankings = ranking_df[ranking_df['event_key'] == event]
        if not event_rankings.empty:
            with st.container(border=True):
                st.caption(f"Event: {event}")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    t1_opr = event_rankings[event_rankings['team_number'] == team1]['oprs'].iloc[0]
                    t2_opr = event_rankings[event_rankings['team_number'] == team2]['oprs'].iloc[0]
                    st.metric("OPR", f"{t1_opr:.1f}", f"{t2_opr:.1f}")
                
                with col2:
                    t1_rank = event_rankings[event_rankings['team_number'] == team1]['rank'].iloc[0]
                    t2_rank = event_rankings[event_rankings['team_number'] == team2]['rank'].iloc[0]
                    st.metric("Rank", int(t1_rank), int(t2_rank))
                
                with col3:
                    rank_diff = int(t1_rank) - int(t2_rank)
                    leader = team1 if rank_diff < 0 else team2
                    st.metric("Rank Difference", abs(rank_diff), f"Team {leader} leads")

    # Performance comparison
    # st.subheader("Performance Metrics")
    
    # Get match data
    matches_df = con.sql("""
        SELECT * FROM tba.matches 
        WHERE event_key IN ({})
    """.format(','.join([f"'{e}'" for e in events]))).df()
    
    # Calculate stats for both teams
    team1_stats = get_team_stats(team1, matches_df)
    team2_stats = get_team_stats(team2, matches_df)
    
    # Compare metrics
    metrics = [col for col in team1_stats.columns 
              if col not in ['team_id', 'margin', 'their_score']
              and not col.endswith('_z')]
    
    # Create comparison chart with proper numeric conversions
    comparison_data = []
    for metric in metrics:
        val_team1 = float(team1_stats[metric].iloc[0][0])
        val_team2 = float(team2_stats[metric].iloc[0][0])
        comparison_data.append({
            'Metric': metric,
            f'Team {team1}': val_team1,
            f'Team {team2}': val_team2,
            'Difference': val_team1 - val_team2
        })

    comparison_df = pd.DataFrame(comparison_data)

    # Determine min and max values for the bar chart column
    diff_min = comparison_df['Difference'].min()
    diff_max = comparison_df['Difference'].max()

    # st.dataframe(
    #     comparison_df,
    #     column_config={
    #         'Metric': 'Metric',
    #         f'Team {team1}': st.column_config.NumberColumn(f'Team {team1}', format="%.2f"),
    #         f'Team {team2}': st.column_config.NumberColumn(f'Team {team2}', format="%.2f"),
    #         'Difference': st.column_config.BarChartColumn(
    #             'Difference',
    #             y_min=diff_min,
    #             y_max=diff_max
    #         )
    #     },
    #     hide_index=True
    # )

    # Pit data comparison
    st.subheader("Robot Specifications")
    pit_df = con.execute("""
        SELECT * FROM scouting.pit 
        WHERE team_number IN (?, ?)
        ORDER BY created_at DESC
    """, [team1, team2]).df()
    
    if not pit_df.empty:
        specs = ['height', 'weight', 'length', 'width']
        for spec in specs:
            col1, col2 = st.columns(2)
            with col1:
                if not pit_df[pit_df['team_number'] == team1].empty:
                    value = pit_df[pit_df['team_number'] == team1][spec].iloc[0]
                    st.metric(f"Team {team1} {spec}", value)
            with col2:
                if not pit_df[pit_df['team_number'] == team2].empty:
                    value = pit_df[pit_df['team_number'] == team2][spec].iloc[0]
                    st.metric(f"Team {team2} {spec}", value)

    else:
        st.info(f"No specs data to display for teams {team1} and {team2} :slightly_frowning_face:")
        st.info("Here is a squirrel to make you feel less sad")
        st.image("./static/squirrel.png", width=75)
        st.link_button("Image credit (Click me)", "https://xkcd.com/1503")
