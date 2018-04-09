# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 15:42:22 2018

@author: mpinkert
"""


import mp_img_manip.dir_dictionary as dird
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.utility_functions as util
import pandas as pd
import numpy as np
import os


def parse_index(roi_str):
    
    sample, modality, roi = blk.file_name_parts(roi_str)
    return sample, modality, roi

def bulk_parse_index(roi_list):
    indices_list = blk.file_name_parts_list(roi_list)
    parsed_indices = np.array(indices_list)
    return parsed_indices


def clean_indices(parsed_indices):
    
    pre_variable_sort_index = ['Sample', 'Modality', 'ROI']
    transposed_indices = np.transpose(parsed_indices)
    mid_clean_index = pd.MultiIndex.from_arrays(transposed_indices,
                                          names = pre_variable_sort_index)
    
    return mid_clean_index


def clean_single_dataframe(dirty_frame):
    """Takes a raw cytospectre dataframe and resorts it for easy analysis"""
    
    new_label_dict = {'Mean orientation' : 'Orientation', 
                       'Circ. variance' : 'Alignment'}
    relabeled_frame = dirty_frame.rename(columns = new_label_dict)
        
    parsed_indices = bulk_parse_index(list(relabeled_frame.index))  
    clean_index = clean_indices(parsed_indices)  
    clean_frame_stacked = relabeled_frame.set_index(clean_index)
    
    clean_frame = clean_frame_stacked.unstack(1)
    
    return clean_frame




def clean_up_dataframes(analysis_list):
    
    dirty_index = 'Image'
    relevant_cols = ['Image', 'Mean orientation', 'Circ. variance']
    dirty_dataframes = blk.dataframe_generator_excel(analysis_list, 
                                                     dirty_index,
                                                     relevant_cols)

    index = ['Sample', 'ROI', 'Variable']
    column_labels = ['PS', 'SHG', 'MMP']     
    clean_dataframes = pd.DataFrame(columns = column_labels)
    clean_dataframes.set_index(index)

    for dirty_frame in dirty_dataframes:
        dataframe = clean_single_dataframe(dirty_frame)
        clean_dataframes.append(dataframe)   
        
    return clean_dataframes
    


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
