import streamlit as st
import duckdb
from sqlalchemy import create_engine

import pandas as pd
import polars as pl
DB_FILE='test.duckdb'
con = duckdb.connect(DB_FILE)
TEST_TABLE="TEST_TABLE"
st.title("Demo Data Editor")

df = con.sql(f"select * from test.{TEST_TABLE}").df()
df = st.data_editor(df,num_rows="dynamic")
confirm = st.button('Save Changes')

if confirm:
    df.to_sql(TEST_TABLE,con,if_exists='replace',index=False)

con.close()
