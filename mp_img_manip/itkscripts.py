# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 09:04:51 2018

@author: mpinkert
"""

import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
# GUI components (sliders, dropdown...).
#from ipywidgets import interact

# Enable display of HTML.
from IPython.display import clear_output



# Callback invoked when the StartEvent happens, sets up our new data.
def start_plot():
    global metric_values, multires_iterations
    
    metric_values = []
    multires_iterations = []

# Callback invoked when the EndEvent happens, do cleanup of data and figure.
def end_plot():
    global metric_values, multires_iterations
    
    del metric_values
    del multires_iterations
    # Close figure, we don't want to get a duplicate of the plot latter on.
    plt.close()

# Callback invoked when the IterationEvent happens, update our data and display new figure.    
def plot_values(registration_method, fixed_image, moving_image,transform):
    global metric_values, multires_iterations
    

    metric_values.append(registration_method.GetMetricValue())                                       
    # Clear the output area (wait=True, to reduce flickering), and plot current data
    clear_output(wait=True)
    
    alpha = 0.7
    moving_transformed = sitk.Resample(moving_image, fixed_image, transform, 
                                       sitk.sitkLinear, 0.0, 
                                       moving_image.GetPixelIDValue()) 
    
    #Blend the registered and fixed images                                   
    combined = (1.0 - alpha)*fixed_image + alpha*moving_transformed
    combined_eightbit = sitk.Cast(sitk.RescaleIntensity(combined), sitk.sitkUInt8)  
    
    #plot the current image
    #plt.subplots(1,2)
    fig, (ax, ax2) = plt.subplots(ncols=2)
    
    #plt.subplot(1,2,1)

    ax.imshow(sitk.GetArrayFromImage(combined_eightbit),cmap=plt.cm.gray)
    
   # plt.title(multires_iterations)
        # Plot the similarity metric values

    #plt.subplot(1,2,2)
    ax2.plot(metric_values, 'r')
    ax2.plot(multires_iterations, [metric_values[index] for index in multires_iterations], 'b*')
    ax2.set_xlabel('Iteration Number',fontsize=12)
    #ax2.set_ylabel('Metric Value',fontsize=12, rotation='0')
    asp = np.diff(ax2.get_xlim())[0] / np.diff(ax2.get_ylim())[0]
    ax2.set_aspect(asp)

    plt.show()
  
    
# Callback invoked when the sitkMultiResolutionIterationEvent happens, update the index into the 
# metric_values list. 
def update_multires_iterations():
    global metric_values, multires_iterations
    multires_iterations.append(len(metric_values))

def affineRegister(fixed_image, moving_image, scale = 4, fixedMask = None, movingMask = None):
    registration_method = sitk.ImageRegistrationMethod()

     # Similarity metric settings.|
    #registration_method.SetMetricAsMeanSquares()
    registration_method.SetMetricAsMattesMutualInformation()
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(1)

    registration_method.SetInterpolator(sitk.sitkLinear)

    if fixedMask:
        registration_method.SetMetricFixedMask(fixedMask)
        
    if movingMask:
        registration_method.SetMetricMovingMask(movingMask)
    
        # Optimizer settings.
    registration_method.SetOptimizerAsRegularStepGradientDescent(20.0, 0.01, 200)
    #registration_method.SetOptimizerAsOnePlusOneEvolutionary(numberOfIterations=100)
    #registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, convergenceMinimumValue=1e-4, convergenceWindowSize=10)
    registration_method.SetOptimizerScalesFromPhysicalShift()

        # Setup for the multi-resolution framework.

    shrinkFactors = [8,4,2,1]
    smoothingSigmas = [2,2,1,1]
    
    if scale > 4:
        scale = 4
        print('Warning, scale was set higher than the maximum value of 4')

        
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors[:scale])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas[:scale])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

        #Redefining initial_transform so the function 
    transform = sitk.AffineTransform(2)
    #transform = sitk.TranslationTransform(2)
    
    # Don't optimize in-place, we would possibly like to run this cell multiple times.
    registration_method.SetInitialTransform(transform)

        # Connect all of the observers so that we can perform plotting during registration.
    registration_method.AddCommand(sitk.sitkStartEvent, start_plot)
    registration_method.AddCommand(sitk.sitkEndEvent, end_plot)
    registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, update_multires_iterations) 
    registration_method.AddCommand(sitk.sitkIterationEvent, lambda: plot_values(registration_method, fixed_image, moving_image,transform))

    #affine_transform = registration_method.Execute(fixed_image,moving_image)
    #print('Final metric value: {0}'.format(registration_method.GetMetricValue()))
    #print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))

    return (registration_method.Execute(fixed_image,moving_image), registration_method.GetMetricValue(), registration_method.GetOptimizerStopConditionDescription())


def askIfGoodRegister():
    """Query the user to see if the registration is good""""
    

def setupImg(imgPath, setupOffset = False):
    """Set up the image spacing and optionally the registration offset"""
    
    
def readOffsetFile(imgPath):
    """"Read in the .txt file that specifies the correct offset for the moving
    images.  This offset is an initial translation so that the registration
    performs better and does not get stuck in a local optima."""
    
def readSpacingFile(imgPath):
    """"Read in the .txt file that specifies the correct spacing for each
    image.  ITK works in physical space, but it doesn't read or write 
    microscopy images well since it works in mm/inches.  In addition, many
    of these files do not have a spacing assigned beforehand."""
    
    
def supervisedRegisterImages(fixedPath, movingPath):
    
    fixedImg = setupImg(fixedPath)
    movingImg = setupImg(movingPath, setupOffset = True)
    
    goodRegister = False
    
    while not goodRegister:    
        (transform, metric, optimizer) = affineRegister(fixedImg, movingImg)
        goodRegister = askIfGoodRegister()
        
    registeredImg = sitk.Resample(movingImg, fixedImg, transform, sitk.sitkLinear, 0.0, movingImg.GetPixelID())    
    
    return registeredImg
    

def bulkSupervisedRegisterImages(fixedDir, movingDir, outputDir, outputSuffix):
    
    (fixedImgPathList, movingImgPathList) = blk.findSharedImages(fixedDir, movingDir)
    
    for i in range(0, np.size(fixedImgPathList)):
        registeredImg = supervisedRegisterImages(fixedImgPathList[i], movingImgPathList[i])
        registeredPath = blk.createNewImagePath(movingImgPathList[i], outputDir, outputSuffix)
        sitk.WriteImage(registeredImg, registeredPath)