import pandas as pd
#from motherduck import con
import numpy as np
import json
from match_dataset_tools import unstack_data_from_color
def column_map(columns:list,color:str) -> ( dict[str,str],list[str]):

    column_color = {
        color + '1':'team1',
        color + '2':'team2',
        color + '3':'team3',
    }

    mapped_fields = set()
    if color == 'red':
        column_color['blue_score'] = 'opp_score'

    if color == 'blue':
        column_color['red_score'] = 'opp_score'

    pre_color = color + '_'

    for i in columns:
        if i.startswith(pre_color):
            computed_field = i.replace(pre_color,'')
            mapped_fields.add(computed_field)
            column_color[i] = computed_field

    return column_color, list(mapped_fields)


def calculate_opr_ccwm_dpr(matches:pd.DataFrame) -> pd.DataFrame:

    #get the unique list of teams
    team_list = pd.unique(matches[['red1','red2','red3','blue1','blue2','blue3']].values.ravel('K'))
    #print("Unique Teams: One column, num rows= Nteams ")

    int_columns = matches.select_dtypes(include='number').columns
    r_columns, mapped_fields = column_map(int_columns,'red')
    b_columns, mapped_fields = column_map(int_columns,'blue')

    r_data = matches.rename(columns=r_columns)
    b_data = matches.rename(columns=b_columns)

    all_data = pd.concat([r_data,b_data])
    all_data['diff'] = all_data['score'] - all_data['opp_score']
    M=[]
    for idx, match in all_data.iterrows():
        r=[]
        for team in team_list:
            if match['team1'] == team or match['team2'] == team or match['team3'] == team:
                r.append(1)
            else:
                r.append(0)
        M.append(r)

    m_m = np.matrix(M)

    rem_columns = ['diff','opp_score'] + mapped_fields

    ez_side = all_data[rem_columns]
    c_c = np.matrix(ez_side)

    pseudo_inverse = np.linalg.pinv(m_m)
    all = np.matmul(pseudo_inverse,c_c)

    results_2 = pd.DataFrame(all,columns=list(ez_side))
    teams_2 = pd.DataFrame(team_list,columns=['team_id'])
    results_all = pd.concat([teams_2, results_2], axis=1)

    """
            team_id        opr       ccwm
        16     1771  59.877861  40.854197
        4      2974  49.007513  27.565074
        19      343  39.377108  11.797834
        ....    
    """
    #return results_all.sort_values(by=['opr'],ascending=False)
    return results_all.sort_values(by=['opp_score'],ascending=False)


def get_match_data():
    #matches = con.sql("select * from frc_2025.tba.matches where event_key = '2024gacmp'").df()
    #return matches[ ['red1','red2','red3','blue1','blue2','blue3','red_score','blue_score']]
    matches = pd.read_parquet("./tests/data/matches.pq")
    return matches


if __name__  == '__main__':
    matches = get_match_data()
    print(matches)
    r = calculate_opr_ccwm_dpr(matches)
    print("Results:")
    print(r)