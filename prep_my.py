import re

import markdown as md
import pandas as pd

from bs4 import BeautifulSoup, Tag

from gen_dataset import GenDatasetStrategy, Dataset


class GenFromMarkdown(GenDatasetStrategy):
    def gen_dataset(self, path):
        """Extracts table data from markdown file.
    
        Args:
            path: str -- path to the file including the name of the file.
        """
        file = open(path)
        
        try:
            parsed_md = md.markdown(file.read())
        
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
        finally:
            file.close()


MD_FILE = "raw_data/Sleep (Complete).md"


if __name__ == "__main__":
    ds = Dataset(GenFromMarkdown())

    print(ds.get_dataset(MD_FILE))