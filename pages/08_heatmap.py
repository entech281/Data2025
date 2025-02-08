import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid
# Load your DataFrame (replace this with your actual data loading method)
import opr3
st.set_page_config(layout="wide")
df = opr3.latest_match() # Ensure your DataFrame has 'team_id' and z-score columns
df.reset_index(drop=True, inplace=True)
df = df.set_index('team_id')
df = df.T


def style_dataframe(df):
    return df.style.set_table_styles(
        [{
            'selector': 'th',
            'props': [
                ('background-color', '#4CAF50'),
                ('color', 'white'),
                ('font-family', 'Arial, sans-serif'),
                ('font-size', '10px')
            ]
        },
            {
                'selector': 'td',
                'props': [
                    ('font-size', '8px')
                ]
            }

        ]
    )

#cols = df.columns
#s = set(df.columns)
#s.remove('team_id')
#columns = ['team_id'] + list(s)
styled_df = style_dataframe(df)
styled_df = df.style.background_gradient(cmap='RdYlGn',vmin=-3.0, vmax=3.0)
styled_df.format("{:.2f}")

st.write(styled_df.to_html(), unsafe_allow_html=True)



