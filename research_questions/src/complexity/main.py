""" Script to gather complexity information, such as lines of code (LOC), 
number of comment lines, number of functions, cyclomatic complexity, 
and number of classes for each file belonging to the dataset splits.

Libraries used:
(https://github.com/boyter/scc)
(https://github.com/terryyin/lizard)

You can run this script with the command:

python -m research_questions.src.complexity.main

from inside the main  directory of this project.

As a limitation, the scc library only runs the loc operation in files in your home
directory, implying it is not possible to run the loc operation directly in an 
external storage device directly. That is why this script copy file by file
of to the current working directory in temporary folders, that are excluded
in the end of the execution of this script. Thus, you can use this script
to run loc in data you keeP in an external hard disk, as an example.

This script can take hours to run. The scc lib was installed with snap, for 
Ubuntu.



"""

import json
import sys
import signal
import os
from pathlib import Path
import subprocess
import shutil
import pandas as pd
from typing import List
import time

from research_questions.configs.configs import Configs
from .FileComplexity import *

config = Configs()



def get_complexity_metrics(source_dir, destination_dir, split):
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
        all_complexity_results: a list with the resulting json for a given file in
        which loc operation was performed
    """

    all_complexity_results = []
    # creating a tmeporary directory, only to copy the files to the current
    # working directory:
    destination_path = Path(destination_dir)

    os.makedirs(destination_path)
    # counting the processed repositories only to print them in the terminal:
    processed_repo_count = 0

    # iterating through all the repositories:
    for repository_dir in source_dir.iterdir():
        files_to_run_loc = filter_desired_files(repository_dir)
        

        for current_file in files_to_run_loc:

            # copy2 ensures the metada of the copied file is kept:
            copied_file = shutil.copy2(current_file, destination_path)
            # getting complexity results for the given file:
            
            complexity_results = FileComplexity(copied_file)
            

            if complexity_results:

                file_results = complexity_results.to_dict()
                filepath_str = str(current_file).split(str(source_dir))[-1]
                file_results['filepath'] = filepath_str.replace("_____", "/")
                all_complexity_results.append(file_results)
            # deleting the copied file, to prevent using too much memory:
            os.remove(copied_file)

        processed_repo_count += 1
        if processed_repo_count % 1 == 0:
            print(f"{processed_repo_count} directories were processed in split {str(split)}")

    # excluding the temporary directory
    shutil.rmtree(destination_dir)

    return all_complexity_results

def get_complexity_metrics_kaggle(source_dir, destination_dir, split):

    all_complexity_results = []
    # creating a temporary directory, only to copy the files to the current
    # working directory:
    destination_path = Path(destination_dir)
    os.makedirs(destination_path)
    # counting the processed repositories only to print them in the terminal:
    processed_file_count = 0
    files_to_run_loc = [filepath for filepath in source_dir.iterdir()]
    print(f'number of files to be processed: {len(files_to_run_loc)}')

    for current_file in files_to_run_loc:

        # copy2 ensures the metada of the copied file is kept:
        copied_file = shutil.copy2(current_file, destination_path)

        complexity_results = FileComplexity(copied_file)
        

        if complexity_results:

            file_results = complexity_results.to_dict()
            filepath_str = str(current_file).split(str(source_dir))[-1]
            file_results['filepath'] = filepath_str.replace("_____", "/")
            all_complexity_results.append(file_results)
        # deleting the copied file, to prevent using too much memory:
        os.remove(copied_file)


    print(f"all Kaggle dataset notebooks were processed!")

    # excluding the temporary directory
    shutil.rmtree(destination_dir)

    return all_complexity_results



def filter_desired_files(repository: Path) -> list:
    """Returns files for detecting language, while ignoring .gitignore,
     files inside .git/ directory,and other fyle types, since makes no sense
     to analyze the language of these files.
    Filters the desired files to run loc from each repository path, passed as
    parameter to this function."""

    desired_files = []
    for filepath in repository.rglob("*"):
        # ignoring files inside .git folders, and also ignoring .gitignore files:
        try:
            if filepath.is_file():
                # ignroing unnecessary files:
                if (
                    filepath.is_file()
                    and ".git" not in filepath.parts
                    and not filepath.suffix.lower()
                    in [".gitignore", ".png", ".jpg", ".jpeg", ".svg"]
                ):
                    desired_files.append(filepath)
        except Exception as e:
            print(e)
            continue

    return desired_files

def create_csv_complexity(all_loc_resuts: List[dict], split: str):
    """Save the results of the loc operation ran over all the
    repositories, according to the script they belong, in a csv
    file."""

    df_results = pd.DataFrame.from_records(all_loc_resuts)
    df_results = df_results.loc[df_results['file_type'].isin(['python', 'notebook'])]

    directory_to_save = Path(Path.cwd(), "research_questions",
                             "src", "complexity", "data_all_repos")

    directory_to_save.mkdir(parents=True, exist_ok=True)

    csv_filepath = directory_to_save / (split + ".csv")
    df_results.to_csv(csv_filepath, index=False)

if __name__ == "__main__":

    # getting SE purpose repos path from configs.json:
    complete_directory_path = config.path_active_SE_py_repos

    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path:", full_directory_path)
   
    all_complexity_results = get_complexity_metrics(full_directory_path, 
        Path(Path.cwd(), "temp_copy_SE_py"), split="SE_py")
    
    create_csv_complexity(all_complexity_results, "SE_py")

    print(f"Finished processing the SE_py repos!")
    
    time.sleep(3)

    # getting educational purpose Python repos path from configs.json:
    complete_directory_path = config.path_active_non_SE_py_repos

    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path:", full_directory_path)
    
    all_complexity_results = get_complexity_metrics(
        full_directory_path, Path(Path.cwd(), "temp_copy_non_SE_py"), split="Educational_py")
    
    create_csv_complexity(all_complexity_results, "Educational_py")

    print(f"Finished processing the Educational_py repos!")

    
    time.sleep(3)

    # getting educational purpose Notebook repos path from configs.json:
    complete_directory_path = config.path_active_non_SE_repos

    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path:", full_directory_path)
    
    all_complexity_results = get_complexity_metrics(
        full_directory_path, Path(Path.cwd(), "temp_copy_non_SE"), split="Educational_nb")
    
    create_csv_complexity(all_complexity_results, "Educational_nb")

    print(f"Finished processing the Educational_nb repos!")

    # getting the SE purpose Notebook repos path from configs.json:
    complete_directory_path = config.path_active_SE_repos

    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path:", full_directory_path)
    
    all_complexity_results = get_complexity_metrics(
        full_directory_path, Path(Path.cwd(), "temp_copy_SE"), split="SE_nb")
    
    create_csv_complexity(all_complexity_results, "SE_nb")

    print(f"Finished processing the SE_nb repos!")

    
    time.sleep(3)

    # getting the Kaggle dataset path from configs.json:
    complete_directory_path = config.kaggle_dataset

    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path:", full_directory_path)
    
    all_complexity_results = get_complexity_metrics_kaggle(
        full_directory_path, Path(Path.cwd(), "temp_copy_Kaggle"), split="Kaggle")
    
    create_csv_complexity(all_complexity_results, "Kaggle")

    print(f"Finished processing the Kaggle dataset!")

