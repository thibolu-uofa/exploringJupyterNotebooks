# Complexity Information

The python script `main.py` gets complexity information, such as lines of code (LOC), number of comment lines, number of functions, cyclomatic complexity, 
and number of classes for each file belonging to the dataset splits. This script assumes you have already cloned the repositories locally in your machine, in the path described in the config.json file. To clone the repositories that compose the dataset, refer to `research_questions/src/clone_repositories`.

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

The information gathered for each file belonging to a given data split is saved in csv files (file type,number of comment lines,markdown lines count,loc,number of functions,average_cyclomatic_complexity,number of classes,and filepath). Each line of the csv represents either a python or a notebook file.

The analysis of the data, including the boxplot, is done in the notebook `complexity_analysis.ipynb` and it uses the csvs data.

