# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 16:11:52 2018

@author: mpinkert
"""

import mp_img_manip.dir_dictionary as dird
import mp_img_manip.analysis as an
import pandas as pd
from pathlib import Path

dir_dict = dird.create_dictionary()

tile_path = Path('F:\Box Sync\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Curve-Align_Tiles.csv')
roi_path = Path('F:\Box Sync\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Curve-Align_ROIs.csv')
cyto_path = Path('F:\Box Sync\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Cytospectre_Tiles.csv')


def get_dfs(tile_path, roi_path, cyto_path):
    tile_df = pd.read_csv(tile_path, header=[0,1], index_col=[0, 1, 2])
    roi_df = pd.read_csv(roi_path, header=[0,1], index_col=[0, 1, 2, 3])
    cyto_df = pd.read_csv(cyto_path, header=[0,1], index_col=[0, 1, 2])
    
    return tile_df, roi_df, cyto_df



