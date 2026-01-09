import json
from pathlib import Path


def load_json(path: str) -> list[dict]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_response_json(path, new_item):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Prevent nested lists
    if isinstance(new_item, list):
        data.extend(new_item)
    else:
        data.append(new_item)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def extract(tool_results):
    result = []
    for tool in tool_results:
        result.append(tool["input"])
        result.append(tool["output"])
    return result
