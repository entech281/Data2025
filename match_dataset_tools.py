import pandas as pd
import json
import re
from dataclasses import dataclass
from typing import Union


def find_single_team_data( matches: pd.DataFrame) -> Union[None,pd.DataFrame]:
    """
    Finds columns that are provided for individual teams.
    Typically, this means there is a field like _robot1, _robot2, and _robot3
    Corresponding to teams red_one, etc
    If there are N fields encoded this way in match data:
       (1) 6 fields are used, one for each team
       (2) the result set will be 6x the rows of the original, but with only one field per
           group.
    Example:
        matches has 100 rows with columns:
           red1, red2, red3,
           blue1,blue2,blue3,
           red_park_robot1, red_park_robot2, red_park_robot3
           blue_park_robot1, blue_park_robot3, blue_park_robot3

        the result will have two columns:
        team, park
        with 600 rows.

    :param matches:
    :return: A dataframe having team number and values corresponding to detected
    fields, or NONE if the dataframe doesnt appear to have team-speicific data
    """
    all_columns = matches.columns
    team_fields = [ 'red1','red2','red3','blue1','blue2','blue3']
    if not (set(team_fields).issubset(set(all_columns))):
        print("Doesnt appear to have all team Fields in it!")
        return None

    found_columns = []
    finder = re.compile(r"^([r][e][d]|[b][l][u][e])_(.*)_robot(\d)", re.IGNORECASE)

    col_groups = {
        'red1': [],
        'red2': [],
        'red3': [],
        'blue1': [],
        'blue2': [],
        'blue3': []
    }

    for colname in all_columns:
        found = finder.match(colname)
        if found is not None:

            col_groups[found.group(1) + found.group(3)].append({
                'original_col': found.group(), # red_parked_robot1
                'new_col' : found.group(2) # parked
            })

    all_dfs = []

    for k,v in col_groups.items():
        cols_to_select = [k]
        rename_fields = { k: 'team'}

        for c in v:
            cols_to_select.append(c['original_col'])
            rename_fields[c['original_col']] = c['new_col']


        df_to_add = matches[cols_to_select].rename(columns=rename_fields)
        all_dfs.append(df_to_add)

    result = pd.concat(all_dfs,axis=0)
    return result

