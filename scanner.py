import os
from pathlib import Path

def scan(dir=".", hidden=False):
    files = []
    IGNORE_DIRS = [
        "Library",
        ".git",
        "node_modules",
        "venv",
        "__pycache__",
        ".venv",
        "dist"
    ]
    home = str(Path.home())
    
    for root, dirs, file in os.walk(dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        

        if not hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            file = [f for f in file if not f.startswith(".")]

        for name in file:
            files.append(os.path.join(root, name))
    return files