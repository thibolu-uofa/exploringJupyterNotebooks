# Exploring-Jupyter-Notebooks

Code and data for the paper "Exploring Complexity, Coding behaviors, and Bugs in Jupyter Notebooks".

### Installing requirements

1. Installing default project requirements

Create an environment with python 3.10, and
from the main directory of this project ("exploringJupyterNotebooks"), run:

```pip install -r requirements.txt```

2. From the main directory of this project ("exploringJupyterNotebooks"), run:

```pip install -e.```

to create the local package.


3. Installing the requirements for analyzing toxicity in Notebook repositories:

Create another environment with python > 3.5, different than the previous environments, and from the `research_questions/src/toxicity`, run:

```pip install -r requirements.txt```

This environment should be activated when running any code inside the directory `src/toxicity`, and should not be activated when running scripts out

4. Installing the requirements and running topic modeling

Refer to the README inside `research_questions/src/topic_modeling` for instructions, since the setup was done in a cluster environment with GPU support.

### Configuring the project

Configure the `research_questions/src/configs/configs.json` according to your system path configurations. This file includes paths to directories where repositories are cloned, dataset paths, specific dates for data consistency, and email for querying the Geopy API. This project has already an example of configurations properly set in `research_questions/src/configs/configs.json` file for a user. Below is an explanation of each field:

- clone_destination: This is the directory where the repositories will be cloned. Set this to the path where you want to store cloned repositories.
E.g:

"clone_destination": "/path/to/your/directory"

- path_cloned_active_repos_SE_purpose: Path to the directory where active Notebook repositories for Software Engineering purposes are cloned.

E.g:

"path_cloned_active_repos_SE_purpose": "/path/to/your/SE_purpose_repos"

- path_cloned_active_repos_non_SE_purpose: Path to the directory where active Notebooks repositories for educational purposes are cloned.

E.g:

"path_cloned_active_repos_non_SE_purpose": "/path/to/your/non_SE_purpose_repos"

- path_cloned_active_repos_SE_py_purpose: Path to the directory where active Python repositories for Software Engineering purposes are cloned.

E.g:

"path_cloned_active_repos_SE_py_purpose": "/path/to/your/SE_py_purpose_repos"

- path_cloned_active_repos_non_SE_py_purpose: Path to the directory where active Python repositories for educational purposes are cloned.

E.g.:

"path_cloned_active_repos_non_SE_py_purpose": "/path/to/your/non_SE_py_purpose_repos"

kaggle_dataset: Path to the Kaggle dataset.

E.g:

"kaggle_dataset": "/path/to/your/kaggle_dataset"

- analyze_data_pevious_to: Fixed date to ensure data consistency. Do not modify this date (although configured, it is not been used at the time).

E.g:
"analyze_data_pevious_to": "04/27/2024"

dataset_AI_split_previous_to: Fixed date for splitting data for ML/AI applications. Do not modify this date.

E.g:

"dataset_AI_split_previous_to": "01/01/2018"

email: Your email for querying the Geopy (Nominatim) API.

E.g:

    "email": "your_email@gmail.com"


After editing the file, save the changes.

- Create a `.env`inside `research_questions/src/configs/` file following the `research_questions/src/configs/.env.txt` template. you just need to insert your GitHub auth token in the `.env`file:

AUTH_TOKEN='ghpXXX'

# Datasets source

# Research Questions

Data and codes used for the research questions of this research are encountered inside the `research_questions/src` directory of this project. Jupyter notebooks with analysis are present for all research questions, and contain the results present in the paper.

## Section 1: Study of Notebook Directories

+ RQ1: How do the number of stargazers, watchers, forks, and issues differ between Notebook and Python repositories?

Check the `research_questions/src/stars_watchers_forks_issues` directory.

+ RQ2: What is the distribution of programming languages used in Jupyter Notebooks files and repositories?

Check the `research_questions/src/language_analysis` directory.

## Section 2: Study of Notebook Software Developers
+ RQ3: How do Notebook development teams work together (team size) ?

Check the `research_questions/src/contributors` directory.

+ RQ4: How experienced are Notebook developers?

Check the `research_questions/src/contributors` directory.

+ RQ5: What is the geographical distribution of developers contributing to Jupyter Notebook repositories?

Check the `research_questions/src/contributors` directory.

+ RQ6: How do Notebook users and developers communicate through GitHub issues (toxicity analysis)?

Check the `research_questions/src/toxicity` directory.


## Section 3: Topic Analysis

+ RQ7: What are the prevalent topics of Jupyter notebooks?

Check the `research_questions/src/topic_modeling` directory.

## Section 4: Notebook Code Analysis
+ RQ8: How does the code complexity of Jupyter Notebooks compare to Python code?

Check the `research_questions/src/complexity` directory.

## Section 5: Notebook Code Change Analysis
+ RQ9: What are the characteristics of code changes in Jupyter Notebook repositories?

Check the `research_questions/src/commits_info` and `research_questions/src/contributors` directories.

+ RQ10: How do developers describe changes in Notebooks?

Check the `research_questions/src/commits_info` directory.
