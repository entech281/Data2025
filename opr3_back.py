import pandas as pd
from motherduck import con
import numpy as np

def column_map_for_color(columns:list[str],color:str) -> list[str]:
    column_map = {
        color + "1":"t1",
        color + "2":"t2",
        color + "3":"t3",
    }
    if ( color == "red"):
        column_map["blue_score"] = "their_score"

    if ( color == "blue"):
        column_map["red_score"] = "their_score"

    color_prefix = color + "_"
    #get columns associated with this team, like team_<value>
    for c in columns:
        if c.startswith(color_prefix):
            column_map[c] = c.replace(color_prefix,"")

    #print("Col map=",column_map)
    return column_map

def calculate_opr_ccwm_dpr(matches:pd.DataFrame) -> pd.DataFrame:

    #get the unique list of teams
    team_list = pd.unique(matches[['red1','red2','red3','blue1','blue2','blue3']].values.ravel('K'))
    #print("Unique Teams: One column, num rows= Nteams ")
    #score_cols = extract_red_and_blue_columns(matches)
    red_col_map = column_map_for_color(matches.columns,'red')
    blue_col_map = column_map_for_color(matches.columns,'blue')
    #return None
    #red_cols = ['red1','red2','red3','blue_score'] + extract_columns_for_color(matches,'red_')
    #blue_cols = ['blue1', 'blue2', 'blue3','red_score'] + extract_columns_for_color(matches, 'blue_')
    #print("Red Cols=",red_cols)
    #print("Blue Cols=", blue_cols)
    #print("R=",matches[red_cols])
    #print("B=",matches[blue_cols])
    #split into a longer dataset with data not split by blue and red
    #red_data = matches[red_cols].rename(columns={
    #    'red1':'t1',
    #    'red2':'t2',
    #    'red3':'t3',
    #    'blue_score':'their_score'
    #})

    #blue_data = matches[blue_cols].rename(columns={
    #    'blue1':'t1',
    #    'blue2':'t2',
    #    'blue3':'t3',
    #    'red_score':'their_score'
    #})
    red_data = matches.rename(columns=red_col_map)
    blue_data = matches.rename(columns=blue_col_map)

    #red_data['margin'] = red_data['score'] - red_data['their_score']
    #blue_data['margin'] = blue_data['score'] - blue_data['their_score']
    all_data = pd.concat([red_data,blue_data])
    #all_data['margin'] = all_data['score'] - all_data['their_score']
    print(all_data)
    return None
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
    left_side = all_data[['our_score','their_score','margin']]
    c_c = np.matrix(left_side)

    pseudo_inverse = np.linalg.pinv(m_m)
    computed = np.matmul(pseudo_inverse,c_c)
    #print("Solution")
    #print(computed)

    results_2 = pd.DataFrame(computed,columns=['opr','dpr','ccwm'])
    teams_2 = pd.DataFrame(team_list,columns=['team_id'])
    results_all = pd.concat([teams_2, results_2], axis=1)

    """
            team_id        opr       ccwm
        16     1771  59.877861  40.854197
        4      2974  49.007513  27.565074
        19      343  39.377108  11.797834
        ....    
    """
    return results_all.sort_values(by=['opr'],ascending=False)


def get_match_data():
    matches = con.sql("select * from frc_2025.tba.matches where event_key = '2024gacmp'").df()
    #return matches[ ['red1','red2','red3','blue1','blue2','blue3','red_score','blue_score']]
    return matches

if __name__  == '__main__':
    matches = get_match_data()
    print(matches)
    r = calculate_opr_ccwm_dpr(matches)
    print("Results:")
    print(r)