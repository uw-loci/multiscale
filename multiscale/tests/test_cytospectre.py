# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 15:43:03 2018

@author: mpinkert
"""

import multiscale.toolkits.cytospectre as cyto
import multiscale.polarimetry.dir_dictionary as dird
import unittest
import pandas as pd
import os
test_dict = dird.create_test_dictionary()


class parse_index_testsuite(unittest.TestCase):
    """Basic test cases."""

    def test_correct_input(self):
        index = 'WP2_PS_Tile-x12-y13.tif'
        correct_output = ('WP2', 'PS', 'Tile-x12-y13')
        output = cyto.parse_index(index)
        self.assertEqual(correct_output, output)
        
    def test_too_many_parts(self):
        assert True
        
    def test_too_few_parts(self):
        assert True
        
if __name__ == '__main__':
    unittest.main()