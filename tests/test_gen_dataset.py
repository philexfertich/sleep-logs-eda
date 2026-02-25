import unittest

import pandas as pd

import gen_dataset


class GenDatasetTest(unittest.TestCase):
    
    def test_dataset(self):
        mock_df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': [5, 6, 7, 8]})
    
        class GenFromFirst(gen_dataset.GenDatasetStrategy):
            def gen_dataset(self, path):
                return mock_df
        ds = gen_dataset.Dataset(GenFromFirst())
        self.assertTrue(ds.get_dataset("").equals(mock_df))

        class GenFromOther(gen_dataset.GenDatasetStrategy):
            def gen_dataset(self, path):
                return mock_df
        ds.set_strategy(GenFromOther())
        self.assertTrue(ds.get_dataset("").equals(mock_df))


if __name__ == '__main__':
    unittest.main()