import os
import os.path
import re


def safe_filename(unsafe):
    """
    Turn an unsafe string into something that ought to be a nice safe filename on both linux and windows.
    """
    maxlength = 50
    keepcharacters = ('.', '_')
    unsafe = re.sub(r"[ \(\)]+", "_", unsafe)
    return "".join(c for c in unsafe if c.isalnum() or c in keepcharacters).rstrip()[:maxlength].strip("_")


def walk(path, pattern = ".*", levels = -1):
    """
    Find files whose name matches a pattern up to a given depth.
    """
    r = re.compile(pattern)

    # yield matching files
    for item in os.listdir(path):
        spath = os.path.join(path, item)
        if os.path.isfile(spath) and r.match(item):
            yield spath

    # recurse
    for item in os.listdir(path):
        spath = os.path.join(path, item)
        if os.path.isdir(spath) and levels != 0:
            for res in walk(spath, pattern, levels - 1):
                yield res


def mkdirs(path):
    """
    Make dir including parent dirs if they do not exist.
    """
    if not os.path.isdir(path):
        os.makedirs(path)
