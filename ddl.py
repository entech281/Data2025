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