"""Script to get all the commit information for all dataset splits. """

import os
from git import Repo
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import tqdm
from research_questions.configs.configs import Configs


def format_repo_url(repo_path: str) -> str:
    repo_name = repo_path.replace("_____", "/")
    repo_url = "https://github.com/" + repo_name

    return repo_url


def get_changed_file(commit):
    """Returns a list with the files changed in a given commit
    and also returns the number of jupyter notebooks changed in
    the given commit"""

    # getting the modified files:
    modified_files = []
    # note that this includes all changes done to notebooks, including to
    # notebook metadata!
    try:
        # getting the diff between the current commit and its parent.
        # 'M' is to gather only modifications done by the commit
        for changed_item in commit.diff(commit.parents[0]).iter_change_type('M'):
            modified_files.append(changed_item.a_path)
    except:
        modified_files.append('error')

    num_changes = 0
    # counting the number of modified files:
    if modified_files:
        for file in modified_files:
            if file.endswith('.ipynb'):
                num_changes += 1

    return modified_files, num_changes


def is_bugfix_commit(commit_message: str) -> str:
    # keywords that commonly describes bugfix messages:
    fix_keywords = ['fix', 'fixing', 'fixed', 'bug', 'bugged', 'issue',
                    'problem', 'resolve', 'resolved', 'patch', 'repair',
                           'repaired', 'repairing', 'corrected', 'correct',
                           'address', 'rectify', 'resolve conflict', 'hotfix',
                           'solve']
    # keywords that seems to describe a bugfix, but are 'false positives',
    # and should not identify a bugfix commit:
    false_positives_keywords = ["rename", "clean up", "clean", "refactor",
                                "refactoring", "cleaning up", "cleaning",
                                "renaming", "mispell", "misspelling", "merge",
                                "merging", "compiler warning"]

    commit_message_lower = commit_message.lower().split()

    has_fix_keyword, has_false_positive_keyword = False, False
    for word in commit_message_lower:
        if word in fix_keywords:
            has_fix_keyword = True
            if word in false_positives_keywords:
                has_false_positive_keyword = True

    if has_fix_keyword and not has_false_positive_keyword:
        return 'Y'
    else:
        return 'N'


def get_all_commits(repo_dir: str, cutoff_date: str) -> dict:
    """
    Get all commits and the current branch name from multiple GitHub repositories.

    Args:
    - repo_dir: Directory where the GitHub repositories are stored.
    - cutoff_date: A string representing the cutoff date in the format 'MM/DD/YYYY'.

    Returns:
    - dict: A dictionary with repository names as keys and a dictionary of branch
    name and commits as values.
    """

    cutoff_datetime = datetime.strptime(cutoff_date, '%m/%d/%Y')
    cutoff_datetime = cutoff_datetime.replace(tzinfo=timezone.utc)

    # listing all directories in the repo_dir
    repo_names = [name for name in os.listdir(
        repo_dir) if os.path.isdir(os.path.join(repo_dir, name))]

    all_commits = {}
    count_processed_repo = 0
    for repo_name in repo_names:
        repo_path = os.path.join(repo_dir, repo_name)

        try:
            repo = Repo(repo_path)

            branch_name = repo.active_branch.name
            commits = list(repo.iter_commits())

            repo_commits = []
            # for commit in commits:
            for commit in repo.iter_commits():
                # selecting only the commits done before the cutoff date:
                if commit.authored_datetime.replace(tzinfo=timezone.utc) < cutoff_datetime:
                    modified_files, num_modified_notebooks = get_changed_file(
                        commit)
                    commit_info = {
                        'sha': commit.hexsha,
                        'author': f"{commit.author.name} <{commit.author.email}>",
                        'date': commit.authored_datetime,
                        'message': commit.message,
                        'is_bugfix_commit': is_bugfix_commit(commit.message),
                        'modified_files': modified_files,
                        'num_notebooks_files_changed': num_modified_notebooks
                    }

                    repo_commits.append(commit_info)

            all_commits[repo_name] = {
                'branch': branch_name,
                'commits': repo_commits
            }

        except Exception as e:
            print(f"Error processing {repo_name}: {e}")
        count_processed_repo += 1

        print(count_processed_repo)

    return all_commits


def generate_csv_results(repos_commit_data: dict, split: str):

    commit_info = []

    for repo_name, data in repos_commit_data.items():
        branch = data['branch']
        for commit in data['commits']:
            commit_info.append({
                'repo_url': format_repo_url(repo_name),
                'branch': branch,
                'commit_sha': commit['sha'],
                'commit_date': commit['date'],
                'commit_msg': commit['message'],
                'is_bugfix_commit': commit['is_bugfix_commit'],
                'modified_files': commit['modified_files'],
                'num_notebooks_files_changed': commit['num_notebooks_files_changed'],
                'author': commit['author']
            })

    all_commit_info = pd.DataFrame(commit_info)

    folder_results = Path(Path.cwd(), "research_questions",
                          "src", "commits_info")

    result_filepath = folder_results
    csv_filename = f'commits_info_{split}.csv'
    csv_filepath = result_filepath / csv_filename
    folder_results.mkdir(exist_ok=True)

    all_commit_info.to_csv(csv_filepath, index=False)


if __name__ == '__main__':

    config = Configs()
    date = config.date

    # get all commits for active SE split.
    split = "active_SE_repos"

    full_directory_path = config.path_active_SE_repos
    repos_data = get_all_commits(full_directory_path, date)

    generate_csv_results(repos_data, split)

    # get all commits for active non SE split:
    split = "active_non_SE_repos"

    full_directory_path = config.path_active_non_SE_repos

    repos_data = get_all_commits(full_directory_path, date)

    generate_csv_results(repos_data, split)
