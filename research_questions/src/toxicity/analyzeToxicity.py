"""
File Summary:

Module has the ability to analyze toxicity for a single sentence or various sentences in each file. Depending on files,
the user needs to specify the type of file it is. Currently, only PerspectiveAPI is used to analyze toxicity text.

"""

#Imports

# Local
from utils import saveData
import config

# Built-in
from itertools import islice
from pathlib import Path
import time
import json


# Installed
from googleapiclient import discovery
from googleapiclient.errors import HttpError



def getPerspectiveApi(text : str) -> dict:
    '''
    Used to analyze a single body of text using PerspectiveAPI. Obtains scores regarding ["toxicity", "severeToxicity",
    "identityAttack","insult", "profanity", "threat"]

    :param text: Text to evaluate using PerspectiveAPI
    :return: Returns dictionary containing all PerspectiveAPI toxicity scores
    '''

    # Check if PerspectiveAPI key is added
    if not config.PERSPECTIVE_API_KEY:
        raise Exception("PerspectiveAPI key must be added in order to measure the toxicity!")

    # Initialize toxicity dictionary
    toxicityDict : dict = dict.fromkeys(["toxicity", "severeToxicity", "identityAttack", "insult", "profanity", "threat"], None)

    # Do not submit toxicity request if text is empty
    if not text:
        print("Empty sentence")
        toxicityDict["error"] = "COMMENT_EMPTY"
        return toxicityDict


    try:

        # Google client request
        client = discovery.build(
            "commentanalyzer",
            "v1alpha1",
            developerKey=config.PERSPECTIVE_API_KEY,
            discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
            static_discovery=False,
        )

        # PerspectiveAPI request data
        analyze_request = {
            'comment': {'text': text},
            'requestedAttributes': {'TOXICITY': {},
                                    'SEVERE_TOXICITY': {},
                                    'IDENTITY_ATTACK': {},
                                    'INSULT': {},
                                    'PROFANITY': {},
                                    'THREAT': {}
                                    }
        }

        # Get all PerspectiveAPI scores
        response : dict = client.comments().analyze(body=analyze_request).execute()["attributeScores"]

    except HttpError as error:

        # Catch rate limit
        if error.resp.status == 429:
            print("Rate Limited, sleeping 1 second")
            time.sleep(1)
            return getPerspectiveApi(text)

        elif error.resp.status == 502:
            print("Bad Gateway, sleeping 30 seconds")
            time.sleep(30)
            return getPerspectiveApi(text)

        elif error.resp.status == 400 and isinstance(error.error_details, str) and "too many bytes" in error.error_details:
            print("Sentence too long")
            toxicityDict["error"] = "COMMENT_TOO_LONG"

        # Caught other error
        elif error.resp.status == 400:

            try:
                toxicityDict["error"] = error.error_details[0]["errorType"]
                print(toxicityDict["error"])
            except:
                print(error)

        else:
            print(error)

        # Return dictionary full of None
        return toxicityDict

    except Exception as err:
        print(err)

        #Return dictionary full of None
        return toxicityDict

    # To prevent being rate limited, as PerspectiveAPI has a 60 request per minute rate limit.
    time.sleep(1)


    # Add all PerspectiveAPI scores to toxicity dictionary
    toxicityDict["toxicity"] = response["TOXICITY"]["summaryScore"]["value"]
    toxicityDict["severeToxicity"] = response["SEVERE_TOXICITY"]["summaryScore"]["value"]
    toxicityDict["identityAttack"] = response["IDENTITY_ATTACK"]["summaryScore"]["value"]
    toxicityDict["insult"] = response["INSULT"]["summaryScore"]["value"]
    toxicityDict["profanity"] = response["PROFANITY"]["summaryScore"]["value"]
    toxicityDict["threat"] = response["THREAT"]["summaryScore"]["value"]

    # Return all PerspectiveAPI toxicity data as a dictionary
    return toxicityDict


def filePerspectiveApi(fileType: str, fileName: str, startLine : int = 1, specifyFilePath : bool = False) -> None:
    '''
    All analysis files need to be the "data/evaluations/" folder

    File type could be "text" or "json". Use "text for a small sample of
    sentences, and "json" for any sample size. Toxicity data is saved every 1000 entries using "json", while
    there are no auto saves for .txt files. JSON file type is recommend for all cases.

    "text" : In .txt file type. Each line of the file is text  separate values.
    "json": In .json file type. Each line of the file is a json object, where it may contain data other than text.
            Must have the key "body" to analyze the text

    :param fileType: File type could be "text" or "json"
    :param fileName: Name of the file in "data/evaluations/" corresponding to the file type
    :param startLine: Line to start at in the file, used for only JSON file types.
    :param specifyFilePath: Boolean for if the user wants to specify the file path of the read file. Use fileName parameter
                            as the file path location.
    :return: Saves all toxicity data to the "./data/results" folder with the same file name
    '''

    #Handle invalid types
    if fileType.lower() != "json" and fileType.lower() != "text":
        raise Exception('Invalid File Types. Only valid types are "text", or "json"')

    # Check if PerspectiveAPI key is added
    if not config.PERSPECTIVE_API_KEY:
            raise Exception("PerspectiveAPI key must be added in order to measure the toxicity!")

    # Raise error to prevent overwriting analyzed data
    if Path(f"./data/results/{fileName}.json").is_file():
        raise Exception("It seems like this file has already been analyzed! Make sure you do not use the same file "
                        "name as a results file!")

    print("Adding PerspectiveAPI rating now")

    match (fileType.lower()):

        case "json":

            if specifyFilePath:

                # Open file to edit lines
                with open(fileName, 'r') as file:
                    # Read a list of lines into data
                    data = file.readlines()

                fileName = fileName.split("/")[-1].split(".")[0]

            else :
                # Open file to edit lines
                with open(f"./data/evaluations/{fileName}.json", 'r') as file:

                    # Read a list of lines into data
                    data = file.readlines()


            # Handle file out of bounds
            if startLine >= len(data):
                raise Exception("Invalid line start! Line number out of bounds")

            # Iterate through each line
            for lineNumber, line in enumerate(islice(data, startLine - 1, None), start=startLine - 1):

                # Turn JSON object into dictionary
                tempDict : dict = json.loads(line)

                # Add perspectiveAPI toxicity scores to dictionary
                tempDict["perspectiveApiToxicity"] = getPerspectiveApi(tempDict["body"])

                # Edit line and turn dictionary back into a JSON object
                data[lineNumber] = json.dumps(tempDict) + "\n"

                if (lineNumber + 1) % 1000 == 0:
                    print(f"Line {(lineNumber + 1)}: Saving Data")
                    # Write everything back to results folder
                    with open(f"./data/results/{fileName}.json", 'w') as file:
                        file.writelines(data)

            # Write everything back to results folder
            with open(f"./data/results/{fileName}.json", 'w') as file:
                file.writelines(data)


        case "text":

            # Initialize list for all the analysis to be stored
            entryEvaluation : list = []

            # Open file

            if specifyFilePath:
                file = open(fileName, "r")
            else:
                file = open(f"./data/evaluations/{fileName}.txt", "r")

            # Iterate though each line of the file
            for line in enumerate(file):

                # Add sentence and perspectiveAPI values to the entryEvaluation list
                entryEvaluation.append([line] + list(getPerspectiveApi(line).values()))

            # Close file
            file.close()

            # Determine the keys for each JSON object
            keys : tuple = (
                "Sentence", "Perspective API Toxicity ", "Perspective API Severe Toxicity",
                "Perspective API Identity Attack", "Perspective API Insult", "Perspective  API Profanity",
                "Perspective API Threat")

            if specifyFilePath:
                fileName = fileName.split("/")[-1].split(".")[0]


            #Save all the data as a JSON file
            saveData.createJsonFile(fileName, keys, entryEvaluation)

    print("Done evaluating all lines using PerspectiveAPI")

