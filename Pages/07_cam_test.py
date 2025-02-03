import streamlit as st
import pandas as pd
from motherduck import con
from PIL import Image
import io

st.set_page_config(layout="wide")

st.title("Camera Test")

cam_input = st.camera_input(label="Camera Test")


if cam_input:
    st.image(cam_input)
    binary_data = cam_input.read()

    con.execute("UPDATE cam_test SET img = ? WHERE id = 1;", [binary_data])
    st.write("Successfully inserted image into database")
    
    st.write("Retrieving image from database")
    retrieved_image = con.sql("SELECT img FROM cam_test WHERE id = 1").df().iloc[0, 0]
    retrieved_image = Image.open(io.BytesIO(retrieved_image))
    st.image(retrieved_image)

    
