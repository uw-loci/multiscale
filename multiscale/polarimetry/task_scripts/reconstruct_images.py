# -*- coding: utf-8 -*-
"""
Reconstruct dataframes into parametric images

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
import multiscale.polarimetry.task_scripts.dir_dictionary as dird


def bulk_construct_images(df_single_modality_variable, modality, dir_modality,
                          dir_output, suffix_output):
        
        # todo: fix the issue of string/number going into multiple groups.  e.g. [1367, 5], ['1367', 5]
        for grp, df in df_single_modality_variable.groupby(['Mouse', 'Slide']):
                
                sample = str(grp[0]) + '-' + str(grp[1])
                path_image = blk.create_new_image_path(sample, dir_output, suffix_output)
                if path_image.exists():
                        continue
                        
                if df.isnull().all():
                        continue
                        
                print('\nCompiling results from {0}_{1} into image'.format(sample, modality))
                
                try:
                        matching_image = find_matching_image(grp, dir_modality)
                        if matching_image is None:
                                continue
                        path_to_image = Path(dir_modality, find_matching_image(grp, dir_modality))

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
        
        if path_image:
                return path_image[0]
        else:
                return None


def write_image(image_array, path_image):
        image = sitk.Cast(sitk.GetImageFromArray(np.transpose(image_array)), sitk.sitkFloat32)
        sitk.WriteImage(image, str(path_image))

#
dir_dict = dird.create_dictionary()
# #
# path_averages = Path(dir_dict['anal'], 'ROIs_averaged_from_base_image_old.csv')
# #
# ret_thresh = 0.5
# #
# df_average = pd.read_csv(path_averages, header=[0, 1], index_col=[0, 1, 2, 3],
#                           dtype={'Mouse': object, 'Slide': object})
# #
# df_ret = df_average.loc[:, 'Retardance'].copy()
# # df_orient = df_average.loc[:, 'Orientation'].copy()
# # df_orient = df_orient[df_ret > ret_thresh]
# df_align = df_average.loc[:, 'Alignment'].copy()
# df_align = df_align[df_ret > ret_thresh]
#
# align_path = Path(dir_dict['images'], 'Alignment')
#
#
# bulk_construct_images(df_align['PS-O'].dropna(), 'PS', dir_dict['ps_reg'],
#                       align_path, 'PS_AvgAlign_Thresh0-5')
# bulk_construct_images(df_align['MHR-O'], 'MHR-O', dir_dict['mhr_large_reg'],
#                       align_path, 'MHR_AvgAlign_Thresh0-5')
# bulk_construct_images(df_align['MLR-O'], 'MLR-O', dir_dict['mhr_large_reg'],
#                       align_path, 'MLR_AvgAlign_Thresh0-5')
# #
# bulk_construct_images(df_orient['PS-O'].dropna(), 'PS', dir_dict['ps_reg'],
#                       dir_dict['images'], 'PS_Avg_Old_Thresh0-5')
# bulk_construct_images(df_orient['MHR-O'], 'MHR-O', dir_dict['mhr_large_reg'],
#                       dir_dict['images'], 'MHR-Avg_Old_Thresh0-5')
# bulk_construct_images(df_orient['MLR-O'], 'MLR-O', dir_dict['mhr_large_reg'],
#                       dir_dict['images'], 'MLR-Avg_Old_Thresh0-5')
# #
# path_rois = Path(dir_dict['anal'], 'Old files', 'Curve-Align_ROIs_18.csv')
# df_rois = pd.read_csv(path_rois, header=[0, 1], index_col=[0, 1, 2, 3],
#                       dtype={'Mouse': object, 'Slide': object})
#
# bulk_construct_images(df_rois['Orientation', 'MLR'], 'MLR', Path(r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Registered images\Old registrations\MLR_Large_Reg'),
#                       dir_dict['images'], 'MLR_ROI_Orientation_CurveAlign')
#
path_rois = Path(dir_dict['anal'], 'Curve-Align_ROIs.csv')
#
df_rois = pd.read_csv(path_rois, header=[0, 1], index_col=[0, 1, 2, 3],
                       dtype={'Mouse': object, 'Slide': object})
bulk_construct_images(df_rois['Alignment', 'SHG'], 'SHG', dir_dict['shg_large'],
                      align_path, 'SHG_Align')