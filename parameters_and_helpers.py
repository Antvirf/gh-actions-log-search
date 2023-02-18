import json

# do not leave this empty - put in either your GitHub username or organization name
REPO_NAME_INCLUDE_PATTERNS = ["Antvirf"]
WORDS_TO_FIND = ["deprecated"]

MAX_NUMBER_OF_RUN_LOGS = 5

# path params
RUN_IDS_JSON_PATH = "repo_run_ids.json"


def save_dict_as_json(input_dict, file_name):
    with open(file_name, "w") as writer:
        json.dump(input_dict, writer, indent=4)


def read_dict_as_json(file_name):
    with open(file_name, "r") as reader:
        return json.load(reader)
