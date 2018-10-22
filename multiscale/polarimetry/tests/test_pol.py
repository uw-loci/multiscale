# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 09:12:30 2018

@author: mpinkert
"""

import multiscale.polarimetry as pol
import SimpleITK as sitk
import unittest
import numpy as np


class convertIntensityToRetardance_TestSuite(unittest.TestCase):

    def test_nm_to_deg(self):
        inputValue = np.array([[100, 200],[563,843]])
        inputImg = sitk.GetImageFromArray(inputValue)
        inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
        
        outputValue = inputValue * (35/65535) * (360/546)
        outputImg = sitk.GetImageFromArray(outputValue)
        
        self.assertEqual(pol.convertIntensityToRetardance(inputImg), 
                         outputImg)
        
    def test_nm_to_deg_diff_wavelength(self):
        inputValue = np.array([[100, 200],[563,843]])
        inputImg = sitk.GetImageFromArray(inputValue)
        inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
        
        wl = 600
        
        outputValue = inputValue * (35/65535) * (360/600)
        outputImg = sitk.GetImageFromArray(outputValue)
        
        self.assertEqual(pol.convertIntensityToRetardance(
                inputImg, wavelength = wl), 
                         outputImg)
        
    def test_nm_to_deg_diff_ceiling(self):
        inputValue = np.array([[100, 200],[563,843]])
        inputImg = sitk.GetImageFromArray(inputValue)
        inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
        
        ceiling = 50
        
        outputValue = inputValue * (50/65535) * (360/546)
        outputImg = sitk.GetImageFromArray(outputValue)
        
        self.assertEqual(pol.convertIntensityToRetardance(
                inputImg, retCeiling = ceiling), 
                         outputImg)
            
    def test_nm_to_nm(self):
        inputValue = np.array([[100, 200],[563,843]])
        inputImg = sitk.GetImageFromArray(inputValue)
        inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
        
        outputValue = inputValue * (35/65535)
        outputImg = sitk.GetImageFromArray(outputValue)
        
        self.assertEqual(pol.convertIntensityToRetardance(
                inputImg, degOutput = False), 
                outputImg)
        
    def test_deg_to_deg(self):
        inputValue = np.array([[100, 200],[563,843]])
        inputImg = sitk.GetImageFromArray(inputValue)
        inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
        
        outputValue = inputValue * (35/65535)
        outputImg = sitk.GetImageFromArray(outputValue)
        
        self.assertEqual(pol.convertIntensityToRetardance(
                inputImg, nmInput = False), 
                         outputImg)
        
    def test_deg_to_nm(self):
        inputValue = np.array([[100, 200],[563,843]])
        inputImg = sitk.GetImageFromArray(inputValue)
        inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
        
        outputValue = inputValue * (35/65535) * (546/360) 
        outputImg = sitk.GetImageFromArray(outputValue)
        
        self.assertEqual(pol.convertIntensityToRetardance(
                inputImg, degOutput = False, nmInput = False), 
                         outputImg)

if __name__ == '__main__':
    unittest.main(verbosity=2)