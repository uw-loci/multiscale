# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 12:58:50 2018

@author: mpinkert
"""

import multiscale.toolkits.cw_ssim as ssim
import multiscale.polarimetry.dir_dictionary as dird
import datetime

dir_dict = dird.create_dictionary()

#mlr_ps = [dir_dict['mlr_small_8bit'], dir_dict['ps_small']]
mlr_shg = [dir_dict['mlr_small_mask'], dir_dict['shg_small_reg']]
#shg_ps = [dir_dict['shg_small_reg'], dir_dict['ps_small']]


date = str(datetime.date.today())
output_name = 'CW-SSIM_' + date + '.csv'

#ssim.bulk_compare_ssim(mlr_ps, dir_dict['ssim'], output_name)
ssim.bulk_compare_ssim(mlr_shg, dir_dict['ssim'], output_name)
#ssim.bulk_compare_ssim(shg_ps, dir_dict['ssim'], output_name)

