from importlib.resources import files
import json

class JSONLDataset:
    def __init__(self, dataset_name, split):
        valid_splits = ["train", "test"]
        if split not in valid_splits:
            raise ValueError(f"Invalid split '{split}'. Must be one of {valid_splits}")
        
        self.split = split
        self._path = files("TBXTools.datasets.data") / f"{dataset_name}_{self.split}.jsonl"

    def to_pandas(self):
        import pandas as pd
        return pd.read_json(self._path, orient='records', lines=True)

    def corpus(self):
        with open(self._path, 'r', encoding='utf-8') as f:
            for line in f:
                yield json.loads(line)["segment"]

    def terms(self):
        with open(self._path, 'r', encoding='utf-8') as f:
            for line in f:
                yield json.loads(line)["terms"]

def load_detech26(split="train", to_pandas=True):
    '''
        Load the DETECH2026 task A dataset for automatic terminology extraction.
    '''
    dataset = JSONLDataset(dataset_name="detech26", split=split)

    if to_pandas:
        return dataset.to_pandas()

    return dataset