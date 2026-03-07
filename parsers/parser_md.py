import re
import logging

import pandas as pd
import numpy as np

from pathlib import Path
from datetime import datetime

from bs4 import BeautifulSoup, Tag
from markdown import markdown

from parsers.gen_dataset import SleepLogsParserStrategy, Dataset


logger = logging.getLogger(__name__)


class TableNotFoundError(Exception):
    pass


class ParserMarkdown(SleepLogsParserStrategy):
    def __extract__(self, path, **kwargs):
        """Extracts table data from markdown file.
    
        Args:
            path: str -- path to the file including the name of the file.
        """
        
        p = Path(path)

        # Check if file within allowed extensions
        if not p.suffix in ['.md', '.markdown']:
            raise ValueError(
                    "Your file does not lead to a markdown file. " \
                    "Change your file to `.md` or `.markdown`"
                )

        # Check if file with one of suffixes is exist and format to right one
        if p.with_suffix('.md').exists():
            p = p.with_suffix('.md')
        else:
            p = p.with_suffix('.markdown')
        
        logging.info(f"File {p} found.")

        # Extract data from the file
        with open(p) as f:
            parsed_md = markdown(f.read())
        
            soup = BeautifulSoup(parsed_md, 'html.parser')
        
            for header in soup.find_all("h1", string="Diary (Complete)"):
                nextNode = header
                
                while True:
                    nextNode = nextNode.next_sibling
                    if nextNode is None:
                        break
                    if isinstance(nextNode, Tag):
                        parsed_md = nextNode.contents
                        logging.info('Table found')
            
            c = re.compile(r"\| (.*?) " * 4 + r"\|")
            matches = c.findall(parsed_md[0])
        
            header = [title.strip() for title in matches[0]]
            data = []
            for row in matches[2:]:
                data.append([data.strip() for data in row])
                logging.info(f'Row added: {row}')
            df = pd.DataFrame(data, columns=header)
            
            logger.info(f'Fetching completed:\n{df.head()}')
            
            return df
    
    def __prepare__(self, /, path: Path | str = None, **kwargs):
        if not 'last_date' in kwargs:
            raise KeyError('Key `last_date` not found.') 
        
        logger.info('Formatting started.')

        self.data = super().__prepare__(path, **kwargs)
        
        self._restructure_table()
        self._format_times(kwargs['last_date'])
        self._format_durations()

        logger.info(f'Parsing finished. Resuling in \n{self.data.head()}')

        return self.data
    
    def _restructure_table(self):
        # Format column names and
        columns ={
            "Gone to bed at": "Sleep Time" ,
            "Woke up at": "Wake Time",
            "Sleep time": "Duration",
        }
        self.data = (
            self.data
            .rename(columns=columns)
            .drop(columns='Stage')
        )
        self.data["Notes"] = pd.Series()
        logger.info(f'Columns Prepared {self.data.columns.to_list()}.')

    def _format_durations(self):
        # Change Duration to timestamp in minutes for compatibility
        def reformat_time(s):
            a = s.split(":")
            return f"{a[0]}h {a[1]}m"
        
        self.data["Duration"] = pd.to_timedelta(
            self.data["Duration"].apply(reformat_time)
        )
        logger.info('Duration formatted.')

    def _format_times(self, date):
        dates = (
            pd
            .date_range(
                end=date, 
                inclusive='neither', 
                periods=self.data.shape[0]+1, 
                unit='s'
            )
            .strftime("%Y-%m-%d")
        )
        logger.info(dates)
        
        def to_timestamp(col):
            self.data[col] = dates + " " + self.data[col]
            self.data[col] = pd.to_datetime(self.data[col])

        for col in ['Sleep Time', 'Wake Time']:
            to_timestamp(col)
        
        logger.info('Sleep Time and Wake Time formatted.')

        self.data.loc[self.data['Wake Time'] < self.data['Sleep Time'], 'Sleep Time'] -= pd.Timedelta('1d')


MD_FILE = "raw_data/Sleep (Complete).markdown"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = ParserMarkdown().__prepare__(path=MD_FILE, last_date='2025-10-27')
    print(df)
    df.info()