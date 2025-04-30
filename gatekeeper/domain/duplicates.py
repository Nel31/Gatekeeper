from collections import Counter

def detect_duplicates(df):
    names = df['nom'] + ' ' + df['prenom']
    c = Counter(names)
    return [name for name, count in c.items() if count > 1]
