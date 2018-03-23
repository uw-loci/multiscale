# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 10:50:24 2018

@author: mpinkert
"""


import mp_img_manip.bulk_img_processing as blk

import numpy as np
import os
import matplotlib.pyplot as plt

from PIL import Image

from ssim import SSIM


def write_ssim(ssim):
    return

def compare_ssim(one_path, two_path):
    """Calculate the complex wavelet structural similarity metric
    """
    one = Image.open(one_path)
    two = Image.open(two_path)
    
    print('Calculating CW-SSIM between {0} and {1}'.format(
            os.path.basename(one), os.path.basename(two)))
    
    ssim = SSIM(one).cw_ssim_value(two)
    
    print('The CW-SSIM between {0} and {1} = {2}'.format(
            os.path.basename(one), os.path.basename(two), str(ssim)))
    
    return ssim


def bulk_compare_ssim(one_dir, two_dir):
    """Calculate CW-SSIM between images in several file directories
    """
    (one_path_list, two_path_list) = blk.find_shared_images(
            one_dir, two_dir)
    
    for i in range(0, np.size(one_path_list)):
        ssim = compare_ssim(one_path_list[i], two_path_list[i])
    
        
    
    return


