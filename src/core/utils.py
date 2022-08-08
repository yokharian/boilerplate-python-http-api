import json

# import yaml


def load_yaml(file_path):
    """Load a yaml file."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def load_json(file_path):
    """Load a json file."""
    with open(file_path, "r") as file:
        return json.load(file)
