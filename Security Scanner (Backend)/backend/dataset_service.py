import json
import os

DATASET_PATH = os.path.join("data", "attackbench.json")

def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# simple in-memory dataset
DATASET = load_dataset()

def get_all_examples(limit=10):
    return DATASET[:limit]

def get_example_by_id(example_id):
    for ex in DATASET:
        if ex["id"] == example_id:
            return ex
    return None
