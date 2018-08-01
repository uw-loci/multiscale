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


def bulk_construct_images(df_single_modality_variable, modality, dir_modality,
                          dir_output, suffix_output):
    
    for grp, df in df_single_modality_variable.groupby(['Mouse', 'Slide']):
        
        path_to_image = find_matching_image(grp, dir_modality)
        dimensions = util.get_image_size(path_to_image)
        image_array = til.roi_values_to_image(df, dimensions, modality)
        
        write_image(image_array, dir_output, suffix_output)
        

def find_matching_image(group, dir_modality):
    
    sample = str(group[0]) + '-' + str(group[1])
    path_image = [Path(image) for image in os.listdir(dir_modality) if image.startswith(sample)]
    
    return path_image


def write_image(image_array, dir_output, suffix_output)