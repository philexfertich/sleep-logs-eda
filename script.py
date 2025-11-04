import re
import markdown as md
import pandas as pd
import os

from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag


def extract_md_table(md_table) -> pd.DataFrame:
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
    data = [(data.strip() for data in row) for row in matches[2:]]

    return pd.DataFrame(data, columns=header)


md_source: pd.DataFrame = None

with open("raw_data/Sleep (Complete).md") as md_file:
    md_source = extract_md_table(md_file.read())

if not md_source is None:
    # >>>>> First format md source >>>>>
    names = {"Gone to bed at": "Sleep Time" ,
             "Woke up at": "Wake Time",
             "Sleep time": "Duration"}
    
    md_source = md_source[names.keys()].rename(columns=names)

    md_source["Sleep Time"] = pd.to_datetime(md_source["Sleep Time"]).dt.strftime("%H:%M")
    md_source["Wake Time"] = pd.to_datetime(md_source["Wake Time"]).dt.strftime("%H:%M")
    md_source["Duration"] = pd.to_datetime(md_source["Wake Time"]).dt.strftime("%-Hh %-Mm")
    md_source["Notes"] = pd.Series()
    # print(md_source)

    del names
    # <<<<< First format md source <<<<<

    # >>>>> Md dates defining and merging >>>>> 
    journal = pd.read_csv("raw_data/Sleep Log Journal Export.txt")
    
    date = journal["Date"].min()
    n_rows = md_source.shape[0]
    dates = pd.date_range(end=date,
                          inclusive="neither",
                          periods=n_rows + 1, unit='s')
    del date, n_rows
    
    md_source["Date"] = pd.to_datetime(pd.Series(dates)).dt.strftime("%Y-%m-%d")
    md_source = md_source.set_index("Date")
    journal = journal.set_index("Date")
    formated = pd.concat([md_source, journal], axis=0, verify_integrity=True)
    del md_source, journal
    # <<<<< Md dates defining and merging <<<<<

    print(formated)

    directory = "formated"

    if not os.path.exists(directory):
        os.makedirs(directory)

    formated.to_csv(f"{directory}/Sleep Log.csv")
