# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""


import os
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.itkscripts as mitk


def perform_registrations():
    """Overall script to perform both mmp and shg registrations, along with mask"""

def register_mmp_to_ps():
    """Register MMP images to PS images.
    
    Output: A transform file
            Small registered MMP images
            Large registered MMP images
            cropped PS images
        """
    return

def register_shg_to_ps():
    """Register SHG images to PS images.
    
    Output: A transform file
        
            Small registered and cropped SHG images
            Large registered and cropped SHG images
        """
    return

def compare_ssim(dirOne, dirTwo):
    """Compare SSIM between two file directories
    """
    return

def downsample_ps_and_shg():
    return


    
