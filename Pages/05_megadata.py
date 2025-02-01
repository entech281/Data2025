import streamlit as st

import opr3
st.set_page_config(layout="wide")
df = opr3.real()


# Sort columns based on the values in the first row (index 0)
#df = df.sort_values(by=0, axis=1)

cc ={
       "weight": st.column_config.NumberColumn(
            width=200,min_value=0, max_value=1,
        step=0.1,pinned=True,default=1.0
    )
}
#st.data_editor(df)
st.data_editor(df,height=1000,column_config=cc)