# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 16:03:35 2018

@author: mpinkert
"""

import mp_img_manip.toolkits.cytospectre as cyto
import pandas as pd
from pathlib import Path
import numpy as np


def analyze_data(xls_path):
    dirty_df = pd.read_excel(xls_path, index_col = 'Image')
    
    clean_df = cyto.clean_single_dataframe(dirty_df) 
    clean_path = Path(xls_path.parent, xls_path.stem + '_Cleaned.csv')
    clean_df.to_csv(clean_path)
    
    return clean_df
       
#    orient = clean_df['Orientation'].dropna()
#    regression_all = three_modality_regression(orient)
#    regression_sample = sample_differentiated_regression(orient)
    
#    align = clean_df['Alignment'].dropna()
#    all_alignment = three_modality_regression(align)
#    sample_alignment= sample_differentiated_regression(align)

#    return regression_all, regression_sample

def sample_differentiated_regression(input_dataframe):
    
    sample_list = []
    sample_df_list = []
    
    for sample, sample_df in input_dataframe.groupby(level = 0):
        sample_regression = three_modality_regression(sample_df)
        
        sample_list.append(sample)
        sample_df_list.append(sample_regression)

    sample_wise_dataframe = pd.concat(sample_df_list, keys = sample_list)
        
    return sample_wise_dataframe




def recast_sin(row):
    new_values = np.sin(np.pi*row.values/180)
    return new_values


def three_modality_regression(three_modality_dataframe):
    index_label = 'Regression Modalities'
    column_labels = ['slope', 'intercept', 'r value', 'p value', 'std error']
    
    linear_regression_results = pd.DataFrame(
            index = pd.Index([], dtype='object', name=index_label), 
            columns = column_labels)

    mlr_to_ps = three_modality_dataframe[['MLR', 'PS']].apply(
            recast_max_diff_90deg, axis = 1)
    linear_regression_results.loc['MLR to PS'] = regress(mlr_to_ps)

    mlr_to_shg = three_modality_dataframe[['MLR', 'SHG']].apply(
            recast_max_diff_90deg, axis = 1)
    linear_regression_results.loc['MLR to SHG'] = regress(mlr_to_shg)

#    mmp_cast_to_ps = three_modality_dataframe[['MMP', 'PS']].apply(
#            recast_max_diff_90deg, axis = 1)
#    linear_regression_results.loc['MMP to PS'] = regress(mmp_cast_to_ps)
#
#    mmp_cast_to_shg = three_modality_dataframe[['MMP', 'SHG']].apply(
#            recast_max_diff_90deg, axis = 1)
#    linear_regression_results.loc['MMP to SHG'] = regress(mmp_cast_to_shg)

    shg_to_ps = three_modality_dataframe[['SHG', 'PS']].apply(
            recast_max_diff_90deg, axis = 1)
    linear_regression_results.loc['SHG to PS'] = regress(shg_to_ps)
    
    n = len(three_modality_dataframe.index)
    linear_regression_results['r2 adjusted'] = linear_regression_results[
            'r value'].apply(lambda x: 1-(1-x**2)*(n-1)/(n-2))
 
    return linear_regression_results
    



clean_df = analyze_data(Path('F:\Box Sync\Research\Polarimetry\Data 04 - Analysis results and graphics\Cytospectre', 'WP2 and WP5 _ 6-1-18.xls'))