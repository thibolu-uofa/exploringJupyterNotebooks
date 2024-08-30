"""
File Summary:

Executes the console application for the user to have access the primary functions created. Should be the first file ran
in the program.
"""

# Imports

# Local
import app


def main() -> None:
    '''
    Calls the main application to have access to the primary functions.

    :return: None
    '''

    # Call the main app
    app.mainMenu()


# Prevents being used as a module
if __name__ == "__main__":
    main()