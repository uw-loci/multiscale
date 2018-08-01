# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 14:53:54 2018

@author: mpinkert
"""
import pandas as pd
import os
from pathlib import Path

import mp_img_manip.analysis as an
import mp_img_manip.plotting as myplot
import mp_img_manip.utility_functions as util
import mp_img_manip.tiling as til


def construct_image(dataframe, mouse, slide, modality, dimensions, roi=False):

    values = dataframe.loc[mouse, slide]
    
    if roi:
        img_array = til.roi_values_to_image(values, dimensions, modality)
    else:
        img_array = til.tile_values_to_image(values, dimensions, modality)
        
    return img_array
            

def retardance_files_to_df(ret_dir):
    list_csvs = util.list_filetype_in_dir(ret_dir, 'csv')
    list_df_rets = [pd.read_csv(item) for item in list_csvs if re.search('64', str(item))]
    
    df_ret_avgs_raw = pd.concat(list_df_rets)
    
    df_ret_avgs = pd.pivot_table(df_ret_avgs_raw, index=['Mouse', 'Slide', 'Tile', 'ROI'],
                                 values=['Alignment', 'Orientation', 'Retardance'],
                                 columns = 'Modality')
    
    return df_ret_avgs