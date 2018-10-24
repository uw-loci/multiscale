# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 16:13:51 2018

@author: mpinkert
"""

import unittest
import multiscale.tiling as til
import numpy as np

#
# class generate_tile_start_end_index_TestSuite(unittest.TestCase):
#     @given(x=st.integers(), y=st.integers())
#     def func_and_generator_yield_same_value(x, y):
#


class get_tile_start_end_index_test_suite(unittest.TestCase):
    
    def test_first_tile(self):
        start_end = til.get_tile_start_end_index(0, 5)
        self.assertEqual(start_end, (0,5))

    def test_second_tile(self):
        start_end = til.get_tile_start_end_index(1, 5)
        self.assertEqual(start_end, (5, 10))
        
    def test_offset_first_tile(self):
        start_end = til.get_tile_start_end_index(0, 5,
                                                 tile_offset = 2)
        self.assertEqual(start_end, (2, 7))

    def test_offset_second_tile(self):
        start_end = til.get_tile_start_end_index(1, 5,
                                                 tile_offset = 2)
        self.assertEqual(start_end, (7, 12))
        
    def test_first_tile_small_step_size(self):
        start_end = til.get_tile_start_end_index(0, 5,
                                                 tile_separation = 2)
        self.assertEqual(start_end, (0, 5))
 
    def test_second_tile_small_step_size(self):
        start_end = til.get_tile_start_end_index(1, 5,
                                                 tile_separation = 2)
        self.assertEqual(start_end, (2, 7))
    
    def test_first_tile_large_step_size(self):
        start_end = til.get_tile_start_end_index(0, 5,        
                                         tile_separation = 7)
        self.assertEqual(start_end, (0, 5))
 
    def test_second_tile_large_step_size(self):
        start_end = til.get_tile_start_end_index(1, 5,
                                                 tile_separation = 7)
        self.assertEqual(start_end, (7, 12))        
       
    def test_2d_same_number(self):
        start_end = til.get_tile_start_end_index([0,0], 5)
        self.assertEqual(start_end, ([0, 0], [5, 5]))
        
    def test_2d_diff_dumber(self):
        start_end = til.get_tile_start_end_index([0, 1], 5)
        self.assertEqual(start_end, ([0,5], [5,10]))

        
class calculate_number_of_tiles_test_suite(unittest.TestCase):
    #Need to make tests for multidimensional
    def test_no_remainder(self):
        tiles_and_offset = til.calculate_number_of_tiles(10,5)
        self.assertEqual(tiles_and_offset,(2,0))

    def test_one_more_than_evenly_divisible(self):
        tiles_and_offset = til.calculate_number_of_tiles(11,5)
        self.assertEqual(tiles_and_offset,(2,0))
        
    def test_one_less_than_evenly_divisible(self): 
        tiles_and_offset = til.calculate_number_of_tiles(9,5)
        self.assertEqual(tiles_and_offset,(1,2))
        
    def test_tile_separation_smaller(self):
        tiles_and_offset = til.calculate_number_of_tiles(
                15, 5, tile_separation = 2)
        
        self.assertEqual(tiles_and_offset,(4,3))
        
    def test_tss_smaller_dim_odd_remainder(self):
        tiles_and_offset = til.calculate_number_of_tiles(
                16, 5, tile_separation = 2)
        
        self.assertEqual(tiles_and_offset,(5,3))


class tile_passes_threshold_test_suite(unittest.TestCase):
    """Basic test cases."""

    test_tile = np.array([[160, 128], [64, 2]])
    

    def test_passes_both_thresholds(self):
        self.assertTrue(til.tile_passes_threshold(self.test_tile, 50, 50))

    def test_fails_num_threshold(self):
        self.assertFalse(til.tile_passes_threshold(self.test_tile, 50, 75))

    def test_fails_val_threshold(self):
        self.assertFalse(til.tile_passes_threshold(self.test_tile, 90, 10))

    def test_fails_both(self):
        self.assertFalse(til.tile_passes_threshold(self.test_tile, 99, 90))

if __name__ == '__main__':
    unittest.main()