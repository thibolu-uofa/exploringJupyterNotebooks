# University of Alberta - Measuring Toxicity Research

Installation instructions to reproduce various toxicity analysis data. The project is directed to analyze various bug tracking report responses for toxicity and find relations to how various attributes impact developer responses. 

## Prerequisites
- Python (3.5+)

## Setup 
1. Clone or download this repository
2. Edit `config.py` with your GitHub API key and PerspectiveAPI key
   - Add your API key like this `EXAMPLE_API_KEY = "YOUR_API_KEY"`
     -  Obtain your GitHub API key here: https://github.com/settings/tokens
     -  Learn how to obtain your PerspectiveAPI access here: https://developers.perspectiveapi.com/s/docs-get-started
3. Install requirements
   - Ensure that you are in the current directory of the project
   - Install requirements by doing `pip install -r requirements.txt`
  
## Understanding Data Folders
- `./data/downloads` : Used for downloading GitHub archive data and other extraneous data such as GitHub repository link files
- `./data/evaluations` : Data that is ready to be evaluated for toxicity, should be a formatted `.json` or `.txt` file
- `./data/results` : Results of evaluated toxicity based on the `./data/evaluations` files

The `./data/evaluations` is currently empty to conserve repository space. To replicate toxicity evaluations, simply move any desired `.json` file from `./data/results` into `./data/evaluations` and analyze the file again. Any `.json` file from `./data/results` is the exact same data that is usually contained in `./data/evaluations`, but with PerspectiveAPI toxicity results.

## Usage
For basic usage use `python main.py`, which allows for the basic ability to obtain GitHub repository data, PerspectiveAPI toxicity scores, and analyze toxicity data.

### Gathering GitHub Repository Data
Access to all made GitHub functions, including gathering GitHub data from GH Archive and through the GitHub API.

```
from github import githubApi, githubArchive
```
An example to obtain GitHub issues from a `.txt` file containing GitHub repository links in `./data/downloads`

```
from github import githubApi

# Repository links file is in "./data/downloads"
githubApi.saveGithubRepositoryLinks("issue", "repositoryLinkFileName", "githubIssues")
```


### Gathering Toxicity Data
To analyze toxicity data of sentences.

```
import analyzeToxicity
```

Currently analyzing toxicity through PerspectiveAPI is the only option. An example to analyze a single sentence and file includes.

```
# Imports
import analyzeToxicity

# Analyze single Sentence
analyzeToxicity.getPerspectiveApi("hello world!")

# Analyze file containing multiple sentences in "./data/evaluations" folder
analyzeToxicity.filePerspectiveApi("json", "githubIssues")
```

### Analyzing Toxicity Data

To analyze toxicity data.
```
from utils import readData
from analyzeData import analyzeData
```

An example to calculate the number of toxic comments in a JSON file.

```
# Imports
from utils import readData
from analyzeData import analyzeData

# Read JSON data of the specified keys
jsonData : list[list] = readData.getJsonData("githubIssues", "perspectiveApiToxicity>toxicity")

# Create analysis object
gitHubToxicity: analyzeData = analyzeData("PerspectiveAPI", jsonData[0])

# Obtain number of toxic sentences
gitHubToxicity.getToxicityCount(0.14)
```

An example to find category label data (TP, FP, TN, FN)

```
# Imports
from utils import readData
from analyzeData import analyzeData

# Read excel column data
toxicityData : list[list] = readData.getExcelData(filePath, evaluatedExcelColumnLetter, accurateExcelColumnLetter, specifyFilePath=True)

# Label categories
analyzeToxicityData : analyzeData = analyzeData("PerspectiveAPI", toxicityData[0], accurateData=toxicityData[1])

# Print category data
print(analyzeToxicityData)
```
