import nbformat


def read_notebook(filepath):
    try:
        with open(filepath, "r") as f:
            notebook = nbformat.read(f, as_version=nbformat.NO_CONVERT)
        return notebook
    except Exception as e:
        print(f"e1: {e}")

def get_code_and_comment_lines_notebook(filepath):

    notebook = read_notebook(filepath)

    code_cells = []
    if "worksheets" in notebook:
        for n in notebook["worksheets"]:
            code_cells += [c for c in n["cells"] if c["cell_type"] == "code"]
    else:
        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]

    source_code = []
    code_line_count = 0
    comment_line_count = 0

    for c in code_cells:
        if "source" in c:
            cell_source = "".join(c["source"])
        elif "input" in c:
            cell_source = "".join(c["input"])
        else:
            assert 1 == 0

        source_code.append(cell_source)
        lines = cell_source.split('\n')
        #
        
        # counting comment lines in this cell
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("#") or stripped_line.startswith('"""'):
                comment_line_count += 1
            else:
                if stripped_line:
                    code_line_count += 1
        
    source_code = "\n".join(source_code)

    return source_code, code_line_count, comment_line_count


def get_markdown_line_count(filepath):

    notebook = read_notebook(filepath)

    markdown_cells = []
    if "worksheets" in notebook:
        for n in notebook["worksheets"]:
            markdown_cells += [c for c in n["cells"] if c["cell_type"] == "markdown"]
    else:
        markdown_cells = [c for c in notebook["cells"] if c["cell_type"] == "markdown"]

    
    markdown_line_count = 0

    for c in markdown_cells:
        if "source" in c:
            cell_source = "".join(c["source"])
        elif "input" in c:
            cell_source = "".join(c["input"])
        else:
            assert 1 == 0
        
        lines = cell_source.split('\n')
        markdown_line_count += len(lines)  # Count lines in this cell

    return markdown_line_count