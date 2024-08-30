# Contributors Information


The scripts in this directory gets contributors information for each repository, such as GitHub user ID, user location, date of creation of the user account and user ocuntry . This script assumes you have configured a valid GitHub auth token in the .env file (see how to configure the project in the main README), and also an
active email for querying the GeoPy library.

To generate the contributors data in csv files, run the following commands in the given order, from inside the main directory of this project:

python -m research_questions.src.contributors.get_contributors_info

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



