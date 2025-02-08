import streamlit as st
from motherduck import con
import pandas as pd
from cached_data import get_teams
from opr3 import *
import altair as alt
import math


def get_team_stats(team_number: int, df: pd.DataFrame) -> pd.DataFrame:
    """
    Get historical statistics for a specific team with both raw and z-scored metrics.
    
    Args:
        team_number (int): FRC team number
        df (pd.DataFrame): DataFrame containing data to analyze
        
    Returns:
        pd.DataFrame: DataFrame with raw metrics and z-scores over time
    """
    # Calculate raw OPR metrics
    raw_metrics = calculate_raw_opr(df)
    
    # Filter for specific team
    team_data = raw_metrics[raw_metrics['team_id'] == team_number]
    
    if len(team_data) == 0:
        return pd.DataFrame()
    
    # Add z-scores for numeric columns
    numeric_cols = team_data.select_dtypes(include=['float64', 'int64']).columns
    z_scores = add_zscores(team_data, numeric_cols)
    
    # Join raw and z-scored metrics
    result = pd.concat([team_data, z_scores], axis=1)
    
    # Clean and sort
    result = result.fillna(0)
    # result = result.sort_values(['event_key', 'match_number'])
    
    return result



st.title("Team Spotlight")

team_list = sorted(get_teams()['team_number'].fillna(0).values.tolist())


# TODO
# Make all of these one one sql statement
event_list = con.sql("SELECT DISTINCT event_key FROM tba.matches").df()['event_key'].values.tolist()
matches_df = con.sql("SELECT * FROM tba.matches").df()
tags_df = con.sql(f"""SELECT te.team_number, count(ta.tag), ta.tag
                        FROM tba.teams te
                        LEFT JOIN scouting.tags ta ON
                        (ta.team_number = te.team_number)
                        GROUP BY te.team_number, ta.tag;""").df()
pit_df = con.sql("SELECT * FROM scouting.pit").df()


team = st.selectbox("Team Number", team_list, format_func=lambda team: int(team))
events = st.pills("Event", event_list, selection_mode="multi")



if team is not None and events is not None and len(events) > 0:
    st.subheader(f"Team {team} Performance")
    
    # Get matches for team
    team_matches = matches_df[
        ((matches_df['red1'] == team) | (matches_df['red2'] == team) | (matches_df['red3'] == team) |
         (matches_df['blue1'] == team) | (matches_df['blue2'] == team) | (matches_df['blue3'] == team)) &
        (matches_df['event_key'].isin(events))
    ].sort_values(['event_key', 'match_number'])
    
    # Calculate running stats for each match
    match_stats = []
    for i in range(1, len(team_matches) + 1):
        match_slice = team_matches.iloc[:i]

        raw_stats = calculate_raw_opr(match_slice)
        numeric_cols = raw_stats.select_dtypes(include=['float64', 'int64']).columns
        numeric_cols = [col for col in numeric_cols if col not in ['team_id', 'match_num']]
        with_z = add_zscores(raw_stats, numeric_cols)
        
        with_z['match_num'] = i
        with_z = with_z[with_z['team_id'] == team]
        with_z = with_z.fillna(0)

        match_stats.append(with_z)

        
    
    # Combine match stats
    team_stats = pd.concat(match_stats)
    
    # st.write(f"Stats shape: {team_stats.shape}")  # Debug
    
    # Select metrics and their z-scores
    base_metrics = [col for col in team_stats.columns 
                   if col not in ['team_id', 'margin', 'their_score', 'match_num']
                   and not col.endswith('_z')]
    
    # Create chart dataframe
    chart_df = pd.DataFrame({"Metric": [], "Trend": []})
    
    # Add both raw and z-score metrics
    for metric in base_metrics:
        raw_values = team_stats[metric].tolist()
        z_values = team_stats[f"{metric}_z"].tolist()
        
        chart_df = pd.concat([
            chart_df,
            pd.DataFrame({
                "Metric": [f"{metric} (Raw)", f"{metric} (Z-Score)"],
                "Trend": [raw_values, z_values]
            })
        ], ignore_index=True)
    
    st.dataframe(
        chart_df,
        column_config={
            "Metric": "Performance Metric",
            "Trend": st.column_config.LineChartColumn(
                "Performance Over Time",
                width="medium"
            )
        },
        hide_index=True
    )

    pit_df = pit_df[(pit_df['team_number']) == team]
    if not pit_df.empty:
        st.divider()
        st.subheader("📝 Pit Scouting Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Height", f"{pit_df['height'].iloc[0]}\"")
            st.metric("Width", f"{pit_df['width'].iloc[0]}\"")
        
        with col2:
            st.metric("Length", f"{pit_df['length'].iloc[0]}\"")
            st.metric("Weight", f"{pit_df['weight'].iloc[0]} lbs")
        
        with col3:
            st.metric("Preferred Start", pit_df['start_position'].iloc[0])
            st.metric("Preferred Scoring", pit_df['preferred_scoring'].iloc[0])
        
        # Strategy section
        st.subheader("🎯 Strategy")
        capabilities = pit_df['scoring_capabilities'].iloc[0].split(',')
        st.write("**Scoring Capabilities:**", ", ".join(capabilities))
        
        # Auto route
        if pit_df['auto_route'].iloc[0] is not None:
            st.subheader("🤖 Auto Route")
            st.image(pit_df['auto_route'].iloc[0], use_container_width=True)
        
        # Notes section
        if pit_df['notes'].iloc[0]:
            st.subheader("📌 Notes")
            st.info(pit_df['notes'].iloc[0])
        
        # Metadata
        st.caption(f"Last updated by {pit_df['author'].iloc[0]} on {pit_df['created_at'].iloc[0].strftime('%Y-%m-%d %H:%M')}")

    else:
        st.info("No pit scouting data available for this team yet")



if team is not None:
    
    st.subheader("Data")

    # Create pivot table
    pivot_df = tags_df[tags_df['team_number'] == team].pivot_table(
        index='team_number',
        columns='tag',
        values='count(ta.tag)',
        fill_value=0
    ).reset_index()

    # Melt for Altair visualization
    chart_df = pivot_df.melt(
        id_vars=['team_number'],
        var_name='tag',
        value_name='count'
    )

    # Create chart
    c = alt.Chart(chart_df).mark_bar().encode(
        x='tag:N',
        y='count:Q'
    )
    


    if pivot_df.empty:
        st.write("No tag data to display :slightly_frowning_face:")
        st.write("Here is a squirrel to make you feel less sad")
        st.image("./static/squirrel.png", width=75)
        st.link_button("Image credit", "https://xkcd.com/1503")
    else:
        st.altair_chart(c)
        st.dataframe(pivot_df.drop(columns='team_number'))
