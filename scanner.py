import os

def scan(dir=".", hidden=False):
    files = []
    for root, dirs, file in os.walk(dir):
        if not hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            file = [f for f in file if not f.startswith(".")]

        for name in file:
            files.append(os.path.join(root, name).lower())
    return files