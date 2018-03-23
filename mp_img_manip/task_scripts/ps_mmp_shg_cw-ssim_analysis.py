# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 10:50:24 2018

@author: mpinkert
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageOps

from ssim import SSIM

def compare_ssim(one_path, two_path):

    one = Image.open(one_path)
    two = Image.open(two_path)
    
    print('Calculating CW-SSIM between {0} and {1}'.format(
            os.path.basename(one), os.path.basename(two)))
    
    ssim = SSIM(one).cw_ssim_value(two)
    
    print('The CW-SSIM between {0} and {1} = {2}'.format(
            os.path.basename(one), os.path.basename(two), str(ssim)))
    
    return ssim

def bulk_compare_ssim(one_dir, two_dir):
    """Compare SSIM between two file directories
    """
    
    
    return


