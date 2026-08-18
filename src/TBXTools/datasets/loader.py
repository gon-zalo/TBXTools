from importlib.resources import files
import json

class JSONLDataset:
    def __init__(self, dataset_name, split):
        valid_splits = ["train", "test"]
        if split not in valid_splits:
            raise ValueError(f"Invalid split '{split}'. Must be one of {valid_splits}")
        
        self.split = split
        self.golden_labels = None
        self.corpus = None
        self.df = None
        self._path = files("TBXTools.datasets.data") / f"{dataset_name}_{self.split}.jsonl"

    def to_pandas(self):
        import pandas as pd
        return pd.read_json(self._path, orient='records', lines=True)

    def segments(self):
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

        Split takes 'train' or 'test'.
    '''
    dataset = JSONLDataset(dataset_name="detech26", split=split)

    if to_pandas:
        df = dataset.to_pandas()
        dataset.df = df
        dataset.golden_labels = df['terms'].to_dict()
        dataset.corpus = df['segment'].to_list()

        return dataset
    
    return dataset