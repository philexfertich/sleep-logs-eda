import pandas as pd

from pathlib import Path
from abc import ABC, abstractmethod


class PathNotSetError(Exception): 
    pass


class ExtractionStrategy(ABC):
    @abstractmethod
    def extract(self, path: Path | str, **kwargs) -> pd.DataFrame:
        raise NotImplementedError


class Dataset(ABC):
    def __init__(self, gen_dataset_strategy: ExtractionStrategy, path: Path | str = None):
        self.extraction_strategy = gen_dataset_strategy
        self.path = path
    
    def get_dataset(self, /, path: Path | str = None, **kwargs) -> pd.DataFrame:
        if not (self.path or path):
            raise PathNotSetError("Please set the path to find the file.")
        
        return self.extraction_strategy.extract(
            (path if path else self.path),
            **kwargs
        )
            
    def set_strategy(self, gen_dataset_strategy: ExtractionStrategy):
        self.extraction_strategy = gen_dataset_strategy

    def set_path(self, path: Path | str):
        self.path = path