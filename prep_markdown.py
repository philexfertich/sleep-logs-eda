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
            # data = [[data.strip() for data in row] for row in matches[2:]]
            data = []
            for row in matches[2:]:
                data.append([data.strip() for data in row])
                logging.info(f'Row added: {row}')

            return pd.DataFrame(data, columns=header)
                
            
class MyMarkdownDataset(Dataset):
    def get_dataset(self, /, path: Path | str = None, **kwargs):
        if not 'last_date' in kwargs:
            raise KeyError('Key `last_date` not found.') 
        
        logger.info('Parsing started.')

        df = super().get_dataset(path, **kwargs)

        # Prepare Date
        date = kwargs['last_date']
        n_rows = df.shape[0]
        dates = pd.date_range(end=date,
                              inclusive='neither',
                              periods=n_rows + 1, unit='s')
    
        df["Date"] = pd.to_datetime(pd.Series(dates)).dt.strftime("%Y-%m-%d")
        df = df.set_index("Date")
        
        # Rename columns
        df = df.rename(columns={
            "Gone to bed at": "Sleep Time" ,
            "Woke up at": "Wake Time",
            "Sleep time": "Duration",
            "Stage": "Notes"
        })
    
        # For compatibility:
        # - Remove unnecessary column
        # - Add a new one
        df["Notes"] = pd.Series()

        logger.info(f'Columns Prepared {df.columns.to_list()}.')
        
        # Change Duration to timestamp in minutes for compatibility
        fmt = r"(\d?\d):(\d\d)"
        def reformat_time(s):
            a = s.split(":")
            return f"{a[0]}h {a[1]}m"
        df["Duration"] = df["Duration"].apply(reformat_time)

        logger.info('Duration formatted.')

        # Prepare column names
        cols = ["Sleep Time", "Wake Time"]
        
        # Format Sleep Time and Wake time of md-source
        fmt_1 = r"(\b\d\b):(\d\d)\s([A|P]M)"
        fmt_2 = r"0\1:\2 \3"
        for c in cols:
            df[c] = df[c].apply(lambda s: re.sub(fmt_1, fmt_2, s))
            # md[c] = pd.to_datetime(md[c], utc=True)
        del fmt_1, fmt_2

        logger.info('Sleep Time and Wake Time formatted.')
        logger.info(f'Parsing finished. Resuling in \n{df.head()}')
        
        # Clear regex cache
        re.purge()

        return df


MD_FILE = "raw_data/Sleep (Complete).markdown"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ds = MyMarkdownDataset(FromMyMarkdown())

    ds.get_dataset(path=MD_FILE, last_date='2025-10-27')

    ds.set_path(MD_FILE)
    ds.get_dataset(last_date='2025-10-27')
    