import os

def scan(dir):
    files = []
    for root, dirs, file in os.walk(dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for name in file:
            files.append(os.path.join(root, name).lower())
    return files

scan("/Users/divpreet/")


