"""Class to analyze the complexity of Python files and Jupyter notebooks. 
It gathers metrics such as lines of code (LOC), number of comment lines, number of
 functions, cyclomatic complexity, and number of classes for each file
 belonging to the dataset splits."""

import ast
from IPython.core import inputtransformer2
import subprocess
import json
import re

from .notebook_utilities import get_code_and_comment_lines_notebook, get_markdown_line_count
from .complexity import get_function_and_cyclomatic_complexity, complexity_notebook


class FileComplexity:

    def __init__(self, filepath: str):

        self.source_code = None
        self.filepath = filepath
        self.file_type = self.get_filetype()
        self.num_comment_lines = None
        self.markdown_lines_count = None
        self.loc = None
        self.num_functions = None
        self.functions = []
        self.average_cyclomatic_complexity = None
        self.avg_scc_cylo = None
        self.num_classes = 0
        self.success_counting_classes = False
        self.errors = None

        try:
            self.get_file_info()
            self.get_complexity_and_functions_info()
            self.count_classes()

        except Exception as e:
            print(f"e2: {e}")
            self.errors = str(e)


    def get_filetype(self):
        file_type = self.filepath.split(".")[-1]

        if file_type == 'ipynb':
            file_type = 'notebook'

        elif file_type == 'py':
            file_type = 'python'


        return file_type



    def get_file_info(self):

        if self.file_type == 'notebook':
            # getting the source code content, loc and comment lines from
            # a Jupyter notebook:
            self.source_code, self.loc ,self.num_comment_lines = get_code_and_comment_lines_notebook(self.filepath)
            self.markdown_lines_count = get_markdown_line_count(self.filepath)
        
        else:
            # parsing other filetypes:
            self.source_code = open(self.filepath, "r", encoding="utf-8").read()            
            scc_results = self.analyze_file_with_scc()
            
            self.loc = scc_results[0]['Code']
            self.num_comment_lines = scc_results[0]['Comment']
            self.markdown_lines_count = 0


    def get_complexity_and_functions_info(self):
        if self.file_type == 'notebook':
            # calculating function and cyclomatic complexity
            # for notebook filetypes:
            function_info, file_complexity = complexity_notebook(self.filepath)
            
        else:
            function_info, file_complexity = get_function_and_cyclomatic_complexity(self.source_code,
                                                                                    self.filepath
                                                                                    )
        # counting the number of functions in the file:
        self.num_functions = len(function_info)

        for function in function_info:
            self.functions.append(function["function_name"])

        self.average_cyclomatic_complexity = file_complexity

    def count_classes(self):
        """Tries to count classes with ast parsing.
        In case the ast parse fails, regex
        is appied to find classes definitions."""
        try:

            source = self.source_code
            code_ast = ast.parse(source)
            count = 0

            for node in ast.walk(code_ast):
                if type(node) == ast.ClassDef:
                    count += 1

            self.success_counting_classes = True
            self.num_classes = count
                    
        except Exception as e:
            

            self.success_counting_classes = False
        
            self.count_classes = 0
            self.find_classes_regex(source)


    def find_classes_regex(self, source_code):
        """Find classes with regex"""
        
        try:
            pattern = r'\bclass\s+\w+\s*:\s*'
            
            self.num_classes = len(re.findall(pattern, source_code))
            self.success_counting_classes = True

        except Exception as e:
            #print(f"e4: {e}")
            self.success_counting_classes = False
            self.num_classes = 0
            self.errors = str(e)

    def analyze_file_with_scc(self):
        """Runs the scc library for a given file to extract loc information"""
        try:
            # run the `scc` command for the specified file and capture the output
            result = subprocess.run(['scc', '--format', 'json', self.filepath], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True, 
                                    check=True)
            
            analysis_result = json.loads(result.stdout)
            return analysis_result

        except subprocess.CalledProcessError as e:
            print(f"Error running scc: {e.stderr}")
            self.errors= str(e)
            return None

    def to_dict(self):
        """Representing a file through its attributes"""
        
        return {
            "file_type": self.file_type,
            "num_comment_lines": self.num_comment_lines,
            "markdown_lines_count": self.markdown_lines_count,
            "loc": self.loc,
            "num_functions": self.num_functions,
            "functions": self.functions,
            "average_cyclomatic_complexity": self.average_cyclomatic_complexity,
            "num_classes": self.num_classes,
            "success_counting_classes": self.success_counting_classes,
            "errors": self.errors
        }


                                                        
        
    
