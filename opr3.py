import pandas as pd
import sys
#from motherduck import con
import numpy as np
from scipy.stats import zscore
from tabulate import tabulate
from match_dataset_tools import unstack_data_from_color,drop_columns_with_word_in_column_name,add_zscores,find_columns_with_suffix
def column_map_for_color(columns:list,color:str) -> ( dict[str,str],list[str]):


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

    print("Col map=",column_map)
    return column_map,list(automapped_fields)

def calculate_opr_ccwm_dpr(matches:pd.DataFrame) -> pd.DataFrame:

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
    print("left Side")
    print(left_side)
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


def get_match_data():
    #matches = con.sql("select * from frc_2025.tba.matches where event_key = '2024gacmp'").df()
    matches = pd.read_parquet("./tests/data/matches.pq")
    return matches


def remove_from_list (original:list[str],to_remove:list[str] )-> list[str]:
    return list( set(original) - set(to_remove))


def add_zscores(df:pd.DataFrame, cols:list[str]):
    new_df = df.copy()
    for c in cols:
        new_df[c + "_z"] = zscore(df[c])
    return new_df


def real():
    matches = get_match_data()

    r = calculate_opr_ccwm_dpr(matches)

    r = drop_columns_with_word_in_column_name(r,'threshold')
    r.to_csv('all_the_things.csv',float_format='%.2f')

    cols_to_use = remove_from_list(r.columns, [ 'team_id'])
    with_z = add_zscores(r, cols_to_use)
    c = find_columns_with_suffix(with_z,'z')
    with_z['weight']= 0

    #weights = pd.DataFrame([0] * len(c), index=c).T
    #weights['auto_speaker_note_points_z'] = 0.1
    #weights['end_game_total_stage_points_z'] = 5


    #for c in with_z.columns:
    #   if c.endswith("_z"):
    #     with_z[c +"_w" ] = with_z[c] * weights.iloc[0][c]

    weighted_columns = find_columns_with_suffix(with_z,"_z") +[ "weight"]
    #print(weighted_columns)
    r = with_z[weighted_columns]
    weight_col= r.pop('weight')
    r.insert(0, 'weight', weight_col)
    r = r.T
    print(r)
    return r.T
    #print(tabulate(with_z[[
    #    'auto_speaker_note_points_z',
    #    'end_game_total_stage_points_z',
    #    'auto_speaker_note_points_z_w',
    #    'end_game_total_stage_points_z_w',
    #]], headers='keys', tablefmt='psql', floatfmt=".2f"))

if __name__  == '__main__':
    pd.set_option('display.max_columns',None)
    real()


