# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""

import SimpleITK as sitk
import mp_img_manip.itkscripts as mitk
import mp_img_manip.bulk_img_processing as blk
import numpy as np

def supervisedRegisterImages(fixedPath, movingPath):
    
    fixedImg = mitk.setupImg(fixedPath)
    movingImg = mitk.setupImg(movingPath, setupOffset = True)
    
    goodRegister = False
    
    while not goodRegister:    
        (transform, metric, optimizer) = mitk.affineRegister(fixedImg, movingImg)
        goodRegister = mitk.askIfGoodRegister()
        
    registeredImg = sitk.Resample(movingImg, fixedImg, transform, sitk.sitkLinear, 0.0, movingImg.GetPixelID())    
    
    return registeredImg
    

def bulkSupervisedRegisterImages(fixedDir, movingDir, outputDir, outputSuffix):
    
    (fixedImgPathList, movingImgPathList) = blk.findSharedImages(fixedDir, movingDir)
    
    for i in range(0, np.size(fixedImgPathList)):
        registeredImg = supervisedRegisterImages(fixedImgPathList[i], movingImgPathList[i])
        registeredPath = blk.createNewImagePath(movingImgPathList[i], outputDir, outputSuffix)
        sitk.WriteImage(registeredImg, registeredPath)