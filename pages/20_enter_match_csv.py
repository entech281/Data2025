import streamlit as st
import pandas as pd
import re
from motherduck import con

st.title("Upload Match CSV Data")

def normalize_column_name(name: str) -> str:
    """
    Normalize a CSV header to a database column name.
    
    This lowercases the string, replaces any non-alphanumeric characters 
    with underscores and strips any leading/trailing underscores.
    
    Parameters:
        name (str): The original column name.
    
    Returns:
        str: Normalized column name.
    """
    # Lowercase the header.
    new_name = name.lower()

    #st.write(new_name)
    new_name = new_name.replace("’", "")
    #st.write(new_name)
    # Replace non-alphanumeric characters with underscore.
    new_name = re.sub(r"[^a-z0-9]+", "_", new_name)
    # Remove leading/trailing underscores.
    new_name = new_name.strip("_")
    return new_name


def infer_duckdb_type(series):
    """Infer DuckDB data type from Pandas Series."""
    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"
    elif pd.api.types.is_float_dtype(series):
        return "DOUBLE"
    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"
    elif pd.api.types.is_string_dtype(series):
        return "TEXT"
    else:
        return "TEXT"  # Default to TEXT for unknown types


def generate_create_table_sql(df, table_name):
    """Generate DuckDB CREATE TABLE statement from a DataFrame."""
    columns = []
    for col in df.columns:
        duckdb_type = infer_duckdb_type(df[col])
        colname = normalize_column_name(col)
        columns.append(f'"{colname}" {duckdb_type}')

    columns_sql = ",\n    ".join(columns)
    create_table_sql = f"CREATE TABLE {table_name} (\n    {columns_sql}\n);"

    return create_table_sql

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])




if uploaded_file is not None:
    try:
        # Read CSV file into DataFrame
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data (raw headers):")
        st.dataframe(df)
        
        # Normalize column names to match the database schema.
        df.columns = [normalize_column_name(col) for col in df.columns]
        
        st.write("Preview of uploaded data (normalized headers):")
        st.dataframe(df)

        st.write("Create Table Statement")
        st.code(generate_create_table_sql(df,"scouting.matches2"))
        # Confirm before upload
        if st.button("Upload to Database"):
            # Build dynamic SQL query based on normalized column names.
            columns = df.columns.tolist()
            col_str = ", ".join(columns)
            placeholders = ", ".join(["?"] * len(columns))
            sql = f"INSERT INTO scouting.matches ({col_str}) VALUES ({placeholders})"
            
            # Convert DataFrame rows to list of tuples
            rows = df.values.tolist()
            
            # Use executemany if supported
            con.executemany(sql, rows)
            st.success(f"Uploaded {len(rows)} rows successfully!")
    except Exception as e:
        st.error(f"Error uploading CSV: {e}")