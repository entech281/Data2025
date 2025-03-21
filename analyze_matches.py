import argparse
from pathlib import Path
from log_tools.cycle_times import load_all_folders_in_path

def main():
    parser = argparse.ArgumentParser(description="Process input folder and load data.")
    parser.add_argument("input", type=Path, help="Path to the input folder")
    parser.add_argument("--nocache", action="store_true", help="Ignore cached file if present")

    args = parser.parse_args()
    input_path = args.input
    use_cache = not args.nocache

    if not input_path.exists() or not input_path.is_dir():
        parser.error(f"The provided path '{input_path}' does not exist or is not a directory.")

    all_dfs = load_all_folders_in_path(input_path,use_cache=use_cache)
    for d in all_dfs:
        print(d['name'])  # Example usage of the dataframe

    #r = load_all_folders_in_path(input_path,use_cache)
    #print(r)


if __name__ == '__main__':
    main()