import duckdb
import polars as pl
import streamlit as st

#ACCESS_TOKEN=st.secrets['motherduck']['token']
ACCESS_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImRhdmUuY293ZGVuQGdtYWlsLmNvbSIsInNlc3Npb24iOiJkYXZlLmNvd2Rlbi5nbWFpbC5jb20iLCJwYXQiOiJMZWhFVURmM1h5VVFEdnEwbFJOWktRSlpjejlCbkR1bVB1aW9nRTRadEJBIiwidXNlcklkIjoiOGM0OWMyNTQtMjViYy00NTgzLTgxM2YtZGJmN2NiNWI4MGE2IiwiaXNzIjoibWRfcGF0IiwiaWF0IjoxNzI4NjU2NzY2fQ.vLCymfRvynWgM4SDtrqReIh9aSdLUjRyMHyH1FgBjP8'
con = duckdb.connect(f"md:frc_2025?motherduck_token={ACCESS_TOKEN}")
SCHEMA_NAME='fsc_2025'


def copy_db_to_local():


    EXPORT_PATH="./data/frc2025_export"
    con.execute(f"EXPORT DATABASE  '{EXPORT_PATH}' ")
    local_con = duckdb.connect("data/frc2025_copy.duckdb")
    local_con.execute(f"IMPORT DATABASE '{EXPORT_PATH}'")

    #local_con.close()
    con.close()

def describe_table( schema: str, table_name:str)-> pl.DataFrame:
    try:
        return con.sql(f"describe table {schema}.{table_name};").pl()
    except duckdb.CatalogException:
        return None


def table_exists( schema: str, table_name:str)-> bool:
    return describe_table(schema,table_name) is not None


def get_table(table_name:str) -> pl.DataFrame:
    if not table_exists(SCHEMA_NAME,table_name):
        return None
    else:
        return con.sql(f"select * from {SCHEMA_NAME}.{table_name}").pl()


def get_events() -> pl.DataFrame:
    return get_table('events')



def get_teams() -> pl.DataFrame:
    return get_table('teams')


def get_matches() -> pl.DataFrame:
    return get_table('matches')


def get_rankings() -> pl.DataFrame:
    return get_table('rankings')


def ranking_summary() -> pl.DataFrame:
    return con.sql("""
            select r.team_id, r.team_name,
                sum(r.wins) as total_wins, 
                sum(r.losses) as total_losses, 
                sum(r.wp) as total_wp, 
                sum(r.ap) as total_ap, 
                sum(r.sp) as total_sp,
                avg(r.wins) as avg_wins, 
                avg(r.losses) as avg_losses, 
                avg(r.wp) as avg_wp, 
                avg(r.ap) as avg_ap, 
                avg(r.sp) as avg_sp  
            from mann_2025.rankings r
            group by r.team_id, r.team_name
            order by total_wp desc;    
    """).pl()

# overall idea: if we have an event that has ended, AND  we have at least 1 row for it
# OR it is > 2 weeks in the future, then we probably have all that we're going to get

def get_events_to_skip_syncing_matches() -> pl.DataFrame:
    if not table_exists(SCHEMA_NAME, 'events'):
        return []

    if not table_exists(SCHEMA_NAME, 'matches'):
        return []

    return list(con.sql(f"""
                select e.id
                from {SCHEMA_NAME}.events e 
                join {SCHEMA_NAME}.matches m on (e.id = m.event_id)
                where  date_diff('day',e.end,current_timestamp) > 2
                group by e.id
                having count(*) > 0
                UNION
                select e.id 
                from {SCHEMA_NAME}.events e 
                where date_diff('day',e.end,current_timestamp) < -2 
    """).pl().get_column('id'))


def get_events_to_skip_syncing_rankings() -> pl.DataFrame:
    if not table_exists(SCHEMA_NAME, 'events'):
        return []

    if not table_exists(SCHEMA_NAME, 'rankings'):
        return []

    return list(con.sql(f"""
                select e.id
                from {SCHEMA_NAME}.events e 
                join {SCHEMA_NAME}.rankings m on (e.id = m.event_id)
                where  date_diff('day',e.end,current_timestamp) > 2
                group by e.id
                having count(*) > 0
                UNION
                select e.id 
                from {SCHEMA_NAME}.events e 
                where date_diff('day',e.end,current_timestamp) < -2 
    """).pl().get_column('id'))



if __name__ == '__main__':
    copy_db_to_local()