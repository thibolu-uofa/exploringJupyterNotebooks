"""Script to get the number of stars, forks, watchers and open issues for the
repositories in all of data splits: 'SE' and 'non SE' for notebooks, and
'SE py' and 'Non SE py' for python repositories.

Before running this script, you should set the variables 'split' and
'repos_interval_{split}' in main, according to your needs. Maybe you need
to run this script more than one time, changing these parameters, to be able 
to query all the desired data from the API. In main, there are intervals that
worked without exceeding the API limit in an hour.

You need a GitHub personal auth token configured in a .env to run this script.

The average speed of the request is around 100 repositories in 6 minutes.
It takes some minutes to run per interval."""

import requests
import pandas as pd
from research_questions.configs.configs import Configs
from pathlib import Path
import time


def get_list_active(txt_filepath):
    """Reads a txt file with repositories url"""

    with open(txt_filepath, 'r', encoding='utf-8') as f:
        active_list = []
        line = f.readline().strip()
        active_list.append(line)
        while line:
            line = f.readline().strip()
            active_list.append(line)

    return active_list


def get_repos_dataset_list(repo_type, txt_directory):
    # datasets related to notebooks ('SE' and 'Non SE' purpose) and for
    # python repositories ('SE_py' and 'non_SE_py').
    allowed_repositories_types = ['SE', 'non_SE', 'SE_py', 'non_SE_py']

    assert repo_type in allowed_repositories_types, f""" Desired split not
        encountered: {repo_type}. Allowed split types: 'SE', 'non_SE',
        'SE_py' and 'non_SE_py'. """

    if repo_type == 'SE':
        txt_filepath = Path(
            txt_directory, "nb_active_SE_purpose_repositories.txt")

    elif repo_type == 'non_SE':
        txt_filepath = Path(
            txt_directory, "nb_active_non_SE_purpose_repositories.txt")

    elif repo_type == 'SE_py':
        txt_filepath = Path(
            txt_directory, "py_active_SE_purpose_repositories.txt")
    elif repo_type == 'non_SE_py':
        txt_filepath = Path(
            txt_directory, "py_active_non_SE_purpose_repositories.txt")

    active_list = get_list_active(txt_filepath)

    return active_list


def configure_request(token):

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    return headers


def format_repo_info(repo_url: str):

    try:
        repo_info = repo_url.split('/')
        repository_owner = repo_info[-2]
        repository_name = repo_info[-1]
    except:
        return None

    return repository_owner, repository_name


def get_repo_info(repo_url, headers):
    try:
        owner, repo_name = format_repo_info(repo_url)
        # GitHub API endpoint for the repository
        api_url = f'https://api.github.com/repos/{owner}/{repo_name}'

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            repo_data = response.json()

            repo_data = {
                'url': repo_url,
                'stargazers': repo_data.get('stargazers_count', 0),
                'watchers': repo_data.get('subscribers_count', 0),
                'forks': repo_data.get('forks_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0)
            }

            return repo_data
        else:

            print(
                f"Attempt  failed for {repo_url}. Status code: {response.status_code}")

            return None
    except:
        print(f"Can't process repo {repo_url}")
        return None


def get_info_all_repos(split: str, txt_directory, headers, interval):

    repos_urls_list = get_repos_dataset_list(split, txt_directory)

    processed_repos = 1
    all_repos_info = []
    urls_in_interval = repos_urls_list[interval[0]:interval[1]]

    for repo_url in urls_in_interval:

        repo_info = get_repo_info(repo_url, headers)

        time.sleep(1)

        if not repo_info:
            continue

        all_repos_info.append(repo_info)
        # avoiding querying the github API so fast:
        time.sleep(2)
        print(f"number of processed repos: {processed_repos}")
        processed_repos += 1

    return all_repos_info


def save_results_in_csv(all_repos_info, split, interval):

    df = pd.DataFrame(all_repos_info)

    interval_str = f"_{interval[0]}_to_{interval[1]}"

    folder_results = Path(Path.cwd(), "research_questions",
                          "src", "stars_watchers_forks_issues",
                          split)

    result_filepath = folder_results
    folder_results.mkdir(exist_ok=True)
    csv_filename = 'repo_info_' + split + interval_str + '.csv'
    csv_filepath = result_filepath / csv_filename
    df.to_csv(csv_filepath, index=False, encoding='utf-8')

    print(f"Repos info has been written to {csv_filename}")


if __name__ == '__main__':

    config = Configs()
    github_auth_token = config.github_auth_token
    headers = configure_request(github_auth_token)

    current_dir = Path(__file__).resolve().parent.parent.parent.parent
    dataset_lists = "dataset_lists/"
    dataset_lists_path = Path(current_dir, "source") / dataset_lists

    # intervals used to obtain the data for notebooks dataset
    # that didn't exceed the API limit:
    # repos_interval_SE = (0, 100)
    # repos_interval_SE = (100, 300)
    # repos_interval_SE = (300, 376)
    # repos_interval_non_SE = (0, 250)
    # repos_interval_non_SE = (250, 526)

    # intervals used to obtain the data for the python dataset:
    # that didn't exceed the API limit:
    # repos_interval_SE_py = (0, 300)
    # repos_interval_SE_py = (300, 608)
    repos_interval_non_SE_py = (0, 110)

    split = 'non_SE_py'
    all_repos_info_SE = get_info_all_repos(
        split=split, txt_directory=dataset_lists_path,
        headers=headers, interval=repos_interval_non_SE_py)

    save_results_in_csv(all_repos_info_SE,
                        split, repos_interval_non_SE_py)
