"""Script that random samples urls of a given size from the 4 datasets (SE,
non_SE, SE_py and non_SE_py) and generates csv files with information of all
forks related to these sampled urls. Only valid forks are collected, implying
only active forks and forks created cefore a date limit are retrieved.
Fork informaiton gathered: forked original repository, fork owner, 
fork repository name, fork html url, fork branch name, fork creation date,
last updated date of the fork, fork stars count, fork watchers count,
number of commits ahead in the fork in relation to the forked original repository, 
commit messages that were done ahead of the original repository, number of 
bugfix messages ahead of the original forked project.
It can take hours to run, accoding to the seed value
and sample size selected."""

import requests
from datetime import datetime, timezone, timedelta
from research_questions.configs.configs import Configs
from pathlib import Path
from research_questions.src.commits_info.get_commit_info_and_bugfix_msgs import is_bugfix_commit
import random
import time
import pandas as pd
import git
import shutil

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
    """Adding the GitHub auth token, present in the .env file,
    to the request"""

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    return headers

def random_sampling_urls(url_list, sample_size, seed_value):
    """Random samples the urls, and choose the number of
    urls as the same size as set in'sample_size'.
    Since it takes too much time to process all repository
    forks, a random sample of the urls repositories
    related to each dataset is needed."""
        
    random.seed(seed_value)
    
    sampled_urls = random.sample(url_list, sample_size)
    print(f"number of urls that were sampled: {len(sampled_urls)}")
    return sampled_urls

def exponential_backoff(func, max_retries=5, initial_wait=120, *args, **kwargs):
    """Function to prevent receiving GitHub API errors related to
    doing many requests in a short amount of time."""
    retries = 0
    wait = initial_wait
    while retries <= max_retries:

        if retries == max_retries:
            print(
                f"Max retries reached, waiting for an hour...")
            time.sleep(3600)
        
        response = func(*args, **kwargs)
        if response.status_code in {200, 404}:
            return response
        elif response.status_code in {403, 429}:
            print(
                f"API limit exceeded: {response.status_code}, retrying in {wait} seconds...")
            time.sleep(wait)
            wait *= 2
            retries += 1
        else:
            print(
                f"Request failed with status code {response.status_code}, retrying in {wait} seconds...")
            time.sleep(wait)
            retries += 1
    return response

def get_all_forks(repo_url, headers,sample_size, seed_value):
    """Given a repository url present in some of our default
    dataset (SE, non_SE, SE_py, non_SE_py), this function
    retrieves all forks from a repository."""

    owner, repo = format_repo_info(repo_url)

    if not owner or not repo:
        return None

    forks_url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    forks = []
    # applying request pagination, for ensuring all forks were gathered:
    page = 1

    while len(forks) < 10:
        # preventing doing too many requests to the API:
        response = exponential_backoff(requests.get, max_retries=5, initial_wait=900,
                                       url=forks_url, headers=headers, params={'page': page, 'per_page': 100})

        # successfull API response:
        if response.status_code == 200:
            forks_page = response.json()
            if not forks_page:
                break
            for fork in forks_page:
                if  fork_is_valid(fork, date_limit):
                    forks.append(fork)
            
            page += 1
            if len(forks) > sample_size:
                forks = random_sampling_urls(forks, sample_size, seed_value)
                
                return forks
            
        # permission denied form GitHub API. The process is finished: 
        elif response.status_code == 403 or response.status_code == 429:
            print(f"API limit exceeded: {response.status_code}")
            print(f"while processing repo: {repo_url}.")
            print(f"Please, process this repo after an hour.")

            return forks

        else:
            print(
                f"Failed to retrieve forks of {repo_url} with code: {response.status_code}")
            break
        
    return forks

def format_repo_info(repo_url: str):
    """Given a GitHub repo url, gets the owner and the repo name."""
    try:
        repo_info = repo_url.split('/')
        repository_owner = repo_info[-2]
        repository_name = repo_info[-1]
    except:
        return None

    return repository_owner, repository_name


def fork_is_valid(fork, date_limit_dt):
    """Checking if a fork was made before a given date limit,
    to ensure data consistency. A fork is considered active if
    it has modifications after 10 minutes after the fork creation."""
    

    created_at = datetime.strptime(
        fork["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

    if created_at >= date_limit_dt:
        # skipíng forks created on or after the date limit:
        return False

    updated_at = datetime.strptime(
        fork["updated_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

    active_fork = True if (
        updated_at - created_at) > timedelta(seconds=600) else False

    return active_fork

def get_branches(repo_owner, repo_name, headers):
    """Get branches of a given fork"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches"

    response = requests.get(url, headers=headers)
    # successful response:
    if response.status_code == 200:

        branches = response.json()
        branch_names = [branch['name'] for branch in branches]
        return branch_names
    else:
        print(f"Error: Unable to fetch branches data from GitHub API (status code {response.status_code})")
        return None

def get_default_branch(repo_owner, repo_name, headers):
    """Get the default branches of repositories present in the
    dataset. Note that it doesn't get branches of forks."""

    common_branches = ['main', 'master']
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"


    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        
        repo_info = response.json()
        default_branch = repo_info['default_branch']
        if default_branch not in common_branches:
            common_branches.append(default_branch)
            
        return common_branches
    else:
        print(f"Error: Unable to fetch repository information from GitHub API (status code {response.status_code})")
        return None
    


def check_commits_ahead_original(fork_url, original_repo_url , headers):
    """Get the number of commits ahead done in a fork in relation to the
    original forked repository (from where the fork was originated).
    For each commit ahead, it also gathers their commit messages."""
     
    forked_repo_owner, forked_repo_name = format_repo_info(fork_url)
    original_repo_owner, original_repo_name = format_repo_info(original_repo_url)
    
    forked_branches = get_branches(forked_repo_owner, forked_repo_name, headers)
    
    if forked_branches is None:
        return None

    # get the default branch of the original repository
    default_branches = get_default_branch(original_repo_owner, original_repo_name, headers)
    
    if default_branches is None:
        return None

    # store the number of commits ahead and their messages for each branch
    commits_ahead_by_branch = {}


    for branch_name in forked_branches:
        # comapring the branches of forks with the brnaches
        # of the original repositories:
        compare_url = f"https://api.github.com/repos/{forked_repo_owner}/{forked_repo_name}/compare/{original_repo_owner}:{branch_name}...{forked_repo_owner}:{branch_name}" 
        response = requests.get(compare_url, headers=headers)

        # successful response:
        if response.status_code == 200:
          
            data = response.json()
            
            ahead_by = data.get('ahead_by', 0)
            commits = data.get('commits', [])

            commits_ahead_by_branch[branch_name] = {
                'ahead_by': ahead_by,
                'commit_messages': []
            }

            # if there are commits ahead, fetch their messages
            if ahead_by > 0 and commits:
                for commit in commits:
                    commit_message = commit.get('commit', {}).get('message', '')
                    commits_ahead_by_branch[branch_name]['commit_messages'].append(commit_message)

        elif response.status_code == 404:
            # Handle case where the branch doesn't exist in the original repository
            print(f"Branch '{branch_name}' does not exist in the original repository.")
            commits_ahead_by_branch[branch_name] = None
            
        else:
            print(f"Error: Unable to fetch data from GitHub API for branch '{branch_name}' (status code {response.status_code})")
            commits_ahead_by_branch[branch_name] = None
            

    return commits_ahead_by_branch

def get_valid_forks_info(date_limit, repo_url, headers,sample_size, seed_value):
    """ Get commits ahead and their messages from valid forks. 
    For each commit ahead, gets how many of them are bugfix messages
    and also returns all available fork information (owner,
    repo name, fork url, number of commits ahead, commit messages,
    number of bugfixes messages ahead the original rpeo, etc)."""
    

    sampled_forks = get_all_forks(repo_url, headers,sample_size, seed_value)
    
   
    forks_info = []
    owner, repo = format_repo_info(repo_url)

    if not owner or not repo:
        return forks_info

    # for fork in forks:
    for fork in sampled_forks:
        
        # if not fork_is_valid(fork, date_limit):
        #     continue

        # checking if the fork has at least one commit ahead of the original repo:

        commits_ahead_by_branch = check_commits_ahead_original(fork["html_url"], repo_url, headers)

        if commits_ahead_by_branch:

            for branch_name, branch_info in commits_ahead_by_branch.items():
                if branch_info:

                    all_bugfix_msgs = []
                    if branch_info['commit_messages']:
                        for commit_msg in branch_info['commit_messages']:
                            if is_bugfix_commit(commit_msg) == 'Y':
                                all_bugfix_msgs.append(commit_msg)
                    

                    fork_info = {
                        "forked_from": repo_url,
                        "full_name": fork["full_name"],
                        "owner": fork["owner"]["login"],
                        "html_url": fork["html_url"],
                        "fork_branch_name": branch_name,
                        "created_at": fork["created_at"],
                        "updated_at": fork["updated_at"],
                        "stargazers_count": fork["stargazers_count"],
                        "watchers_count": fork["watchers_count"],
                        "forks_count": fork["forks_count"],
                        "commits_ahead_by": branch_info["ahead_by"],
                        "commit_msgs": branch_info['commit_messages'],
                        "number_bugfix_msgs": len(all_bugfix_msgs),
                        "bugfix_msgs": all_bugfix_msgs
                    }
                    forks_info.append(fork_info)

    return forks_info

def get_forks_all_repos(split: str, 
                        txt_directory, 
                        headers, 
                        date_limit,
                        sample_size,
                        seed_value,
                        interval):
    
    """Get the urls from the desired dataset passed as paramenter,
    samples them and get all fork information from the desired sample size."""

    repos_urls_list = get_repos_dataset_list(split, txt_directory)
    urls_in_interval = repos_urls_list[interval[0]:interval[1]]
    # repos_urls_sampled = random_sampling_urls(repos_urls_list, sample_size, seed_value)
    
    processed_repos = 0
    all_forks_information = []

    for repo_url in urls_in_interval:
        forks_info = get_valid_forks_info(date_limit, repo_url, headers, sample_size, seed_value)
        
        if forks_info:
            all_forks_information.extend(forks_info)
            
        processed_repos += 1

        print(f"Number of processed repos: {processed_repos}")

    return all_forks_information


def save_results_in_csv(all_forks, split, sample_size, seed_value,repos_interval):

    df = pd.DataFrame(all_forks)


    folder_results = Path(Path.cwd(), "research_questions",
                          "src", "forked_project_analysis",
                          split)

    result_filepath = folder_results
    folder_results.mkdir(exist_ok=True)
    csv_filename = 'forks_' + split + '_seed=' + str(seed_value)+ '_random_sampling' +str(sample_size)+ "_interval_" + str(repos_interval) +'.csv'
    csv_filepath = result_filepath / csv_filename

    df.to_csv(csv_filepath, index=False, encoding='utf-8')

    print(f"Fork information has been written to {csv_filename}")

if __name__ == '__main__':

    config = Configs()
    github_auth_token = config.github_auth_token
    headers = configure_request(github_auth_token)

    current_dir = Path(__file__).resolve().parent.parent.parent.parent
    dataset_lists = "dataset_lists/"
    dataset_lists_path = Path(current_dir, "source") / dataset_lists

    # split = "SE"
    # split = "non_SE"
    # split = "SE_py"
    split = "non_SE_py"

    date_limit_str = config.date
    sample_size = 10
    # please, don't change this seed value:
    seed_value = 15
    repos_interval = (0,110)
    

    date_limit = datetime.strptime(
        date_limit_str, "%m/%d/%Y").replace(tzinfo=timezone.utc)
    forks_all_repos = get_forks_all_repos(
        split, dataset_lists_path, headers, date_limit, sample_size, seed_value, repos_interval)

    save_results_in_csv(forks_all_repos,
                        split, sample_size, seed_value, repos_interval)