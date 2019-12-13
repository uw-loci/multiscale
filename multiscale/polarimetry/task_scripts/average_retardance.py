# -*- coding: utf-8 -*-
"""
This script shows how to calculate averaged retardance values, including converting Polscope intensity to retardance

Created on Wed Jul 18 16:18:01 2018

@author: mpinkert
"""

import multiscale.polarimetry.task_scripts.dir_dictionary as dird
import multiscale.utility_functions as util
import multiscale.polarimetry.retardance as pol
import pandas as pd
import re

from pathlib import Path


def convert_ps_to_retardance(dir_dict):
        pol.bulk_intensity_to_retardance(dir_dict['ps_reg'], dir_dict['ps_reg'], 'PS_Large_Registered')
        pol.bulk_orientation_to_proper_degrees(dir_dict['ps_reg_orient'], dir_dict['ps_reg_orient'],
                                               'PS_Large_Registered_Orient')

def average_images(dir_dict):
        
        pol.bulk_process_orientation_alignment(
                dir_dict['mhr_large_reg'], dir_dict['mhr_large_reg_orient'], dir_dict['avg_ret'],
                'MHR', [512, 512], roi_size=[64, 64])
        
        pol.bulk_process_orientation_alignment(
                dir_dict['mlr_large_reg'], dir_dict['mlr_large_reg_orient'], dir_dict['avg_ret'],
                'MLR', [512, 512], roi_size=[64, 64])
        
        pol.bulk_process_orientation_alignment(dir_dict['ps_reg'], dir_dict['ps_reg_orient'], dir_dict['avg_ret'],
                                               'PS', [512, 512], roi_size=[64, 64])

def scrape_averaged_files_to_df(dir_avg):
        list_csvs = util.list_filetype_in_dir(dir_avg, 'csv')
        list_dfs = [pd.read_csv(item) for item in list_csvs if re.search('64', str(item))]
        
        df_avg_raw = pd.concat(list_dfs)
        
        df_avg = pd.pivot_table(df_avg_raw, index=['Mouse', 'Slide', 'Tile', 'ROI'],
                                values=['Alignment', 'Orientation', 'Retardance'],
                                columns='Modality')
        
        df_avg = df_avg[df_avg['Retardance'] > 0]
        
        return df_avg


dir_dict = dird.create_dictionary()

convert_ps_to_retardance(dir_dict)

average_images(dir_dict)

dir_avg = dir_dict['avg_ret']
df_avg = scrape_averaged_files_to_df(dir_avg)


path_avg = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics',
                'ROIs_averaged_from_base_image_old2.csv')

df_avg.to_csv(path_avg)