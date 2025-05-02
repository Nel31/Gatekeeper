# gatekeeper/duplicate_detector.py
import sys
import pandas as pd

def check_duplicates(df: pd.DataFrame):
    in_sgb = df[df['category']=='in_sgb']
    names = in_sgb['last_name'].str.strip() + ' ' + in_sgb['first_name'].str.strip()
    dupes = names.value_counts()[lambda x: x>1]
    if not dupes.empty:
        print(f"Duplicate detected: {dupes.to_dict()}")
        sys.exit(84)
