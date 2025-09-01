import random
from collections import Counter
from pathlib import Path


def read_lines(file_obj):
    path = Path(file_obj.file.path)
    with path.open(encoding="utf-8") as f:
        return f.readlines()


def random_line(file_obj):
    lines = read_lines(file_obj)
    idx = random.randint(0, len(lines) - 1)
    line = lines[idx].rstrip("\n")
    most_common = Counter(line.replace(" ", "")).most_common(1)
    return {
        "line_number": idx + 1,
        "file_name": Path(file_obj.file.name).name,
        "line": line,
        "most_common_letter": most_common[0][0] if most_common else None,
    }
