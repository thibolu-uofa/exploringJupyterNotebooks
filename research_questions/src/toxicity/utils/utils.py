"""
File Summary:
Module contains unrelated functions to all modules, but can be generalized for any module use. Module contains functions
such as obtaining nested dictionary values, area under curve, and grouping a list into any specified size of list.

"""
import tkinter
# Imports

# Built-in
from tkinter import filedialog
import json
import re


# Installed
import numpy as np

def getMenuNumber(interfaceRange : int) -> int:
    '''
    Obtains the user input between one and the specified range.
    :param interfaceRange: Specified range of the menu
    :return: Returns the input string as a number within the bounds
    '''

    # Initialize user input variable
    userInput: str = ""

    # Check if the user input is a digit
    while not userInput.isdigit():
        userInput = input("Enter the above numbers: \n")

        # Check if it is a digit while being in the specified range
        if userInput.isdigit() and (int(userInput) > interfaceRange or int(userInput) <= 0):
            userInput = ""
            continue

    # Return the number in the range
    return int(userInput)

def getThresholdNumber() -> float:

    # Initialize user input variable
    userInput: float

    while True:
        try:
            userInput = float(input("Enter a threshold number (range between 0-1): \n"))

            if userInput < 0 or userInput > 1: continue

            break
        except:
            pass

    return userInput

def getUserSelection(allowedSelection : list) -> str:
    '''
    Allows the user to select a single element in a list

    :param allowedSelection: List of allowed selection elements
    :return: Returns the element the user selected
    '''

    # Initialize user input variable
    userInput: str = ""

    while userInput not in allowedSelection:
        userInput = input("Enter the above selection: \n")

    return userInput

def getUserListSelection(allowedSelection : list) -> list:
    '''
    Allows the user to select multiple elements of a list

    :param allowedSelection: List of allowed selection elements
    :return: Returns all the elements the user selected
    '''
    # Initialize user input variable
    userInput: str | list | None = None

    while userInput not in allowedSelection:
        userInput : str = input("Enter the above selection using ',' to split labels: \n")

        if "all" in userInput: return allowedSelection

        userInput : list = userInput.replace(' ', '').split(',')

        for selections in userInput:
            if selections not in allowedSelection:
                print(f"{selections} is not valid in {['all'] + allowedSelection}!")
                userInput = getUserListSelection(allowedSelection)
                break

        return userInput


def getFilePath() -> str:
    '''
    Allows the user to select a file in file explorer

    :return: File path of selected file
    '''
    tkinter.Tk().withdraw()
    return filedialog.askopenfilename()


def getNestedDictionaryValue(dictionary : dict, key : str):
    '''
    Each nested dictionary key needs to be separated by '>' in order to indicate it being nested

    :param key: Dictionary key, use '>' to indicate nested dictionary keys
    :return: Returns key value
    '''

    if '>' not in key:
        raise Exception("Make sure you use '>' to indicate nested keys!")

    # Obtain all nested keys
    splitKeys : list = key.split(">")


    tempValue = dictionary

    for key in splitKeys:
        tempValue = tempValue.get(key, {})

        if isinstance(tempValue, dict): continue

        return tempValue

def cleanText(text : str) -> str:
    '''
    Used to clean data by removing new lines, links, code blocks, Markdown, and utf-8 text.

    :param text: Text to clean
    :return: Returns a text with specified attributes removed
    '''

    #Remove new lines
    text = text.replace("\n", '')
    text = text.replace("\r", "")

    #Remove Websites
    text = re.sub(r'http\S+', '', text)

    #Remove Code Blocks
    text = re.sub(r'```.*?```', '', text)

    #Remove Markdown Text
    text = text.replace("`", "")
    text = text.replace("*", "")

    # Remove utf-8 text
    text = text.encode('ascii', errors='ignore').decode('ascii')

    # Return cleaned text
    return text.strip()

def integrate( x : list, y : list) -> float:
    '''
    Uses trapezoidal rule integration from numpy. Function used to calculate the area under the curve.

    :param x: List of x values
    :param y: List of y values
    :return:  Returns the area under the curve
    '''

    #Trapezoidal rule integration
    area = np.trapz(y=y, x=x)

    #Return area
    return area


def groupJsonKeys(fileData : list[str], keys : list, elementsPerList : int = 2000) -> list[list]:
    '''
    Groups a list of JSON object keys from a file into separate lists of 2000. Function is used to help gather
    mass follower counts of GitHub users. Nested JSON object keys are currently not supported

    :param fileData: JSON file data
    :param keys: Keys to put in each individual list, in order
    :param elementsPerList: Number of elements per list
    :return: Returns a list containing multiple grouped lists of 2000 GitHub usernames, if applicable
    '''

    # Initialize groups, each list contains a maximum of 2000 users
    groups : list[list] = [[]]

    # Iterate through each JSON object to request follower count in batches
    for lineNumber,line in enumerate(fileData, start=1):

        # Make new list if 2000 users are in a list
        if lineNumber % (elementsPerList / len(keys)) == 0:
            groups.append([])

        # Read JSON object into dictionary
        loadedDict : dict = json.loads(line)

        # Iterate through though each key and add it to list
        for key in keys:
            groups[-1].append(loadedDict[key])


    # Return a list of 2000 users grouped
    return groups
