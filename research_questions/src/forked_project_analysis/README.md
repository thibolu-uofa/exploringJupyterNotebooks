# Forks Information


For each repository belonging to the Notebooks and Python dataset splits (corresponding splits: Notebook repositories for Software Engineer and Educational purposes, Python repositories for Software Engineer and Educational purposes), we collect up to 10 active forks available through GitHub API. And then, for each fork, we analyze how many of them have commits ahead of the original forked repository, and how many of its messages  are related to bugfixing.

To generate the fork information data in csv files, run the following command from inside the main directory of this project:

python -m research_questions.src.forked_project_analysis.get_forks_info

python -m research_questions.src.contributors.get_country_contributors

After that, you can reproduce the analysis by running the cells in the `contributors_analysis.ipynb` notebook, and run:

python -m research_questions.src.contributors.country2continents

To map each user country to a given continent.

Libraries used:
(https://github.com/boyter/scc)
(https://github.com/terryyin/lizard)

Some txt files with results are generated during the previous commands.

This script can take hours to run. The scc lib was installed with snap, for 
Ubuntu.

The information gathered for each user belonging to a given data split is saved in csv files. Each line of the csv represents a user.



