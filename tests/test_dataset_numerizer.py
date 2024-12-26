import pytest
import pandas as pd
from dataset_numerizer import numerize_dataset
from pandas.testing import assert_frame_equal
from motherduck import con
import json

def test_basic_numerizer_defaults():
    """
    Maps that convert Booleans and strings to ints are automatically generated.
    Booleans:
        True: 1, False: 0
    Strings
        'Yes and No like' become 1 for Yes and 0 for NO
        otherwise, values are assigned ints beginning with 0, in order from most frequent to least frequent
    :return:
    """
    d = pd.DataFrame({
        'a': [ 1 , 0, 2],
        'b': [ True, False,False],
        'c' : [ 'foo', 'foo','bar']
    })
    r = numerize_dataset(d)
    assert {
        "b": {
            True: 1,
            False: 0
        },
        "c": {
            "foo": 0,
            "bar": 1
        }
    } == r.mapping

    MAPPED = pd.DataFrame({
        'a': [1, 0, 2],
        'b': [True, False, False],
        'c': ['foo', 'foo', 'bar'],
        'm_b': [1, 0, 0],
        'm_c': [0, 0, 1]
    })
    assert_frame_equal(d,r.original)
    assert_frame_equal( MAPPED,r.transformed)

def test_numerizer_overwrite_columns_with_empty_prefix():
    # with an empty prefix, the original columns are replaced
    d = pd.DataFrame({
        'a': [ 1 , 0, 2],
        'b': [ True, False,False],
        'c' : [ 'foo', 'foo','bar']
    })
    r = numerize_dataset(d,prefix="")
    assert {
        "b": {
            True: 1,
            False: 0
        },
        "c": {
            "foo": 0,
            "bar": 1
        }
    } == r.mapping

    MAPPED = pd.DataFrame({
        'a': [1, 0, 2],
        'b': [1, 0, 0],
        'c': [0, 0, 1]
    })
    assert_frame_equal(d,r.original)
    assert_frame_equal( MAPPED,r.transformed)


def test_basic_extra_mapping():
    d = pd.DataFrame({
        'a': [ 1 , 0, 2],
        'b': [ True, False,False],
        'c' : [ 'foo', 'foo','bar']
    })
    r = numerize_dataset(d,value_map_overrides={
        'c':{
            'foo': 2,
            'bar': 3
        }
    })
    assert {
        "b": {
            True: 1,
            False: 0
        },
        'c':{
            'foo': 2,
            'bar': 3
        }
    } == r.mapping

    MAPPED = pd.DataFrame({
        'a': [1, 0, 2],
        'b': [True, False, False],
        'c': ['foo', 'foo', 'bar'],
        'm_b': [1, 0, 0],
        'm_c': [2, 2, 3]
    })
    assert_frame_equal(d,r.original)
    assert_frame_equal( MAPPED,r.transformed)


def test_disabling_a_mapping():
    d = pd.DataFrame({
        'a': [ 1 , 0, 2],
        'b': [ True, False,False],
        'c' : [ 'foo', 'foo','bar']
    })
    r = numerize_dataset(d,value_map_overrides={
        'c':None
    })
    assert {
        "b": {
            True: 1,
            False: 0
        }
    } == r.mapping

    MAPPED = pd.DataFrame({
        'a': [1, 0, 2],
        'b': [True, False, False],
        'c': ['foo', 'foo', 'bar'],
        'm_b': [1, 0, 0]
    })
    assert_frame_equal(d,r.original)
    assert_frame_equal( MAPPED,r.transformed)


def test_numerizing_matches_using_():
    matches = pd.read_parquet("./tests/data/matches.pq")
    r = numerize_dataset(matches, skip_columns=['key','event_key','comp_level','_dlt_id','_dlt_load_id'])
    assert len(matches) == len(r.transformed)
    print(r.transformed.columns)
    print(json.dumps(r.mapping,indent=4))



