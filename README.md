# GitHub Actions logs searcher

This small tool allows you to search for specific words among the GitHub Actions logs you have access to. A common use case for this is to look for incoming deprecations of components/steps/actions in use within your workflows.

Note that for larger organisations or user accounts with a lot of repositories (or if you oversize the `MAX_NUMBER_OF_RUN_LOGS` parameter) you can very quickly reach the [GitHub API rate limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28#rate-limiting) (5k per hour per regular user).

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
