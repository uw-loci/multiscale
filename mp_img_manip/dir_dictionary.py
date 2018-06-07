# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 10:56:37 2018

@author: mpinkert

My personal directories
"""

import os


def create_test_dictionary(test_dir = 'tests'):
    
    test_files_dir = os.path.join(test_dir, 'test_files')
    
    test_dict = {
            'test_dir': test_dir,
            'test_files_dir': test_files_dir,
            'test_cyto': os.path.join(test_files_dir,'test_cyto')
            }
    return test_dict


def create_dictionary(
        base_dir = os.path.normpath('F:\Box Sync\Research\Polarimetry'),
        prep_dir = 'Data 02 - Python prepped images',
        mid_analysis_dir = 'Data 03 - Mid-python analysis images',
        post_analysis_dir = 'Data 04 - Analysis results and graphics'):
        
    retardance_dir = mid_analysis_dir + '\\Step 00 - PS Intensity to Retardance'
    
    resize_dir = mid_analysis_dir + '\\Step 01 - Resizing images'
    reg_dir = mid_analysis_dir + '\\Step 02 - Registered images'
    mask_dir = mid_analysis_dir + '\\Step 03 - Masked images'
    eight_bit_dir = mid_analysis_dir + '\\Step 04 - Eight-bit images'
    tile_dir = mid_analysis_dir + '\\Step 05 - Tiling images'
    
    ssim_dir = post_analysis_dir + '\\CW-SSIM Values'
    cyto_dir = post_analysis_dir + '\\Cytospectre'

    dir_dict = {
        "ps_large": os.path.join(base_dir, prep_dir, 'PS_Large'),
        "mmp_small": os.path.join(base_dir, prep_dir, 'MMP_Small'),
        "shg_large": os.path.join(base_dir, prep_dir, 'SHG_Large'),
        "mhr_large": os.path.join(base_dir, prep_dir, 'MHR_Large'),
        "mlr_large": os.path.join(base_dir, prep_dir, 'MLR_Large'),
        "mlr_large_orient": os.path.join(base_dir, prep_dir, 
                                         'MLR_Large', 'Orientation'),

        "ps_large_ret": os.path.join(base_dir, retardance_dir),

        "ps_small": os.path.join(base_dir,resize_dir,'PS_Small'),
        "shg_small": os.path.join(base_dir,resize_dir,'SHG_Small'),
        "mmp_large": os.path.join(base_dir,resize_dir,'MMP_Large'),
        "mhr_small": os.path.join(base_dir, resize_dir, 'MHR_Small'),
        "mlr_small": os.path.join(base_dir, resize_dir, 'MLR_Small'),

        "mhr_small_reg": os.path.join(base_dir,reg_dir,'MHR_Small_Reg'),
        "mlr_small_reg": os.path.join(base_dir,reg_dir,'MLR_Small_Reg'),
        "mmp_small_reg": os.path.join(base_dir,reg_dir,'MMP_Small_Reg'),
        "shg_small_reg": os.path.join(base_dir,reg_dir,'SHG_Small_Reg'),

        "mhr_large_reg": os.path.join(base_dir,reg_dir,'MHR_Large_Reg'),
        "mlr_large_reg": os.path.join(base_dir,reg_dir,'MLR_Large_Reg'),
        'mlr_large_reg_orient': os.path.join(base_dir, reg_dir, 'MLR_Large_Reg_Orient'),
        "mmp_large_reg": os.path.join(base_dir,reg_dir,'MMP_Large_Reg'),
        "shg_large_reg": os.path.join(base_dir,reg_dir,'SHG_Large_Reg'),

        "ps_small_mask": os.path.join(base_dir,mask_dir,'PS_Small_Mask'),
        "shg_small_mask": os.path.join(base_dir,mask_dir,'SHG_Small_Mask'),
        "mlr_small_mask": os.path.join(base_dir,mask_dir,'MLR_Small_Mask'),

        "ps_large_mask": os.path.join(base_dir,mask_dir,'PS_Large_Mask'),
        "shg_large_mask": os.path.join(base_dir,mask_dir,'SHG_Large_Mask'),
        "mlr_large_mask": os.path.join(base_dir,mask_dir,'MLR_Large_Mask'),
        "mlr_large_mask_orient": os.path.join(base_dir, mask_dir, 'MLR_Large_Mask_Orient'),

        "ps_large_8bit": os.path.join(base_dir, eight_bit_dir,'PS_Large_8Bit'),
        "shg_large_8bit": os.path.join(base_dir, eight_bit_dir,'SHG_Large_8Bit'),
        "mmp_large_8bit": os.path.join(base_dir, eight_bit_dir,'MMP_Large_8Bit'),
        "mhr_large_8bit": os.path.join(base_dir, eight_bit_dir,'MHR_Large_8Bit'),
        "mlr_large_8bit": os.path.join(base_dir, eight_bit_dir,'MLR_Large_8Bit'),

        "ps_small_8bit": os.path.join(base_dir, eight_bit_dir,'PS_Small_8Bit'),
        "shg_small_8bit": os.path.join(base_dir, eight_bit_dir,'SHG_Small_8Bit'),
        "mmp_small_8bit": os.path.join(base_dir, eight_bit_dir,'MMP_Small_8Bit'),
        "mhr_small_8bit": os.path.join( base_dir, eight_bit_dir,'MHR_Small_8Bit'),
        "mlr_small_8bit": os.path.join(base_dir, eight_bit_dir,'MLR_Small_8Bit'),

        "ps_tile": os.path.join(base_dir, tile_dir,'PS_Tiles'),
        "shg_tile": os.path.join(base_dir, tile_dir,'SHG_Tiles'),
        "mmp_tile": os.path.join(base_dir, tile_dir,'MMP_Tiles'),
        "mhr_tile": os.path.join(base_dir, tile_dir,'MHR_Tiles'),
        "mlr_tile": os.path.join(base_dir, tile_dir,'MLR_Tiles'),

        "ssim": os.path.join(base_dir, ssim_dir),
        "cyto": os.path.join(base_dir, cyto_dir)
    }
    
    for key in dir_dict:
        os.makedirs(dir_dict[key], exist_ok=True)
    
    return dir_dict    