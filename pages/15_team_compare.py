import streamlit as st
from motherduck import con
import pandas as pd
from cached_data import get_teams,get_event_list
from opr3 import *
import altair as alt
from pages_util.team_stats import get_team_stats

st.title("Team Comparison")

# Get data
team_list = sorted(get_teams()['team_number'].fillna(0).astype(int).values.tolist())
event_list = get_event_list()

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
                
                t1_opr = float(event_rankings.loc[event_rankings['team_number'] == team1, 'oprs'].iloc[0])
                t2_opr = float(event_rankings.loc[event_rankings['team_number'] == team2, 'oprs'].iloc[0])
                t1_rank = int(event_rankings.loc[event_rankings['team_number'] == team1, 'rank'].iloc[0])
                t2_rank = int(event_rankings.loc[event_rankings['team_number'] == team2, 'rank'].iloc[0])
                
                # Compute delta for OPR
                delta_opr = t1_opr - t2_opr
                if delta_opr > 0:
                    opr_status = f"Team {team1} leads"
                elif delta_opr < 0:
                    opr_status = f"Team {team2} leads"
                else:
                    opr_status = "Tied"
                
                # Compute delta for Rank. (Lower rank is better.)
                delta_rank = t2_rank - t1_rank  
                if delta_rank > 0:
                    rank_status = f"Team {team1} leads"
                elif delta_rank < 0:
                    rank_status = f"Team {team2} leads"
                else:
                    rank_status = "Tied"
                
                with col1:
                    st.metric("OPR Difference", f"{abs(t1_opr - t2_opr):.1f}", delta=opr_status)
                with col2:
                    st.write("Idk what to put here yet")
                    st.image("static/squirrel.png", width=50)
                with col3:
                    st.metric("Rank Difference", abs(t1_rank - t2_rank), delta=f"{rank_status}")
    with st.container(border=True):
        # Overall Average Rankings Section
        st.subheader("Overall Average Rankings")
        # Filter rankings for the selected events and teams
        team1_all = ranking_df[(ranking_df['team_number'] == team1) & (ranking_df['event_key'].isin(events))]
        team2_all = ranking_df[(ranking_df['team_number'] == team2) & (ranking_df['event_key'].isin(events))]

        if not team1_all.empty and not team2_all.empty:
            avg_team1 = team1_all[['oprs', 'rank']].mean()
            avg_team2 = team2_all[['oprs', 'rank']].mean()
            
            col1, col2, col3 = st.columns(3)
            
            # OPR Comparison for overall averages
            delta_opr_avg = avg_team1['oprs'] - avg_team2['oprs']
            if delta_opr_avg > 0:
                overall_opr_status = f"Team {team1} leads"
            elif delta_opr_avg < 0:
                overall_opr_status = f"Team {team2} leads"
            else:
                overall_opr_status = "Tied"
            
            # Rank Comparison for overall averages (note: lower is better)
            delta_rank_avg = avg_team2['rank'] - avg_team1['rank']
            if delta_rank_avg > 0:
                overall_rank_status = f"Team {team1} leads"
            elif delta_rank_avg < 0:
                overall_rank_status = f"Team {team2} leads"
            else:
                overall_rank_status = "Tied"
        
            with col1:
                st.metric("Avg OPR Difference", f"{abs(delta_opr_avg):.1f}", delta=overall_opr_status)
            with col2:
                st.write("Idk what to put here yet")
                st.image("static/squirrel.png", width=50)
            with col3:
                st.metric("Avg Rank Difference", f"{abs(delta_rank_avg):.1f}", delta=overall_rank_status)
        else:
            st.info("Insufficient overall rankings data for one or both teams.")

    # Performance comparison
    st.subheader("Performance Metrics")
    
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

    st.dataframe(
        comparison_df,
        column_config={
            'Metric': 'Metric',
            f'Team {team1}': st.column_config.NumberColumn(f'Team {team1}', format="%.2f"),
            f'Team {team2}': st.column_config.NumberColumn(f'Team {team2}', format="%.2f"),
            'Difference': st.column_config.NumberColumn('Difference')
        },
        hide_index=True
    )

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
