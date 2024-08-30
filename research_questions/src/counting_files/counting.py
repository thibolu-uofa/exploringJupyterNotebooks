""" Script to count the number of Jupyter notebooks belonging to both SE and
Non SE splits. This script assumes that you already have the cloned 
repositories stored in the path you have configured in configs/configs.json."""

from research_questions.configs.configs import Configs
from pathlib import Path

config = Configs()


def count_total_notebooks(path: Path) -> int:

    # getting the files that are only jupyter notebooks:
    notebook_paths = list(path.glob('**/*.ipynb'))
    total_notebooks = len(notebook_paths)

    return total_notebooks


def count_notebooks_in_split():

    complete_directory_path = config.path_active_SE_repos
    path_SE_notebooks = Path(complete_directory_path)

    total_notebooks_SE = count_total_notebooks(path_SE_notebooks)
    print(f"Number of notebooks in the SE purpose split: {total_notebooks_SE}")

    complete_directory_path = config.path_active_non_SE_repos
    path_non_SE_notebooks = Path(complete_directory_path)

    total_notebooks_non_SE = count_total_notebooks(path_non_SE_notebooks)
    print(
        f"Number of notebooks in the Non SE purpose split: {total_notebooks_non_SE}")

    result_filepath = Path(Path.cwd(), "research_questions",
                           "src", "counting_files")

    # txt file to save the results:
    txt_filepath = Path(result_filepath, "notebook_counting.txt")

    with open(txt_filepath, 'w') as f:
        print(
            f"Number of notebooks in the SE purpose split: {total_notebooks_SE}", file=f)
        print(
            f"Number of notebooks in the non SE purpose split: {total_notebooks_non_SE}", file=f)


if __name__ == "__main__":

    count_notebooks_in_split()
