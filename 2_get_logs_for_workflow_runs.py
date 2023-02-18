import asyncio
import os
import time
import zipfile

import aiofiles
import aiohttp
from github import Github

from parameters_and_helpers import (REPO_NAME_INCLUDE_PATTERNS,
                                    RUN_IDS_JSON_PATH, read_dict_as_json)


def get_repositories_and_action_run_ids_read_only(access_token):
    run_ids = read_dict_as_json(RUN_IDS_JSON_PATH)

    py_github = Github(access_token)
    repo_list = py_github.get_user().get_repos()

    # limit repositories to a particular organisation or other name pattern
    repo_list = [x for x in repo_list if (
        any([include_name in x.url for include_name in REPO_NAME_INCLUDE_PATTERNS]))]

    return repo_list, run_ids


async def fetch_single_log(session, repository, wf_id):
    url = f"https://api.github.com/repos/{repository}/actions/runs/{wf_id}/logs"
    filename = f"{str(repository).replace('/', '-')}_{wf_id}"
    extracted_file_path = f"./logs_extracted/{str(repository).replace('/', '-')}/{wf_id}"

    # Check if the particular workflow has already been downloaded - if yes, skip
    if os.path.exists(extracted_file_path):
        return
    async with session.get(url) as resp:
        content = await resp.read()
        status = resp.status

    if status == 200:
        zip_filename = f"./logs/{filename}.zip"
        async with aiofiles.open(zip_filename, "+wb") as file_writer:
            print(f"Downloaded {filename}...")
            await file_writer.write(content)

        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()
            found_names = [x for x in zip_contents if '.txt' in x]
            for name in found_names:
                file_path = f"{extracted_file_path}/{name}"
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                with open(file_path, "wb") as file_writer:
                    file_writer.write(zip_ref.read(name))
    elif status in [404, 410]:
        return
    else:
        print(status)


async def fetch_logs(repo_list, run_ids, access_token):
    async with aiohttp.ClientSession(headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    },
            auto_decompress=True) as session:
        tasks = []

        for repo in repo_list:
            list_of_ids = run_ids.get(repo.full_name, [])

            # check if we have anything to process
            for wf_id in list_of_ids:
                tasks.append(asyncio.ensure_future(
                    fetch_single_log(session, repo.full_name, wf_id)))

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    with open(".secrets", "r") as secrets:
        access_token = secrets.readlines()[0].strip()

    repo_list, run_ids = get_repositories_and_action_run_ids_read_only(
        access_token)

    # download and unzip logs
    num_of_records = sum([len(x) for x, _ in run_ids.items()])
    start_time = time.time()
    asyncio.run(fetch_logs(repo_list, run_ids, access_token))
    total_time = max(time.time() - start_time, 0.01)
    print(f"--- {num_of_records} action logs processed in {total_time} seconds ({num_of_records/total_time} per second) ---")
