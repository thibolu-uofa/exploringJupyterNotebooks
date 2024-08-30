import re
import pandas as pd


def remove_html_and_urls(text):
    text = str(text)
    # Remove HTML tags
    clean_text = re.sub(r'<.*?>', '', text)
    # Remove URLs
    clean_text = re.sub(r'http[s]?://\S+', '', clean_text)
    clean_text = clean_text.split(" ")

    cleaned_text = [sentence for sentence in clean_text if any(
        char.isalnum() for char in sentence)]

    # Join the cleaned sentences back into a single string
    cleaned_text = ' '.join(cleaned_text)

    return cleaned_text


def get_list_active_SE():

    with open("active_SE_purpose_repositories.txt", 'r', encoding='utf-8') as f:
        active_list = []
        line = f.readline().strip()
        active_list.append(line)
        while line:
            line = f.readline().strip()
            active_list.append(line)

    return active_list


def get_list_non_active_SE():

    with open("active_non_SE_purpose_repositories.txt", 'r', encoding='utf-8') as f:
        active_list = []
        line = f.readline().strip()
        active_list.append(line)
        while line:
            line = f.readline().strip()
            active_list.append(line)

    return active_list


def generate_headers_dataset(csv_name):

    dtypes = {
        'header': str,
        'url': str,
        'github_path': str
    }

    headers_dataset = pd.read_csv(
        csv_name, dtype=dtypes, sep=',', low_memory=False, lineterminator='\n')
    headers_dataset['cleaned_header'] = headers_dataset['header'].apply(
        remove_html_and_urls)

    headers_dataset = headers_dataset[[
        'header', 'cleaned_header', 'url', 'github_path']]
    headers_dataset.to_csv(csv_name, index=False)


def get_active_SE_repo(dataset_csv):
    # repos_SE_purpose_df = pd.read_csv(repos_SE_purpose)
    # urls_SE_purpose_list = repos_SE_purpose_df['URL'].to_list()
    active_SE_purpose_list = get_list_active_SE()

    dataset_df = pd.read_csv(dataset_csv)
    # print(f"dataset size: {len(dataset_df)}")
    # dataset_df['is_SE_purpose'] = 'n'
    # print(len(dataset_df['url'].isin(urls_SE_purpose_list)))

    dataset_df = dataset_df.loc[dataset_df['url'].isin(active_SE_purpose_list)]

    print(f"len final dataset: {len(dataset_df)}")
    print(dataset_df['url'].nunique())

    dataset_df.to_csv("active_SE_repos_headers.csv", index=False)


def get_active_non_SE_repo(dataset_csv):
    # repos_SE_purpose_df = pd.read_csv(repos_SE_purpose)
    # urls_SE_purpose_list = repos_SE_purpose_df['URL'].to_list()
    active_non_SE_purpose_list = get_list_non_active_SE()

    dataset_df = pd.read_csv(dataset_csv)
    # print(f"dataset size: {len(dataset_df)}")
    # dataset_df['is_SE_purpose'] = 'n'
    # print(len(dataset_df['url'].isin(urls_SE_purpose_list)))

    dataset_df = dataset_df.loc[dataset_df['url'].isin(
        active_non_SE_purpose_list)]

    print(f"len final dataset: {len(dataset_df)}")
    print(dataset_df['url'].nunique())

    dataset_df.to_csv("active_non_SE_repos_headers.csv", index=False)


def generate_filtered_csvs(dataset_csv):
    dataset_df = pd.read_csv(dataset_csv)
    repos_SE_purpose_df = dataset_df.loc[dataset_df['is_SE_purpose'] == 'y']
    repos_non_SE_purpose_df = dataset_df.loc[dataset_df['is_SE_purpose'] == 'n']

    repos_SE_purpose_df.to_csv(
        "headers_jupyter_dataset_top_1000_SE_purpose.csv", index=False)
    repos_non_SE_purpose_df.to_csv(
        "headers_jupyter_dataset_top_1000_non_SE_purpose.csv", index=False)


def label_active_repos(dataset):
    dataset_df = pd.read_csv(dataset)

    active_list = get_list_active_SE()
    print(active_list[0])
    print(type(active_list[0]))
    print(len(active_list))

    # dataset_df['is_active'] = 'n'
    dataset_df['url'] = dataset_df['url'].astype(str)
    # print(dataset_df['url'].isin(active_list))
    # dataset_df.loc[dataset_df['url'].isin(active_list), 'is_active'] = 'y'
    k = dataset_df.loc[dataset_df['url'].isin(active_list)]
    k['is_active'] = 'y'

    # print(dataset_df['is_active'].value_counts())
    print(k['is_active'].value_counts())
    print(k['url'].nunique())

    k.to_csv(dataset, index=False)


if __name__ == '__main__':

    csv_name = "markdown_headers_dataset_jupyter_notebooks_top_1000.csv"
    # label_active_repos(csv_name)
    generate_headers_dataset(csv_name)
    get_active_SE_repo(csv_name)
    get_active_non_SE_repo(csv_name)

    # repos_SE_purpose = "SE_purpose_repositories.csv"

    # generate_filtered_csvs(csv_name)
