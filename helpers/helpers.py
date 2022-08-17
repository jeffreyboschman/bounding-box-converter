import os
import pathlib


def ensure_directory_exists(dir_path):
    """Creates directory (and the path leading up to it) if it does not exist. If it already exists, then does nothing."""
    if not os.path.exists(dir_path):
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def standardize_string(text):
    """Standardizes texts to be lowercase and use underscores instead of spaces."""
    text = text.strip()
    text = text.lower()
    text = text.replace(" ", "_")
    return text