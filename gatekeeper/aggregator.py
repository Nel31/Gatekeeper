# gatekeeper/aggregator.py
import pandas as pd

def aggregate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby('cuti')
    return grp.agg(
        last_login=('last_login', 'max'),
        extraction_date=('extraction_date', 'first'),
        lib_anomaly=('lib', lambda s: s.nunique()>1),
        lputi_extracted=('lputi', 'first'),
        lputi_anomaly=('lputi', lambda s: s.nunique()>1),
        status_anomaly=('status', lambda s: s.nunique()>1)
    ).reset_index()
