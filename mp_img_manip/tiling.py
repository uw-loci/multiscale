import numpy as np
import SimpleITK as sitk
import os
import mp_img_manip.utility_functions as util

def get_tile_start_end_index(tile_number, tile_size,
                             tile_offset = None, tile_step_size = None):
    """Calculate the starting and ending index along a single dimension"""

    #todo: implement tests

    if not tile_step_size:
        tile_step_size = tile_size
        
    if not tile_offset:
        tile_offset = 0
            
    start_index = (tile_number*tile_step_size)+tile_offset
    end_index = start_index + tile_size
    
    return (start_index, end_index)



def calculate_number_of_tiles(size_of_image_dimension, tile_size,
                              tile_step_size = None):
    """Calculate the number of tiles that fit along an image dimension,
     given a certain tile size, and step size."""
    
    border = 0
    
    if not tile_step_size:
        tile_step_size = tile_size
            
    if tile_size > tile_step_size:
        border = (tile_size - tile_step_size)

    idx_range = size_of_image_dimension-2*border

    number_of_tiles = np.fix(idx_range/tile_step_size)
    remainder = np.remainder(idx_range,tile_step_size)  
    offset = np.fix(remainder/2) + border

    return int(number_of_tiles), int(offset)


def tile_passes_threshold(tile, val_threshold, num_threshold):
    """Given a np array, check if it has enough entries larger than a value"""
    
    thresholded_tile = np.ma.masked_less_equal(tile, val_threshold)
        
    num_values = np.ma.count(thresholded_tile)
        
    if num_values > num_threshold:
        return True
    else:
        return False
    
    
def query_tile_size_and_separation(diff_separation = False):
    message_tile_size = 'How many pixels should the tile width/height be?'
    tile_size = util.query_int(message_tile_size)


    if diff_separation:       
        message_separation = 'What is the separation between tiles?'
        separation = util.query_int(message_separation)
    else:
        separation = tile_size

    
    return tile_size, separation


def query_tile_thresholds():
    message_intensity = 'What percentage intensity is the value threshold?'
    message_number = 'What percentage of pixels need to be above the threshold?'
    
    intensity_threshold = util.query_int(message_intensity)
    number_threshold = util.query_int(message_number)
    
    return intensity_threshold, number_threshold




def extract_image_tiles(image_path, output_dir, output_suffix,
                        diff_separation = False):
    
    basename = os.path.basename(image_path)
    print('Extracting tiles from {0}'.format(basename))
    
    input_image = sitk.ReadImage(image_path)
    input_array = sitk.GetArrayFromImage(input_image)
    
    image_dimens = np.shape(input_array)
    tile_size, separation = query_tile_size_and_separation(diff_separation)
