import pandas as pd

from abc import ABC, abstractmethod


class GenDatasetStrategy(ABC):
    @abstractmethod
    def gen_dataset(self, path) -> pd.DataFrame:
        raise NotImplementedError


class Dataset(ABC):
    def __init__(self, gen_dataset_strategy: GenDatasetStrategy):
        self.gen_dataset_strategy = gen_dataset_strategy
    
    def get_dataset(self, path) -> pd.DataFrame:
        return self.gen_dataset_strategy.gen_dataset(path)
    
    def set_strategy(self, gen_dataset_strategy: GenDatasetStrategy):
        self.gen_dataset_strategy = gen_dataset_strategy