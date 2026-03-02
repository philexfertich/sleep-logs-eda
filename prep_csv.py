import logging
import pandas as pd

from pathlib import Path

from gen_dataset import ExtractionStrategy, Dataset


logger = logging.getLogger(__name__)


class FromMyCSV(ExtractionStrategy):
    def extract(self, path, **kwargs):
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
        df = pd.read_csv(p, index_col="Date")

        logger.info(f'Fetching completed:\n{df.head()}')

        return df


class MyCSVDataset(Dataset):
    def get_dataset(self, /, path = None, **kwargs):
        self.data = super().get_dataset(path, **kwargs)
        
        logger.info('Preparation started.')

        cols = ["Sleep Time", "Wake Time"]
        self.data[cols] = self.data[cols].apply(lambda s: pd.to_datetime(s, format="%H:%M"))
        self.data["Duration"] = pd.to_timedelta(self.data["Duration"])
        
        logger.info('Preparation ended.')

        return self.data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = MyCSVDataset(FromMyCSV()).get_dataset(path="raw_data/Sleep Log Journal Export.txt")
    print(df.head())
    df.info()