# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 15:43:03 2018

@author: mpinkert
"""

import mp_img_manip.toolkits.cytospectre as cyto
import mp_img_manip.polarimetry.dir_dictionary as dird
import unittest
import pandas as pd
import os
test_dict = dird.creat_test_dictionary()


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
        
        
class Clean_single_dataframe_testsuite(unittest.TestCase):
    """Basic test cases."""

    def test_results_1(self):
        dirty_index = 'Image'
        relevant_cols = ['Image', 'Mean orientation', 'Circ. variance']
        clean_index = ['Sample', 'ROI', 'Variable']


        result_1_path = os.path.join(test_dict['test_cyto'],
                                     'cytospectre_results-1.xls')
        
        clean_1_path = os.path.join(test_dict['test_cyto'],
                                     'clean_results-1.csv')
        
        df_input = pd.read_excel(result_1_path, index_col = dirty_index,
                                 columns = relevant_cols)
        
        df_clean = pd.read_csv(clean_1_path, index_col = clean_index)
        
        df_output = cyto.clean_single_dataframe(df_input)
        
        self.assertEqual(df_clean, df_output)
        
        

if __name__ == '__main__':
    unittest.main()