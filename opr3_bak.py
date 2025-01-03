import pandas as pd
from motherduck import con
import numpy as np
from match_dataset_tools import unstack_data_from_color
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
    print("Automapped=",automapped_fields)
    #one row per team performance ( twice the number of matches)
    all_data = pd.concat([red_data,blue_data])

    all_data['margin'] = all_data['score'] - all_data['their_score']
    #print(all_data)
    #print(list(all_data.columns))

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
    #print("Solution")
    #print(computed)

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

if __name__  == '__main__':
    #matches = get_match_data()
    #print(matches)
    #r = calculate_opr_ccwm_dpr(matches)
    #print("Results:")
    #print(r)
    #r.to_csv('out.csv',index=False)

    teams = pd.DataFrame({'teams':[281,1319,4451]})
    team_numbers = teams['teams']
    matches = pd.DataFrame({
        't1' : [ 281, 1319, 281, 451],
        't2' : [ 4451, 4451,1319,281],
        'score': [20,30,40,10 ]
    })
    team_part = matches[['t1','t2']]
    print("Team Numbers")
    print(team_part)
    all_teams = team_part.melt(var_name='Alliance', value_name='Team').drop(columns='Alliance')
    flattened = team_part.stack().reset_index(level=1, drop=True)
    print("Flattened")
    print(flattened)

    # Step 2: Create one-hot encoding for all teams in the flattened column
    print("Dummies")
    print(pd.get_dummies(flattened))

    binary_matrix = pd.get_dummies(flattened).groupby(level=0).sum()
    print("Step1")
    print(binary_matrix)

    # Step 3: Reindex the columns to include all team numbers and ensure integer type
    binary_matrix = binary_matrix.reindex(columns=team_numbers, fill_value=0).astype(int)
    print("Result")
    print(binary_matrix)
    m = np.matrix(binary_matrix)
    print("Matrix")
    print(m)