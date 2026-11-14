import unittest
import numpy as np
import pandas as pd
from timeseriesformatting import determine_dynamic_sequence_length, create_activity_sequences

class SequenceTests(unittest.TestCase):
    def test_short_dataset_still_has_target(self):
        for size in range(2, 20):
            frame = pd.DataFrame({'cow':[1.0] * size})
            length = determine_dynamic_sequence_length(frame)
            self.assertLess(length, size)
            self.assertGreater(length, 0)
    def test_windows_targets_and_dates_align(self):
        frame = pd.DataFrame({'cow':[1,2,3,4]})
        X,y,dates = create_activity_sequences(frame,2,['a','b','c','d'])
        np.testing.assert_array_equal(X[:,:,0], [[1,2],[2,3]])
        np.testing.assert_array_equal(y[:,0], [3,4])
        self.assertEqual(dates,[['a','b'],['b','c']])
    def test_invalid_windows_and_nonfinite_values_rejected(self):
        frame = pd.DataFrame({'cow':[1,2,3]})
        for length in [0,-1,3,True,1.5]:
            with self.assertRaises(ValueError): create_activity_sequences(frame,length)
        with self.assertRaises(ValueError): create_activity_sequences(pd.DataFrame({'cow':[1,np.nan]}),1)
        with self.assertRaises(ValueError): create_activity_sequences(frame,1,['one'])
        with self.assertRaises(ValueError): determine_dynamic_sequence_length([])
if __name__ == '__main__': unittest.main()
