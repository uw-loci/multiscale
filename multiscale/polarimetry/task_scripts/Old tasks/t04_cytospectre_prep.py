# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 12:53:48 2018

@author: mpinkert
"""

import multiscale.polarimetry as pol
import multiscale.polarimetry.dir_dictionary as dird

dir_dict = dird.create_dictionary()

#def extract_tiles_from_images(tile_size = 512,
#                                   intensity_threshold = 1, 
#                                   number_threshold = 10):
    
#    til.bulk_extract_image_tiles(dir_dict['ps_large'], 
#                                 dir_dict['ps_tile'],
#                                 'PS',
#                                 tile_size = tile_size, 
#                                 intensity_threshold = intensity_threshold, 
#                                 number_threshold = number_threshold)
#    
#    til.bulk_extract_image_tiles(dir_dict['shg_large_reg'], 
#                                 Path(dir_dict['shg_tile'], 'x64'),
#                                 'SHG',
#                                 tile_size = 64, 
#                                 intensity_threshold = intensity_threshold, 
#                                 number_threshold = number_threshold)
  
#    til.bulk_extract_image_tiles(dir_dict['mlr_mask'],
#                                 dir_dict['mlr_tile'],
#                                 'MLR',
#                                 tile_size = tile_size, 
#                                 intensity_threshold = intensity_threshold, 
#                                 number_threshold = number_threshold)
    

def average_orientation_for_tile_comparison(tile_size = 512,
                                            intensity_threshold = 1,
                                            number_threshold = 10):
    
    pol.bulk_process_orientation_alignment(dir_dict['mlr_large_mask'],
                                           dir_dict['mlr_large_mask_orient'],
                                           dir_dict['cyto'],
                                           tile_size=tile_size)
    
    return
    
#extract_tiles_from_images()
average_orientation_for_tile_comparison()