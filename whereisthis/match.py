import os
import re

def fuzzy(query, target):
    max_gap = 2
    if query == target:
        return 100000

    if len(query) <= 4:
        return 500 if query in target else None

    query_i = 0
    score = 0
    last_match = -2

    for index, cur in enumerate(target):
        if query_i < len(query) and cur == query[query_i]:
            score += 10
            if index == last_match + 1:
                score += 8

            if index == 0 or target[index - 1] in "_-.":
                score += 6

                
                if last_match != -2 and (index - last_match - 1) > max_gap:
                    return None

            last_match = index
            query_i += 1

    if query_i == len(query):
        score -= (len(target) - len(query)) * 2
        return score

    return None


def match(files, query):
    if isinstance(query, list):
        query = " ".join(query)
    terms = [t for t in re.split(r"[^a-z0-9]+", query.lower()) if t]
    matches = []

    for path in files:
        filename = os.path.basename(path).lower()
        tokens = re.split(r"[^a-z0-9]+", filename)

        total_score = 0
        ok = True

        for term in terms:
            best = None
            for tok in tokens:
                if not tok:
                    continue
                score = fuzzy(term, tok)
                if score is not None and (best is None or score > best):
                    best = score

            if best is None:
                ok = False
                break

            total_score += best

        if ok:
            matches.append((total_score, path))

    matches.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in matches]