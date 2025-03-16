from log_helpers import read_log_to_dataframe
from pathlib import Path
import pandas as pd
from time import time
import re
from collections import namedtuple
from datetime import datetime


MatchInfo = namedtuple('MatchInfo', ['event_time', 'event_key', 'match_type', 'match_number'])
MAX_REASONABLE_TIME = 90

def parse_wpilog_filename(file_path: Path):
    # Get the filename from the Path object
    filename = file_path.name
    print(f"Processing filename: {filename}")  # Debugging output

    # Updated regular expression to correctly match match type and match number
    pattern = r'([a-zA-Z]+)_(?P<date>\d{2}-\d{2}-\d{2})_(?P<time>\d{2}-\d{2}-\d{2})_(?P<event_key>[a-zA-Z]+)_(?P<match_type>[a-z])(?P<match_number>\d+)\.wpilog'
    practice_pattern = r'([a-zA-Z]+)_(?P<date>\d{2}-\d{2}-\d{2})_(?P<time>\d{2}-\d{2}-\d{2})\.wpilog'
    match = re.match(pattern, filename)
    practice_match= re.match(practice_pattern,filename)
    # Debugging: print if the match is successful or not
    match_counter=0
    if match:
        event_key = match.group('event_key')
        date_str = match.group('date')
        time_str = match.group('time')
        match_type = match.group('match_type')
        match_number = int(match.group('match_number'))

        # Convert date and time to a datetime object
        event_time = datetime.strptime(f"{date_str} {time_str}", "%y-%m-%d %H-%M-%S")
    elif practice_match:
        event_key = 'practice'
        date_str = practice_match.group('date')
        time_str = practice_match.group('time')
        match_type = 'p'
        match_number = match_counter
        match_counter+= 1

        # Convert date and time to a datetime object
        event_time = datetime.strptime(f"{date_str} {time_str}", "%y-%m-%d %H-%M-%S")
    else:
        raise ValueError(f"Filename '{filename}' does not match the expected pattern.")

    # Extract matched groups

    # Map match type to a descriptive name
    match_type_map = {'p': 'Prac', 'e': 'Comp', 'q': 'Qual'}
    match_type = match_type_map.get(match_type, 'Unknown')
    event_key_with_year = f"2025{event_key}"
    return MatchInfo(event_time=event_time, event_key=event_key_with_year, match_type=match_type, match_number=match_number)


def load_wpilib_log(file_path:Path):
    s = time()
    (df,error) = read_log_to_dataframe(input_path=file_path)
    print(f"Load: {time()-s } s ")
    print(df)
    return df

def add_match_info(df:pd.DataFrame, mf:MatchInfo)-> pd.DataFrame:
    df['event_key'] = mf.event_key
    df['ts'] = mf.event_time
    df['match_type'] = mf.match_type
    df['match_number'] = mf.match_number
    return df


def extract_cycles(df) -> pd.DataFrame:
    df_filtered = df[df['Name'] == '/RealOutputs/InternalCoralDetectorOutput/HasCoral']
    # Identify transitions from False to True
    df_filtered['Prev_Value'] = df_filtered['Value'].shift(1)  # Shift previous row

    df_filtered['Start'] = (df_filtered['Prev_Value'] == False) & (df_filtered['Value'] == True)

    # Extract timestamps for Start and End
    start_times = df_filtered.loc[df_filtered['Start']]
    start_times['start_timestamp'] = start_times['Timestamp'].shift(1)
    start_times['end_timestamp'] = start_times['Timestamp']
    start_times['duration'] = start_times['end_timestamp'] - start_times['start_timestamp']
    start_times = start_times.dropna()
    #print(start_times)
    return start_times


def analyze_cycle_phases(cycle_timestamps:pd.DataFrame, full_df) -> pd.DataFrame:
    # Phase 2: Analyze travel_to, deploy, travel_from, and cycle_type for each cycle
    cycle_results = []


    for _, cycle in cycle_timestamps.iterrows():
        cycle_start_time = cycle['start_timestamp']
        cycle_end_time = cycle['end_timestamp']

        # Filter rows within the cycle and where Name == /RealOutputs/ElevatorOutput/currentPosition
        cycle_data = full_df[(full_df['Timestamp'] >= cycle_start_time) &
                             (full_df['Timestamp'] <= cycle_end_time) &
                             (full_df['Name'] == '/RealOutputs/ElevatorOutput/currentPosition')]

        # Initialize phase times
        travel_to_end = deploy_start = deploy_end = None

        max_position = cycle_data['Value'].max()

        # Set cycle type based on max currentPosition
        if max_position > 18.0:
            cycle_type = 'L4'
        elif max_position > 9.0:
            cycle_type = 'L3'
        elif max_position > 4.0:
            cycle_type = 'L2'
        else:
            cycle_type = 'L1'

        deploy_start_timestamp = cycle_data[ cycle_data['Value'] > 1]['Timestamp'].min()
        deploy_end_timestamp = cycle_data[cycle_data['Value'] < 0.05 ]['Timestamp'].max()
        deploy_time = deploy_end_timestamp - deploy_start_timestamp
        travel_to_time  =deploy_start_timestamp- cycle_start_time
        travel_from_time  = cycle_end_time - deploy_end_timestamp

        c = {
            'start_timestamp': cycle_start_time,
            'end_timestamp': cycle_end_time,
            'duration': cycle['duration'],
            'travel_to': travel_to_time,
            'deploy': deploy_time,
            'travel_from': travel_from_time,
            'cycle_type': cycle_type
        }
        if cycle['duration'] <= MAX_REASONABLE_TIME:
            cycle_results.append(c)
        else:
            print(f"Warning: discarded weird cycle {c}")

    return pd.DataFrame(cycle_results)


def load_single_logfile(wpi_log_file:Path) -> pd.DataFrame:
    all_data = load_wpilib_log(wpi_log_file)
    mf = parse_wpilog_filename(wpi_log_file)
    cycle_summary = extract_cycles(all_data)

    cycle_details = analyze_cycle_phases(cycle_summary, all_data)

    if len(cycle_details) == 0:
        return None


    r = add_match_info(cycle_details, mf)
    #print(r)

    #tricky! We need to get a timestamp that is unified over all time, for plotting on horizontal axis
    #to do that, each file has a timestamp ( in r['ts']), and
    # then a timestamp from start of match ( in start_timestamp).
    r['cycle_timestamp'] = r['ts'] + pd.to_timedelta(r['start_timestamp'], unit='s')
    r['filename'] = str(wpi_log_file.name)
    #print(r)
    return r


def load_all_logs_from_path(log_dir:Path) -> pd.DataFrame:
    all_data = []
    for file_path in log_dir.iterdir():
        if file_path.is_file():
            print(f"Loading File: {file_path}")
            l = load_single_logfile(file_path)
            if l is not None:
                all_data.append( l)
            print(f"Finished File: {file_path}")
    r = pd.concat(all_data)
    return r

def reorder_and_add_rownum(df):
    df.sort_values(by=['cycle_timestamp'],ascending=True)
    df = df.reset_index(drop=True)
    df['match_index'] = df.index + 1
    return df

def test_one_file():
     print ( reorder_and_add_rownum(
         load_single_logfile( Path("./match_logs/hartsville/akit_25-03-07_15-52-34_schar_q17.wpilog") )
     ))

def main():

    all_cycles = load_all_logs_from_path(Path("./match_logs/3-15-practice/"))
    all_cycles = reorder_and_add_rownum(all_cycles)
    print(all_cycles)
    all_cycles.to_csv("./data/cycle_data_3_15_25.csv",header=True,quotechar='"',index=False)

if __name__ == '__main__':
    #test_one_file()
    main()