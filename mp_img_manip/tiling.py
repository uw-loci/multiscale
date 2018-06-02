import os

import numpy as np
import SimpleITK as sitk
from pathlib import Path

import mp_img_manip.utility_functions as util
import mp_img_manip.bulk_img_processing as blk


def get_tile_start_end_index(tile_number, tile_size,
                             tile_offset = None, tile_separation = None):
    """Calculate the starting and ending index along a single dimension"""

    if not tile_separation:
        tile_separation = tile_size
        
    if not tile_offset:
        tile_offset = 0
            
    start_index = (tile_number*tile_separation) + tile_offset
    end_index = start_index + tile_size
    
    return start_index, end_index


def generate_tile_start_end_index(total_num_tiles, tile_size,
                                  tile_offset=None, tile_separation=None):

    if not tile_separation:
        tile_separation = tile_size
        
    if not tile_offset:
        tile_offset = 0
    
    for x in range(total_num_tiles[0]):
        for y in range(total_num_tiles[1]):
            tile_number = np.array([x,y])
            start_index = (tile_number*tile_separation)+tile_offset
            end_index = start_index + tile_size
            yield start_index, end_index, tile_number 
    
    
def generate_tile(input_array, tile_size, tile_separation=None):
    
    image_dimens = np.shape(input_array)
    
    total_num_tiles, tile_offset = calculate_number_of_tiles(
            image_dimens, tile_size)
    
    for start, end, tile_number in generate_tile_start_end_index(
            total_num_tiles, tile_size,
            tile_offset=tile_offset, tile_separation=tile_separation):
    
        yield input_array[start[0]:end[0], start[1]:end[1]], tile_number
        
        
def calculate_number_of_tiles(size_of_image_dimension, tile_size,
                              tile_separation=None):
    """Calculate the number of tiles that fit along an image dimension,
     given a certain tile size, and step size."""
    
    border = 0
    
    if not tile_separation:
        tile_separation = tile_size
            
    if tile_size > tile_separation:
        border = (tile_size - tile_separation)

    number_of_tiles = []
    offset = []

    for i in range(2):
        idx_range = size_of_image_dimension[i]-2*border
        
        num_tiles = np.fix(idx_range/tile_separation)
        number_of_tiles.append(int(num_tiles))
        
        remainder = np.remainder(idx_range,tile_separation)  
        offset.append(int(np.fix(remainder/2) + border))

    return number_of_tiles, offset


def tile_passes_threshold(tile, intensity_threshold, number_threshold,
                          input_max_value=255):
    """Given a np array, check if it has enough entries larger than a value"""
    
    perc_int = input_max_value*0.01*intensity_threshold 
    perc_num = np.size(tile)*0.01*number_threshold
        
    thresholded_tile = np.ma.masked_less_equal(tile, perc_int)   
    num_values = np.ma.count(thresholded_tile)
        
    if num_values >= perc_num:
        return True
    else:
        return False
    
    
def query_tile_size_and_separation(diff_separation=False):
    message_tile_size = 'How many pixels should the tile width/height be? >>>'
    tile_size = util.query_int(message_tile_size)

    if diff_separation:       
        message_separation = 'What is the separation between tiles?'
        separation = util.query_int(message_separation)
    else:
        separation = tile_size
    
    return tile_size, separation


def query_tile_thresholds():
    message_intensity = 'What percentage intensity is the value threshold? >>>'
    message_number = 'What percentage of pixels above the threshold? >>>'
    
    intensity_threshold = util.query_int(message_intensity)
    number_threshold = util.query_int(message_number)
    
    return intensity_threshold, number_threshold


def write_tile(tile, image_path, output_dir, output_suffix, x, y):
    
    tile_image = sitk.GetImageFromArray(tile)
                
    tile_suffix = output_suffix + '_' + str(x) + 'x-' +str(y) + 'y'
    tile_path = blk.create_new_image_path(image_path, output_dir,
                                                      tile_suffix)
    sitk.WriteImage(tile_image, str(tile_path))
    

def extract_image_tiles(image_path, output_dir, output_suffix,
                          diff_separation = False,
                          tile_size = None, tile_separation = None,
                          intensity_threshold = None,
                          number_threshold = None):
    
    print('Extracting tiles from {0}'.format(image_path.name))
    
    if not tile_size:
        tile_size, tile_separation = query_tile_size_and_separation(diff_separation)
        
    if not intensity_threshold or not number_threshold:
        intensity_threshold, number_threshold = query_tile_thresholds()
    
    output_suffix_with_thresholds = (output_suffix + 
                                     '_IntThresh{0}-NumThresh{1}'.format(
                                             intensity_threshold, 
                                             number_threshold))

    input_image = sitk.ReadImage(str(image_path))
    input_array = sitk.GetArrayFromImage(input_image)
    input_max_value = np.max(input_array)

    for tile, tile_number in generate_tile(input_array, tile_size, 
                                           tile_separation=tile_separation):
        if tile_passes_threshold(tile,
                                 intensity_threshold, number_threshold,
                                 input_max_value=input_max_value):
            
            write_tile(tile, image_path, output_dir, 
                           output_suffix_with_thresholds,
                           tile_number[0], tile_number[1])
    
            
def bulk_extract_image_tiles(input_dir, output_dir, output_suffix,
                             search_subdirs=False,
                             diff_separation=False,
                             tile_size=None, tile_separation=None,
                             intensity_threshold=None,
                             number_threshold=None):
    
    if not tile_size:
        tile_size, tile_separation = query_tile_size_and_separation(diff_separation)
    if not tile_separation:
        tile_separation = tile_size
    if not intensity_threshold or not number_threshold:
        intensity_threshold, number_threshold = query_tile_thresholds()
        
    if search_subdirs:    
        image_path_list = util.list_filetype_in_subdirs(input_dir, '.tif')
    else:
        image_path_list = util.list_filetype_in_dir(input_dir, '.tif')
    
    for path in image_path_list:   
        output_dir_sub = os.path.join(output_dir, path.stem)
        os.makedirs(output_dir_sub, exist_ok = True)
        
        extract_image_tiles(path, output_dir_sub, 
                            output_suffix,
                            diff_separation, tile_size, tile_separation,
                            intensity_threshold, number_threshold)
            
