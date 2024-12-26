import pandas as pd
from match_dataset_tools import find_single_team_data
from pandas.testing import assert_frame_equal


def test_match_data():
    matches = pd.read_parquet("./tests/data/matches.pq")
    r = find_single_team_data(matches)
    assert 6*len(matches) == len(r)
    assert ['team','auto_line','end_game'] == list(r.columns)
