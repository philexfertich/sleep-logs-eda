import logging
import pandas as pd

from pathlib import Path

from parsers.gen_dataset import SleepLogsParserStrategy, Dataset


logger = logging.getLogger(__name__)


class ParserCSV(SleepLogsParserStrategy):
    def __extract__(self, path, **kwargs):
        p = Path(path)

        # Check if file within allowed extensions
        if not p.suffix in ['.csv', '.txt']:
            raise ValueError(
                    "Your file does not lead to a CSV file. " \
                    "Change your file to `.txt` or `.csv`"
                )

        # Check if file with one of suffixes is exist and format to right one
        if p.with_suffix('.csv').exists():
            p = p.with_suffix('.csv')
        else:
            p = p.with_suffix('.txt')

        logger.info(f'File {p} found.')

        # Read csv-source journal
        df = pd.read_csv(
            p, 
            parse_dates=[0], 
            date_format='%Y-%m-%d',
            converters={'Duration': pd.to_timedelta}
        )

        logger.info(f'Fetching completed:\n{df.head()}')

        return df
    
    def __prepare__(self, /, path = None, **kwargs):
        self.data = super().__prepare__(path, **kwargs)
        
        logger.info('Preparation started.')

        def to_timestamp(col):
            self.data[col] = self.data['Date'].dt.strftime(date_format='%Y-%m-%d') + " " + self.data[col]
            self.data[col] = pd.to_datetime(self.data[col])

        for col in ['Sleep Time', 'Wake Time']:
            to_timestamp(col)
        
        self.data.loc[self.data['Wake Time'] < self.data['Sleep Time'], 'Sleep Time'] -= pd.Timedelta('1d')
        
        del self.data['Date']

        logger.info('Preparation finished.')

        return self.data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = ParserCSV().__prepare__(path="raw_data/Sleep Log Journal Export.txt")
    print(df.head())
    df.info()