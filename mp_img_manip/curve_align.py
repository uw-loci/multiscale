# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 10:19:59 2018

@author: mpinkert
"""

import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.tiling as til

import SimpleITK as sitk
import pandas as pd
import numpy as np
import scipy.io as sio
from pathlib import Path
import datetime


def create_rois_from_tile(tile, roi_size):

    date = str(datetime.date.today())
    time = str(datetime.datetime.now().timestamp())
    roi_shape = 1

    tile_dim = np.shape(tile)

    num_rois, roi_offset = til.calculate_number_of_tiles(tile_dim, roi_size, roi_size)

    separate_rois = {}

    for start, end, roi_number in til.generate_tile_start_end_index(num_rois, roi_size,
                                                                    roi_offset):

        roi_def = [start[0], start[1], roi_size[0], roi_size[1]]
        enclosing_rect = [start[0], start[1], end[0], end[1]]
        ym = start[1] + roi_size[1]/2
        xm = start[0] + roi_size[0]/2
        boundary = np.array((1,), dtype=np.object)
        boundary_object = np.array([[start[0], start[1]],
                    [start[0], end[1]],
                    [start[1], end[1]],
                    [start[1], end[0]],
                    [start[0], end[0]]], dtype=np.object)
        boundary[0] = boundary_object
    
        roi = {
            'date': date,
            'time': time,
            'shape': roi_shape,
            'roi': roi_def,
            'enclosing_rect': enclosing_rect,
            'ym': ym,
            'xm': xm,
            'boundary': boundary
        }

        roi_name = 'ROI' + str(roi_number[0]) + 'x' + str(roi_number[1]) + 'y'

        separate_rois[roi_name] = roi

    return separate_rois


def save_rois(output_dir, tile_number, rois):
    return


def process_image_to_rois(image_path, output_dir, output_suffix='Tile',
                          tile_size=520, tile_separation=512,
                          roi_size=64,
                          intensity_threshold=1,
                          number_threshold=10):

    image = sitk.ReadImage(image_path)
    image_array = sitk.GetArrayFromImage(image)
    max_value = np.max(image_array)

    for tile, tile_number in til.generate_tile(image, tile_size, tile_separation=tile_separation):

        if til.tile_passes_threshold(tile, intensity_threshold, number_threshold, max_value):

            separate_rois = create_rois_from_tile(tile, roi_size)
            save_rois(output_dir, tile_number, separate_rois)
            write_tile(tile, image_path, output_dir, output_suffix,
                       tile_number[0], tile_number[1])


def create_batches_for_chtc(image_dir, batch_size=10):




    return
