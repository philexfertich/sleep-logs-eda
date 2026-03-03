import os
import logging

import pandas as pd

from typing import Any, Literal
from pathlib import Path
from abc import ABC, abstractmethod


class PathNotSetError(Exception): 
    pass


class SleepLogsParserStrategy(ABC):
    @abstractmethod
    def __extract__(self, path: Path | str, **kwargs) -> pd.DataFrame:
        raise NotImplementedError
    
    def __prepare__(self, /, path: Path | str = None, **kwargs) -> pd.DataFrame:
        return self.__extract__(path, **kwargs)


logger = logging.getLogger(__name__)

FileMeta = tuple[
    type[SleepLogsParserStrategy], 
    Path|str, 
    dict[str, Any]
]
DistType = Literal['separate', 'unify', 'both']


STRUCTURE = ['Date', 'Sleep Time', 'Wake Time', 'Duration', 'Notes']
DEFAULT_OUTPUT_DIR = 'dataset/'
DEFAULT_FILENAME_SEP = 'sleep-logs-cluster'
DEFAULT_FILENAME_SEP = 'sleep=logs-dataset'


class Dataset:
    def __init__(self, distribution: DistType = None, output_dir: str = None):
        self.distribution = distribution
        self.ouput_dir = output_dir

    def __save__(self, data: pd.DataFrame, path: str):
        logger.warning(f'Saving is not implemented.')

    def __call__(
        self,
        *args: FileMeta,
        save: bool = False,
        distribution: DistType = 'unify',
        name_pattern: str = None,
        output_dir: str = DEFAULT_OUTPUT_DIR
    ):
        output_dir = output_dir.strip('/')
        
        p = Path(output_dir)
        if save and distribution == 'separate':
            (p / 'clusters').mkdir(parents=True, exist_ok=True)
        else:
            p.mkdir(exist_ok=True)
        del p

        file_name = name_pattern if name_pattern else DEFAULT_FILENAME_SEP
        
        df = pd.DataFrame(columns=STRUCTURE)        

        i = 1
        for strategy, path, kwargs in args:
            logger.info(f"Exracting {path} with {strategy.__name__}, arguments:\n{kwargs}")
            
            new = strategy().__prepare__(path, **kwargs)
            df = pd.concat([df, new])

            if save and distribution in ['separate', 'both']:
                self.__save__(df, f'{output_dir}/clusters/{file_name}-{i}.csv')
                i += 1
        
        if save and distribution in ['unify', 'both']:
            self.__save__(df, f'{output_dir}/{file_name}.csv')
