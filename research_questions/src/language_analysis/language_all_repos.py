""" Script used ot gather language and complexity info about all the active
repositories, splitted according to their SE/Non SE purposes.
Bytes, CodeBytes, Lines, Code lines,Comment lines, Blank lines,
Complexity,Count of number of files and WeightedComplexity are also evaluated.
The library for language/complexity estimation is the scc library
(https://github.com/boyter/scc)
As a limitation, this lib only runs the loc operation in files in your home
directory, implying it is not possible to run the loc operation directly in an 
external storage device directly. That is why this script copy file by file
of to the current working directory in temporary folders, that are excluded
in the end of the execution of this script. Thus, you can use thsi script
to run loc in data you keeo in an external hard disk, as an example.

This script can take hours to run. The scc lib was installed with snap, for 
Ubuntu."""

import json
import sys
import signal
import os
from pathlib import Path
import subprocess
import shutil
import pandas as pd
from typing import List

from research_questions.configs.configs import Configs

config = Configs()


def run_scc_single_file(path: Path):
    """Returns the results obtained from running loc of scc library
    in a single file, passed as parameter to the function.
    The results obtained are the language of the file, and file numbers
    such as: Bytes, CodeBytes, Lines, Code lines,Comment lines, Blank lines,
    Complexity,Count of number of files and WeightedComplexity."""
    try:
        # the output format is json:
        byteOutput = subprocess.check_output(
            ['scc', '-f', 'json', path], timeout=15)

        return json.loads(byteOutput.decode('UTF-8'))
    # some credentials files (e.g: .credentials from AWS) can raise
    # error when trying to running loc on them:
    except PermissionError as pe:
        print(pe)
        return None
    except Exception as e:
        print(e)
        return None


def copy_repository_to_run_loc(source_dir, destination_dir, split):
    """Function that copies the files to your current working directory 
    (directory of this project), and uses the scc lib to run
    loc (and also infer the file language). Since scc lib installed with snap 
    has the limitation of only allowing running loc inside /home directory
    Args:
        source_dir: the path which your repositories are stored
        destination_dir: the directory to copy the desired files to. The files
        are copied one by one, and the loc is always executed in a single file
        at a time.
        Returns:
        all_loc_results: a list with the resulting json for a given file in
        which loc operation was performed
    """

    all_loc_results = []
    # creating a tmeporary directory, only to copy the files to the current
    # working directory:
    destination_path = Path(destination_dir)
    os.makedirs(destination_path)
    # counting the processed repositories only to print them in the terminal:
    processed_repo_count = 0

    # iterating through all the repositories:
    for repository_dir in source_dir.iterdir():
        # running loc (infers language) on a given file:
        files_to_run_loc = filter_desired_files(repository_dir)

        for current_file in files_to_run_loc:

            # copy2 ensures the metada of the copied file is kept:
            copied_file = shutil.copy2(current_file, destination_path)
            # getting loc/language results for the given file:
            loc_results = run_scc_single_file(copied_file)

            if loc_results:

                loc_results = loc_results[0]
                # only formatting information to save in csv file:
                # formatting the current filename:
                loc_results['filename'] = str(copied_file).split('/')[-1]
                # formatting the name of the repository that contains
                # the analyzed file:
                loc_results['repository'] = str(
                    repository_dir).split('/')[-1].replace("_____", "/")
                del loc_results['Files']

                all_loc_results.append(loc_results)
            # deleting the copied file, to prevent using too much memory:
            os.remove(copied_file)

        processed_repo_count += 1
        if processed_repo_count % 1 == 0:
            print(f"{processed_repo_count} were processed in split {str(split)}")

    # excluding the temporary directory
    shutil.rmtree(destination_dir)

    return all_loc_results


def create_csv_loc_results(all_loc_resuts: List[dict], split: str):
    """Save the results of the loc operation ran over all the
    repositories, according to the script they belong, in a csv
    file."""

    df_results = pd.DataFrame.from_records(all_loc_resuts)

    directory_to_save = Path(Path.cwd(), "research_questions",
                             "src", "language_analysis", "data_all_repos")

    directory_to_save.mkdir(parents=True, exist_ok=True)

    csv_filepath = directory_to_save / (split + ".csv")
    df_results.to_csv(csv_filepath, index=False)

# detects when you type 'ctrl c' in the terminal to interrupt a given process:


def signal_handler(sig, frame):
    print('[SIGINT] Ctrl+C received.')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def filter_desired_files(repository: Path) -> list:
    """Returns files for detecting language, while ignoring .gitignore,
     files inside .git/ directory,and other fyle types, since makes no sense 
     to analyze the language of these files.
    Filters the desired files to run loc from each repository path, passed as
    parameter to this function."""

    desired_files = []
    for filepath in repository.rglob('*'):
        # ignoring files inside .git folders, and also ignoring .gitignore files:
        try:
            if filepath.is_file():
                # ignroing unnecessary files:
                if filepath.is_file() and '.git' not in filepath.parts and not filepath.suffix.lower() in ['.gitignore', '.png', '.jpg', '.jpeg', '.svg']:
                    desired_files.append(filepath)
        except Exception as e:
            print(e)
            continue

    return desired_files


if __name__ == "__main__":

    # getting SE purpose repos path from configs.json:
    complete_directory_path = config.path_active_SE_repos

    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path:", full_directory_path)

    all_loc_results = copy_repository_to_run_loc(
        full_directory_path, Path(Path.cwd(), "temp_copy_SE"), split="SE")

    print(f"Finished processing the SE repos!")

    create_csv_loc_results(all_loc_results, "language_all_SE_repos")

    # getting non SE purpose repos path from configs.json:

    complete_directory_path = config.path_active_non_SE_repos

    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path:", full_directory_path)

    all_loc_results = copy_repository_to_run_loc(
        full_directory_path, Path(Path.cwd(), "temp_copy_non_SE"), split="non_SE")

    create_csv_loc_results(all_loc_results, "language_all_non_SE_repos")

    print(f"Finished processing the non SE repos!")
