# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 16:13:51 2018

@author: mpinkert
"""

import unittest

import mp_img_manip.tiling as til
import numpy as np

class tile_passes_threshold_test_suite(unittest.TestCase):
    """Basic test cases."""

    test_tile = np.array([[0, 0, 1, 1, 2, 2], [0, 0, 1, 1, 2, 2]])
    

    def test_passes_both_thresholds(self):
        self.assertTrue(til.tile_passes_threshold(self.test_tile, 1, 3))

    def test_fails_num_threshold(self):
        self.assertFalse(til.tile_passes_threshold(self.test_tile, 0, 11))

    def test_fails_val_threshold(self):
        self.assertFalse(til.tile_passes_threshold(self.test_tile, 4, 1))

    def test_fails_both(self):
        self.assertFalse(til.tile_passes_threshold(self.test_tile, 4, 11))

if __name__ == '__main__':
    unittest.main()