"""Set global configurations of the project. Be aware that dates shouldn't be
modified."""
import json
from pathlib import Path
from dotenv import load_dotenv
import os


class Configs:
    def __init__(self) -> None:
        self._settings = self.project_configs()
        # your complete path to the directory inside which the active
        # repositories for SE purposes repositories were cloned. You should
        # edit it in configs.json file according to your preferences:
        self.path_active_SE_repos = self._settings['path_cloned_active_repos_SE_purpose']
        # your complete path to the directory inside which the active
        # repositories for non SE purposes repositories were cloned. You should
        # edit it in configs.json file according to your preferences:
        self.path_active_non_SE_repos = self._settings['path_cloned_active_repos_non_SE_purpose']
        self.path_active_SE_py_repos = self._settings['path_cloned_active_repos_SE_py_purpose']
        self.path_active_non_SE_py_repos = self._settings['path_cloned_active_repos_non_SE_py_purpose']
        self.kaggle_dataset = self._settings['kaggle_dataset']
        # path in which the repositories are going to be cloned inside:
        self.clone_destination = self._settings['clone_destination']
        # fixed date to ensure data consistency. You shouldn't edit it in
        # configs.json file:
        self.date = self._settings['analyze_data_pevious_to']
        # fixed date for splitting data for ML/AI applications.
        # this specific date generates a split of number of notebooks
        # ideal to compose train/validation/test sets. It is advised
        # to don't change this date in configs.json file:
        self.date_split_cross_val = self._settings['dataset_AI_split_previous_to']
        # email for querying geopy (Nominatin) API:
        self.email = self._settings['email']

        self.github_auth_token = self.get_auth_token()

    def project_configs(self):
        # current_path = Path.cwd()
        json_configs = Path(Path.cwd(), "research_questions",
                            "configs", "configs.json")
        with open(json_configs, "r") as f:
            config = json.load(f)
        return config

    def get_auth_token(self):
        """Reads a github personal authorization token that was inseted in 
        your .env file of this project. Your token must be valid."""

        env_file_path = Path(Path.cwd(), "research_questions",
                             "configs", ".env")

        # loading GitHub auth token from .env file:
        load_dotenv(env_file_path)
        github_token = os.getenv("AUTH_TOKEN")

        return github_token
