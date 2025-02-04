import cachetools.func
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
    
    

