import os

def match(files, query):
    terms = " ".join(query).lower().split() if isinstance(query, list) else query.lower().split()
    matches = []
    for i in files:
        filename = os.path.basename(i).lower()
        if all(term in filename for term in terms):
            matches.append(i)

    return matches
