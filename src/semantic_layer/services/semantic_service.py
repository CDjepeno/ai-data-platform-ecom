from pathlib import Path
import yaml

SEMANTIC_PATH = Path(__file__).parent / "semantic_tables"

def load_semantic_models():

    models = []

    for file in SEMANTIC_PATH.glob("*.yml"):

        with open(file, "r") as f:
            models.append(yaml.safe_load(f))

    return models