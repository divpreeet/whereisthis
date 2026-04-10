import os

def match(files, query):
    terms = " ".join(query).lower().split() if isinstance(query, list) else query.lower().split()
    matches = []
    for i in files:
        if all(term in os.path.basename(i) for term in terms):
            matches.append(i)
    return matches
