# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 12:53:48 2018

@author: mpinkert
"""

import mp_img_manip.tiling as til
import mp_img_manip.dir_dictionary as dird

dir_dict = dird.create_dictionary()



def extract_tiles_from_8bit_images(tile_size = 512,
                                   intensity_threshold = 1, 
                                   number_threshold = 10):
    
    til.bulk_extract_image_tiles(dir_dict['ps_large_8bit'], 
                                 dir_dict['ps_large_tile'], 
                                 'PS',
                                 tile_size = tile_size, 
                                 intensity_threshold = intensity_threshold, 
                                 number_threshold = number_threshold)
    
    til.bulk_extract_image_tiles(dir_dict['shg_large_8bit'], 
                                 dir_dict['shg_large_tile'], 
                                 'SHG',
                                 tile_size = tile_size, 
                                 intensity_threshold = intensity_threshold, 
                                 number_threshold = number_threshold)
    
    til.bulk_extract_image_tiles(dir_dict['mmp_large_8bit'], 
                                 dir_dict['mmp_large_tile'], 
                                 'MMP',
                                 tile_size = tile_size, 
                                 intensity_threshold = intensity_threshold, 
                                 number_threshold = number_threshold)
    