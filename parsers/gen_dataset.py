import os
import logging

import pandas as pd

from typing import Any, Literal, Collection
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


STRUCTURE = ['Sleep Time', 'Wake Time', 'Duration', 'Notes']
DEFAULT_OUTPUT_DIR = 'dataset/'
DEFAULT_FILENAME = 'sleep-logs'


class Dataset:
    def __init__(self, output_dir: str = None):
        self.ouput_dir = output_dir
        self.data = pd.DataFrame(columns=STRUCTURE)

    def __save__(self, path: str):
        self.data.to_csv(path, index=False)

    def __call__(
        self,
        *args: FileMeta,
        name_pattern: str = None,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        save: bool = False
    ):
        output_dir = output_dir.strip('/')
        
        p = Path(output_dir)
        
        p.mkdir(exist_ok=True)

        file_name = name_pattern if name_pattern else DEFAULT_FILENAME
                    
        for strategy, path, kwargs in args:
            logger.info(f"Exracting {path} with {strategy.__name__}, arguments:\n{kwargs}")
            
            new = strategy().__prepare__(path, **kwargs)
            
            if not new.columns.equals(self.data.columns):
                logger.error(f'Table format does not follows {STRUCTURE}')
                continue

            self.data = pd.concat([self.data, new])
        
        self.data = self.data.sort_values(by=['Wake Time', 'Sleep Time'], axis=0)
   
        if save:
            self.__save__(f'{output_dir}/{file_name}.csv')
        
        return self.data
        

if __name__ == '__main__':
    from .parser_csv import ParserCSV
    from .parser_md import ParserMarkdown
    
    meta = [
        (ParserCSV, 'raw_data/Sleep Log Journal Export.txt', {}),
        (ParserMarkdown, 'raw_data/Sleep (Complete).md', {'last_date': '2025-10-27' },)
    ]

    class MyDataset(Dataset):
        def __call__(
            self, 
            *args, 
            name_pattern = None, 
            output_dir = DEFAULT_OUTPUT_DIR, 
            save = False
        ):
            super().__call__(*args, name_pattern=name_pattern, output_dir=output_dir, save=save)
            self.data['Duration'] = self.data['Wake Time'] - self.data['Sleep Time']

            return self.data
    ds = MyDataset()
    df = ds(*meta, save=True)
    df.info()
    print(df.head())
    print(df.tail())