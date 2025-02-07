import streamlit as st
from motherduck import con
import pandas as pd
from cached_data import get_teams
from opr3 import *

# Ok I copied and pasted this but that is definitely not the 
# right way to do it
# I was gonna import it but the filename starts with a number
@st.cache_data( ttl=120)
def get_historical_match_data() :
    df = matches_over_time()  # Ensure your DataFrame has 'team_id' and z-score columns
    df.reset_index(drop=True, inplace=True)
    #df['team_id'] = df['team_id'].apply(str)
    return df


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

team_list = sorted(get_teams()['team_number'].values.tolist())

event_list = con.sql("SELECT DISTINCT event_key FROM tba.matches").df()['event_key'].values.tolist()
matches_df = con.sql("SELECT * FROM tba.matches").df()

team = st.selectbox("Team Number", team_list)
events = st.multiselect("Event", event_list)



if team is not None and len(events) > 0:
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
        # Calculate raw metrics
        raw_stats = calculate_raw_opr(match_slice)
        raw_stats = raw_stats[raw_stats['team_id'] == team]
        
        # Add z-scores
        numeric_cols = raw_stats.select_dtypes(include=['float64', 'int64']).columns
        numeric_cols = [col for col in numeric_cols if col not in ['team_id', 'match_num']]
        with_z = add_zscores(raw_stats, numeric_cols)
        
        with_z['match_num'] = i
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