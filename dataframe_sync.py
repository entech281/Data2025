import logging
from motherduck import con
import pandas as pd
import numpy as np
log = logging.getLogger("df_sync")
import time


def _run_sql(conn,sql):
    s = time.time()
    #log.debug(f"SQL: {sql}")
    conn.execute(sql)
    con.commit()
    rows_affected = con.rowcount
    log.info(f"SQL [{time.time()-s} ms, {rows_affected} rows] :  {sql}")

def sync_df(conn, df: pd.DataFrame, table_name: str, key_field_names=list[str]) -> None:
    """
    Synchronizes a Pandas DataFrame with a MotherDuck table called 'match_cmm'.

    Args:
        conn (duckdb.DuckDBPyConnection): An active MotherDuck connection.
        df (pd.DataFrame): The DataFrame containing match data.
    """
    if df.empty:
        log.warn("DataFrame is empty. No data to sync.")
        return

    # Ensure the table exists
    column_definitions = ", ".join(f'"{col}" {pd_to_duckdb_type(df[col])}' for col in df.columns)
    key_column_list  = ','.join(key_field_names)
    key_condition = " AND ".join([f"match_cmm.{field} = df.{field}" for field in key_field_names])

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {column_definitions},
        PRIMARY KEY({key_column_list})
    );
    """
    conn.execute(create_table_query)


    # Generate column list and placeholders
    #placeholders = ", ".join("?" for _ in df.columns)
    #columns = ", ".join(f'"{col}"' for col in df.columns)
    #updates = ", ".join(f'"{col}" = EXCLUDED."{col}"' for col in df.columns if col not in key_field_names)

    #insert_query = f"""
    #INSERT INTO {table_name} ({columns})
    #VALUES ({placeholders})
    #ON CONFLICT({key_column_list}) DO UPDATE SET {updates};
    #"""

    #conn.executemany(insert_query, df.itertuples(index=False, name=None))


    con.register("df",df)

    #delete rows that conflict with the new ones, if any

    _run_sql(con,f"""
        delete from {table_name}
        using df
        where {key_condition};
    """)

    _run_sql(con,f"""
        insert into {table_name}
        select * from df
    """)

    log.info(f"Synchronization complete inserted: {conn.rowcount} rows.")


def pd_to_duckdb_type(series: pd.Series) -> str:
    """Helper function to map Pandas dtypes to DuckDB SQL types, guessing the best type if needed."""

    dtype_mapping = {
        "int64": "BIGINT",
        "float64": "DOUBLE",
        "object": "TEXT",
        "bool": "BOOLEAN",
        "datetime64[ns]": "TIMESTAMP"
    }

    # First, try the explicit mapping
    dtype = str(series.dtype)

    if dtype in dtype_mapping:
        return dtype_mapping[dtype]

    # If it's a type we haven't explicitly mapped, try to infer the type
    if np.issubdtype(series.dtype, np.integer):
        return "BIGINT"  # For any integer-like types
    elif np.issubdtype(series.dtype, np.floating):
        return "DOUBLE"  # For any floating-point types
    elif np.issubdtype(series.dtype, np.datetime64):
        return "TIMESTAMP"  # For datetime-like types
    elif np.issubdtype(series.dtype, np.bool_):
        return "BOOLEAN"  # For boolean types

    # Default to TEXT if we can't infer
    return "TEXT"


# Example usage with an existing MotherDuck connection

initial_rows = pd.DataFrame({
    "event_key": ["2024sc_cmp", "2024ga_reg"],
    "match_key": ["qm1", "qm2"],
    "score_red": [125, 110],
    "score_blue": [98, 105]
})

more_rows=  pd.DataFrame({
    "event_key": ["2024sc_cmp", "2024ga_reg"],
    "match_key": ["qm1", "qm3"],
    "score_red": [90, 90],
    "score_blue": [90, 90]
})

if __name__ == '__main__':
    sync_df(con, initial_rows,'match_cmm2',['event_key','match_key'])
    sync_df(con, more_rows,'match_cmm2',['event_key','match_key'])

