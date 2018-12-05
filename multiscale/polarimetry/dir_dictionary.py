# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 10:56:37 2018

@author: mpinkert

My personal directories
"""

import os


def create_test_dictionary(test_dir='tests'):
        test_files_dir = os.path.join(test_dir, 'test_files')
        
        test_dict = {
                'test_dir': test_dir,
                'test_files_dir': test_files_dir,
                'test_cyto': os.path.join(test_files_dir, 'test_cyto')
        }
        return test_dict


def create_dictionary(
            base_dir=os.path.normpath(r'F:\Research\Polarimetry'),
            prep_dir='Data 02 - Python prepped images',
            mid_analysis_dir='Data 03 - Mid-python analysis images',
            post_analysis_dir='Data 04 - Analysis results and graphics'):
        # retardance_dir = mid_analysis_dir + '\\Step 00 - PS Intensity to Retardance'
        #mask_dir = mid_analysis_dir + '\\Masked images'
        
        #resize_dir = mid_analysis_dir + '\\Step 02 - Resizing images'
        reg_dir = mid_analysis_dir + '\\Registered images'
        tile_dir = mid_analysis_dir + '\\Tiled images'
        
        #    eight_bit_dir = mid_analysis_dir + '\\Step 05 - Eight-bit images'
        
        ssim_dir = post_analysis_dir + '\\CW-SSIM Values'
        cyto_dir = post_analysis_dir + '\\Cytospectre'
        curve_dir = post_analysis_dir + '\\Curve Align'
        avg_dir = post_analysis_dir + '\\Averaged Retardance'
        
        dir_dict = {
                "shg_large": os.path.join(base_dir, prep_dir, 'SHG_Large'),
                "mhr_large": os.path.join(base_dir, prep_dir, 'MHR_Large'),
                "mhr_large_orient": os.path.join(base_dir, prep_dir, 'MHR_Large_Orient'),
                "mlr_large": os.path.join(base_dir, prep_dir, 'MLR_Large'),
                "mlr_large_orient": os.path.join(base_dir, prep_dir, 'MLR_Large_Orient'),
                #"he_small": os.path.join(base_dir, resize_dir, 'HE_Small'),
                "he_large": os.path.join(base_dir, prep_dir, 'HE_Large'),
                
                #"shg_small": os.path.join(base_dir, resize_dir, 'SHG_Small'),
                #"mhr_small": os.path.join(base_dir, resize_dir, 'MHR_Small'),
                #"mlr_small": os.path.join(base_dir, resize_dir, 'MLR_Small'),
                #"mhr_small_orient": os.path.join(base_dir, resize_dir, 'MHR_Small_Orient'),
                #"mlr_small_orient": os.path.join(base_dir, resize_dir, 'MLR_Small_Orient'),
                
                #"mhr_small_reg": os.path.join(base_dir, reg_dir, 'MHR_Small_Reg'),
                #"mlr_small_reg": os.path.join(base_dir, reg_dir, 'MLR_Small_Reg'),
                #"mhr_small_reg_orient": os.path.join(base_dir, reg_dir, 'MHR_Small_Reg_Orient'),
                #"mlr_small_reg_orient": os.path.join(base_dir, reg_dir, 'MLR_Small_Reg_Orient'),
                #"he_small_reg": os.path.join(base_dir, reg_dir, 'HE_Small_Reg'),
                
                "mhr_large_reg": os.path.join(base_dir, reg_dir, 'MHR_Large_Reg'),
                "mlr_large_reg": os.path.join(base_dir, reg_dir, 'MLR_Large_Reg'),
                'mlr_large_reg_orient': os.path.join(base_dir, reg_dir, 'MLR_Large_Reg_Orient'),
                'mhr_large_reg_orient': os.path.join(base_dir, reg_dir, 'MHR_Large_Reg_Orient'),
                "he_large_reg": os.path.join(base_dir, reg_dir, 'HE_Large_Reg'),
                
                "ps": os.path.join(base_dir, prep_dir, 'PS_Large'),
                "ps_orient": os.path.join(base_dir, prep_dir, 'PS_Large_Orient'),
                "ps_reg": os.path.join(base_dir, reg_dir, 'PS_Large_Reg'),
                "ps_reg_raw": os.path.join(base_dir, reg_dir, 'PS_Large_Reg', 'Raw'),
                "ps_reg_orient": os.path.join(base_dir, reg_dir, 'PS_Large_Reg_Orient'),
                "ps_reg_orient_raw": os.path.join(base_dir, reg_dir, 'PS_Large_Reg_Orient', 'Raw'),
        
                #"mlr_large_mask": os.path.join(base_dir, mask_dir, 'MLR_Large_Mask'),
                #"mhr_large_mask": os.path.join(base_dir, mask_dir, 'MHR_Large_Mask'),
                #"mlr_large_mask_orient": os.path.join(base_dir, mask_dir, 'MLR_Large_Mask_Orient'),
                #"mhr_large_mask_orient": os.path.join(base_dir, mask_dir, 'MHR_Large_Mask_Orient'),
                
                "shg_tile": os.path.join(base_dir, tile_dir, 'SHG_Tiles'),
                "mhr_tile": os.path.join(base_dir, tile_dir, 'MHR_Tiles'),
                "mlr_tile": os.path.join(base_dir, tile_dir, 'MLR_Tiles'),
                
                "ssim": os.path.join(base_dir, ssim_dir),
                "cyto": os.path.join(base_dir, cyto_dir),
                "curve": os.path.join(base_dir, curve_dir),
                "avg_ret": os.path.join(base_dir, avg_dir),
                
                "images": os.path.join(base_dir, post_analysis_dir, 'Images'),
                "anal": os.path.join(base_dir, post_analysis_dir)
                
        }
        
        for key in dir_dict:
                os.makedirs(dir_dict[key], exist_ok=True)
        
        return dir_dict
