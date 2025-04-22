import pytest
from scripts.comparator import classify_accounts
import pandas as pd

def test_classify_accounts_empty():
    # Test that classification returns empty DataFrames on empty input
    rh_df = pd.DataFrame(columns=["Identifiant Local"])
    df_all = pd.DataFrame(columns=["CUTI", "DATE DERNIÈRE CONNEXION", "DATE_EXTRACTION"])
    result = classify_accounts(df_all, rh_df)
    assert all(df.empty for df in result.values())
