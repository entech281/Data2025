import cachetools.func
import pandas as pd

from motherduck import con
import polars as pl

CACHE_SECONDS = 600

# Example controller to cache queries
# this will only run the query if it needs cache refresh
@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_matches() -> pl.DataFrame:
    return con.sql("select * from tba.matches").df();

@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_rankings() -> pl.DataFrame:
    return con.sql("select * from tba.event_rankings").df();

@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_teams() -> pl.DataFrame:
    return con.sql("select * from tba.teams").df();

@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_event_list() -> pd.DataFrame:
    return con.sql("SELECT DISTINCT event_key FROM tba.matches ORDER BY event_key").df()[
        'event_key'].values.tolist()

@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_oprs_and_ranks() -> pd.DataFrame:
    return con.sql("""
            select er.team_number, er.event_key,er.wins, er.losses, er.ties,er.rank,er.dq, op.oprs, op.ccwms, op.dprs
            from frc_2025.tba.event_rankings er
            join frc_2025.tba.oprs op on er.team_number = op.team_number and er.event_key = op.event_key
            order by er.rank asc;
    """).df()
