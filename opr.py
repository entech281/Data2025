import pandas as pd
from motherduck import con
import numpy as np


def calculate_opr_ccwm_dpr(matches:pd.DataFrame) -> pd.DataFrame:

    #get the unique list of teams
    team_list = pd.unique(matches[['red1','red2','red3','blue1','blue2','blue3']].values.ravel('K'))
    print("Unique Teams: One column, num rows= Nteams ")

    M=[]
    for idx,match in matches.iterrows():
        r=[]
        for team in team_list:
            if match['red1'] == team or match['red2'] == team or match['red3'] == team:
                r.append(1)
            else:
                r.append(0)
        M.append(r)

        b = []
        for team in team_list:
            if match['blue1'] == team or match['blue2'] == team or match['blue3'] == team:
                b.append(1)
            else:
                b.append(0)
        M.append(b)

    combined = []
    for index,match in matches.iterrows():
        combined.extend([
            [match['red_score'],match['red_score'] - match['blue_score']],
            [match['blue_score'],match['blue_score'] - match['red_score'] ]
        ])

    m_m = np.matrix(M)
    c_c = np.matrix(combined)

    pseudo_inverse = np.linalg.pinv(m_m)
    all = np.matmul(pseudo_inverse,c_c)

    def get_matrix_into_one_list(m,):
        return np.reshape(m,(1,-1)).tolist()[0]

    results_2 = pd.DataFrame(all,columns=['opr','ccwm'])
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
    return matches[ ['red1','red2','red3','blue1','blue2','blue3','red_score','blue_score']]


if __name__  == '__main__':
    matches = get_match_data()
    print(matches)
    r = calculate_opr_ccwm_dpr(matches)
    print("Results:")
    print(r)