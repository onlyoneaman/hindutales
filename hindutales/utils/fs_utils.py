import os
import re


def sanitize_filename(filename: str) -> str:
    filename = filename[:220]
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

def make_dir(dir: str) -> str:
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def make_dirs(dirs: list[str]) -> list[str]:
    for dir in dirs:
        make_dir(dir)
    return dirs
    
def save_to_file(content: bytes, path: str, mode: str = "wb") -> None:
    with open(path, mode) as f:
        f.write(content)
