# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 12:58:50 2018

@author: mpinkert
"""

import mp_img_manip.cw_ssim as ssim
import mp_img_manip.dir_dictionary as dird

dir_dict = dird.create_dictionary()

mmp_ps = [dir_dict['mmp_small_reg'], dir_dict['ps_small_mask']]
mmp_shg = [dir_dict['mmp_small_8bit'], dir_dict['shg_small_8bit']]
shg_ps = [dir_dict['shg_small_8bit'], dir_dict['ps_small_8bit']]



output_name = 'CW-SSIM Small physical mmp_ps 8bit else.csv'

ssim.bulk_compare_ssim(mmp_ps, dir_dict['ssim'], output_name)
ssim.bulk_compare_ssim(mmp_shg, dir_dict['ssim'], output_name)
ssim.bulk_compare_ssim(shg_ps, dir_dict['ssim'], output_name)

