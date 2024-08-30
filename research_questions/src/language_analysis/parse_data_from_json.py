"""Script that process the results obtained for the language of jupyter 
notebooks for both SE/Non SE splits. This script also analyze data consistency,
such as printing the numbers of notebooks in each split"""

import re
import pandas as pd
from pathlib import Path
import json


def get_list_active(txt_filepath):

    with open(txt_filepath, 'r', encoding='utf-8') as f:
        active_list = []
        line = f.readline().strip()
        active_list.append(line)
        while line:
            line = f.readline().strip()
            active_list.append(line)

    print(f"number of listed repos in {txt_filepath}: {len(active_list)-1}")

    return active_list


def get_active_repo(dataset_df, column_url_name, repo_type, txt_directory):

    if repo_type == 'SE':
        txt_filepath = Path(
            txt_directory, "nb_active_SE_purpose_repositories.txt")

        active_list = get_list_active(txt_filepath)
    else:
        txt_filepath = Path(
            txt_directory, "nb_active_non_SE_purpose_repositories.txt")
        active_list = get_list_active(txt_filepath)

    print(
        f"len of unique repos_url before filtering for {repo_type} repos: {dataset_df[column_url_name].nunique()}")
    print(
        f"len of all repos_url before filtering for {repo_type} repos: {len(dataset_df[column_url_name])}")

    dataset_df = dataset_df.loc[dataset_df[column_url_name].isin(active_list)]

    print(
        f"len of unique repos_url after filtering for {repo_type} repos: {dataset_df[column_url_name].nunique()}")
    print(
        f"common rows between the dataframes after filtering for {repo_type} repos: {len(dataset_df)}")

    csv_filepath = "active_" + repo_type + "_purpose.csv"
    dataset_df.to_csv(csv_filepath, index=False)

    return dataset_df


def generate_csv_from_json(json_filepath):
    print("json filepath", json_filepath)

    with open(json_filepath, 'r') as f:
        data = json.load(f)

    notebook_in_GitHub, name, version, reason, gitHub_url = [], [], [], [], []

    for key, item in data.items():

        notebook_in_GitHub.append(key)
        try:
            name.append(item['name'])
        except KeyError:
            name.append("")
        try:
            version.append(item['version'])
        except KeyError:
            version.append("")
        try:
            reason.append(item['reason'])
        except KeyError:
            reason.append("")
        try:
            gitHub_url.append(item['repo_url'])
        except KeyError:
            gitHub_url.append("")

    df = pd.DataFrame({'notebook_path': notebook_in_GitHub,
                       'language': name,
                       'version': version,
                       'reason': reason,
                       'github_url': gitHub_url
                       })

    return df


def get_repos_language_according_to_purpose(json_filepath, dataset_list_dir,
                                            split, result_filepath):

    df = generate_csv_from_json(json_filepath)

    df_active_split = get_active_repo(dataset_df=df.copy(),
                                      column_url_name='github_url',
                                      repo_type=split,
                                      txt_directory=dataset_list_dir)

    print(
        f"number of active notebooks belonging to {split} purposes repositories: {len(df_active_split)}")
    print("len df:", len(df_active_split))
    csv_filename = f"language_info_active_{split}_purpose_repos.csv"
    csv_path = Path(result_filepath, csv_filename)
    print(df_active_split.head(5))
    df_active_split.to_csv(csv_path)

    return df_active_split


def count_total(df_SE, df_non_SE, dataset_list_dir):
    """Count the total number of notebooks belonging to each SE/Non SE split.
    Also ensures all notebooks were 'grouped' in its respective split"""

    df = pd.concat([df_SE, df_non_SE])

    txt_filepath_SE = Path(
        dataset_list_dir, "nb_active_SE_purpose_repositories.txt")

    active_list_SE = get_list_active(txt_filepath_SE)

    txt_filepath_non_SE = Path(
        dataset_list_dir, "nb_active_non_SE_purpose_repositories.txt")

    active_list_non_SE = get_list_active(txt_filepath_non_SE)
    total = active_list_SE + active_list_non_SE
    total = [url for url in total if url != ""]

    print(f"all urls repos (SE + Non SE actives): {len(total)}")

    all_notebooks = df.loc[df['github_url'].isin(total)]
    print(
        f" number of SE + Non SE active total notebooks: {len(all_notebooks['notebook_path'])}")

    # ensuring all notebooks were 'grouped' in its respective split:
    not_included = df.loc[~df['github_url'].isin(total)]
    print(f"number of not_included urls: {len(not_included)}")


if __name__ == '__main__':

    current_dir = Path(__file__).resolve(
    ).parent.parent.parent.parent

    dataset_lists = "dataset_lists/"

    dataset_lists_path = Path(current_dir, "source") / dataset_lists

    print("Full Directory Path:", dataset_lists_path)

    result_filepath = Path(Path.cwd(), "research_questions",
                           "src", "language_analysis", "data_only_notebooks")

    # parsing data from the SE split:

    json_filepath = Path(
        result_filepath, 'language_info_SE_purposes_repos.json')

    df_active_SE = get_repos_language_according_to_purpose(
        json_filepath, dataset_lists_path, "SE", result_filepath)

    # parsing data from the non SE split:
    json_filepath = Path(
        result_filepath, 'language_info_non_SE_purposes_repos.json')

    df_active_non_SE = get_repos_language_according_to_purpose(
        json_filepath, dataset_lists_path, "non_SE", result_filepath)

    count_total(df_active_SE, df_active_non_SE, dataset_lists_path)
