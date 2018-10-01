# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 13:00:47 2018

@author: mpinkert
"""

import mp_img_manip.cw_ssim as cw_ssim
import mp_img_manip.polarimetry.dir_dictionary as dird
import datetime

dir_dict = dird.create_dictionary()

mlr_mhr_small =  [dir_dict['mlr_small_reg'], dir_dict['mhr_small_reg']]
mlr_mhr = [dir_dict['mlr_large_reg'], dir_dict['mhr_large_reg']]


date = str(datetime.date.today())

output_name_small = 'CW_SSIM_Small_' + date + '.csv'
output_name = 'CW-SSIM_' + date + '.csv'


cw_ssim.bulk_compare_ssim(mlr_mhr_small, dir_dict['ssim'], output_name)

cw_ssim.bulk_compare_ssim(mlr_mhr, dir_dict['ssim'], output_name)

