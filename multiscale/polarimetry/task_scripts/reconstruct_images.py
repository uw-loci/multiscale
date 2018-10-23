# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 14:53:54 2018

@author: mpinkert
"""
import pandas as pd
import os
from pathlib import Path
import SimpleITK as sitk
import numpy as np

import multiscale.itk.metadata as meta
import multiscale.tiling as til
import multiscale.bulk_img_processing as blk
import multiscale.polarimetry.dir_dictionary as dird


def bulk_construct_images(df_single_modality_variable, modality, dir_modality,
                          dir_output, suffix_output):
        for grp, df in df_single_modality_variable.groupby(['Mouse', 'Slide']):
                
                sample = str(grp[0]) + '-' + str(grp[1])
                path_image = blk.create_new_image_path(sample, dir_output, suffix_output)
                if path_image.exists():
                        continue
                
                print('\nCompiling results from {0}_{1} into image'.format(sample, modality))
                
                if df.isnull().all():
                        continue
                
                path_to_image = Path(dir_modality, find_matching_image(grp, dir_modality))
                try:
                        dimensions = get_image_dimensions(path_to_image)
                except OSError:
                        print('Cannot open original image file')
                        continue
                
                image_array = til.roi_values_to_sitk_image_array(df, dimensions, modality)
                
                write_image(image_array, path_image)


def get_image_dimensions(path_to_image, tile_size=np.array([512, 512])):
        size_full = meta.get_image_size_from_path(path_to_image)
        num_tiles, offset_tile = til.calculate_number_of_tiles(size_full, tile_size)
        size_roi = np.array(num_tiles) * 8
        
        return size_roi


def find_matching_image(group, dir_modality):
        sample = str(group[0]) + '-' + str(group[1])
        path_image = [Path(image) for image in os.listdir(dir_modality) if (image.startswith(sample) and
                                                                            image.endswith('.tif'))]
        
        return path_image[0]


def write_image(image_array, path_image):
        image = sitk.Cast(sitk.GetImageFromArray(np.transpose(image_array)), sitk.sitkFloat32)
        sitk.WriteImage(image, str(path_image))


dir_dict = dird.create_dictionary()

path_averages = Path(dir_dict['anal'], 'ROIs_averaged_from_base_image.csv')
df_averages = pd.read_csv(path_averages, header=[0, 1], index_col=[0, 1, 2, 3],
                          dtype={'Mouse': object, 'Slide': object})
#
bulk_construct_images(df_averages['Orientation', 'MLR-O'], 'MLR-O', dir_dict['mlr_large_reg'],
                      dir_dict['images'], 'MLR-O_Averaged_Orientation')
bulk_construct_images(df_averages['Orientation', 'MHR-O'], 'MHR-O', dir_dict['mhr_large_reg'],
                      dir_dict['images'], 'MHR-O_Averaged_Orientation')

# path_rois = Path(dir_dict['anal'], 'Curve-Align_ROIs.csv')
# df_rois = pd.read_csv(path_rois, header=[0, 1], index_col=[0, 1, 2, 3],
#                       dtype={'Mouse': object, 'Slide': object})
#
# bulk_construct_images(df_rois['Orientation', 'SHG'], 'SHG', dir_dict['shg_large'],
#                       dir_dict['images'], 'SHG_ROI_Orientation')
