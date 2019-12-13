# -*- coding: utf-8 -*-
"""
Compare polarimetry images and calculate the SSIM values for each tile.

Created on Fri Jul 13 13:00:47 2018

@author: mpinkert
"""

import multiscale.toolkits.cw_ssim as cw_ssim
import multiscale.polarimetry.task_scripts.dir_dictionary as dird
from pathlib import Path

dir_dict = dird.create_dictionary()

base_dir = Path(r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 04 - Tiling images\Flipped indices')
mhr_dir = Path(base_dir, 'MHR_Tiles')
mlr_dir = Path(base_dir, 'MLR_Tiles')
shg_dir = Path(base_dir, 'SHG_Tiles')

dir_list = [shg_dir, mhr_dir, mlr_dir]

output_name = 'CW-SSIM_Tiles.csv'

cw_ssim.calculate_ssim_across_multiple_directories(dir_list, dir_dict['ssim'], output_name,
                                                   file_parts_to_compare=[0, 2])

#
# mlr_mhr_small =  [dir_dict['mlr_small_reg'], dir_dict['mhr_small_reg']]
# mlr_mhr = [dir_dict['mlr_large_reg'], dir_dict['mhr_large_reg']]
#
#
# date = str(datetime.date.today())
#
# output_name_small = 'CW_SSIM_Small_' + date + '.csv'
# output_name = 'CW-SSIM_' + date + '.csv'
#
#
# cw_ssim.bulk_compare_ssim(mlr_mhr_small, dir_dict['ssim'], output_name)
#
# cw_ssim.bulk_compare_ssim(mlr_mhr, dir_dict['ssim'], output_name)
