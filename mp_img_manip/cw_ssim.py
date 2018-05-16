# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 10:50:24 2018

@author: mpinkert
"""


import mp_img_manip.bulk_img_processing as blk
import os
from PIL import Image
from ssim import SSIM


def compare_ssim(one_path, two_path):
    """Calculate the complex wavelet structural similarity metric
    
    Inputs:
    one_path -- Path to image one
    two_path -- Path to image two
    
    Output:
    ssim -- The Complex wavelet structural similarity metric
    """
    
    one = Image.open(one_path)
    two = Image.open(two_path)
    
    print('Calculating CW-SSIM between {0} and {1}'.format(
            os.path.basename(one_path), 
            os.path.basename(two_path)))
    
    ssim = SSIM(one).cw_ssim_value(two)
    
    print('CW-SSIM  = {0}'.format(str(ssim)))
    
    return ssim


def bulk_compare_ssim(dir_list, 
                      output_dir, output_name = 'CW-SSIM Values.csv'):
    """Calculate CW-SSIM between images in several file directories
    
    Inputs:
    dir_list -- The list of dirs to compare between
    output_dir -- Directory to save the cw-ssim values
    output_name -- Filename for the CW-SSIM value file
    """
    path_lists = blk.find_bulk_shared_images(dir_list)
    num_images = len(path_lists[0])
    num_dirs = len(dir_list)
    
    file_path = os.path.join(output_dir, output_name)
    
    for image_index in range(num_images):
        
        core_name = blk.get_core_file_name(path_lists[0][image_index])
        
        for index_one in range(num_dirs - 1):
            for index_two in range(index_one + 1, num_dirs):
                ssim = compare_ssim(path_lists[index_one][image_index],
                                    path_lists[index_two][image_index])
                
                modality_one = blk.file_name_parts(
                        path_lists[index_one][image_index])[1]
                modality_two = blk.file_name_parts(
                        path_lists[index_two][image_index])[1]
            
                column = modality_one + '-' + modality_two
                
                blk.write_pandas_value(file_path, core_name, ssim, column,
                                       'Sample')
    

