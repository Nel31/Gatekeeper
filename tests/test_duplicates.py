import pandas as pd
from gatekeeper.domain.duplicates import detect_duplicates

def test_detect_duplicates():
    df = pd.DataFrame({'nom': ['A','A'], 'prenom': ['X','X']})
    dups = detect_duplicates(df)
    assert dups == ['A X']
