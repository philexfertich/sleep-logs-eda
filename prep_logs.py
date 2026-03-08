import kagglehub
import pandas as pd

from kagglehub import KaggleDatasetAdapter


df: pd.DataFrame = kagglehub.dataset_load(
    KaggleDatasetAdapter.PANDAS,
    'philexfertich/personal-sleep-tracking-and-quality-logs',
    "sleep-logs.csv",
    pandas_kwargs={
        'parse_dates': ['Sleep Time', 'Wake Time'],
        'date_format': r'%Y-%m-%d %H:%M:%S',
        'converters': {'Duration': pd.to_timedelta}
    }
)

print(df)
df.info()