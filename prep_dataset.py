import pandas as pd
import parsers.gen_dataset as gds

from pathlib import Path
from parsers import ParserDefault

KAGGLE_PATH = '/kaggle/input/datasets/philexfertich/sleep-logs/sleep-logs.csv' 
LOCAL_PATH = './dataset/sleep-logs.csv'

ds = gds.Dataset()

if Path(KAGGLE_PATH).exists():
    df = ds((ParserDefault, KAGGLE_PATH, {}))
else:
    df = ds((ParserDefault, LOCAL_PATH, {}))

print(df)