"""
File Summary:

Class is used to analyze data to get data such as ROC curves, AUC score, precision, recall, F1 score are more.
Accurate data is a required parameter to analyze conditions.
"""

#Imports

# Local
from utils import utils

# Installed
import matplotlib.pyplot as plt

class analyzeData:


    def __init__(self, testName : str, evaluatedData : list, *, accurateData : list[str] = None):
        '''
        Initialization of variables, necessary to use keyword arguments

        :param testName: Name of the test, usually the evaluating data AI model
        :param evaluatedData: Evaluating data containing a threshold of 0.0-1.0 or 'y' / 'n'
        :param accurateData: Accurate data containing 'y' / 'n', optional argument but needed to calculate conditions
        :param sentenceData: Optional argument used for saving toxicity data in an Excel file
        '''

        # Constructor Variables
        self.testName : str = testName
        self.evaluatedData : list = evaluatedData
        self.accurateData : list[str] = accurateData


        # Global variables

        self.truePositives : int = 0
        self.falseNegatives : int = 0

        self.trueNegatives : int = 0
        self.falsePositives : int = 0

        self.toxicityCount : int = 0




    def getPrecisionScore(self) -> float:
        return (self.truePositives) / (self.truePositives + self.falsePositives)

    def getRecallScore(self) -> float:
        return (self.truePositives) / (self.truePositives + self.falseNegatives)

    def getF1Score(self) -> float:
        return 2 * (self.getPrecisionScore() * self.getRecallScore()) / (self.getPrecisionScore() + self.getRecallScore())

    def getSpecificityScore(self) -> float:
        return (self.trueNegatives) / (self.trueNegatives + self.falsePositives)

    def getFalsePositiveRate(self) -> float:
        return 1 - self.getSpecificityScore()

    def getRocData(self, dataPoints: int = 100) -> list[list]:
        '''
        Obtains ROC data for the specified number of data points in 0.0 - 1.0. ROC data obtained is threshold, FPR,
        and TPR.

        :param dataPoints: Number of data points in the range 0.0 - 1.0
        :return: Returns a list of [ROC data, FPR list, TPR list]
        '''

        # To contain a uniform number of data points
        if not dataPoints % 10 == 0:
            raise Exception("Data points must be a factor of 10")

        # ROC data contains multiple lists containing [Threshold, FPR, TPR]
        rocData = []

        # Initialize lists of FPR and TPR
        fprData = []
        tprData = []

        # Iterate through each interval of 0.0 - 1.0
        for threshold in range(dataPoints, -1, -1):

            # Calculate the condition value
            self.calculateConditions(threshold / dataPoints)

            # Add calculated values to each corresponding list
            rocData.append([threshold / dataPoints, self.getFalsePositiveRate(), self.getRecallScore()])

            fprData.append(self.getFalsePositiveRate())
            tprData.append(self.getRecallScore())

        # Return all lists as one list
        return [rocData, fprData, tprData]

    def getAuc(self, dataPoints: int = 100) -> float:

        # To contain a uniform number of data points
        if not dataPoints % 10 == 0: raise Exception("Data points must be a factor of 10")

        rocData, xData, yData = self.getRocData(dataPoints)

        # Return AUC
        return utils.integrate(xData, yData)

    def getValidAnalyzedCount(self) -> int:
        '''
        Obtains the number of toxicity data actually analyzed

        :return: Returns the count of toxicity data analyzed
        '''

        tempCount : int = 0

        # Iterate through each evaluation
        for toxicityData in self.evaluatedData:

            # Check if data is invalid
            if not toxicityData: continue

            tempCount += 1

        print(f"There is {tempCount} valid PerspectiveAPI analyzed responses in the file")
        return tempCount


    def getToxicityCount(self, threshold : float = 0.5) -> int:
        '''
        Gets the number of toxic sentences based on the specified threshold, where it returns a count of
        any evaluation higher than the threshold

        :param threshold: Range of 0.00 - 1.00, default is 0.5
        :return: Returns the count of toxic sentences higher than the threshold
        '''

        # Reset the count
        self.setToxicityCount(0)


        # Iterate through each evaluation
        for toxicityData in self.evaluatedData:

            # Check if data is invalid
            if not toxicityData: continue

            # Check if data meets the threshold
            if toxicityData >= threshold:

                # Update toxicity count variable
                self.toxicityCount += 1

        # Print the toxicity count
        print(f"Toxicity Count for the threshold of {threshold} is {self.toxicityCount}")
        return self.toxicityCount

    def setToxicityCount(self, number : int) -> None:
        self.toxicityCount = number



    def resetAnalysisData(self) -> None:
        '''
        Resets all conditions such as true positives, false negatives, true negatives, and false positives.

        :return: None
        '''

        self.truePositives = 0
        self.falseNegatives = 0
        self.trueNegatives = 0
        self.falsePositives = 0




    def calculateConditions(self, threshold : float = 0.5) -> list[int]:
        '''
        Compares accurate and evaluated data and identifies the conditions. Conditions are categorized as true positives,
        false negatives, true negatives, and false positives. Each individual condition helps calculate variables such
        as precision, recall, F1 score and more.


        :param threshold: Minimum threshold the evaluated data must be in order to be considered positive
        :return: Returns a list of each condition count
        '''

        # Check if there is any accurate data to compare with
        if not self.accurateData:
            raise Exception("There is no data to evaluate. As there needs to be an accurate set of data to compare.")

        # Check if accurate data is in 'y' / 'n'
        if len(self.accurateData[0]) != 1:
            raise Exception("Accurate data must be 'y' / 'n'")

        # Reset data
        self.resetAnalysisData()

        # Check if evaluation data is numbers or 'y' / 'n'
        if isinstance(self.evaluatedData[0], float):

            # Iterate through each accurate and evaluated value to compare each other
            for accurateValue, evaluatedValue in zip(self.accurateData, self.evaluatedData):

                # Identify condition
                if accurateValue == 'y' and evaluatedValue >= threshold:
                    self.truePositives += 1
                elif accurateValue == 'n' and evaluatedValue < threshold:
                    self.trueNegatives += 1
                elif accurateValue == 'n' and evaluatedValue >= threshold:
                    self.falsePositives += 1
                elif accurateValue == 'y' and evaluatedValue < threshold:
                    self.falseNegatives += 1

        elif isinstance(self.evaluatedData[0], str):

            # Handle potential errors
            if len(self.evaluatedData[0]) != 1: raise Exception("Evaluation data must be 'y' / 'n'")

            # Iterate through each accurate and evaluated value to compare each other
            for accurateValue, evaluatedValue in zip(self.accurateData, self.evaluatedData):

                # Identify condition
                if accurateValue == evaluatedValue == 'y':
                    self.truePositives += 1
                elif accurateValue == evaluatedValue == 'n':
                    self.trueNegatives += 1
                elif accurateValue == 'n' and evaluatedValue == 'y':
                    self.falsePositives += 1
                elif accurateValue == 'y' and evaluatedValue == 'n':
                    self.falseNegatives += 1

        else:
            raise Exception("Invalid evaluation data type. Must be either a float or 'y'/'n'")


        # Return all conditions
        return [self.truePositives, self.trueNegatives, self.falsePositives, self.falseNegatives]


    def viewRocCurve(self, dataPoints : int = 100) -> None:
        '''
        Prints a table of all the ROC data and displays the ROC curve using matplotlib

        :param dataPoints: Number of data points in the range 0.0 - 1.0
        :return: None
        '''

        # Obtain ROC Data
        rocData, fprData, tprData = self.getRocData(dataPoints)

        # Print a table of the data
        print(f" {'_ ' * 23}")

        # Print labels
        print(f"| {'Threshold':^11} | {'FPR':<20} | {'TPR':<6} |")

        # Print data
        for data in rocData:
            print(f"| {data[0]:<11} | {data[1]:<20} | {data[2]:<6} |")

        # End of table
        print(f" {'‾ ' * 23}")

        # Display ROC curve

        plt.figure()

        # Plot points
        plt.plot(fprData, tprData, label=f"AOC: {round(utils.integrate(fprData, tprData), 3)}")
        plt.plot([0, 1], [0, 1], 'k--', label='No Skill')

        # Graph scale
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])

        # Graph labels
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')

        # Graph title
        plt.title(f"ROC Curve: Human Evaluated Data vs {self.testName}")

        plt.legend()
        plt.show()







    def __str__(self) -> str:
        '''
        Returns all condition data for the object
        :return: Returns condition data
        '''
        self.calculateConditions()
        return f"""
Comparison: Human Evaluated Data vs {self.testName}

Data:
True Positives: {self.truePositives}
False Positives: {self.falsePositives}
True Negatives: {self.trueNegatives}
False Negatives: {self.falseNegatives}

Scores:
Precision Score: {self.getPrecisionScore()}
Recall Score: {self.getRecallScore()}
F1 Score: {self.getF1Score()}
"""
