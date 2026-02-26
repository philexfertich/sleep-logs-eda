import re

import pandas as pd

from pathlib import Path

from bs4 import BeautifulSoup, Tag
from markdown import markdown

from gen_dataset import GenDatasetStrategy, Dataset


class GenFromMarkdown(GenDatasetStrategy):
    def gen_dataset(self, path):
        """Extracts table data from markdown file.
    
        Args:
            path: str -- path to the file including the name of the file.
        """
        
        p = Path(path)

        # Check if file within allowed extensions
        if not p.suffix in ['.md', '.markdown']:
            raise ValueError(
                    "Your file does not lead to a markdown file. " \
                    "Change your file to `.md` or `markdown`"
                )

        # Check if file with one of suffixes is exist and format to right one
        if p.with_suffix('.md').exists():
            p = p.with_suffix('.md')
        else:
            p = p.with_suffix('.markdown')

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
            
            pattern = r"\| (.*?) " * 4 + r"\|"
            matches = re.findall(pattern, parsed_md[0])
        
            header = [title.strip() for title in matches[0]]
            data = [[data.strip() for data in row] for row in matches[2:]]
        
            return pd.DataFrame(data, columns=header)
                
            
class DatasetMarkdown(Dataset):
    def get_dataset(self, path):
        df = super().get_dataset(path)
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
        
        # Change Duration to timestamp in minutes for compatibility
        fmt = r"(\d?\d):(\d\d)"
        def reformat_time(s):
            a = s.split(":")
            return f"{a[0]}h {a[1]}m"
        df["Duration"] = df["Duration"].apply(reformat_time)

        # Prepare column names
        cols = ["Sleep Time", "Wake Time"]
        
        # Format Sleep Time and Wake time of md-source
        fmt_1 = r"(\b\d\b):(\d\d)\s([A|P]M)"
        fmt_2 = r"0\1:\2 \3"
        for c in cols:
            df[c] = df[c].apply(lambda s: re.sub(fmt_1, fmt_2, s))
            # md[c] = pd.to_datetime(md[c], utc=True)
        del fmt_1, fmt_2

        return df


MD_FILE = "raw_data/Sleep (Complete).markdown"


if __name__ == "__main__":
    ds = DatasetMarkdown(GenFromMarkdown())

    print(ds.get_dataset(MD_FILE).info())