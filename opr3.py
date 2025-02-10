import pandas as pd
import sys
from motherduck import con
import util
from pandasql import sqldf
import numpy as np
from scipy.stats import zscore
from tabulate import tabulate
import time
import logging
import dataframe_sync
log = logging.getLogger("cmm")
from match_dataset_tools import unstack_data_from_color,drop_columns_with_word_in_column_name,add_zscores,find_columns_with_suffix


def column_map_for_color(columns:list,color:str) -> ( dict[str,str],list[str]):
    """
    Creates a mapping of column names based on the specified color.

    Args:
        columns (list): List of column names.
        color (str): The color to base the mapping on ('red' or 'blue').

    Returns:
        tuple: A dictionary mapping original column names to new names, and a list of automatically mapped fields.
    """
    column_map = {
        color + "1":"t1",
        color + "2":"t2",
        color + "3":"t3",
    }
    automapped_fields = set()
    if ( color == "red"):
        column_map["blue_score"] = "their_score"

    if ( color == "blue"):
        column_map["red_score"] = "their_score"

    color_prefix = color + "_"
    #get columns associated with this team, like team_<value>
    for c in columns:
        if c.startswith(color_prefix):
            computed_field = c.replace(color_prefix,"")
            automapped_fields.add(computed_field)
            column_map[c] = computed_field

    #print("Col map=",column_map)
    return column_map,list(automapped_fields)


def calculate_opr_ccwm_dpr(matches: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates OPR (Offensive Power Rating), CCWM (Calculated Contribution to Winning Margin),
    and DPR (Defensive Power Rating) for teams based on match data.

    Args:
        matches (pd.DataFrame): DataFrame containing match data with red/blue alliance teams and scores

    Returns:
        pd.DataFrame: Sorted DataFrame with team statistics including OPR, CCWM, DPR calculations
    """
    #get the unique list of teams
    team_list = pd.unique(matches[['red1','red2','red3','blue1','blue2','blue3']].values.ravel('K'))
    #print("Unique Teams: One column, num rows= Nteams ")
    #score_cols = extract_red_and_blue_columns(matches)

    #lets only consider numeric columns for now. later we can add converters for booleans and strings
    numeric_columns = matches.select_dtypes(include='number').columns
    red_col_map,automapped_fields = column_map_for_color(numeric_columns,'red')
    blue_col_map,automapped_fields = column_map_for_color(numeric_columns,'blue')

    red_data = matches.rename(columns=red_col_map)
    blue_data = matches.rename(columns=blue_col_map)

    all_data = pd.concat([red_data,blue_data])
    all_data['margin'] = all_data['score'] - all_data['their_score']


    m=[]
    for idx,match in all_data.iterrows():
        r=[]
        for team in team_list:
            if match['t1'] == team or match['t2'] == team or match['t3'] == team:
                r.append(1)
            else:
                r.append(0)
        m.append(r)
    m_m = np.matrix(m)

    #left side values are all the columsn in the map, MINUS a key few
    computed_cols = ['margin','their_score'] + automapped_fields

    #left_side = all_data[['our_score','their_score','margin']]
    left_side = all_data[computed_cols]
    #print("left Side")
    #print(left_side)
    c_c = np.matrix(left_side)

    pseudo_inverse = np.linalg.pinv(m_m)
    computed = np.matmul(pseudo_inverse,c_c)

    results_2 = pd.DataFrame(computed,columns=computed_cols)
    teams_2 = pd.DataFrame(team_list,columns=['team_id'])
    results_all = pd.concat([teams_2, results_2], axis=1)

    """
            team_id        opr       ccwm
        16     1771  59.877861  40.854197
        4      2974  49.007513  27.565074
        19      343  39.377108  11.797834
        ....    
    """
    return results_all.sort_values(by=['score'],ascending=False)


def get_match_data() -> pd.DataFrame:
    """
    Retrieves match data from parquet file for analysis.

    Returns:
        pd.DataFrame: DataFrame containing match data
    """
    #matches = con.sql("select * from frc_2025.tba.matches where event_key = '2024gacmp'").df()
    matches = pd.read_parquet("./tests/data/matches.pq")
    return matches


def get_ordered_matches() -> pd.DataFrame:
    s = time.time()
    r = con.sql("select * from frc_2025.tba.matches where actual_time is not null and event_key='2024gacmp' order by actual_time desc;").df()
    log.info(f"Fetched {len(r)} matches, {time.time()-s } s")
    return r

def remove_from_list (original:list[str],to_remove:list[str] ) -> list[str]:
    """
    Removes specified elements from a list.

    Args:
        original (list[str]): Original list of strings
        to_remove (list[str]): List of strings to remove

    Returns:
        list[str]: New list with specified elements removed
    """
    return list( set(original) - set(to_remove))


def add_zscores(df:pd.DataFrame, cols:list[str]) -> pd.DataFrame:
    """
    Adds z-score columns for specified numeric columns in DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame
        cols (list[str]): List of column names to calculate z-scores for

    Returns:
        pd.DataFrame: DataFrame with added z-score columns (suffixed with '_z')
    """
    new_df = df.copy()
    for c in cols:
        new_df[c + "_z"] = zscore(df[c])
    return new_df


def analyze_ccm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs Competitive Component Matrix analysis on match data.

    Args:
        df (pd.DataFrame): DataFrame containing match data

    Returns:
        pd.DataFrame: Processed DataFrame with CCM analysis results and z-scores
    """
    s = time.time()
    matches = df
    r = calculate_opr_ccwm_dpr(matches)

    r = drop_columns_with_word_in_column_name(r,'threshold')

    cols_to_use = remove_from_list(r.columns, [ 'team_id'])
    
    with_z = add_zscores(r, cols_to_use)

    #print(with_z.columns)
    #c = find_columns_with_suffix(with_z,'z')
    #with_z['weight']= 0

    #weights = pd.DataFrame([0] * len(c), index=c).T
    #weights['auto_speaker_note_points_z'] = 0.1
    #weights['end_game_total_stage_points_z'] = 5


    #for c in with_z.columns:
    #   if c.endswith("_z"):
    #     with_z[c +"_w" ] = with_z[c] * weights.iloc[0][c]

    #weighted_columns = find_columns_with_suffix(with_z,"_z") +[ "team_id"]
    #weighted_columns = with_z
    #print(weighted_columns)
    with_z['team_id'] = r['team_id']
    #r = with_z[weighted_columns]
    #weight_col= r.pop('weight')
    #r.insert(0, 'weight', weight_col)
    #r = r.T
    #print(r)

    #print(r.columns)
    #print(tabulate(r[r.columns[-4:]], headers='keys', tablefmt='psql', floatfmt=".2f"))
    team_count = with_z['team_id'].count()
    log.debug(f"CCM: {len(cols_to_use)} attributes ({len(with_z)} cols), {team_count} teams")
    return with_z


def calculate_match_by_match(all_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates team performance metrics incrementally over groups of matches.

    Args:
        all_data (pd.DataFrame): DataFrame containing all match data

    Returns:
        pd.DataFrame: Concatenated results of incremental analyses
    """
    batch = 0
    batch_size = 5
    result_dfs = []

    while batch < len(all_data):
        batch += batch_size
        r = analyze_ccm(all_data.head(batch))
        r['batch'] = batch
        result_dfs.append(r)

    return  pd.concat(result_dfs)


def rolling_match_cmm(all_matches_sorted_by_time_desc: pd.DataFrame, windows_name:str, window_size:int) -> list[pd.DataFrame]:
    total_rows = len(all_matches_sorted_by_time_desc)
    num_windows = int(total_rows - window_size)

    r = []
    for i in range(num_windows):
        window_start = i
        window_end = i + window_size

        match_window = all_matches_sorted_by_time_desc.iloc[window_start:window_end]

        analyzed_matches = analyze_ccm(match_window)
        analyzed_matches['window_name'] = windows_name
        analyzed_matches['window_index'] = i
        analyzed_matches['windows_size'] = len(match_window)
        analyzed_matches['window_min_actual_time'] = match_window['actual_time'].min()
        analyzed_matches['window_max_actual_time'] = match_window['actual_time'].max()
        r.append(analyzed_matches)
    return r


def rolling_match_cmm_batch(all_matches_sorted_by_time_desc: pd.DataFrame,rolling_windows:dict[str,int] ) -> pd.DataFrame:
    r = []
    s = time.time()
    for name, window_size in rolling_windows.items():
        r.extend(rolling_match_cmm(all_matches_sorted_by_time_desc,name,window_size))

    return pd.concat(r)


def get_new_matches_that_need_analyzing():
    """
    Assumes matches have already been synchronized
    could be sped up by querying a dataframe we fetched already ( but cmm table is potentially big, not
    selecting all of that is probably faster )
    :return:
    """
    last_match_actual_time_analyzed = con.execute("select max(actual_time) from frc2025.scouting.match_cmm").fetchone()[0]
    matches_that_need_analyzing = con.execute("select * from frc2025.tba.matches where actual_time > {last_match_actual_time_analyzed}").df()
    log.info(f"{len(matches_that_need_analyzing)} Matches to Analyze")
    return matches_that_need_analyzing


def rolling_match_cmm2(all_matches_sorted_by_time_desc: pd.DataFrame, window_name:str, window_size:int,last_analyzed_actual_time:int) -> list[pd.DataFrame]:

    #total_rows = len(all_matches_sorted_by_time_desc)
    #num_windows = int(total_rows - window_size)

    #get the matches we need to analyze. its only the ones since we analyzed last. we need to compute a new window
    #BEGINNING with each one of these
    #we'll use the actual_time to make it easy to select the ranges.
    #each window is just the next window_size rows where actual time is <= the selected match
    match_actual_times_to_analyze = sqldf(f"""
        select actual_time from all_matches_sorted_by_time_desc
        where actual_time > {last_analyzed_actual_time}
        order by actual_time DESC
    """, locals())["actual_time"].tolist()


    if len(match_actual_times_to_analyze) <= 0:
        log.info(f"Window: {window_name}: No new matches to handle: we are up to date. Last match actual time: {last_analyzed_actual_time }")
        return []
    else:
        log.info(f"Looks like we have {len(match_actual_times_to_analyze)} new matches to handle since {last_analyzed_actual_time}")

    log.debug(f"New Match times = {match_actual_times_to_analyze}")
    r = []
    # each match to be analyzed has a unique actual time.
    # we want to compute a moving window _ending_ with each match, so
    # each window will end with the actual_time of a single match
    # each window definition can have its own set
    # the dataset will have a row per team,
    # so the primary key of the table is the team_id, the window_name, and the actual_time of the ending match in that window.
    for actual_time  in match_actual_times_to_analyze: #
        log.debug(f"Handle Match Actual time: {actual_time}")

        log.debug(f"DF columns = {all_matches_sorted_by_time_desc.columns}")

        matches_window = sqldf(f"""
            select * from all_matches_sorted_by_time_desc
            where actual_time <= {actual_time}
            order by actual_time DESC
            LIMIT {window_size}
        """,locals() )
        log.debug(f"Window: {window_name} : Analyze {window_size} matches <= {actual_time} rows={len(matches_window)}")
        log.debug(matches_window[['key','actual_time']])
        actual_window_size = len(matches_window) # could be lower if there are insufficient rows to complete the window
        window_start_actual_time = matches_window['actual_time'].min()
        window_end_actual_time = matches_window['actual_time'].max()
        log.debug(f"Window has {len(matches_window)} matches")
        analyzed_matches = analyze_ccm(matches_window)
        analyzed_matches['window_name'] = window_name
        analyzed_matches['window_size'] = actual_window_size
        analyzed_matches['window_start_actual_time'] = window_start_actual_time
        analyzed_matches['window_end_actual_time'] = window_end_actual_time
        log.info(f"Results: name={window_name}, size={actual_window_size}, start={window_start_actual_time}, end={window_end_actual_time}, matches={actual_window_size}, teams={len(analyzed_matches)}")
        log.debug(f"""To see the matches and data for this  window, run:
                Matches:
                select * from frc2025.tba.matches where actual_time<= {window_end_actual_time} and actual_time > {window_start_actual_time} order by actual_time desc;
                
                Data:
                select * from frc2025.scouting.matches_cmm where window_name={window_name} and window_end_actual_time = {window_end_actual_time} order by team_id desc;
        """)

        r.append(analyzed_matches)
    return r


def rolling_match_cmm_batch2(all_matches_sorted_by_time_desc: pd.DataFrame,rolling_windows:dict[str,int] ) -> pd.DataFrame:
    r = []
    s = time.time()
    last_match_actual_time_analyzed = -1
    try:
        last_match_actual_time_analyzed = con.execute("select max(window_end_actual_time) from frc_2025.scouting.match_cmm").fetchone()[0]
        log.info(f"Last analyzed match time : {last_match_actual_time_analyzed}")
    except Exception as e:
        log.error(f"No existing analysis-- we'll start over! {e}", exc_info=False)

    for name, window_size in rolling_windows.items():
        log.debug(f"Process Window '{name}':size={window_size}")
        r.extend(rolling_match_cmm2(all_matches_sorted_by_time_desc,name,window_size,last_match_actual_time_analyzed))

    if len(r)> 0:
        results = pd.concat(r)
        #the primary key of each analysis is the actual_time of the LAST match in the window.
        #its a LITTLE dangerous to use this, but i dont think two matches could begin or end in the same millisecond.
        dataframe_sync.sync_df(con,results,"frc_2025.scouting.match_cmm",key_field_names=['team_id','window_name','window_end_actual_time'])
        log.info(f"Analysis complete: {time.time() - s} sec, saving {len(results)} rows.")
    else:
        log.info(f"Run completed: There were no new matches to analyze.")
    return len(r)





def fake_analyze() -> pd.DataFrame:
    """
    Performs test analysis using sample match data.

    Returns:
        pd.DataFrame: Results of match-by-match analysis
    """
    d = get_match_data()
    r = calculate_match_by_match(get_match_data())
    return r


def latest_match() -> pd.DataFrame:
    """
    Analyzes the most recent match data.

    Returns:
        pd.DataFrame: Analysis results for the latest match
    """
    return analyze_ccm(get_match_data())


def test_select() -> None:
    """
    Tests metric selection and weighting functionality.
    Prints weighted analysis results in tabular format.
    """
    original = latest_match()
    #print( df.columns)
    selected_metrics = ['score_z','foul_count_z']
    weights=[1.0,-0.1]
    selected_metrics = original[selected_metrics]
    weighted = selected_metrics.mul(weights)
    weighted['total_z'] = weighted.sum(axis=1)
    #print(weighted)
    all = pd.concat([original[['team_id']], weighted],axis=1)
    all = all.sort_values(by='total_z', ascending=False)
    all['rank'] = all['total_z'].rank(ascending=False)
    all = pd.melt(all,id_vars=['team_id'])
    log.info(tabulate(all, headers='keys', tablefmt='psql', floatfmt=".3f"))


def matches_over_time() -> pd.DataFrame:
    """
    Analyzes match data over time using incremental batches.

    Returns:
        pd.DataFrame: Time series analysis of match performance
    """
    return calculate_match_by_match(get_match_data())

if __name__  == '__main__':
    #all = latest_match()
    #all = all.reset_index()
    #all = all.set_index('team_id')
    #all = all.T
    #print(all.columns)
    #print(tabulate(all, headers='keys', tablefmt='psql', floatfmt=".3f"))
    util.setup_logging()

    m = get_ordered_matches()

    r = rolling_match_cmm_batch2(m, {
        'rolling-100': 100,
        'rolling-75': 75
    })

    #pd.set_option('display.max_columns',None)
    #test_select()
    #start = time.time()
    #d = get_match_data()
    #r = calculate_match_by_match(get_match_data())
    #r.to_csv('all_the_things.csv', float_format='%.2f')
    #print (r.shape)
    #print ( f"Total time: {time.time()-start} sec") #0.32 sec on my laptop for all matches, read off disk=0.1
    print(r)


def calculate_raw_opr(matches: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates raw OPR metrics without z-scores.
    
    Args:
        matches (pd.DataFrame): DataFrame with match data
        
    Returns:
        pd.DataFrame: Raw OPR values for each team
    """
    # Get unique teams
    team_list = pd.unique(matches[['red1','red2','red3','blue1','blue2','blue3']].values.ravel('K'))
    
    # Get column mappings
    numeric_columns = matches.select_dtypes(include='number').columns
    red_col_map, automapped_fields = column_map_for_color(numeric_columns, 'red')
    blue_col_map, _ = column_map_for_color(numeric_columns, 'blue')
    
    # Transform data
    red_data = matches.rename(columns=red_col_map)
    blue_data = matches.rename(columns=blue_col_map)
    all_data = pd.concat([red_data, blue_data])
    all_data['margin'] = all_data['score'] - all_data['their_score']
    
    # Build match matrix
    m = []
    for _, match in all_data.iterrows():
        r = []
        for team in team_list:
            if match['t1'] == team or match['t2'] == team or match['t3'] == team:
                r.append(1)
            else:
                r.append(0)
        m.append(r)
    m_m = np.matrix(m)
    
    # Calculate OPR
    computed_cols = ['margin', 'their_score'] + automapped_fields
    left_side = all_data[computed_cols]
    c_c = np.matrix(left_side)
    
    pseudo_inverse = np.linalg.pinv(m_m)
    computed = np.matmul(pseudo_inverse, c_c)
    
    # Format results
    results = pd.DataFrame(computed, columns=computed_cols)
    teams_df = pd.DataFrame(team_list, columns=['team_id'])
    final_results = pd.concat([teams_df, results], axis=1)
    
    return final_results.sort_values(by=['score'], ascending=False)