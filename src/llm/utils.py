import json
import os


def load_json(file_path: str) -> list:
    if not os.path.exists(file_path):
        data = []
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []

    return data


def append_response_json(file_path: str, new_item):
    data = load_json(file_path)
    if isinstance(new_item, list):
        data.extend(new_item)
    else:
        data.append(new_item)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def extract(tool_results):
    result = []
    for tool in tool_results:
        if tool["input"]["name"] == "get_user_curriculum_tool":
            continue
        result.append(tool["input"])
        result.append(tool["output"])
    return result


def add_message(final_data):
    chat_history = []
    tools = extract(final_data["tool_calls"])
    if final_data["assistant_text"].strip():
        assistant = {"role": "assistant", "content": final_data["assistant_text"]}
        tools.append(assistant)
    if isinstance(tools, list):
        chat_history.extend(tools)
    else:
        chat_history.append(tools)
    return chat_history