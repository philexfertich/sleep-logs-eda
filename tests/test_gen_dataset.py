import unittest
import pandas as pd

from pathlib import Path
import parsers.gen_dataset as gds


class GenDatasetTest(unittest.TestCase):
    def setUp(self):
        self.mock_df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': [5, 6, 7, 8]})
        
        class ExtractMock(gds.SleepLogsParserStrategy):
            def __extract__(self, path, **kwargs):
                return pd.DataFrame()

        self.mock_meta = [(ExtractMock, "mock_file", {"mock_arg": 0}) for i in range(10)]


    def test_strategy(self):
        extraction_path: str
        mock = self.mock_df
    
        class ExtractMock(gds.SleepLogsParserStrategy):
            def __extract__(self, path):
                nonlocal extraction_path
                extraction_path = path
                return mock
            
        df = ExtractMock().__prepare__("some_dir/")
        self.assertIsNotNone(extraction_path)
        self.assertTrue(df.equals(mock))
    

    def test_dataset_saving(self):
        saving_result_data: pd.DataFrame = None
        saving_result_path: str = None

        class SleepLogsDataset(gds.Dataset):
            def __save__(self, data, path):
                nonlocal saving_result_data, saving_result_path
                saving_result_data = data
                saving_result_path = path

        prep = SleepLogsDataset()
        self.helper(prep)
        self.assertIsNotNone(saving_result_data)
        self.assertIsNotNone(saving_result_path)

    def test_unify_distribution(self):
        self.distr_helper(1, 'unify')

    def test_separate_distribution(self):
        self.distr_helper(10, 'separate')

    def test_both_distribution(self):
        self.distr_helper(11, 'both')

    def test_custom_naming(self):
        mock_name = 'test'
        expected_names = [f'{mock_name}-{i}' for i in range(1, 11)]
        expected_names.append(mock_name)
        names = []

        class SleepLogsDataset(gds.Dataset):
            def __save__(self, data, path):
                p = Path(path).stem
                names.append(p)
        
        prep = SleepLogsDataset(distribution='both')
        prep(*self.mock_meta, name_pattern=mock_name)

        self.assertListEqual(expected_names, names)

    def test_default_naming(self):
        expected_names = [f'{gds.DEFAULT_FILENAME}-{i}' for i in range(1, 11)]
        expected_names.append(gds.DEFAULT_FILENAME)
        names = []

        class SleepLogsDataset(gds.Dataset):
            def __save__(self, data, path):
                p = Path(path).stem
                names.append(p)
        
        prep = SleepLogsDataset(distribution='both')
        prep(*self.mock_meta)

        self.assertListEqual(expected_names, names)

    def helper(self, prep, distr=None):
        prep(*self.mock_meta, distribution=distr)

    def distr_helper(self, expected_num_of_calls, distr):
        num_of_calls = 0

        class SleepLogsDataset(gds.Dataset):
            def __save__(self, data, path):
                nonlocal num_of_calls
                num_of_calls += 1
        
        prep = SleepLogsDataset(distribution=distr)
        self.helper(prep)
        self.assertEqual(num_of_calls, expected_num_of_calls)
        

if __name__ == '__main__':
    unittest.main()