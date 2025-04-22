import pytest
from scripts.excel_loader import clean_and_load

def test_clean_and_load_empty(tmp_path):
    # Placeholder: ensure function returns an empty DataFrame when given an empty file
    # Create an empty Excel file
    file = tmp_path / "empty.xlsx"
    import pandas as pd
    pd.DataFrame().to_excel(file, index=False)
    df = clean_and_load(str(file))
    assert df.empty
