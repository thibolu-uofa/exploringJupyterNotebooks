"""
File Summary:

Allows the user to have access to the primary functions used to gather GitHub paper data, analyze sentences and
processes of viewing AI model accuracy. This interface is limited to all the functions created such as gathering GitHub
archive data. Use the actual modules directly to have access to them.

"""
import itertools
import json
from itertools import islice

# Imports

# Local

from github import githubApi

from analyzeToxicity import filePerspectiveApi
from analyzeData import analyzeData
from utils import saveData, readData, utils

def mainMenu() -> None:
    '''
    Main menu to allow the user to select a process

    :return: None
    '''

    # Prompt selection
    print(
f"""
1. GitHub Aspects
2. Analyze Toxicity
3. Analyze Toxicity Data
4. Exit
""")

    # Get user input in the selection range
    userInput : int = utils.getMenuNumber(5)


    # Call the selected function
    match(userInput):
        case(1):
            githubAspectsMenu()

        case(2):
            analyzeToxicityMenu()

        case(3):
            analyzeToxicityDataMenu()

        case(4):
            exit(1)


def githubAspectsMenu() -> None:
    '''
    Allows the user to select the specified GitHub process

    :return: None
    '''
    print("""
1. Save Github Repository Type
2. Main Menu
    """)

    # Obtain user input within selection range
    userInput: int = utils.getMenuNumber(2)

    # Call specified function
    match(userInput):

        case(1):

            # Obtain file path of repository links

            # Initialize file path variable
            filePath : str = ""

            # The file of repository links must be a .txt file
            while ".txt" not in filePath:
                print("Select the file that contains GitHub repository links. Must be a .txt file \n")

                # Allow the user to select the file in file explorer
                filePath : str = utils.getFilePath()

            # Initialize GitHub type variable
            githubType : str = ""

            # The GitHub type must be 'issue' or 'comment'
            while githubType not in ["issue", "comment"]:

                # Obtain GitHub type
                githubType : str = input("Select GitHub type to obtain. Types Include: ('issue', 'comment'): \n")

            # Obtain save file name
            saveFileName : str = input("What would you like the save file name to be? \n")

            # Call save GitHub repository function

            try:
                githubApi.saveGithubRepositoryLinks(githubType, filePath, saveFileName, specifyFilePath=True)
            except Exception as error:
                print(error)
                raise Exception("Invalid file. Each line on the file must be a GitHub repository link!")

        case(2):

            # Go back to main menu
            mainMenu()


def analyzeToxicityMenu() -> None:
    '''
    Allows the user to select the specified toxicity analysis process

    :return: None
    '''
    print("""
1. PerspectiveAPI
2. Main Menu
    """)

    # Obtain user input within selection range
    userInput: int = utils.getMenuNumber(2)

    # Call specified function
    match(userInput):

        case(1):
            print("Select the file that you would like to analyze the toxicity")

            # Allow the user to select a file in file explorer
            filePath : str = utils.getFilePath()


            try :
                # Check what type of file the user selected
                if "json" in filePath:

                    # Analyze JSON file
                    filePerspectiveApi("json", filePath,specifyFilePath=True)

                elif "txt" in filePath:

                    # Analyze JSON file
                    filePerspectiveApi("text", filePath, specifyFilePath=True)
                else:
                    raise Exception("Invalid file type. Must be either .json or .txt")

            except Exception as error:
                print(error)
                raise Exception("Invalid file. The file must be organized as the specified type.")


        case(2):
            mainMenu()


def analyzeToxicityDataMenu() -> None:
    '''
    Allows the user to select the specified analysing toxicity proess
    :return:
    '''

    print(""" 
1. Create Excel file of specified toxicity data analyzed by PerspectiveAPI
2. Analyze Excel toxicity performance and ROC curve (Accurate Data Required)
3. Get most common values of PerspectiveAPI analyzed file
4. Analyze most common values of only accurate PerspectiveAPI data
5. Check flagged PerspectiveAPI labels versus general toxicity
6. Get toxicity label count of analyzed PerspectiveAPI file
7. Get number of valid toxicity data analyzed by Perspective API in file
8. Main Menu
""")

    userInput : int = utils.getMenuNumber(8)

    match(userInput):
        case(1):
            _convertPerspectiveToxicityIntoExcel()
        case(2):
            _analyzeAccurateExcelRocCurve()
        case(3):
            _analyzeToxicityMostCommon()
        case(4):
            _analyzeCommonAccurateToxicityData()
        case(5):
            _checkNewToxicityLabelFlags()
        case(6):
            _filePerspectiveToxicityCount()
        case(7):
            _filePerspectiveValidCount()

        case(8):
            mainMenu()


def _convertPerspectiveToxicityIntoExcel() -> None:
    '''
    Converts a specified analyzed PerspectiveAPI JSON file into a Excel file

    :return: Creates a Excel file with the user specified data
    '''
    print("Select the PerspectiveAPI analyzed .json file")

    # Obtain file path
    filePath : str = utils.getFilePath()

    # Handle possible user error
    if ".json" not in filePath:
        raise Exception("Please select a analyzed PerspectiveAPI analyzed .json file")

    # Ask what data the user wants
    print("What type of GitHub data is the file? List includes : 'issue' or 'comment'")
    githubType : str = utils.getUserSelection(["issue", "comment"])

    print("What type of toxicity do you want to count? List includes : 'toxicity', 'severeToxicity', 'identityAttack', "
          "'insult', 'profanity', and 'threat'")
    print("Note: List is case sensitive")

    userToxicitySelection : str = utils.getUserSelection(["toxicity", "severeToxicity", "identityAttack", "insult", "profanity", "threat"])

    print("What categories do you want to put in the Excel file?")

    # Print out labels

    if githubType.lower() == "issue":
        allAcceptedLabels : list = ['type', 'title', 'repositoryOwner', 'repositoryName', 'issueNumber', 'created',
                                'updated', 'state', 'locked', 'user', 'userFollowers']
    else:
        allAcceptedLabels: list = ['type', 'repositoryOwner', 'repositoryName', 'issueNumber', 'created',
                                   'updated', 'user', 'userFollowers']


    print(f"List includes: {['all'] + allAcceptedLabels}")

    specifiedLabels : list = utils.getUserListSelection(allAcceptedLabels)

    # Obtain JSON data of the specified data
    jsonData: list[list] = readData.getJsonData(filePath, "body", "perspectiveApiToxicity>" + userToxicitySelection,
                                                    *specifiedLabels
                                                    , specifyFilePath=True)

    # Split the wanted data into a separate list
    extraData : list = jsonData[2:]



    # Get user input threshold
    specifiedThreshold : float = utils.getThresholdNumber()


    # Obtain a selection of evaluating text
    print("Do you want a space to manually evaluate text? Answer 'yes' or 'no'")
    userEvaluateTextSelection: str = utils.getUserSelection(["yes", "no"])

    # Add a new column to the data if user wants to evaluate text
    if userEvaluateTextSelection.lower() == "yes":
        specifiedLabels = ["Human Evaluated Score"] + specifiedLabels
        extraData = [[" " for _ in range(len(extraData[0]))]] + extraData


    # Obtain save file
    saveFileName : str = input("What would you like the save file name to be? \n")

    # Save filtered toxicity data as an Excel
    saveData.toxicityDataToExcel(saveFileName, jsonData[0], jsonData[1],
                     extraDataLabels=tuple([userToxicitySelection] + specifiedLabels), extraData=extraData,
                     threshold=specifiedThreshold)


def _checkNewToxicityLabelFlags():
    '''
    Obtains the number of new flagged PerspectiveAPI labels versus the general toxicity.

    The user needs to input a PerspectiveAPI analyzed JSON file.

    :return: None
    '''

    print("Select the JSON file of the PerspectiveAPI data")

    # Obtain file path
    filePath : str = utils.getFilePath()

    # Handle possible user error
    if ".json" not in filePath:
        raise Exception("Please select a .json file")

    # Open file
    jsonFile = open(filePath, "r")

    # Obtain threshold to check
    checkThreshold : float = utils.getThresholdNumber()

    # Initialize new flagged count
    newSevereToxicityFlags : int = 0
    newIdentityAttackFlags : int = 0
    newInsultFlags : float = 0
    newProfanityFlags : float = 0
    newThreatFlags : float = 0

    # Iterate through each JSON object
    for line in set(jsonFile):

        # Obtain perspectiveApiToxicity Scores
        jsonData : dict = json.loads(line)["perspectiveApiToxicity"]

        # Assign values
        toxicityScore : float = jsonData["toxicity"]
        severeToxicityScore : float = jsonData["severeToxicity"]
        identityAttackScore : float = jsonData["identityAttack"]
        insultScore : float = jsonData["insult"]
        profanityScore : float = jsonData["profanity"]
        threatScore : float = jsonData["threat"]

        # Compare new flagged attributes
        if severeToxicityScore and severeToxicityScore >= checkThreshold and toxicityScore < checkThreshold:
            newSevereToxicityFlags += 1

        if identityAttackScore and identityAttackScore >= checkThreshold and toxicityScore < checkThreshold:
            newIdentityAttackFlags += 1

        if insultScore and insultScore >= checkThreshold and toxicityScore < checkThreshold:
            newInsultFlags += 1

        if profanityScore and profanityScore >= checkThreshold and toxicityScore < checkThreshold:
            newProfanityFlags += 1

        if threatScore and threatScore >= checkThreshold and toxicityScore < checkThreshold:
            newThreatFlags += 1
    print(
f"""
New Labeled Categories based on a {checkThreshold} Threshold:
Severe Toxicity: {newSevereToxicityFlags}
Identity Attack: {newIdentityAttackFlags}
Insult: {newInsultFlags}
Profanity: {newProfanityFlags}
Threat: {newThreatFlags}
""")


    jsonFile.close()



def _analyzeToxicityMostCommon() -> None:
    '''

    Checks the most common elements of various labels such as repositories, year, or user. Averages of user followers
    and toxicity score is also included.

    The user must input a toxicity analyzed JSON file to get the most common elements.

    :return: None
    '''


    print("Select the JSON file of the PerspectiveAPI data")

    # Obtain file path
    filePath : str = utils.getFilePath()

    # Handle possible user error
    if ".json" not in filePath:
        raise Exception("Please select a .json file")

    # Open file
    jsonFile = open(filePath, "r")

    # Obtain threshold to filter out responses
    filterThreshold : float = utils.getThresholdNumber()


    # Initialize values
    filteredRepositories : list = []
    filteredCreatedDates : list = []
    filteredUsers : list = []
    filteredUserFollowerCount : list = []
    filteredToxicityScores : list = []

    # Iterate through each line to filter out responses based on filter threshold
    for line in set(jsonFile):

        # Turn JSON data into a dictionary
        jsonData : dict = json.loads(line)

        # Obtain filter toxicity score
        toxicityScore : float = jsonData["perspectiveApiToxicity"]["toxicity"]

        # Separate dictionary values into their own list
        if toxicityScore and toxicityScore >= filterThreshold:
            filteredRepositories.append(jsonData["repositoryOwner"] + "/" + jsonData["repositoryName"])
            filteredCreatedDates.append(jsonData["created"].split("-")[0])
            filteredUsers.append(jsonData["user"])
            filteredToxicityScores.append(toxicityScore)

            if jsonData["userFollowers"]:
                filteredUserFollowerCount.append(jsonData["userFollowers"])
            else:
                filteredUserFollowerCount.append(0)

    mostCommonRepository: str = max(set(filteredRepositories), key=filteredRepositories.count)
    mostCommonUser: str = max(set(filteredUsers), key=filteredUsers.count)

    print(f"""
Most Common Toxic Categories by Human Evaluation:
Repository: {None if filteredRepositories.count(mostCommonRepository) == 1 else mostCommonRepository}
Year: {max(set(filteredCreatedDates), key=filteredCreatedDates.count)}
User: {None if filteredUsers.count(mostCommonUser) == 1 else mostCommonUser}

Average User Followers: {sum(filteredUserFollowerCount) / len(filteredUserFollowerCount)}
Average Toxicity Score: {sum(filteredToxicityScores) / len(filteredToxicityScores)}
    """)

    jsonFile.close()


def _analyzeCommonAccurateToxicityData() -> None:
    '''
    Checks the most common elements of various labels such as repositories, year, or user. Averages of user followers
    and toxicity score is also included.

    The user must input a toxicity analyzed Excel file to get the most common elements

    :return: None
    '''

    # Initialize Label Data
    toxicityData: list = []
    repositoryOwnerData: list = []
    repositoryNameData: list = []
    createdData: list = []
    userData: list = []
    userFollowersData: list = []
    humanEvaluatedData: list = []

    print("Select the PerspectiveAPI analyzed Excel file that contains accurate data \n")
    print("The following label must be in the Excel file:")
    print(["toxicity", "repositoryOwner", "repositoryName", "created", "user", "userFollowers"])

    filePath: str = utils.getFilePath()

    # Obtain labels of file
    excelLabels = readData.getExcelLabels(filePath, specifyFilePath=True)

    # Handle possible errors
    if len(excelLabels) > 23: raise Exception("Invalid PerspectiveAPI Excel File")

    if "Human Evaluated Score" not in excelLabels: raise Exception("Human Evaluated Score not in file!")

    # Extract information from each individual label column
    for labelNumber, label in enumerate(excelLabels):
        if label == "Human Evaluated Score": humanEvaluatedData = \
        readData.getExcelData(filePath, chr(64 + labelNumber + 1), specifyFilePath=True)[0]
        if label == "repositoryName": repositoryNameData = \
        readData.getExcelData(filePath, chr(64 + labelNumber + 1), specifyFilePath=True)[0]
        if label == "repositoryOwner": repositoryOwnerData = \
        readData.getExcelData(filePath, chr(64 + labelNumber + 1), specifyFilePath=True)[0]
        if label == "created": createdData = \
        readData.getExcelData(filePath, chr(64 + labelNumber + 1), specifyFilePath=True)[0]
        if label == "user": userData = readData.getExcelData(filePath, chr(64 + labelNumber + 1), specifyFilePath=True)[
            0]
        if label == "userFollowers": userFollowersData = \
        readData.getExcelData(filePath, chr(64 + labelNumber + 1), specifyFilePath=True)[0]
        if label == "toxicity": toxicityData = \
        readData.getExcelData(filePath, chr(64 + labelNumber + 1), specifyFilePath=True)[0]

    # Merge the repository owner and repository name
    if repositoryOwnerData and repositoryNameData:
        repositoryData : list = [f"{x[0]}/{x[1]}" for x in zip(repositoryOwnerData, repositoryNameData)]
    else:
        raise Exception("repositoryOwner or repositoryName is not in Excel file!")

    # Initialize filtered lists
    filteredRepositories: list = []
    filteredCreatedDates: list = []
    filteredUsers: list = []
    filteredUserFollowerCount: list = []
    filteredToxicityScores: list = []

    # Filter data based on identified toxic comments
    for dataNumber, data in enumerate(humanEvaluatedData):

        # Check if the response is toxic
        if data and data == "y":

            # Check if data exists
            if repositoryData: filteredRepositories.append(repositoryData[dataNumber])
            if createdData: filteredCreatedDates.append(createdData[dataNumber].split("-")[0])
            if userData: filteredUsers.append(userData[dataNumber])
            if userFollowersData: filteredUserFollowerCount.append(userFollowersData[dataNumber])

            filteredToxicityScores.append(toxicityData[dataNumber])

    # Get most common data
    mostCommonRepository: str = max(set(filteredRepositories), key=filteredRepositories.count)
    mostCommonUser: str = max(set(filteredUsers), key=filteredUsers.count)

    print(f"""
Most Common Toxic Categories by Human Evaluation:
Repository: {None if filteredRepositories.count(mostCommonRepository) == 1 else mostCommonRepository}
Year: {max(set(filteredCreatedDates), key=filteredCreatedDates.count)}
User: {None if filteredUsers.count(mostCommonUser) == 1 else mostCommonUser}

Average User Followers: {sum(filteredUserFollowerCount) / len(filteredUserFollowerCount)}
Average Toxicity Score: {sum(filteredToxicityScores) / len(filteredToxicityScores)}
    """)


def _filePerspectiveToxicityCount() -> None:
    '''
    Shows the toxicity count of specified file. The file must be .json

    :return: None
    '''

    print("Select the PerspectiveAPI analyzed .json file")

    # Obtain file path
    filePath : str = utils.getFilePath()

    # Handle possible user error
    if ".json" not in filePath:
        raise Exception("Please select a analyzed PerspectiveAPI analyzed .json file")

    print("What type of toxicity do you want to count? List includes : 'toxicity', 'severeToxicity', 'identityAttack', "
          "'insult', 'profanity', and 'threat'")
    print("Note: List is case sensitive")
    userSelection = utils.getUserSelection(["toxicity", "severeToxicity", "identityAttack", "insult", "profanity", "threat"])



    # Read JSON data of the specified keys
    jsonData : list[list] = readData.getJsonData(filePath, "perspectiveApiToxicity>" + userSelection
                                                 ,specifyFilePath=True)

    # Create analysis object
    gitHubToxicity: analyzeData = analyzeData("PerspectiveAPI", jsonData[0])

    # Get threshold from user
    specifiedThreshold: float = utils.getThresholdNumber()

    # Get toxicity count based on PerspectiveAPI ROC curve data
    gitHubToxicity.getToxicityCount(specifiedThreshold)


def _filePerspectiveValidCount() -> None:
    '''
    Obtains the number of valid PerspectiveAPI analyzed results.

    The user must input a analyzed PerspectiveAPI JSON file.

    :return: None
    '''
    print("Select the PerspectiveAPI analyzed .json file")

    # Obtain file path
    filePath : str = utils.getFilePath()

    # Handle possible user error
    if ".json" not in filePath:
        raise Exception("Please select a analyzed PerspectiveAPI analyzed .json file")


    # Read JSON data of the specified keys
    jsonData : list[list] = readData.getJsonData(filePath, "perspectiveApiToxicity>toxicity"
                                                 ,specifyFilePath=True)

    # Create analysis object
    gitHubToxicity: analyzeData = analyzeData("PerspectiveAPI", jsonData[0])

    # Get valid toxicity count
    gitHubToxicity.getValidAnalyzedCount()



def _analyzeAccurateExcelRocCurve() -> None:
    '''
    Used to view the ROC curve and data of a specific Excel file.

    :return: None
    '''
    print("Select the PerspectiveAPI analyzed Excel file that contains evaluated and accurate data")
    filePath : str = utils.getFilePath()

    # Ask user for column letters
    evaluatedExcelColumn : str = input("What column is the evaluated data in the Excel file? \n")

    accurateExcelColumn : str = input("What column is the accurate data in the Excel file? \n")

    # Read excel column data
    toxicityData : list[list] = readData.getExcelData(filePath, evaluatedExcelColumn, accurateExcelColumn, specifyFilePath=True)

    # Label categories
    analyzeToxicityData : analyzeData = analyzeData("PerspectiveAPI", toxicityData[0], accurateData=toxicityData[1])

    # Print category data
    print(analyzeToxicityData)

    # Show ROC curve
    analyzeToxicityData.viewRocCurve()





