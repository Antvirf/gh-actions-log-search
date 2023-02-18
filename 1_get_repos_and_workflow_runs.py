import os

from github import Github

from parameters_and_helpers import (MAX_NUMBER_OF_RUN_LOGS,
                                    REPO_NAME_INCLUDE_PATTERNS,
                                    RUN_IDS_JSON_PATH, read_dict_as_json,
                                    save_dict_as_json)


def get_repositories_and_action_run_ids(access_token):

    py_github = Github(access_token)
    repo_list = py_github.get_user().get_repos()

    # limit repositories to a particular organisation or other name pattern
    repo_list = [x for x in repo_list if (
        any([include_name in x.url for include_name in REPO_NAME_INCLUDE_PATTERNS]))]

    # Only fetch repos if ID file does NOT exist. Otherwise, use the file.
    run_ids = {}
    print(f"{len(repo_list)} repositories to process.")
    if not os.path.exists(RUN_IDS_JSON_PATH):
        for repo in repo_list:
            ids = []
            print(f"Getting workflow run list for {repo.full_name}...")
            count = 0
            for wf in repo.get_workflow_runs():
                if count >= MAX_NUMBER_OF_RUN_LOGS:
                    break
                ids.append(wf.id)
                count += 1

            if ids:
                run_ids[repo.full_name] = ids

        save_dict_as_json(run_ids, RUN_IDS_JSON_PATH)
    else:
        run_ids = read_dict_as_json(RUN_IDS_JSON_PATH)

    return repo_list, run_ids


if __name__ == "__main__":
    with open(".secrets", "r") as secrets:
        access_token = secrets.readlines()[0].strip()

    get_repositories_and_action_run_ids(access_token)
