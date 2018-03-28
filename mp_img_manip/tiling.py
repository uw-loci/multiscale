import numpy as np


def get_tile_start_end_index(tile_number, tile_size,
                             tile_offset = None, tile_step_size = None):
    """Calculate the starting and ending index along a single dimension"""

    #todo: implement tests

    if not tile_step_size:
        tile_step_size = tile_size
        
    if not tile_offset:
        tile_offset = 0
            
    start_index = ((tile_number-1)*tile_step_size)+tile_offset - 1
    end_index = start_index + tile_size - 1
    
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

    return (int(number_of_tiles), int(offset))

def tile_passes_threshold(tile, val_threshold, num_threshold):
    """Given a np array, check if it has enough entries larger than a value"""
    
    thresholded_tile = np.ma.masked_greater(tile, val_threshold)
    
    num_values = np.ma.count(thresholded_tile)
    
    if num_values > num_threshold:
        return True
    else:
        return False
    