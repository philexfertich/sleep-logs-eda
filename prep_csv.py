import pandas as pd

from pathlib import Path

from gen_dataset import ExtractionStrategy, Dataset

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

        # Read csv-source journal
        df = pd.read_csv(p, index_col="Date")
        return df


class MyCSVDataset(Dataset):
    def get_dataset(self, /, path = None, **kwargs):
        df = super().get_dataset(path, **kwargs)
        
        # Prepare Sleep Time and Wake Time of csv-source
        for c in ["Sleep Time", "Wake Time"]:
            df[c] = pd.to_datetime(
                df[c],
                format='%H:%M',
                errors='coerce'
            ).dt.strftime('%I:%M %p')
        
        return df


if __name__ == "__main__":
    df = MyCSVDataset(FromMyCSV()).get_dataset(path="raw_data/Sleep Log Journal Export.txt")
    print(df.head())