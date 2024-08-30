"""
File Summary:

Module is unfinished as GitHub API was the primary use to obtain data. Module is used to obtain data from a specified
time frame from GH Archive and filter GitHub type data from a single GitHub archive file.


TODO: After timeframe download, iterate through each download and filter the specified GitHub type to a single file in
      "./data/evaluations/"


Resources Used:

GH Archive: https://www.gharchive.org/

"""

# Imports

# Local
from github import githubApi
import utils
from utils import utils

# Built-in

# Used for saving GitHub archives
import os
import json
import gzip

import datetime
from datetime import timedelta, datetime

# Used for requesting data
import urllib
from urllib.request import Request

# Used for mass follower count
import asyncio



def downloadGithubArchiveTimeframe(startDate : str, endDate : str) -> None:
    '''
    Downloads all GitHub archive data between a start and end date. End date is not inclusive

    Dates need to be formatted in year-month-day form

    :param startDate: First date to start downloading data in year-month-day
    :param endDate: Last date to start downloading data in year-month-day
    :return: Downloads all archive data in "./data/downloads/" and in a folder name with the corresponding timeframe
    '''

    #Check if dates are valid
    try:
        datetime.strptime(startDate, "%Y-%m-%d")
        datetime.strptime(endDate, "%Y-%m-%d")
    except Exception as error:
        raise Exception("Start date or end date is invalid!")


    # Separate year-month-day to turn into a actual date
    splitStartDate : list = list(map(int, startDate.split("-")))
    startDateTime : datetime = datetime.datetime(splitStartDate[0], splitStartDate[1], splitStartDate[2])

    splitEndDate : list = list(map(int, endDate.split("-")))
    endDateTime : datetime = datetime.datetime(splitEndDate[0], splitEndDate[1], splitEndDate[2])

    # Determine folder name to save based on timeframe
    newFolderName : str = f'./data/downloads/{startDate}_{endDate}'

    # Check if timeframe file already exists
    if not os.path.exists(newFolderName):
        os.makedirs(newFolderName)

    # Iterate until reaching specified endDate time
    while(startDateTime != endDateTime):

        #Iterate though each hour of the day
        for hour in range(0, 24):

            # Downloads each hours archive
            _downloadGithubDateArchive(f"{startDate}_{endDate}", format(startDateTime, "%Y-%m-%d-%-H"))

            # Iterate by one hour
            startDateTime += timedelta(hours=1)


def filterGithubArchiveType(githubType: str, fileName: str, specifyFilePath : bool = False) -> None:
    '''
    Function filters the specified githubType from a specified GitHub archive file. Obtains necessary information in a
    JSON object, where it includes text and follower count of users. Uses private function _getGithubArchiveData, to
    clean and filter the data of only needed information. Additionally, uses GraphQL GitHub requests to obtain follower
    count of each user in groups of 2000.

     GitHub Type List Includes: ['push', 'pullRequest', 'issue', 'issueComment']

    'push':         Outputs the message regarding the GitHub PushEvent

    'pullRequest':  Outputs the title regarding the GitHub PullRequestEvent

    'issue':        Outputs the title and messages in regarding GitHub IssuesEvent

    'comment': Outputs the original issue data, and the commented message regarding IssueCommentEvent

    :param githubType: GitHub type to filter
    :param fileName: File name of the GitHub archive date
    :param specifyFilePath: Boolean for if the user wants to specify the file path of the read file. Use fileName parameter
                            as the file path location.
    :return: Creates a file in "./data/evaluations/" corresponding to the specified file name and GitHub type
    '''

    # Handle possible user error
    if ".json" in fileName and not specifyFilePath:
        raise Exception("Only specify the file name without the '.json'!")

    # Open archive file and write file

    if specifyFilePath:

        # Read specified file data
        archiveFile = open(fileName, "r")
    else:

        # Read file name data
        archiveFile = open(f"./data/downloads/{fileName}.json", "r")

    writeFile = open(f"./data/evaluations/{fileName}_{githubType}.json", "a")

    # Iterate through each JSON in the archive data
    for line in archiveFile:
        # Parse the JSON data from the archive
        parsedData : dict = json.loads(line)

        # Obtained only the needed data
        obtainedData : dict = _getGithubArchiveData(githubType, parsedData)

        # Skip to next JSON data if not the needed type
        if not obtainedData: continue

        # Write data in json format to file
        writeFile.write(json.dumps(obtainedData))

        # Write new line
        writeFile.write('\n')


    print(f"Done Cleaning {githubType}.")

    # Close files
    archiveFile.close()
    writeFile.close()

    # Return if there is no applicable user
    if githubType.lower() != "issue" and githubType.lower() != "comment": return

    print("Now adding follower count")



    # Open file to edit lines
    with open(f"./data/evaluations/{fileName}_{githubType}.json", 'r') as file:
        # read a list of lines into data
        data = file.readlines()

    # Check the GitHub type, whether there are two users in a JSON object or one
    if githubType.lower() == "issue":
        # Group all the users in a file in lists of 2000
        userGroups : list[list] = utils.groupJsonKeys(data, ["user"])

        # Run requests of each user group
        fileUserFollowers : list = asyncio.run(githubApi.setupMassGithubUserFollowerCalls(userGroups))

        # Individuality add each follower count to the corresponding JSON object
        for lineNumber, line in enumerate(data):
            # Turn JSON object into a dictionary
            tempDict : dict = json.loads(line)

            # Add user followers
            tempDict["userFollowers"] = fileUserFollowers[lineNumber]

            # Turn dictionary into a JSON array and edit the line
            data[lineNumber] = json.dumps(tempDict) + "\n"

    elif githubType.lower() == "comment":
        # Group all the users in a file in lists of 2000
        userGroups : list[list] = utils.groupJsonKeys(data, ["user", "originalUser"])

        # Run requests of each user group
        fileUserFollowers : list = asyncio.run(githubApi.setupMassGithubUserFollowerCalls(userGroups))

        # Set followers as iterator object to regroup the users in batches of two
        iterUserGroup : iter = iter(fileUserFollowers)

        # Iterate through by two users to re-add into a single JSON object
        for lineNumber, followerCount in enumerate(iterUserGroup):

            # Turn JSON object into a dictionary
            tempDict : dict = json.loads(data[lineNumber])

            #Add both user and original user followers into dictionary
            tempDict["userFollowers"] = followerCount
            tempDict["originalUserFollowers"] = next(iterUserGroup)

            # Turn dictionary into a JSON array and edit the line
            data[lineNumber] = json.dumps(tempDict) + "\n"


    # Write everything back into the file
    with open(f"./data/evaluations/{fileName}_{githubType}.json", 'w') as file:
        file.writelines(data)

    # Done adding follower count
    print("Done adding follower count")


def _getGithubArchiveData(githubType : str, parsedData: dict) -> dict:
    '''
    Function filters all the needed data like title or body corresponding to what the GitHub type is.
    Obtains text such as title and body of the corresponding GitHub parsedData if applicable.

    GitHub Types:['push', 'pullRequest', 'issue', 'issueComment']

    :param githubType: The corresponding to the GitHub type
    :param parsedData: Parsed data in the form of JSON, obtained from GitHub archive
    :return: Returns all the needed data regarding the type
    '''

    # Initialize the dictionary
    tempDict = dict()

    print(parsedData)

    # Add the username to the dictionary
    tempDict["user"] = parsedData["actor"]["login"]

    # Initialize key in dictionary
    tempDict["userFollowers"] = None

    # Check need to initialize other keys in the dictionary
    if githubType.lower() == "comment" and parsedData["type"] == "IssueCommentEvent":
        tempDict["originalUser"] = parsedData["payload"]["issue"]["user"]["login"]
        tempDict["originalUserFollowers"] = None

    match (githubType.lower()):

        case "issue":

            # Check if the iterated data matches the type and if it has a valid set of data
            if parsedData["type"] != "IssuesEvent" or not parsedData["payload"]["issue"]["body"]:
                return dict()

            # Define type
            tempDict["type"] = "issue"


            # Add the title and body in the issue dictionary
            tempDict["title"] = parsedData["payload"]["issue"]["title"]
            tempDict["body"] = utils.cleanText(parsedData["payload"]["issue"]["body"])

        case "comment":
            # Check if the iterated data matches the type and if it has a valid set of data
            if parsedData["type"] != "IssueCommentEvent" or not parsedData["payload"]["comment"]["body"] or not \
            parsedData["payload"]["issue"]["body"]:
                return dict()

            # Define type
            tempDict["type"] = "issueComment"

            # Add the original issue data in the issue comment dictionary
            tempDict["originalIssueTitle"] = parsedData["payload"]["issue"]["title"]
            tempDict["originalIssueBody"] = utils.cleanText(parsedData["payload"]["issue"]["body"])

            # Add the issue comment into the dictionary
            tempDict["body"] = parsedData["payload"]["comment"]["body"]

        case "pullrequest":
            # Check if it is a pull request event and if there is a valid title
            if parsedData["type"] == "PullRequestEvent" and parsedData["payload"]["pull_request"]:
                # Define type
                tempDict["type"] = "pullRequest"

                # Add the title to the dictionary
                tempDict["body"] = parsedData["payload"]["pull_request"]["title"]

        case "push":
            # Check if it is a push event and if there is a valid message
            if parsedData["type"] == "PushEvent" and parsedData["payload"]["commits"]:

                # Define type
                tempDict["type"] = "push"

                # Add the message to the dictionary
                tempDict["body"] = utils.cleanText(parsedData["payload"]["commits"][0]["message"])

        case _:
            raise Exception("Invalid Type.")

    # Return the added data
    return tempDict


def _downloadGithubDateArchive(filePath : str , date: str) -> None:
    '''
    Private function that downloads an hour of GitHub archive data based on year-month-day-hour format.
    Used in hand with downloadGithubArchiveTimeframe function that download archive data on a day-by-day basis.

    :param filePath: Folder to download the hour of data in
    :param date: Date in year-month-day-hour format
    :return: Downloads GitHub archive data in a .json file in the specified file path folder
    '''

    # Required Parameters to prevent being blocked
    req = Request(
        url=f"http://data.gharchive.org/{date}.json.gz",
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    # Request all the data as a compressed gz file
    response = urllib.request.urlopen(req)

    # Decompress the gzip file in bytes
    decompressedData : bytes = gzip.GzipFile(fileobj=response).read()

    # Write to the file in the form of bytes
    with open(f"./data/downloads/{filePath}/{date}.json", 'wb') as f:
        f.write(decompressedData)

    print("Done Scrapping " + date)