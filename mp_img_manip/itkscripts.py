# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 09:04:51 2018

@author: mpinkert
"""
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.utility_functions as util

import SimpleITK as sitk
import numpy as np
import os


# GUI components (sliders, dropdown...).
#from ipywidgets import interact

# Enable display of HTML.
from IPython.display import clear_output

#Set up our plotting environment
import matplotlib.pyplot as plt
#import matplotlib.animation as ani
#plt.ion()



#class registration_plot(ani.FuncAnimation):
#    
#    def __init__(self):
#        self.metric_values = []
#        self.multires_iterations = []
#        
#        self.fig, self.ax = plt.subplots(ncols=2)
#        self.fig.tight_layout()
#        
#        self.ax[0].axis('off')
#    
#        self.ax[1].set_xlabel('Iteration Number',fontsize=12)
#        self.ax[1].set_ylabel('Metric Value',fontsize=12, rotation='90')
#        
#        ani.FuncAnimation(self.fig, self.update_iteration)
#    
#    def update_iteration(self, new_metric_value, fixed_image, moving_image, transform):
#        metric_values.append(new_metric_value)                                       
#        
#        moving_image_transformed = sitk.Resample(moving_image, fixed_image, transform, 
#                                       sitk.sitkLinear, 0.0, 
#                                       moving_image.GetPixelIDValue()) 
#        
#        combined_array = overlay_images(fixed_image, moving_image_transformed)
#
#        self.ax[0].imshow(combined_array,cmap=plt.cm.gray)
#        self.ax[0].axis('off')
#        
#        self.ax[1].plot(self.metric_values, 'r')
#        self.ax[1].plot(self.multires_iterations, [self.metric_values[index] for index in self.multires_iterations], 'b*')
#   
#        asp = np.diff(self.ax[1].get_xlim())[0] / np.diff(self.ax[1].get_ylim())[0]
#        self.ax[1].set_aspect(asp)        
#        
#    def update_scale(self):
#        self.multires_iterations.append(len(self.metric_values))
#        

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
    
    moving_transformed = sitk.Resample(moving_image, fixed_image, transform, 
                                       sitk.sitkLinear, 0.0, 
                                       moving_image.GetPixelIDValue()) 
    
    #Blend the registered and fixed images                                   
    combined_array = overlay_images(fixed_image, moving_transformed)
    
    #plot the current image
    fig, (ax, ax2) = plt.subplots(ncols=2)
    fig.tight_layout()
    
    ax.imshow(combined_array,cmap=plt.cm.gray)
    ax.axis('off')
    
    ax2.plot(metric_values, 'r')
    ax2.plot(multires_iterations, [metric_values[index] for index in multires_iterations], 'b*')
    ax2.set_xlabel('Iteration Number',fontsize=12)
    ax2.set_ylabel('Metric Value',fontsize=12, rotation='90')
    
    asp = np.diff(ax2.get_xlim())[0] / np.diff(ax2.get_ylim())[0]
    ax2.set_aspect(asp)
    
  
# Callback invoked when the sitkMultiResolutionIterationEvent happens, update the index into the 
# metric_values list. 
def update_multires_iterations():
    global metric_values, multires_iterations
    multires_iterations.append(len(metric_values))

def overlay_images(fixed_image, moving_image, alpha = 0.7):
    
    fixed_array = sitk.GetArrayFromImage(fixed_image)
    fixed_normalized = (fixed_array - np.amin(fixed_array))/(np.amax(fixed_array)+np.amin(fixed_array))

    try: #Post-registration
        moving_array = sitk.GetArrayFromImage(moving_image)
        moving_normalized = (moving_array - np.amin(moving_array))/(np.amax(moving_array)+np.amin(moving_array))
        
        combined_array = (1.0 - alpha)*fixed_normalized + alpha*moving_normalized
        return combined_array
    except: #Pre-registration
        initial_transform = sitk.Similarity2DTransform()
        moving_resampled = sitk.Resample(moving_image, fixed_image, 
                                         initial_transform, sitk.sitkLinear, 0.0, moving_image.GetPixelID())
        
        moving_array = sitk.GetArrayFromImage(moving_resampled)
        moving_normalized = (moving_array - np.amin(moving_array))/(np.amax(moving_array)+np.amin(moving_array))

        combined_array = (1.0 - alpha)*fixed_normalized + alpha*moving_normalized
        return combined_array
        


def affineRegister(fixed_image, moving_image, scale = 4, iterations = 200, fixedMask = None, movingMask = None):
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
    registration_method.SetOptimizerAsRegularStepGradientDescent(20.0, 0.01, iterations)
    #registration_method.SetOptimizerAsOnePlusOneEvolutionary(numberOfIterations=100)
    #registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, convergenceMinimumValue=1e-4, convergenceWindowSize=10)
    registration_method.SetOptimizerScalesFromPhysicalShift()

        # Setup for the multi-resolution framework.

    shrinkFactors = [8,4,2,1]
    smoothingSigmas = [2,2,1,1]
    
    if scale > 4:
        scale = 4
        print('Warning, scale was set higher than the maximum value of 4')

        
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors[(4-scale):])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas[(4-scale):])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

        #Redefining initial_transform so the function 
    transform = sitk.AffineTransform(2)
    #transform = sitk.TranslationTransform(2)
    
    # Don't optimize in-place, we would possibly like to run this cell multiple times.
    registration_method.SetInitialTransform(transform)

    # Connect all of the observers so that we can perform plotting during registration.
    
  #  animation = registration_plot
    
    #registration_method.AddCommand(sitk.sitkStartEvent, start_plot)
    #registration_method.AddCommand(sitk.sitkEndEvent, end_plot)
 #   registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, lambda: animation.update_scale) 
#    registration_method.AddCommand(sitk.sitkIterationEvent, lambda: animation.update_iteration(registration_method.GetMetricValue(),fixed_image, moving_image, transform))

    #affine_transform = registration_method.Execute(fixed_image,moving_image)
    #print('Final metric value: {0}'.format(registration_method.GetMetricValue()))
    #print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))

    return (registration_method.Execute(fixed_image,moving_image), registration_method.GetMetricValue(), registration_method.GetOptimizerStopConditionDescription())

    

def setup_image(imgPath, setupOrigin = False):
    """Set up the image spacing and optionally the registration origin"""
    img = sitk.ReadImage(imgPath)
    
    (imgDir, imgName) = os.path.split(imgPath)
    file_path = imgDir + '/Image Parameters.csv'
    
    image_parameters = blk.read_write_pandas_row(file_path,imgName,'Image',
                                                 ['X Spacing', 'Y Spacing', 'X Origin', 'Y Origin'])
    
    print(image_parameters)
    print('')
    
    spacing = [float(image_parameters['X Spacing']), float(image_parameters['Y Spacing'])]
    img.SetSpacing(spacing)
    
    if setupOrigin:
        origin = [float(image_parameters['X Origin']), float(image_parameters['Y Origin'])]
        img.SetOrigin(origin)
        
    return img
    
                 
    
def query_origin_change(moving_image, fixed_image):
    """Ask if the user wants to set a new 2D ITK origin"""
    
    plt.imshow(overlay_images(fixed_image, moving_image), cmap=plt.cm.gray)
    plt.show()
    change_origin = util.yes_no('Do you want to change the origin? [y/n] >>> ')
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
            plt.imshow(overlay_images(fixed_image, moving_image), cmap=plt.cm.gray)
            plt.show()
            
            #bug: The image does not show up till after the question
            if util.yes_no('Is this origin good? [y/n] >>> '): break
        
        return newOrigin
    else:
        return origin
    
    
def supervisedRegisterImages(fixedPath, movingPath, iterations = 200, scale = 4):
    
    fixed_image = setup_image(fixedPath)
    moving_image = setup_image(movingPath, setupOrigin = True)
    
    while True:    
        moving_image.SetOrigin(query_origin_change(moving_image, fixed_image))
        (transform, metric, stop) = affineRegister(fixed_image, moving_image, iterations = iterations, scale = scale)
        
        print('Final metric value: {0}'.format(metric))
        print('Optimizer\'s stopping condition, {0}'.format(stop))
        
        transform_params = transform.GetParameters()
        matrix = np.array([transform_params[0:2], transform_params[2:4]])
        translation = np.array(transform_params[4:6])
        print('Transform Matrix: {0}'.format(matrix))
        print('Transform Translation: {0}'.format(translation))
        
        if util.yes_no('Is this registration good? [y/n] >>> '): break
 
    
       
    registered_image = sitk.Resample(moving_image, fixed_image, transform, sitk.sitkLinear, 0.0, moving_image.GetPixelID())       
    return registered_image
    

def bulkSupervisedRegisterImages(fixedDir, movingDir, outputDir, outputSuffix, iterations = 200, scale = 4):
    
    (fixed_imagePathList, moving_imagePathList) = blk.findSharedImages(fixedDir, movingDir)
    
    for i in range(0, np.size(fixed_imagePathList)):
        registered_image = supervisedRegisterImages(fixed_imagePathList[i], moving_imagePathList[i], iterations = iterations, scale = scale)
        registeredPath = blk.createNewImagePath(moving_imagePathList[i], outputDir, outputSuffix)
        sitk.WriteImage(registered_image, registeredPath)