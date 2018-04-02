# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 16:03:35 2018

@author: mpinkert
"""

import mp_img_manip.dir_dictionary as dird
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.utility_functions as util
import pandas as pd


def parse_roi_number(roi_str):
    return

def clean_up_dataframes(analysis_list):
    index = 'Image'
    relevant_cols = ['Mean orientation', 'Circ. variance']
    
    #read in the dataframes
    dataframe_generator = (
            pd.read_csv(item, usecols = relevant_cols, index_col = index) for
            item in analysis_list)
    
    column_labels = ['Variable', 'PS', 'SHG', 'MMP']
        
    clean_dataframe = pd.DataFrame(
            index = pd.Index([], dtype='object', name=index),
            columns = column_labels)
    
    return clean_dataframe
    
def write_roi_comparison_file(sample_dir, output_dir, output_suffix):
    
    analysis_list = util.list_filetype_in_dir(sample_dir, '.csv')
    
    clean_dataframe = clean_up_dataframes(analysis_list)
    
    
        #Find the ROI string
        
    
    return

def bulk_write_roi_comparison_file():
    #For each sample
    #write roi comparison file
    return

def plot_roi_comparison():
    return

def r2_roi_comparison():
    return

