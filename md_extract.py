import re
import pandas as pd
import contextlib
import markdown as md

from bs4 import BeautifulSoup, NavigableString, Tag


@contextlib.contextmanager
def extract_table(path):
    """Extracts table data from markdown file.
    
    Args:
        path: str -- path to the file including the name of the file.
    """
    file = open(path)
    
    try:
        parsed_md = md.markdown(file.read())
    
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
    
        yield pd.DataFrame(data, columns=header)
    finally:
        file.close()