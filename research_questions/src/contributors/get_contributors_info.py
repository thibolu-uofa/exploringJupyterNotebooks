"""
Get data details from each contributor that contributes to a given repository.
Get data from both splits of SE/non SE for notebooks dataset and also for 
python files dataset (SE py and Non SE py).

Before running this script, you should set the variables 'split' and
'repos_interval_{split}' in main, according to your needs. Maybe you need
to run this script more than one time, changing these parameters, to be able 
to query all the desired data form the API. In main, there are intervals that
worked without exceeding the API limit.

You need a GitHub personal auth token configured in a .env to run this script.

In general, it is possible to query 250 repositories at once, and the average
speed of the request is 3 repositories in one minute. After querying 250 
repositories, wait for at least an hour to run the script again, to prevent 
exceeding the limit of 5000 requests per hour from GitHub rest API.

You can run this script with the command:

python -m research_questions.src.contributors.get_contributors_info

from inside the main  directory of this project."""

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


def format_api_response(user_response, login):

    user_data = user_response.json()
    user_id = user_data.get('id')
    name = user_data.get('name')
    email = user_data.get('email')
    location = user_data.get('location')
    hireable = user_data.get('hireable')
    public_repos = user_data.get('public_repos')
    created_at = user_data.get('created_at')
    followers = user_data.get('followers')
    following = user_data.get('following')
    user_company = user_data.get('company')

    contributer_info = {
        "user_id": user_id,
        "name": name,
        "num_user_public_repos": public_repos,
        "login": login,
        "email": email,
        "location": location,
        "created_at": created_at,
        "hireable": hireable,
        "num_followers": followers,
        "num_following": following,
        "user_company": user_company
    }

    return contributer_info


def fetch_contributors(repo_url, headers):
    contributors = []
    page = 1

    try:
        owner, repo = format_repo_info(repo_url)

        while True:
            # Send the request to fetch contributors
            url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
            params = {'per_page': 100, 'page': page}
            response = requests.get(url, headers=headers, params=params)

            # check if the request was successful
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break

                for contributor in data:

                    login = contributor.get('login')

                    user_url = f"https://api.github.com/users/{login}"
                    # getting user contributor info:
                    user_response = requests.get(user_url, headers=headers)

                    if user_response.status_code == 200:

                        contributor_info = format_api_response(
                            user_response, login)
                        contributor_info['repo_url'] = repo_url

                        contributors.append(contributor_info)
                    else:
                        print(
                            f"Failed to fetch details for user {login}: {user_response.status_code}")

                page += 1  # move to the next page of the request
            elif response.status_code == 403 or response.status_code == 429:
                print(
                    f"API limit exceeded. Couldn't process all repos. \n"
                    f" Last repo_url processed: {repo_url}")

            else:
                print(
                    f"Query failed with status code {response.status_code}: {response.text} for {repo_url}")
                break

        return contributors

    except:
        print(f"Can't process repo {repo_url}")
        return None


def get_contributors_all_repos(split: str, txt_directory, headers, interval):

    repos_urls_list = get_repos_dataset_list(split, txt_directory)

    processed_repos = 1
    all_contributors = []
    urls_in_interval = repos_urls_list[interval[0]:interval[1]]

    for repo_url in urls_in_interval:

        contributors = fetch_contributors(repo_url, headers)
        time.sleep(1)

        if not contributors:
            continue

        all_contributors.extend(contributors)
        # avoiding querying the github API so fast:
        time.sleep(2)
        print(f"number of processed repos: {processed_repos}")
        processed_repos += 1

    return all_contributors


def save_results_in_csv(all_contributors, split, interval):

    df = pd.DataFrame(all_contributors)

    interval_str = f"_{interval[0]}_to_{interval[1]}"

    folder_results = Path(Path.cwd(), "research_questions",
                          "src", "contributors",
                          split)

    result_filepath = folder_results
    folder_results.mkdir(exist_ok=True)
    csv_filename = 'contributors_' + split + interval_str + '.csv'
    csv_filepath = result_filepath / csv_filename
    df.to_csv(csv_filepath, index=False, encoding='utf-8')

    print(f"Contributors information has been written to {csv_filename}")


if __name__ == '__main__':

    config = Configs()
    github_auth_token = config.github_auth_token
    headers = configure_request(github_auth_token)

    current_dir = Path(__file__).resolve().parent.parent.parent.parent
    dataset_lists = "dataset_lists/"
    dataset_lists_path = Path(current_dir, "source") / dataset_lists

    # the number of repositories you want to query information of from the
    # GitHub API. In general, it is possible to query 250 repositories
    # at once without exceeding the API limit.

    # intervals used to obtain the data for notebooks dataset:
    # repos_interval_SE = (0, 250)
    # repos_interval_SE = (250, 376)
    # repos_interval_non_SE = (0, 250)
    # e.g: querying from the 250th repo to 525th repo from the dataset_lists:
    # repos_interval_non_SE = (250, 526)

    # intervals used to obtain the data for python dataset:
    # repos_interval_SE = (0, 250)

    # repos_interval_SE_py = (0, 250)
    # repos_interval_SE_py = (250, 500)
    # repos_interval_SE_py = (500, 608)
    # allowed splits: 'SE' and 'non_SE' for notebooks dataset,
    # and 'SE_py' and 'non_SE_py' for python dataet
    # change split to 'SE' when getting information from the SE split
    # of notebooks:
    repos_interval_non_SE_py = (0, 110)
    split = 'non_SE_py'
    all_contributors_non_SE_info = get_contributors_all_repos(
        split=split, txt_directory=dataset_lists_path,
        headers=headers, interval=repos_interval_non_SE_py)

    save_results_in_csv(all_contributors_non_SE_info,
                        split, repos_interval_non_SE_py)
