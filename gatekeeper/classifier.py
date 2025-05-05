# gatekeeper/classifier.py
import pandas as pd
from .config import settings

def classify_accounts(summary: pd.DataFrame, rh: pd.DataFrame) -> pd.DataFrame:
    merged = summary.merge(
        rh, left_on='cuti', right_on='rh_id',
        how='left', indicator=True
    )
    merged['category'] = merged['_merge'].map({
        'both':'in_sgb', 'left_only':'out_sgb'
    })
    merged['days_inactive'] = (
        merged['extraction_date'] - merged['last_login']
    ).dt.days.fillna(float('inf'))
    merged['in_sgb_status'] = merged.apply(
        lambda r: 'never_used' if pd.isna(r['last_login'])
                  else ('dormant' if r['days_inactive']>settings.threshold_days_inactive
                        else 'active'),
        axis=1
    )
    return merged
