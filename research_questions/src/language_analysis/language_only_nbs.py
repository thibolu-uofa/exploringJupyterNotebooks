"""Script for getting the language of notebooks. When the language is not 
available in the Jupyter notebook metadata, it is guessed using guesslang 
library. 
To run this script, activate the environment where you have installed
the dependencies of requirements_lang_info.txt

This script runs fast, in some minutes."""
from pathlib import Path
import nbformat
import time
import json
from guesslang import Guess

from research_questions.configs.configs import Configs

config = Configs()


def get_code_lines(notebook: Path) -> str:
    """Extracts the content of only the code cells of a notebook"""

    source_code = []
    code_cells = [c["source"]
                  for c in notebook['cells'] if c['cell_type'] == 'code']

    if not code_cells:
        return source_code

    source_code = '\n'.join(code_cells)

    return source_code


def get_language_info(ipynb_path: Path) -> dict:

    lang_info = None
    try:
        notebook = nbformat.read(ipynb_path, as_version=nbformat.NO_CONVERT)

    except:
        print(f"[{time.time()}] Error parsing notebook at: {str(ipynb_path)}")
    try:
        lang_info = notebook["metadata"]["language_info"]
    except:
        lang_info = {"name": "unknown", "version": "unknown"}

    return lang_info


def get_and_guess_language_info(ipynb_path: Path) -> dict:
    """Gathers the language info from the metadata of the notebook,
    when available, or try to guess its language"""

    notebook = None
    try:
        notebook = nbformat.read(ipynb_path, as_version=nbformat.NO_CONVERT)

        num_changes, notebook = nbformat.validator.normalize(
            notebook, relax_add_props=True, strip_invalid_metadata=True)

        nbformat.validate(notebook)

    except Exception as e:
        print(f"[{time.time()}] Error parsing notebook at: {str(ipynb_path)}")

        return {"name": "unknown", "version": "unknown", "reason": "parse_fail"}

    try:

        if "language_info" in notebook["metadata"]:
            assert len(notebook["metadata"]["language_info"]["name"]) > 0
            lang_info = notebook["metadata"]["language_info"]
            lang_info["reason"] = "metadata_language_info"
            return lang_info
        else:
            assert len(notebook["metadata"]["kernelspec"]["name"]) > 0
            lang_info = notebook["metadata"]["kernelspec"]
            lang_info["reason"] = "metadata_kernelspec"
            return lang_info
    except:
        try:
            guesser = Guess()
            source_code = get_code_lines(notebook)
            lang_name = None

            if source_code:
                lang_name = guesser.language_name(source_code)

                assert lang_name != None
                if lang_name == 'Python' or 'python':

                    return {"name": lang_name, "version": "unknown", "reason": "guess"}
                else:
                    return {"name": 'Others', "version": "unknown", "reason": "guess", "guessed_name": lang_name}
            else:
                return {"name": "markdown", "version": "unknown", "reason": "no_code"}
        except:
            return {"name": "unknown", "version": "unknown", "reason": "guess_fail"}

    return {"name": "unknown", "version": "unknown", "reason": "unknown"}


def format_github_repo_url(notebook_path: Path) -> str:

    repo_url_info = str(notebook_path).split("_____")
    repo_autor = repo_url_info[0].split("/")[-1]
    repo_title = repo_url_info[-1].split("/")[0]

    repo_url = "https://github.com/" + repo_autor + "/" + repo_title

    return repo_url


def format_github_notebook_url(notebook_path: Path) -> str:

    notebook_url = str(notebook_path).split("latest/")[-1]
    notebook_url = notebook_url.replace("_____", "/")

    return notebook_url


def generate_lang_info_from_local_nbs(path: Path) -> dict:

    total_notebooks = len(path)
    processed_count = 0

    all_notebooks_lang_info = {}

    for notebook_path in path:

        lang_info = get_and_guess_language_info(notebook_path)

        formatted_repo_url = str(format_github_repo_url(notebook_path))
        lang_info["repo_url"] = formatted_repo_url

        formatted_notebook_path = str(
            format_github_notebook_url(notebook_path))

        all_notebooks_lang_info[formatted_notebook_path] = lang_info
        processed_count += 1
        print(f"{processed_count} processed notebooks of {total_notebooks}")

    return all_notebooks_lang_info


if __name__ == "__main__":

    # getting path from configs.json:
    complete_directory_path = config.path_active_SE_repos
    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path:", full_directory_path)

    notebook_paths = list(full_directory_path.glob('**/*.ipynb'))

    lang_info = generate_lang_info_from_local_nbs(notebook_paths)
    folder = Path(Path.cwd(), "research_questions", "src",
                  "language_analysis", "data_only_notebooks")
    result_filepath = folder
    folder.mkdir(exist_ok=True)

    # json with th language info extracted or guessed:
    with open(Path(result_filepath,
                   'language_info_SE_purposes_repos.json'), 'w') as f:
        json.dump(lang_info, f, indent=4)

    complete_directory_path = config.path_active_non_SE_repos
    full_directory_path = Path(complete_directory_path)
    print("Full Directory Path:", full_directory_path)

    notebook_paths = list(full_directory_path.glob('**/*.ipynb'))

    lang_info = generate_lang_info_from_local_nbs(notebook_paths)
    # json with th language info extracted or guessed:
    with open(Path(result_filepath,
                   'language_info_non_SE_purposes_repos.json'), 'w') as f:
        json.dump(lang_info, f, indent=4)
