# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 16:18:01 2018

@author: mpinkert
"""

# What do I need to do?
# Take a registered Registration/Orientation image
# Take analyzed data (in an array)
# Measure average retardance/orientation in the registered image
# Compare to analyzed data

import mp_img_manip.dir_dictionary as dird
import mp_img_manip.utility_functions as util
import pandas as pd
import re

from pathlib import Path

def scrape_averaged_files_to_df(dir_avg):
    list_csvs = util.list_filetype_in_dir(dir_avg, 'csv')
    list_dfs = [pd.read_csv(item) for item in list_csvs if re.search('64', str(item))]
    
    df_avg_raw = pd.concat(list_dfs)
    
    df_avg = pd.pivot_table(df_avg_raw, index=['Mouse', 'Slide', 'Tile', 'ROI'],
                                 values=['Alignment', 'Orientation', 'Retardance'],
                                 columns = 'Modality')
    
    return df_avg
    

dir_dict = dird.create_dictionary()
dir_avg = dir_dict['avg_ret']
df_avg = scrape_averaged_files_to_df(dir_avg)

path_avg = Path()

df_avg.to_csv