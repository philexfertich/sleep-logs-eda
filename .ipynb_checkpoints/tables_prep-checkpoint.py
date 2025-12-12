import os
import re
import numpy as np
import pandas as pd
import md_extract as mext
from contextlib import contextmanager


md_file = "raw_data/Sleep (Complete).md"
csv_file = "raw_data/Sleep Log Journal Export.txt"


with mext.MarkdownExtractor(md_file) as md:
    # Rename columns
    md = md.rename(columns={
        "Gone to bed at": "Sleep Time" ,
        "Woke up at": "Wake Time",
        "Sleep time": "Duration",
        "Stage": "Notes"
    })

    # For compatibility:
    # - Remove unnecessary column
    # - Add a new one
    md["Notes"] = pd.Series()
    
    # Change Duration to timestamp in minutes for compatibility
    fmt = r"(\d?\d):(\d\d)"
    def reformat_time(s):
        a = s.split(":")
        return f"{a[0]}h {a[1]}m"
    md["Duration"] = md["Duration"].apply(reformat_time)

    
    # Read cdv-source journal
    csv = pd.read_csv(csv_file, index_col="Date")

    # Prepare md-source dates 
    date = csv.index.min()
    n_rows = md.shape[0]
    dates = pd.date_range(end=date,
                          inclusive="neither",
                          periods=n_rows + 1, unit='s')
    del date, n_rows

    md["Date"] = pd.to_datetime(pd.Series(dates)).dt.strftime("%Y-%m-%d")
    md = md.set_index("Date")
    del dates

    # Prepare csv Sleep Time and Wake Time
    fmt = '%I:%M %p'
    for column in ["Sleep Time", "Wake Time"]:
        csv[column] = pd.to_datetime(
            csv[column],
            format='%H:%M',
            errors='coerce'
        ).dt.strftime(fmt)

    del fmt, column
    re.purge()
    
    # Resulting table
    table = pd.concat([csv, md])