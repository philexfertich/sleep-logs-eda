import os
import re
import numpy as np
import pandas as pd
import md_extract as mdex
from contextlib import contextmanager


md_file = "raw_data/Sleep (Complete).md"
csv_file = "raw_data/Sleep Log Journal Export.txt"


with mdex.extract_table(md_file) as md:
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

    # Prepare column names
    cols = ["Sleep Time", "Wake Time"]
    
    # Format Sleep Time and Wake time of ms-source
    fmt_1 = r"(\b\d\b):(\d\d)\s([A|P]M)"
    fmt_2 = r"0\1:\2 \3"
    for c in cols:
        md[c] = md[c].apply(lambda s: re.sub(fmt_1, fmt_2, s))
        # md[c] = pd.to_datetime(md[c], utc=True)
    del fmt_1, fmt_2
    
    # Prepare Sleep Time and Wake Time of csv-source
    for c in cols:
        csv[c] = pd.to_datetime(
            csv[c],
            format='%H:%M',
            errors='coerce'
        ).dt.strftime('%I:%M %p')
    del fmt, c, cols

    # Clear regex cache
    re.purge()
    
    # ===== Finalizing table =====
    sleep_logs = pd.concat([csv, md])

    # Convert types
    sleep_logs.index = pd.to_datetime(sleep_logs.index)
    sleep_logs["Duration"] = pd.to_timedelta(sleep_logs["Duration"])