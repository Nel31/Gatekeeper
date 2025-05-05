# gatekeeper/duplicate_detector.py
import sys
import pandas as pd

def check_duplicates(df: pd.DataFrame):
    in_sgb = df[df['category']=='in_sgb']
    dupes = (
        in_sgb
        .assign(full_name=in_sgb['last_name'].str.strip() + ' ' +
                           in_sgb['first_name'].str.strip())
        .full_name.value_counts()
    )
    dupes = dupes[dupes > 1]
    if not dupes.empty:
        print(f"Duplicate accounts: {dupes.to_dict()}")
        sys.exit(84)
