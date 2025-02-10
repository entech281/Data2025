# this contains the code to create schmea objects,
# if we have manually created tables
from motherduck import con



def create_schema():
    con.sql("""
        create or replace table scouting.test (
            id INTEGER PRIMARY KEY,
            foo varchar,
            bar varchar,
            mod_dte timestamp default current_timestamp
        );
    """)

    con.sql("""
        create or replace table scouting.tags (
            team_number INTEGER PRIMARY KEY,
            tag varchar,
             mod_dte timestamp default current_timestamp
        );
    """)

    # create a handy view over this table that creates timestamps for the windows
    con.sql(f"""
        CREATE VIEW IF NOT EXISTS frc_2025.scouting.v_match_cmm AS (
            select *,  
            TO_TIMESTAMP(window_start_actual_time) AS start_time, 
            TO_TIMESTAMP(window_end_actual_time) AS end_time
            from frc_2025.scouting.match_cmm
        )
    """)