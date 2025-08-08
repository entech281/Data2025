import cachetools.func
import pandas as pd
import json
from motherduck import con
import polars as pl
from langchain.tools import tool
import numpy as np
import opr3
CACHE_SECONDS = 600

def convert_ndarrays(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

@tool
def get_bot_matches(event_key:str) -> str:
    """
    Given an FRC event key like '2025schar', returns all of the matches played
    
    the keys in the response are of the format 'scoring_category_z', so you can take off
    the _z suffix when matching data from a user query.
    
    Accepts:
    - event_key: string like "2025schar"
    
    Returns:
    - JSON string listing all match data, including which teams played ( red1, red2, red3, and blue1, blue2,blue3)
    as well as the scores for both teams, the match time, and all of the bonus achievements and scoring in the match
    """
    m = get_matches_for_event(event_key)
    return json.dumps(m.to_dict(orient='records'),indent=2)

def get_matches_for_event(event_key:str) -> pd.DataFrame:
    all_matches = get_matches()
    return all_matches [ all_matches['event_key'] == event_key].sort_values(by=['time'], ascending=[True])


@tool
def get_team_zscores(event_key:str) -> str:
    """
    Given an FRC event key like '2025schar', returns the z scores for every robot
    in all blue alliance performance categories.
    see the statistics term z-score.

    the keys in the response are of the format 'scoring_category_z', so you can take off
    the _z suffix when matching data from a user query.

    Accepts:
    - event_key: string like "2025schar"

    Returns:
    - JSON string listing each scoring area, with an _z after it, and then for each of those,
      a dict of z scores for each team within that scoring category
    """
    df = opr3.get_ccm_data_for_event(event_key)
    df = opr3.select_z_score_columns(df, ['team_id'])

    df.reset_index(drop=True, inplace=True)
    df = df.set_index('team_id')
    #df = df.T
    df = df.sort_index()
    d = df.to_dict()
    return json.dumps(d,indent=2)

# Example controller to cache queries
# this will only run the query if it needs cache refresh
#@tool
@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_matches() -> pl.DataFrame:
    """Gets all of the matches available in the blue alliance"""
    return con.sql("select * from tba.matches").df();



@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_rankings() -> pl.DataFrame:
    "Gives rankings for all robots at all events"
    return con.sql("select * from tba.event_rankings").df();

@tool
def get_defense_bot(event_key: str) -> str:
    """
    Given an FRC event key like '2025schar', returns defense bot data including
    team number, OPR, drive type, and other stats in JSON format.

    Accepts:
    - event_key: string like "2025schar"

    Returns:
    - JSON string listing team number, pit data, OPR, drive type, CCWM, and size.
    """
    df = get_defense()  # returns a polars or pandas DataFrame

    df_clean = df.applymap(convert_ndarrays)
    records = df_clean.to_dict(orient="records")

    s = json.dumps(records, indent=2)
    print(s)
    return s

#@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_defense() -> pl.DataFrame:
    "gives a data summary for all robots, with data about how well they might play defense. "
    return con.sql("""
        select pit.team_number, pit.drive_type, GREATEST(height,width) as max_size, 
        t.all_tags, o.oprs as opr, o.dprs as dpr, o.ccwms as ccwm,
        case pit.drive_type
            when 'Swerve' then 1
            when 'Tank' then 2
            when 'Mecanum' then 3
            else 999
        end as drive_rank
        from scouting.pit

    INNER JOIN ( 
        select team_number, list(tag) as all_tags
        from scouting.tags
        where 'Defense' in (select tag from scouting.tags where team_number = pit.team_number)
        group by team_number
    ) as t
    on ( t.team_number = pit.team_number)

    INNER JOIN tba.oprs as o
    on ( t.team_number = o.team_number and pit.team_number = o.team_number  )

    where o.event_key = '2025schar'
    group by pit.team_number, pit.drive_type, pit.height, pit.width, t.all_tags, o.oprs, o.dprs, o.ccwms, drive_rank
    order by drive_rank asc, max_size desc, dpr desc;
""").df()

#@tool
@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_team_list(event_key:str) -> list:
    "gets a data frame of all the teams available, based on input of an event key"
    df = con.sql(f"""
            select red1, red2, red3, blue1, blue2, blue3
            from tba.matches
            where event_key = '{event_key }'
    """).df()
    unique_teams = pd.unique(df.values.ravel())
    return sorted(unique_teams.tolist())


def get_most_recent_event() -> str:
    all_events = get_event_list()
    if len(all_events) > 0:
        return all_events[0]
    else:
        return None


def get_event_list() -> pd.DataFrame:
    event_df = get_events()
    return event_df['event_key'].values.tolist()


@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_events() -> pd.DataFrame:
    return con.sql("""
            select event_key, max(actual_time) from tba.matches 
            group by event_key
            order by max(actual_time) desc;    
    """).df()


@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def _get_tba_oprs_and_ranks() -> pd.DataFrame:
    tba_ranks =  con.sql("""
            select er.team_number, er.event_key,er.wins, er.losses, er.ties,er.rank,er.dq, op.oprs as opr, op.ccwms as ccwm, op.dprs as dpr
            from frc_2025.tba.event_rankings er
            join frc_2025.tba.oprs op on er.team_number = op.team_number and er.event_key = op.event_key
            order by er.rank asc;
    """).df()
    return tba_ranks

@tool
def get_tba_oprs_and_ranks_for_event(event_key:str) -> pd.DataFrame:
    """
    Given an FRC event key like '2025schar', returns rankings for all bots at the event.
    Accepts:
    - event_key: string like "2025schar"

    Returns:
    - JSON string listing team_number,rank,
    avg_rp,	opr,	wins,	losses,	ties,	total_rp,	avg_win_rp,	avg_auto_rp	avg_coral_rp,
    	avg_barge_rp,	dpr,	ccwm
    """
    r =  _get_tba_oprs_and_ranks()
    r = r[ r['event_key'] == event_key]
    return r

def get_oprs_and_ranks_for_event(event_key:str) -> pd.DataFrame:
    all_ranks = _get_tba_oprs_and_ranks()
    all_ranks_this_event = all_ranks[all_ranks['event_key'] == event_key]
    rank_summary_this_event = get_ranking_point_summary_for_event(event_key)
    return all_ranks_this_event.merge(rank_summary_this_event,on='team_number',how='inner')


def get_oprs_and_ranks_for_team(event_key:str, team_number: int) -> dict:
    all_ranks = get_oprs_and_ranks_for_event(event_key)
    filtered_for_team = all_ranks[ all_ranks['team_number'] == team_number]
    r = filtered_for_team.to_dict(orient='records')
    return r[0] if len(r) > 0 else {}


def get_robot_specific_data_from_matches( event_key:str) -> pd.DataFrame:
    # gets values out of the matches where we essentially DO have a value
    # per robot, per match
    d = []
    team_list = get_team_list(event_key)
    matches = get_matches_for_event(event_key)

    def _get_robot_specific_value(row, team_number: int, prefix: str, index: i )-> list:
        team_col = f"{prefix}{index}"
        suffix = f"robot{index}"
        if team_number in [row[team_col]]:
            return [{
                'team_number': row[team_number],
                'auto_line': row[f"red_auto_line_{suffix}"],
                'end_game': row[f"red_end_game_{suffix}"]
            }]
        else:
            return []

    for t in team_list:
        for _, row in matches.iterrows():
            d.extend(_get_robot_specific_value(row, t, 'red', 1 ))
            d.extend(_get_robot_specific_value(row, t, 'red', 2))
            d.extend(_get_robot_specific_value(row, t, 'red', 3))
            d.extend(_get_robot_specific_value(row, t, 'blue', 1 ))
            d.extend(_get_robot_specific_value(row, t, 'blue', 2))
            d.extend(_get_robot_specific_value(row, t, 'blue', 3))
    return pd.DataFrame(d)

#@tool
@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_ranking_point_summary_for_event(event_key:str) -> pd.DataFrame:
    """
    This computes a summary of how many RPs each team has, and how they got them
    :param event_key:
    :return:
    """
    team_data = {}
    def get_team_summary(team_number:int):
        if team_number not in team_data:
            team_data[team_number] = {
                'team_number': team_number,
                'total_rp': 0,
                'auto_rp': 0,
                'win_rp': 0,
                'coral_rp': 0,
                'barge_rp': 0,
                'total_rp_sum': 0,
                'match_count': 0
            }
        return team_data[team_number]

    #there is probably a faster way to do this that's vectorized but
    #i dont want to figure it out right now
    matches = get_matches_for_event(event_key)
    matches = matches [ matches['comp_level'] == 'qm'] #only consider qualifiers for rankings


    def _add_team_rps_with_prefix(prefix:str,row):
        if prefix == "red":
            anti_prefix = "blue"
        else:
            anti_prefix = "red"

        for col in [f"{prefix}1", f"{prefix}2", f"{prefix}3"]:
            team_number = row[col]

            td = get_team_summary(team_number)

            # blue alliance calculated rp
            td['total_rp'] += row[f"{prefix}_rp"]
            td['match_count'] += 1
            # 3 for win, 1 for a tie
            our_score=row[f"{prefix}_score"]
            their_score=row[f"{anti_prefix}_score"]

            if our_score > their_score:
                td['win_rp'] += 3
            elif our_score == their_score:
                td['win_rp'] += 1

            if row[f'{prefix}_auto_bonus_achieved'] == 1:
                td['auto_rp'] += 1

            if row[f'{prefix}_coral_bonus_achieved'] == 1:
                td['coral_rp'] += 1

            if row[f'{prefix}_barge_bonus_achieved'] == 1:
                td['barge_rp'] += 1


    for _,row in matches.iterrows():
        _add_team_rps_with_prefix('red',row)
        _add_team_rps_with_prefix('blue', row)


    r = pd.DataFrame(team_data.values())
    r['avg_rp'] = r['total_rp'] / r['match_count']
    r['avg_win_rp'] = r['win_rp'] / r['match_count']
    r['avg_auto_rp'] = r['auto_rp'] / r['match_count']
    r['avg_coral_rp'] = r['coral_rp'] / r['match_count']
    r['avg_barge_rp'] = r['barge_rp'] / r['match_count']
    return r


def clear_caches():
    get_ranking_point_summary_for_event.cache_clear()
    _get_tba_oprs_and_ranks.cache_clear()
    get_matches.cache_clear()
    get_defense.cache_clear()
    get_rankings.cache_clear()
    get_team_list.cache_clear()
    get_events.cache_clear()