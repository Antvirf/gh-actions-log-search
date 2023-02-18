# GitHub Actions logs searcher

This small tool allows you to search for specific words among the GitHub Actions logs you have access to. A common use case for this is to look for incoming deprecations of components/steps/actions in use within your workflows.

Note that for larger organisations or user accounts with a lot of repositories (or if you oversize the `MAX_NUMBER_OF_RUN_LOGS` parameter) you can very quickly reach the [GitHub API rate limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28#rate-limiting) (5k per hour per regular user). The maximum number of calls that will be made is modeled below.

```math
1+N_{repositories}*min(MAX\_NUMBER\_OF\_RUN\_LOGS, N_{workflow runs in repository})
```

As an example, for a user with `20` repositories, where each repo has `10` workflow runs, but where `MAX_NUMBER_OF_RUN_LOGS` is set to `5`, the script will make one initial call to get the list of repositories, and then 5 calls for each repository-run, for a total of `1 + 20 * 5 = 101` calls. The actual number may vary slightly if repositories contain less workflow runs than `MAX_NUMBER_OF_RUN_LOGS`.

## Overview of code structure

1. `1_get_repos_and_workflow_runs.py`
    1. Given your access token and repository name inclusion pattern, make 1 API call to get list of your repositories.
    1. For every repository, call the GitHub API to [get a list of workflow runs](https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-repository). The tool will now truncate the response to `MAX_NUMBER_OF_RUN_LOGS`, which is set to 5 by default.
    1. At this stage, your list of repositories and list of workflow runs in them is stored as a JSON `repo_run_ids.json`. It has `X` keys, each mapped to an entry containing at most `MAX_NUMBER_OF_RUN_LOGS` entries.
1. `2_get_logs_for_workflow_runs.py`
    1. Read `repo_run_ids.json`.
    1. Next, an API call is made for each repository's workflow runs (zipped logs are saved in `./logs/`), and then extracted into `./logs_extracted/`. This operation is asynchronous.
1. `3_find_words_in_logs.py`
    1. Finally, go through every file, line-by-line, in `./logs_extracted/` and save any that contain (case-insensitively) the words provided in the `WORDS_TO_FIND` parameter in a JSON file `matched_lines.json`. This contains a dictionary where repository names are keys, and the items are lists of log-lines that contained one or more of the words provided in `WORDS_TO_FIND`.

Steps 1 and 2 both cache their outputs, so repeated runs will not make further calls. You can delete the previously cached information with `make clean`.

## Usage - clone, install dependencies, run

1. Clone repository and `cd` into it:

    ```shell
    git clone https://github.com/Antvirf/gh-logs-search && cd gh-actions-log-search
    ```

1. Install required Python packages - `aiofiles`, `aiohttp`, `PyGithub`:

    ```shell
    pip install -r requirements.txt
    ```

1. Create your [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) and add it to a file called `.secrets`:

    ```shell
    echo YOUR_PERSONAL_ACCESS_TOKEN > .secrets
    ```

1. Configure the `parameters_and_helpers.py` file with your own values:

    ```python
    REPO_NAME_INCLUDE_PATTERNS = ["Antvirf"] # include at least your GitHub username or organization name, or specific repository name if desired

    WORDS_TO_FIND = ["deprecated"] # configure as required based on what you are looking for
    ```

1. Run the tool

    ```shell
    make full-run
    ```

    If you don't have make (i.e. you get `command not found: make` or so), run each file in sequence:

    ```shell
    python 1_get_repos_and_workflow_runs.py
    python 2_get_logs_for_workflow_runs.py
    python 3_find_words_in_logs.py
    ```

1. Inspect results, saved in `matched_lines.json`

    ```shell
    open matched_lines.json
    ```
