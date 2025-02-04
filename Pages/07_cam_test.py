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

    # Convert the image to PNG format
    image = Image.open(io.BytesIO(binary_data))
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Insert the PNG image into the database
    con.execute("UPDATE cam_test SET img = ? WHERE id = 1;", [img_byte_arr])
    st.write("Successfully inserted image into database")

    # Retrieve the image from the database
    st.write("Retrieving image from database")
    retrieved_image = con.sql("SELECT img FROM cam_test WHERE id = 1").df().iloc[0, 0]
    retrieved_image = Image.open(io.BytesIO(retrieved_image))
    st.image(retrieved_image)
