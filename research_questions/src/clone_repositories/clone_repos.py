"""Script for cloning our assembled dataset ('SE' and 'non_SE' splits
of the Jupyter notebooks dataset, and the splits 'SE_py', 'non_SE_py'
of the Python dataset. You should have your configurations set in the
config.json file.

This script take hours to clone the repositories. Adjust the configurations
in main (such as path and split) to clone the repositories related to the
desired dataset."""

from pathlib import Path
from typing import List
import os
import requests
import pandas as pd
import json
from research_questions.configs.configs import Configs

config = Configs()

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

def retrieve_top_1000_repositories(filepath: str):
    '''
        Function to retrieved the URLs for the top 1000 starred jupyter
        notebooks from GitHub API. The retrieved URLs are saved in the txt
        file passed as parameter.
        This function does not clone the repositories.
    '''

    url = 'https://api.github.com/search/repositories?q=language:jupyter-notebook&sort=stars&order=desc&per_page=100'

    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Get the JSON data from the response
        data = response.json()

        with open('top_1000_repositories.json', 'w') as f:
            json.dump(response.json(), f)
            print('Repository data saved to top_1000_repositories.json')

        urls = [repo['html_url'] for repo in data['items']]

        # getting results of all resulting request pages:
        for i in range(1, 11):
            
            response = requests.get(url + '&page=' + str(i+1))

            # check if the request was successful 
            if response.status_code == 200:
                
                data = response.json()

                with open(("top_1000_repositories" + str(i) + '.json'), 'a+') as f:
                    json.dump(data, f)
                    print('Repository data saved to top_1000_repositories.json')

               
                urls.extend([repo['html_url'] for repo in data['items']])
            else:
                print('Error:', response.status_code)

       
        with open(filepath, 'w') as f:
            index = 1
            for url in urls:
                f.write(url + " " + str(index) + '\n')
                index += 1

        print(f'Results saved in {filepath}')
    else:
        print('Error:', response.status_code)


def clone_in_batches(urls_list: List, batch_folder: str, 
                    destination_path: str):
    # create the directory to save the cloned repositories

    path = Path(destination_path)
    
    path.mkdir(parents=True, exist_ok=True)

    cloned_sucessfully_urls = []

    for url in urls_list:
        
        repo_name_and_author = url.split("/")[-2:]
        repo_name_and_author = "_____".join(repo_name_and_author)

 
        repo_path = Path(
            destination_path,
            batch_folder, repo_name_and_author)
        try:
            os.system(f'git clone "{url}" "{repo_path}"')
        except:
            print(f"It wasn't possible to clone {url} from {batch_folder}!")

        try:
            cloned_sucessfully_urls.append(url)
        except:
            print(f"Wasn't possible to save the url!")

    return cloned_sucessfully_urls


if __name__ == '__main__':

    current_dir = Path(__file__).resolve().parent.parent.parent.parent
    dataset_lists = "dataset_lists/"
    dataset_lists_path = Path(current_dir, "source") / dataset_lists

    #split = 'non_SE_py'
    split = 'SE_py'
    repos_urls_list = get_repos_dataset_list(split, dataset_lists_path)
    # filepath in which the repositories are going to be cloned
    complete_directory_path = config.clone_destination

    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path in which the repos are going to be cloned:", 
          full_directory_path)

    destination_path= config.path_active_SE_py_repos
    clone_in_batches(repos_urls_list, split, destination_path)
    print(f"Cloned repos successfuly!")