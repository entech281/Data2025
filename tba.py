import requests
import json
import logging
import pandas as pd
from datetime import datetime,date
import time
import streamlit as st
from flatten_json import flatten
logger = logging.getLogger(__name__)


def set_logger(new_logger):
    global logger
    logger = new_logger

DATE_FORMAT="%Y-%m-%d"
TBA_ACCESS_TOKEN=st.secrets['tba']['auth_key']
TBA_API_ROOT = 'https://www.thebluealliance.com/api/v3/'
DISTRICT_KEY='2025fsc'
DISTRICT_EVENTS=[ '2025schar','2025sccha', '2025sccmp' ]


def team_number_from_key(frc_team_key):
    return int(frc_team_key.replace('frc', ''))


def get_fields(from_dict:dict, fields:list[str])-> dict:
    r = {}
    for f in fields:
        if f in from_dict.keys():
            r[f] = from_dict[f]
    return r

def flatten_with_color_prefix(prefix, original:dict):
    r = {}
    for k,v in original.items():
        new_key = prefix + k
        r[new_key] = v
    return r

def _get(url, result_type='json'):

    response = requests.get(TBA_API_ROOT + url, headers={
        'X-TBA-Auth-Key': TBA_ACCESS_TOKEN
    })
    if result_type == 'json':
        return response.json()
    else:
        return response.text


def get_teams_for_district():
    return _get(f'/district/{DISTRICT_KEY}/teams')


def get_teams_for_event(event_name):
    return _get(f'/event/{event_name}/teams')


def get_matches_for_event(event_name):
    matches= _get("/event/{event_key}/matches".format(event_key=event_name))

    def flatten_match(match):
        r = get_fields(match, [ 'actual_time','match_number','key','event_key','comp_level'])
        blue_teams = match["alliances"]["blue"]["team_keys"]
        red_teams = match["alliances"]["red"]["team_keys"]
        r["red1"] = team_number_from_key(red_teams[0])
        r["red2"] = team_number_from_key(red_teams[1])
        r["red3"] = team_number_from_key(red_teams[2])
        r['red_score'] =  match['alliances']['red']['score']
        r["blue1"] = team_number_from_key(blue_teams[0])
        r["blue2"] = team_number_from_key(blue_teams[1])
        r["blue3"] = team_number_from_key(blue_teams[2])
        r['blue_score'] = match['alliances']['blue']['score']

        r.update(flatten(match['score_breakdown']))
        return r

    return [flatten_match(m) for m in matches]


def zero_if_column_missing(df,col_name):
    df_return = df
    if col_name not in df.columns:
        df_return[col_name] = 0
    return df_return


def get_event_rankings(event_key):
    r = _get("/event/{event_key}/rankings".format(event_key=event_key))
    if r is None:
        return []

    def flatten_record(rec):
        r = get_fields(rec,['dq','matches_played','qual_average','rank','team_key'])
        r['team_number'] = team_number_from_key(rec['team_key'])
        r['event_key'] = event_key
        if 'record' in rec:
            r['wins'] = rec['record']['wins']
            r['losses'] = rec['record']['losses']
            r['ties'] = rec['record']['ties']
        return r

    return [ flatten_record(x) for x in r['rankings']]


def get_event_oprs(event_key):

    r = _get("/event/{event_key}/oprs".format(event_key=event_key), result_type='text')
    df = pd.read_json(r, orient='columns').reset_index()
    df['team_number'] = df['index'].apply(team_number_from_key)

    df = zero_if_column_missing(df,'oprs')
    df = zero_if_column_missing(df, 'dprs')
    df = zero_if_column_missing(df, 'ccwms')
    df = zero_if_column_missing(df, 'team_number')

    df = df[['team_number', 'oprs', 'dprs', 'ccwms']]
    df['event_key'] = event_key
    return df.to_dict('records')

def get_event_scoring_components(event_key):

    r = _get("/event/{event_key}/coprs".format(event_key=event_key))
    if r is None:
        return []

    result = []
    # this is a weird one: the root is a dict of componnents, with a dict of teams under each
    for component_key,team_dict in r.items():
        for team_key,val in team_dict.items():
            result.append({
                'event_key': event_key,
                'component': component_key,
                'team_key': team_key,
                'team_number': team_number_from_key(team_key),
                'component_val': val
            })

    return result

def get_rankings_for_district(district_key):
    r = _get(f'/district/{district_key}/rankings')
    if r is None:
        return []

    def flatten_ranking(rec):
        rec= get_fields(rec, ['point_total','rank','rookie_bonus','team_key'])
        rec['team_number'] = team_number_from_key(rec['team_key'])
        rec['district_key'] = district_key
        return rec

    return [ flatten_ranking(x) for x in r]


def get_match_predictions_for_event(event_key):
    r = _get(f"/event/{event_key}/predictions")
    if r is None:
        return []


    def flatten_prediction(match_key,rec):
        r = get_fields(rec, ['winning_alliance','prob'])
        r["match_key"] = match_key
        r["event_key"] = event_key
        r.update(flatten_with_color_prefix("blue_", rec["blue"]))
        r.update(flatten_with_color_prefix("red_", rec["red"]))
        return r

    match_predictions = {}

    if "playoff" in r["match_predictions"]:
        match_predictions.update(r['match_predictions']['playoff'])

    if "qual" in r["match_predictions"]:
        match_predictions.update(r['match_predictions']['qual'])

    result = []
    for k,v in match_predictions.items():
        result.append( flatten_prediction(k,v) )

    return result


def setup_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
                        handlers=[stream_handler])


if __name__ == '__main__':
    setup_logging()
    #print ( json.dumps(get_rankings_for_district(),indent=4))''
    #print(json.dumps(get_event_rankings('2025schar'), indent=4))
    #r=get_match_predictions_for_event('2024gacmp')
    #r2=get_rankings_for_district('2024pch')
    r2=get_event_scoring_components('2024gacmp')
    print(json.dumps(r2,indent=4))