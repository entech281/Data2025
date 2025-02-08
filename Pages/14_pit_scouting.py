import streamlit as st
import pandas as pd
from motherduck import con
from opr3 import *
from cached_data import get_teams

st.title("Pit Scouting Form")

with st.form("pit_scouting"):
    # Team Selection
    team_list = sorted(get_teams()['team_number'].fillna(0).astype(int).values.tolist())
    team = st.selectbox("Team Number", team_list)
    
    # Physical Specifications
    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("Robot Height Extended w/out bumpers (inches)", min_value=0.0, max_value=100.0)
        length = st.number_input("Robot Length w/out bumpers (inches)", min_value=0.0, max_value=100.0)
    with col2:
        weight = st.number_input("Robot Weight w/out bumpers (lbs)", min_value=0.0, max_value=150.0)
        width = st.number_input("Robot Width w/out bumpers (inches)", min_value=0.0, max_value=100.0)
    
    # Starting Position
    start_pos = st.selectbox(
        "Preferred Starting Position",
        ["Climb Side", "Center", "Processor Side", "No Preference"]
    )
    
    # Auto Route
    auto_route = st.text_area("Auto Route Description")
    
    scoring_possibilities = ["Coral L1", "Coral L2", "Coral L3", "Coral L4", "Processor", "Barge", "Deep Climb", "Shallow Climb"]

    # Scoring Capabilities
    scoring_capabilities = st.pills(
        "Scoring Capabilities",
        scoring_possibilities,
        selection_mode="multi"
    )
    
    # Preferred Scoring
    preferred_scoring = st.pills(
        "Preferred Scoring Method",
        scoring_possibilities,
        selection_mode="multi",
        key="oipauergh"
)
    
    # Additional Notes
    notes = st.text_area("Additional Notes")
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        # Create data for insertion
        data = {
            'team_number': team,
            'height': height,
            'weight': weight,
            'length': length,
            'width': width,
            'start_position': start_pos,
            'auto_route': auto_route,
            'scoring_capabilities': ','.join(scoring_capabilities),
            'preferred_scoring': preferred_scoring,
            'notes': notes
        }

        st.write(data)
        
        # Insert into database
        # try:
        #     con.sql("""
        #         INSERT INTO scouting.pit_data 
        #         (team_number, height, weight, length, width, 
        #         start_position, auto_route, scoring_capabilities, 
        #         preferred_scoring, notes)
        #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        #     """, [
        #         data['team_number'], data['height'], data['weight'],
        #         data['length'], data['width'], data['start_position'],
        #         data['auto_route'], data['scoring_capabilities'],
        #         data['preferred_scoring'], data['notes']
        #     ])
        #     st.success("Data saved successfully!")
        # except Exception as e:
        #     st.error(f"Error saving data: {str(e)}")