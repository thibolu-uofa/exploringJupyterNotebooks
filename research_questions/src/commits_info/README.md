# Commit Information

A python script that gets all the commit information for all dataset splits (Notebook and Python for Software Engineering purposes and educational purposes. )
purpose split. This script assumes you have already cloned the repositories
locally in your machine, in the path described in the config.json file. To 
clone the repsoitories that compose the dataset, refer to `research_questions/src/clone_repositories`. To ensure consistency, this script gets only commits done previous to 04/27/2024.

You can run the main script to gather commit information with the command:

python -m research_questions.src.commits_info.get_commit_info_and_bugfix_msgs

from inside the main  directory of this project.


The information gathered is saved in csv files (commit sha, commit author,
commit datetime,commit branch, commit message, if the commit message is a
bugfix, if the commit changes a jupyter notebook and how many notebook files
are changed in the commit, and GitHub repository url)

The analysis of the data, including the boxplot, is done in the notebook `general_analysis_and_statistical_tests.ipynb` and it uses the csvs data.

