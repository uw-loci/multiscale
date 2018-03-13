# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 09:04:51 2018

@author: mpinkert
"""
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.utility_functions as util

import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
import os


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

def overlay_images_grayscale(fixed_image, moving_image, alpha = 0.7):
    try:
        combined_image = sitk.Cast((1.0 - alpha)*fixed_image + alpha*moving_image, sitk.sitkUInt8)
        combined_array = sitk.GetArrayFromImage(combined_image)
        return combined_array
    except:
        initial_transform = sitk.Similarity2DTransform()
        moving_resampled = sitk.Resample(moving_image, fixed_image, 
                                         initial_transform, sitk.sitkLinear, 0.0, fixed_image.GetPixelID())
        
        combined_image = sitk.Cast((1.0 - alpha)*fixed_image + alpha*moving_resampled, sitk.sitkUInt8)
        combined_array = sitk.GetArrayFromImage(combined_image)
        return combined_array
        
    
# Callback invoked when the IterationEvent happens, update our data and display new figure.    
def plot_values(registration_method, fixed_image, moving_image,transform):
    global metric_values, multires_iterations
    

    metric_values.append(registration_method.GetMetricValue())                                       
    # Clear the output area (wait=True, to reduce flickering), and plot current data
    clear_output(wait=True)
    
    
    moving_transformed = sitk.Resample(moving_image, fixed_image, transform, 
                                       sitk.sitkLinear, 0.0, 
                                       moving_image.GetPixelIDValue()) 
    
    #Blend the registered and fixed images                                   
    combined_array = overlay_images_grayscale(fixed_image, moving_transformed)
    
    #plot the current image
    fig, (ax, ax2) = plt.subplots(ncols=2)
    
    ax.imshow(combined_array,cmap=plt.cm.gray)
    
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

    

def setup_image(imgPath, setupOrigin = False):
    """Set up the image spacing and optionally the registration origin"""
    img = sitk.ReadImage(imgPath)
    
    spacingList = blk.read_write_column_file(imgPath, 'PixelSpacing.csv')
    spacing = [float(spacingList[1]), float(spacingList[2])]
    img.SetSpacing(spacing)
    print('Spacing: ' + str(spacingList))
    
    if setupOrigin:
        originList = blk.read_write_column_file(imgPath, 'Origin.csv')
        origin = [float(originList[1]), float(originList[2])]
        print('Origin: ' + str(originList))
        
        img.SetOrigin(origin)
    
    return img
    
                 
    
def query_origin_change(moving_image, fixed_image):
    """Ask if the user wants to set a new 2D ITK origin"""
    
    plt.imshow(overlay_images_grayscale(fixed_image, moving_image), cmap=plt.cm.gray)
    change_origin = util.yes_no('Do you want to change the origin? ')
    origin = moving_image.GetOrigin()
    print(moving_image.GetOrigin())
    
    #todo: have it change the origin file too....  
    
    if change_origin:
        
        while True:
            print('Current origin: '+str(origin))
            newOrigin_x = util.query_int('Enter new X origin: ')
            newOrigin_y = util.query_int('Enter new Y origin: ')
            
            newOrigin = (newOrigin_x, newOrigin_y)
            
            moving_image.SetOrigin(newOrigin)
            plt.imshow(overlay_images_grayscale(fixed_image, moving_image), cmap=plt.cm.gray)
            
            #bug: The image does not show up till after the question
            if util.yes_no('Is this origin good?'): break
        
        return newOrigin
    else:
        return origin
    
    
def supervisedRegisterImages(fixedPath, movingPath):
    
    fixed_image = setup_image(fixedPath)
    moving_image = setup_image(movingPath, setupOrigin = True)
    
    goodRegister = False
    
    while not goodRegister:    
        moving_image.SetOrigin(query_origin_change(moving_image, fixed_image))
        (transform, metric, optimizer) = affineRegister(fixed_image, moving_image)
        goodRegister = util.yes_no('Is this registration good?')
        
    registered_image = sitk.Resample(moving_image, fixed_image, transform, sitk.sitkLinear, 0.0, moving_image.GetPixelID())    
    
    return registered_image
    

def bulkSupervisedRegisterImages(fixedDir, movingDir, outputDir, outputSuffix):
    
    (fixed_imagePathList, moving_imagePathList) = blk.findSharedImages(fixedDir, movingDir)
    
    for i in range(0, np.size(fixed_imagePathList)):
        registered_image = supervisedRegisterImages(fixed_imagePathList[i], moving_imagePathList[i])
        registeredPath = blk.createNewImagePath(moving_imagePathList[i], outputDir, outputSuffix)
        sitk.WriteImage(registered_image, registeredPath)