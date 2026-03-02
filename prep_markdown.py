import re
import logging

import pandas as pd
import numpy as np

from pathlib import Path
from datetime import datetime

from bs4 import BeautifulSoup, Tag
from markdown import markdown

from gen_dataset import ExtractionStrategy, Dataset


logger = logging.getLogger(__name__)


class TableNotFoundError(Exception):
    pass


class FromMyMarkdown(ExtractionStrategy):
    def extract(self, path, **kwargs):
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
                
            
class MyMarkdownDataset(Dataset):
    def get_dataset(self, /, path: Path | str = None, **kwargs):
        if not 'last_date' in kwargs:
            raise KeyError('Key `last_date` not found.') 
        
        logger.info('Formatting started.')

        self.data = super().get_dataset(path, **kwargs)
        
        self._generate_dates(kwargs['last_date'])
        self._restructure_table()
        self._format_times()
        self._format_durations()

        logger.info(f'Parsing finished. Resuling in \n{self.data.head()}')

        return self.data
    
    def _generate_dates(self, date):
        # TODO Change method for dates generation
        # Prepare Date
        n_rows = self.data.shape[0]
        dates = pd.date_range(end=date,
                              inclusive='neither',
                              periods=n_rows + 1, unit='s')
        self.data["Date"] = (
            pd
            .to_datetime(pd.Series(dates))
            .dt.strftime("%Y-%m-%d")
        )
        self.data = self.data.set_index("Date")
        logger.info(f'Date index prepared: {self.data.head().index}')
    
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

    def _format_times(self):
        # Format Sleep Time and Wake time of md-source
        def format_time(s):
            logger.info(f'{s.name} column formating...')
            return  pd.to_datetime(s, utc=True, format="%I:%M %p")
        cols = ['Sleep Time', 'Wake Time']
        self.data[cols] = self.data[cols].apply(format_time)

        logger.info('Sleep Time and Wake Time formatted.')
        

MD_FILE = "raw_data/Sleep (Complete).markdown"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ds = MyMarkdownDataset(FromMyMarkdown())

    ds.get_dataset(path=MD_FILE, last_date='2025-10-27')

    ds.set_path(MD_FILE)
    ds.get_dataset(last_date='2025-10-27').info()

    