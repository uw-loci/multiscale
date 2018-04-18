# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 16:03:35 2018

@author: mpinkert
"""

import mp_img_manip.cytospectre as cyto
import mp_img_manip.dir_dictionary as dird
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np
from scipy import stats

dir_dict = dird.create_dictionary()

def process_raw_data(dir_dict):
    cyto.write_roi_comparison_file(dir_dict['cyto'])


def analyze_data(dir_dict):
    clean_path = Path(dir_dict['cyto'] + '/Cleaned data.csv')
    clean_df = pd.read_csv(clean_path, header = [0, 1], index_col = [0, 1, 2])
    
    orient = clean_df['Orientation'].dropna()

    all_sample_regression = three_modality_regression(orient)
    
    sample_wise_regression = sample_differentiated_regression(orient)
    



def sample_differentiated_regression(input_dataframe):
    
    sample_list = []
    sample_df_list = []
    
    for sample, sample_df in input_dataframe.groupby(level = 0):
        sample_regression = three_modality_regression(sample_df)
        
        sample_list.append(sample)
        sample_df_list.append(sample_regression)
        
        
    sample_wise_dataframe = pd.concat(sample_df_list, keys = sample_list)
        
    return sample_wise_dataframe


def recast_max_diff_90deg(row):
    value_one, value_two = row.values
    diff = value_one - value_two
    if diff > 90:
        new_value = value_one - 180.0
    elif diff < -90:
        new_value = value_one + 180.0
    else:
        new_value = value_one + 0
    
    return new_value, value_two

def three_modality_regression(three_modality_dataframe):
    index_label = 'Regression Modalities'
    column_labels = ['slope', 'intercept', 'r value', 'p value', 'std error']
    
    linear_regression_results = pd.DataFrame(
            index = pd.Index([], dtype='object', name=index_label), 
            columns = column_labels)
    
    mmp_cast_to_ps = three_modality_dataframe[['MMP', 'PS']].apply(
            recast_max_diff_90deg, axis = 1)
    linear_regression_results.loc['MMP to PS'] = regress(mmp_cast_to_ps)

    
    mmp_cast_to_shg = three_modality_dataframe[['MMP', 'SHG']].apply(
            recast_max_diff_90deg, axis = 1)
    linear_regression_results.loc['MMP to SHG'] = regress(mmp_cast_to_shg)

    shg_cast_to_ps = three_modality_dataframe[['SHG', 'PS']].apply(
            recast_max_diff_90deg, axis = 1)
    linear_regression_results.loc['SHG to PS'] = regress(shg_cast_to_ps)
    
    return linear_regression_results
    

def regress(two_column_df):
    original_columns = two_column_df.columns.tolist()
    x = two_column_df[original_columns[1]]
    y = two_column_df[original_columns[0]]

    results = stats.linregress(x,y)
    
    return results

    