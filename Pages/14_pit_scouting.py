import streamlit as st
import pandas as pd
from motherduck import con
from opr3 import *
from cached_data import get_teams
from PIL import Image
import io

st.title("Pit Scouting Form")

with st.form("pit_scouting"):
    # Team Selection
    team_list = sorted(get_teams()['team_number'].fillna(0).astype(int).values.tolist())
    team = st.selectbox("Team Number", team_list)
    
    # Physical Specifications
    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("Robot Height Extended w/out bumpers (inches)", min_value=0, max_value=120, step=1, value=60)
        length = st.number_input("Robot Length w/out bumpers (inches)", min_value=0, max_value=60, step=1, value=36)
    with col2:
        weight = st.number_input("Robot Weight w/out bumpers (lbs)", min_value=0, max_value=125, step=1, value=100)
        width = st.number_input("Robot Width w/out bumpers (inches)", min_value=0, max_value=60, step=1, value=36)
    
    # Starting Position
    start_pos = st.selectbox(
        "Preferred Starting Position",
        ["Climb Side", "Center", "Processor Side", "No Preference"]
    )
    
    # Auto Route
    cam_input = st.camera_input(label="Auto Route (draw a picture please)")

    auto_route = []

    if cam_input:
        binary_data = cam_input.read()

        # Convert the image to PNG format
        image = Image.open(io.BytesIO(binary_data))
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        auto_route = [img_byte_arr]
    
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