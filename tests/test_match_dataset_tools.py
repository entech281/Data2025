import pandas as pd
from match_dataset_tools import find_single_team_data,unstack_data_from_color
from pandas.testing import assert_frame_equal


def test_extracting_single_team_data():
    matches = pd.read_parquet("./tests/data/matches.pq")
    r = find_single_team_data(matches)
    assert 6*len(matches) == len(r)
    assert ['team','auto_line','end_game'] == list(r.columns)

def test_unstacking_team_data():
    matches = pd.read_parquet("./tests/data/matches.pq")
    r = unstack_data_from_color(matches)
    assert 2*len(matches) == len(r)
    print(list(r.columns))
    assert {'t1','t2','t3','score','their_score','rp','their_rp'}.issubset(set(r.columns))

    #assert {'blue1','blue2','blue3','red1','red2','red3'}.isdisjoint(set(r.columns))