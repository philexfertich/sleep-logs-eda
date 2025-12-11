import re
import pandas as pd
import markdown as md

from bs4 import BeautifulSoup, NavigableString, Tag


class MarkdownExtractor:
    def __enter__(self):
        return self.df

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

    def __init__(self, path):
        self.file = open(path)
        self.df = self.extract_table(self.file.read())
    
    def extract_table(self, md_table):
        """Extracts data md_table markdown table.
        
        Args:
            file: A sting
        """
    
        parsed_md = md.markdown(md_table)
    
        soup = BeautifulSoup(parsed_md, "lxml")
    
        for header in soup.find_all("h1", string="Diary (Complete)"):
            nextNode = header
            
            while True:
                nextNode = nextNode.nextSibling
                if nextNode is None:
                    break
                if isinstance(nextNode, Tag):
                    parsed_md = nextNode.contents
        
    
        pattern = r"\| (.*?) " * 4 + r"\|"
        matches = re.findall(pattern, parsed_md[0])
    
        header = [title.strip() for title in matches[0]]
        data = [[data.strip() for data in row] for row in matches[2:]]
    
        return pd.DataFrame(data, columns=header)