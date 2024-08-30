"""
File Summary:

Module is primarily used obtain issues and issue comments from a specified GitHub repository or many repositories in a
.txt file. Additionally, the module is used to obtain the user follower counts of each issue / issue comment.
"""

# Imports

# Local
import config
import utils
from utils import utils


# Built-in

import json

import time
import datetime
from datetime import datetime


import ssl  # Used for requesting data from APIs
import urllib
from urllib.request import Request
from urllib.error import HTTPError
import asyncio

# Installed
import certifi


def getGithubRateLimit(githubRequestType : str = "core") -> tuple | None:
    '''
    Gets and prints rate limit data regarding the request type.

    Type: Regular(Core) Requests and GraphQL Requests

    'regular'/'core': Requests regarding data from repositories or individual follower counts

    'graphql': Requests regarding data of mass grouped follower counts

    :param githubRequestType: GitHub request type
    :return: Regarding the type, returns the number of requests and time till reset as a tuple.
             (requests remaining, reset time)
    '''

    # Turn type to lower case to not be case-sensitive
    githubRequestType : str = githubRequestType.lower()

    # Check if it is a valid type
    if githubRequestType != "core" and githubRequestType != "regular" and githubRequestType != "graphql":
        raise Exception("Invalid type! Only types of 'core','regular', and 'graphql' are allowed!")



    if githubRequestType == "regular":
        githubRequestType = "core"

    # Obtain response from GitHub API
    data : dict = _connectToGithubApi("https://api.github.com/rate_limit")

    requestData : dict = data["resources"][githubRequestType]

    print(
        f"""
Checking Rate Limit Type: {githubRequestType}
Request Limit: {requestData["limit"]}
Requests Used: {requestData["used"]}
Requests Remaining: {requestData["remaining"]}
Reset Time UNIX: {requestData["reset"]}
Reset Time: {datetime.fromtimestamp(requestData["reset"]).strftime('%Y-%m-%d %H:%M:%S')}
            """)

    # Returns remaining requests and time until reset
    return (requestData["remaining"],requestData["reset"])


def getGithubUserFollowers(username: str) -> int | None:
    '''
    Used for an accurate measurement of a GitHub account's followers, as it uses the API. Only should be used to check
    individual users follower count, rather than a group of users as it used one request per user. Uses
    _getMassGithubUserFollowers for groups of users.

    If None is returned, it is due to any of the following cases: The user changed their name, has no followers, or hid
     their follower count

    :param username: Username of the GitHub user
    :return:         Returns the follower count of the GitHub user.
    '''

    #Obtain response from GitHub API
    followerCount : dict = _connectToGithubApi(f"https://api.github.com/users/{username}")

    # Invalid username
    if not followerCount: return None

    # Return Followers
    return followerCount["followers"]


def scrapeGithubUserFollowers(username: str) -> int | None:
    '''
     Used for an estimated measurement of a GitHub account's followers, as it scrapes the data from the direct user page.
     Useful for making unlimited requests when API rate limit is used.

     If None is returned, it is due to any of the following cases: The user changed their name, has no followers, or hid
     their follower count

    :param username: Username of the GitHub user
    :return:         Returns the follower count of the GitHub user.
    '''
    try:

        # Request from the GitHub API regarding the username
        myRequest = urllib.request.Request(f"https://github.com/{username}",  headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    })

        # Add certification to prevent being blocked
        context = ssl.create_default_context(cafile=certifi.where())
        connect = urllib.request.urlopen(myRequest, context=context)

        # Obtain GitHub API response
        html : bytes = connect.read()

        # Decode and parse the follower count
        followerCount : str = html.decode('utf-8').split('<span class="text-bold color-fg-default">')[1].split('<')[0]

        # Check if the user has over a thousand followers and convert the string into a estimated number
        if "k" in followerCount:
            followerCount : float = float(followerCount[:-1]) * 1000


    except Exception as error:
        print(error)
        return None

    # Return Followers as int
    return int(followerCount)


def saveGithubRepository(githubType : str, saveFileName : str, repositoryLink : str) -> int:
    '''
    Used to save data from a single GitHub repository. Obtains all corresponding GitHub type data from the specified
    repository link. Saves all data in an individual JSON object in the "./data/evaluations/" folder with the saveFileName.
    Saves data such as repository information, GitHub type information, and body paragraphs. There is a maximum limit
    of 30,000 issues / issue comments from the GitHub API.

    GitHub Types:

    'issue': GitHub issues

    'comment': GitHub issue comments

    :param githubType: GitHub type of either 'issue' or 'comment'
    :param saveFileName: Name of the file to save all the repository data in. Do not use file type, as it will be .json.
    :param repositoryLink: The GitHub repository link to obtain the data from
    :return: Returns the number of issues / issue comments that was gathered
    '''

    # Turn type into lower case, to prevent case-sensitivity
    githubType : str = githubType.lower()

    # Open file
    writeFile = open(f"./data/evaluations/{saveFileName}.json", "a")

    # Split data to get repository owner and repository name
    splitString = repositoryLink.split("/")

    # Initialize variables to keep track of requested data
    tempArray : list[dict] | None = [{"tempKey" : None}]
    tempPage : int = 1

    #Initialize variable to keep track of issue count
    issueCount : int = 0

    # Check if the current JSON object request is empty or not. If empty, then all data is gathered from repository
    while tempArray:

        # Obtain response data based on GitHub type
        if githubType == "issue":
            tempArray = _connectToGithubApi(f"https://api.github.com/repos/{splitString[-2]}/{splitString[-1]}/issues?page={tempPage}&per_page=100&state=all")

        elif githubType == "comment":
            tempArray = _connectToGithubApi(
                f"https://api.github.com/repos/{splitString[-2]}/{splitString[-1]}/issues/comments?page={tempPage}&per_page=100&state=all")

        # If tempArray returned None, there is an error that occurred while getting data from the API
        if tempArray is None:

            # Check if rate limited and sleep if rate limited
            _sleepUntilRateLimit()

            # Retry page request
            if githubType == "issue":
                tempArray = _connectToGithubApi(
                    f"https://api.github.com/repos/{splitString[-2]}/{splitString[-1]}/issues?page={tempPage}&per_page=100&state=all")

            elif githubType == "comment":
                tempArray = _connectToGithubApi(
                    f"https://api.github.com/repos/{splitString[-2]}/{splitString[-1]}/issues/comments?page={tempPage}&per_page=100&state=all")

        # Iterate through each of the issues / issue comments and obtain wanted data
        for data in tempArray:

            # Obtain data based on the specified GitHub type
            if githubType == "issue" and "issues" in data["html_url"]:

                # Initialize dictionary to later be turned into a JSON object
                tempDict = dict()

                # Add response data into dictionary
                tempDict["type"] = "issue"
                tempDict["repositoryOwner"] = splitString[-2]
                tempDict["repositoryName"] = splitString[-1]
                tempDict["issueNumber"] = data["url"].split("/")[-1]
                tempDict["created"] = data["created_at"]
                tempDict["updated"] = data["updated_at"]
                tempDict["state"] = data["state"]
                tempDict["locked"] = data["locked"]
                tempDict["user"] = data["user"]["login"]
                tempDict["userFollowers"] = None

                #Check if data is empty before cleaning
                if not data["title"] or not data["body"]: continue

                #Clean title and body of issue of links, markdown, and code
                tempDict["title"] = utils.cleanText(data["title"])
                tempDict["body"] = utils.cleanText(data["body"])

                # Check if data is empty after cleaning
                # if not tempDict["title"] or not tempDict["body"]: continue

                # Add JSON file as a line to the specified save file
                writeFile.write(json.dumps(tempDict) + "\n")

                # Increment issue count
                issueCount += 1

            elif githubType == "comment" and "issuecomment" in data["html_url"] and "pull" not in data["html_url"]:

                # Initialize dictionary to later be turned into a JSON object
                tempDict = dict()

                # Add response data into dictionary
                tempDict["type"] = "issue comment"
                tempDict["repositoryOwner"] = splitString[-2]
                tempDict["repositoryName"] = splitString[-1]
                tempDict["issueNumber"] = data["issue_url"].split("/")[-1]
                tempDict["created"] = data["created_at"]
                tempDict["updated"] = data["updated_at"]
                tempDict["user"] = data["user"]["login"]
                tempDict["userFollowers"] = None

                # Check if body is empty before cleaning
                if not data["body"]: continue

                # Clean body of issue  comment of links, markdown, and code
                tempDict["body"] = utils.cleanText(data["body"])

                # Check if body is empty after cleaning
                # if not tempDict["body"]: continue

                # Add JSON file as a line to the specified save file
                writeFile.write(json.dumps(tempDict) + "\n")

                # Increment issue count
                issueCount += 1

        # Update GitHub API page iteration
        tempPage += 1

    print(f"Obtained {issueCount} {githubType}s \n")

    # Close the file
    writeFile.close()

    # Return the number of issues gathered
    return issueCount


def saveFileUserFollowers(fileName : str, specifyFilePath : bool = False) -> None:
    '''
    Used to add the follower count for every GitHub user in a .json file. Every JSON object needs to have the key of
    'user' in order to find the corresponding follower count. Function groups each user in a file into groups of 2000,
    then uses _getMassGithubUserFollowers function which uses GitHubs GraphQL API to request the batch of users. Finally,
    each individual user is added to the corresponding JSON object.

    :param fileName: JSON file name in "./data/evaluations/" without the .json extension
    :param specifyFilePath: Boolean for if the user wants to specify the file path of the read file. Use fileName parameter
                            as the file path location.
    :return: Edits the specified JSON file with GitHub follower counts if each user.
    '''

    # Handle possible user error
    if ".json" in fileName and not specifyFilePath:
        raise Exception("Only specify the file name without the '.json'!")


    if specifyFilePath:

        # Open specified file
        with open(fileName, 'r') as file:
            # read a list of lines into data
            data = file.readlines()
    else:

        # Open file based on file name to edit lines
        with open(f"./data/evaluations/{fileName}.json", 'r') as file:
            # read a list of lines into data
            data = file.readlines()

    # Successfully opened file and now adding users
    print("Adding follower count to users now")

    # Turn every user in lists of 2000
    userGroups : list[list] = utils.groupJsonKeys(data, ["user"])

    # Obtain mass follower count for each group of users
    fileUserFollowers : list = asyncio.run(setupMassGithubUserFollowerCalls(userGroups))

    # Individuality add each follower count to the corresponding JSON object
    for lineNumber, line in enumerate(data):
        tempDict : dict = json.loads(line)
        tempDict["userFollowers"] = fileUserFollowers[lineNumber]
        data[lineNumber] = json.dumps(tempDict) + "\n"


    # Write everything back into the file
    with open(f"./data/evaluations/{fileName}.json", 'w') as file:
        file.writelines(data)

    print("Done obtaining followers in the file")


def saveGithubRepositoryLinks(githubType : str, fileName : str, saveFileName: str, specifyFilePath  : bool = False) -> None:
    '''
    Used to save mass gathered issues / issue comments from each repository in a .txt file into a single JSON file.
    The .txt file must be in the "./data/downloads/" and each line should correspond to a GitHub repository link.
    Each JSON object includes repository information, GitHub type information, body paragraphs and user follower count.
    Saves all data in an individual JSON object in the "./data/evaluations/" folder with the saveFileName.


    Valid types to obtain is: 'issue' or 'comment'

    GitHub Types:

    'issue': GitHub issues

    'comment': GitHub issue comments


    :param githubType: GitHub type of either 'issue' or 'comment'
    :param fileName: File name of the .txt file, which contains GitHub repository links. Do not include .txt extension
    :param saveFileName: Name of the JSON save file in "./data/evaluations/"
    :param specifyFilePath: Boolean for if the user wants to specify the file path of the read file. Use fileName parameter
                            as the file path location.
    :return: Creates JSON file containing all the needed information of the requested type
    '''

    # Initialize variable to keep track of data obtained
    responseCount : int = 0

    # Handle possible user error
    if ".txt" in fileName and not specifyFilePath:
        raise Exception("Only specify the file name without the '.txt'!")


    if githubType.lower() != "issue" and githubType.lower() != "comment":
        raise Exception("Invalid type. Valid types are 'issue' or 'comment'")

    if specifyFilePath:
        # Open specified file containing GitHub repository links
        githubLinkFile = open(fileName, "r")
    else:
        # Open file containing GitHub repository links
        githubLinkFile = open(f"./data/downloads/{fileName}.txt", "r")

    # Iterate through each of the GitHub repository links
    for link in githubLinkFile:
        print(f"Checking {link.strip()}")

        # Save all specified GitHub type data to JSON file and update repose count
        responseCount += saveGithubRepository(githubType, saveFileName, link.strip())


    print(f"Retrieved {responseCount} {githubType}s")

    # Add the follower count to each of the users in the file
    saveFileUserFollowers(saveFileName)

    # Close file
    githubLinkFile.close()


async def setupMassGithubUserFollowerCalls(userGroups : list[list[str]]) -> list[int]:
    '''
    Sets up the mass user follower calls for asyncio. Function calls requests for obtaining follower counts for 2000
    users at a time using GraphQL GitHub requests.

    :param userGroups: List of many 2000 grouped GitHub users, if applicable.
    :return: Returns the follower count of all the users in the userGroup list as a single list
    '''

    # Set up task list
    tasks : list = [_getMassGithubUserFollowers(_) for _ in userGroups]

    # Initialize follower count list
    results : list = []

    # Queue all the requests using asyncio
    results += await asyncio.gather(*tasks)

    #Return merged list of all the results
    return sum(results, [])



def _sleepUntilRateLimit(githubRequestType : str = "core") -> None:
    '''
    Checks the rate limit regarding the GitHub request type and sleeps until the rate limit time resets.


    GitHub Request Type: Regular(Core) Requests and GraphQL Requests

    'regular'/'core': Requests regarding data from repositories or individual follower counts

    'graphql': Requests regarding data of mass grouped follower counts

    :param githubRequestType: GitHub request type of 'regular', 'core, or 'graphql'
    :return: None
    '''

    # Get rate limit data containing (remaining requests, time till rate limit reset)
    rateLimitData : (int, datetime) = getGithubRateLimit(githubRequestType)

    # Obtain the current time
    currentTime : time = time.time()

    # Determine the difference between two times
    sleepTime : float = rateLimitData[1] - currentTime


    #Check if remaining requests and if current time is before the rate limit time
    if rateLimitData[0] == 0 and sleepTime >= 0:

        #Rate limited message
        print(f"Rate limited, waiting {datetime.fromtimestamp(sleepTime).strftime('%M:%S')} minutes")

        #Sleep until not rate limited
        time.sleep(sleepTime)

        #Double check that it is not rate limited still
        _sleepUntilRateLimit()
    else:
        print("Not rate limited!")


def _connectToGithubApi(apiUrl : str, encodedData : bytes = None) -> dict | list[dict] | None:
    '''
    Obtains the response of the specified GitHub API link and returns all API data in a dictionary or list with multiple
    dictionaries. Used for obtaining data of repositories and user followers. A GitHub API key is recommended for a
    large number of requests, as unauthorized requests are limited to 60 per hour compared to 5000 per hour. There are
    different types of GitHub requests 'core' and 'graphql'. Core requests are used for obtaining repository data and
    single user follower counts. GraphQL requests are used to obtain mass grouped user follower count.

    To add a GitHub API key, add it to GITHUB_API_KEY in config.py as a string.

    If None is returned, there has been an error with the request.

    :param apiUrl: The GitHub API url to obtain a response
    :param encodedData: Used for mass user grouped follower counts, JSON object that is utf-8 encoded
    :return: Returns API response as a dictionary. None is returned if an error occurred.
    '''

    # Check if there is a GitHub API key currently added
    if config.GITHUB_API_KEY is None:
        headerData = {}
        print("There is no GitHub API key provided in config.py! Checking based on unauthenticated API requests.")

    else:

        # Set Request Headers
        headerData = {
            "Authorization": "Bearer " + config.GITHUB_API_KEY,
            "X-GitHub-Api-Version": "2022-11-28"
        }

    # Try to do the request
    try:
        # Request from the GitHub API regarding the username
        myRequest = urllib.request.Request(apiUrl, headers=headerData, data=encodedData)

        # Add certification to prevent being blocked
        context = ssl.create_default_context(cafile=certifi.where())
        connect = urllib.request.urlopen(myRequest, context=context)

        # Obtain GitHub API response
        html = connect.read()

        # Make API response data easily readable by turning it into a dictionary or list with many dictionaries
        return json.loads(html)

    # Catch errors
    except urllib.error.HTTPError as error:

        #GitHub repository is not pageable anymore
        if error.code == 422 or error.code == 404:
            return dict()

        # Print errors
        print(apiUrl)
        print(error)

        # Return None
        return None

    # Handle unknown errors
    except Exception as error:
        print(error)
        print("Retrying")
        return _connectToGithubApi(apiUrl, encodedData)


async def _getMassGithubUserFollowers(userGroups : list[str]) -> list[int] | None:
    '''
    Accepts a list of up to 2000 GitHub users, then uses a single GraphQL GitHub request to obtain the follower count
    for each one of them.

    :param userGroups: A list of up to 2000 GitHub users
    :return: Returns a single list, corresponding to the follower count of each user in userGroups
    '''

    # Check if there are more than 2000 users in a list
    if len(userGroups) > 2000:
        raise Exception("Too many users in list! There is a maximum of 2000 users per list!")

    # List containing the follower count of each user
    tempUserFollowers : list = []

    # Set up GraphQL query data
    tempGraphqlQuery : str = "query {"

    # Add each GitHub user to the GraphQL query
    for number, user in enumerate(userGroups, start=1):
        tempGraphqlQuery += f'''
user{number}: user(login: "''' + user + '''") {
  login
    followers {
     totalCount
    }
  }'''

    # Set up end of the GraphQL data
    queryData : dict = {'query': tempGraphqlQuery + "}"}

    # Limit to request 5 URLs at a time
    async with asyncio.Semaphore(5):

        # Request the follower count of each user in userGroups by encoding the GraphQL query in utf-8
        requestData = _connectToGithubApi("https://api.github.com/graphql",json.dumps(queryData).encode('utf-8'))

    # Possibly rate limited if no request data
    if not requestData:

        # Check rate limited
        print("Checking rate limit:")
        _sleepUntilRateLimit("graphql")

        # Retry obtaining follower count
        print("Did not receive data retrying")
        return await _getMassGithubUserFollowers(userGroups)


    #Iterate through request of user follower count
    for userNumber in range(1, len(requestData["data"]) + 1):

        # Obtain user follower count
        userData = requestData["data"]["user" + str(userNumber)]

        #Invalid user
        if not userData:
            tempUserFollowers.append(None)
            continue

        #Add follower count
        tempUserFollowers.append(userData["followers"]["totalCount"])

    # Return a single list, corresponding to the follower count of each user in userGroups
    return tempUserFollowers
