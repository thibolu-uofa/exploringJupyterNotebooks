"""This module analyzes the cyclomatic complexity of source code of python files and 
Jupyter notebooks,also returning, for each file, the number of functions and their 
respective names. 

If the average cyclomatic complexity is zero, it to adjustments to the source code
for the library to return a more correct result."""

from lizard import analyze_file
import os
import tempfile
from .notebook_utilities import read_notebook


def add_function_to_fix_complexity(source_code, path_name):

    # fixing zero complexity returned by Lizard library:
    source_code = f"def main():\n" + source_code
    new_complexity_results = analyze_file.analyze_source_code(path_name, source_code)

    return new_complexity_results



def get_function_and_cyclomatic_complexity(source_code: str, path_name: str):
    
    complexity_results = analyze_file.analyze_source_code(path_name, source_code)
    function_results = []
      
    if complexity_results:

        if complexity_results.average_cyclomatic_complexity == 0:
            # fixing zero complexity returned by Lizard library:
            complexity_results = add_function_to_fix_complexity(source_code,path_name)
        
        avg_cyclomatic_complexity_file = complexity_results.average_cyclomatic_complexity
        # getting the result for each function detected by Lizard library:
        for function in complexity_results.function_list:
            
            function_result = {"filename": str(path_name),
                                "function_name": function.name,
                                "function_cyclomatic_complexity": function.cyclomatic_complexity
                                }
            
            function_results.append(function_result)
        
    return function_results, avg_cyclomatic_complexity_file

def complexity_notebook(filepath):
    
    notebook = read_notebook(filepath)
    code_cells = [cell['source'] for cell in notebook.cells if cell.cell_type == 'code']
    # getting the code content of the notebook cells:
    combined_code = '\n'.join(code_cells)

    # creating a temp file to parse the notebooks with lizard:
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
        temp_file.write(combined_code.encode())
        temp_file_path = temp_file.name

    function_results = []
    complexity_results = analyze_file(temp_file_path)

    # fixing zero complexity returned by Lizard library:
    if complexity_results.average_cyclomatic_complexity == 0:
    
        combined_code = "def main():\n" + combined_code

        # creating a temp file to parse the notebooks with lizard:
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(combined_code.encode())
            temp_file_path = temp_file.name


        complexity_results = analyze_file(temp_file_path)
        
    
    avg_cyclomatic_complexity_file = complexity_results.average_cyclomatic_complexity

    for function in complexity_results.function_list:
        # getting the result for each function detected by Lizard library:

        function_result = {"filename": str(filepath),
                            "function_name": function.name,
                            "function_cyclomatic_complexity": function.cyclomatic_complexity
                            }
        
        function_results.append(function_result)

    os.remove(temp_file_path)
        
    return function_results, avg_cyclomatic_complexity_file


def get_function_and_cyclomatic_complexity(source_code: str, path_name: str):
    
    complexity_results = analyze_file.analyze_source_code(path_name, source_code)
    function_results = []

    if complexity_results:
        # fixing zero complexity returned by Lizard library:
        if complexity_results.average_cyclomatic_complexity == 0:
        
            complexity_results = add_function_to_fix_complexity(source_code,path_name)
            
        
        avg_cyclomatic_complexity_file = complexity_results.average_cyclomatic_complexity

        for function in complexity_results.function_list:
        # getting the result for each function detected by Lizard library:
            
            function_result = {"filename": str(path_name),
                                "function_name": function.name,
                                "function_cyclomatic_complexity": function.cyclomatic_complexity
                                }
            
            function_results.append(function_result)
            
        
    return function_results, avg_cyclomatic_complexity_file