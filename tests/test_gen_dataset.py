import unittest

import pandas as pd

import gen_dataset as gds


class GenDatasetTest(unittest.TestCase):
    # TODO Requires more tests
    
    def test_strategy(self):
        mock_df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': [5, 6, 7, 8]})
    
        class GenFromFirst(gds.SleepLogsParserStrategy):
            def __extract__(self, path):
                return mock_df
            
        df = GenFromFirst().__prepare__()
        self.assertTrue(df.equals(mock_df))
    

    def test_engine(self):
        mock_df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': [5, 6, 7, 8]})
        
        class GenFromFirst(gds.SleepLogsParserStrategy):
            def __extract__(self, path, **kwargs):
                return mock_df
        
        saving_result_data: pd.DataFrame = None
        saving_result_path: str = None

        class SleepLogsDataset(gds.Dataset):
            def __save__(self, data, path):
                nonlocal saving_result_data, saving_result_path
                saving_result_data = data
                saving_result_path = path

        mock_meta = (GenFromFirst, "mock_file", {"mock_arg": 0})

        prep = SleepLogsDataset()
        prep(mock_meta, save=True, distribution='separate')

        self.assertIsNotNone(saving_result_data)
        self.assertIsNotNone(saving_result_path)


if __name__ == '__main__':
    unittest.main()