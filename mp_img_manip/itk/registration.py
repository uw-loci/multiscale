# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:38:19 2018

@author: mpinkert
"""
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.utility_functions as util

import mp_img_manip.itk.metadata as meta
import mp_img_manip.itk.transform as tran
import mp_img_manip.itk.process as proc

import SimpleITK as sitk
import numpy as np
import os

import matplotlib.pyplot as plt
from IPython.display import clear_output

    
def start_plot():
    """Event: Initialize global values for graphing registration values"""
    global metric_values, multires_iterations
    
    metric_values = []
    multires_iterations = []
    

def end_plot():
    """Event: Delete global values for graphing registration values"""
    global metric_values, multires_iterations
    
    del metric_values
    del multires_iterations
    # Close figure, we don't want to get a duplicate of the plot latter on.
    plt.close()
    
     
def plot_values(registration_method, fixed_image, moving_image, transform):
    """Event: Update and plot new registration values"""
    
    global metric_values, multires_iterations
    
    metric_values.append(registration_method.GetMetricValue())             
                          
    # Clear the output area (wait=True, to reduce flickering)
    clear_output(wait=True)
    
    moving_transformed = sitk.Resample(moving_image, fixed_image, transform, 
                                       sitk.sitkLinear, 0.0, 
                                       moving_image.GetPixelIDValue()) 
    
    #Blend the registered and fixed images                                   
    combined_array = proc.overlay_images(fixed_image, moving_transformed)
    
    #plot the current image
    fig, (ax, ax2) = plt.subplots(ncols=2)
    fig.tight_layout()
    
    ax.imshow(combined_array,cmap=plt.cm.gray)
    ax.axis('off')
    
    ax2.plot(metric_values, 'r')
    ax2.plot(multires_iterations, 
             [metric_values[index] for index in multires_iterations], 'b*')
    
    ax2.set_xlabel('Iteration Number',fontsize=12)
    ax2.set_ylabel('Metric Value',fontsize=12, rotation='90')
    
    asp = np.diff(ax2.get_xlim())[0] / np.diff(ax2.get_ylim())[0]
    ax2.set_aspect(asp)
    
  
# Callback invoked when the sitkMultiResolutionIterationEvent happens,
# update the index into the metric_values list. 
    
def update_multires_iterations():
    """Event: Add the index for when the registration switches scales"""
    global metric_values, multires_iterations
    multires_iterations.append(len(metric_values))



def affine_register(fixed_image, moving_image,
                    scale = 4, iterations = 200,
                    fixed_mask = None, moving_mask = None):
    """Perform an affine registration using MI and RSGD over up to 4 scales
    
    Uses mutual information and regular step gradient descent
    
    Inputs:
    fixed_image -- The image that is registered to
    moving_image -- The image that is being registered
    scale -- how many resolution scales the function uses
    iterations -- Iterations per scale before the function stops
    fixed_mask -- Forces calculations over part of the fixed image
    moving_mask -- Forces calculations over part of the moving image
    
    Outputs:
    transform -- The calculated image transform for registration
    metric -- The mutual information value at the stopping poin
    stop -- the stopping condition of the optimizer
    """
    
    registration_method = sitk.ImageRegistrationMethod()

    # Similarity metric settings.|
    registration_method.SetMetricAsMattesMutualInformation()
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(1)

    registration_method.SetInterpolator(sitk.sitkLinear)

    if fixed_mask:
        registration_method.SetMetricFixedMask(fixed_mask)
        
    if moving_mask:
        registration_method.SetMetricMovingMask(moving_mask)
    
    # Optimizer settings.
    registration_method.SetOptimizerAsRegularStepGradientDescent(20.0, 0.01,
                                                                 iterations)
    #registration_method.SetOptimizerAsOnePlusOneEvolutionary(
    #       numberOfIterations=100)
    #registration_method.SetOptimizerAsGradientDescent(
    #       learningRate=1.0, numberOfIterations=100,
    #       convergenceMinimumValue=1e-4, convergenceWindowSize=10)
    registration_method.SetOptimizerScalesFromPhysicalShift()

        # Setup for the multi-resolution framework.

    shrink_factors = [8,4,2,1]
    smoothing_sigmas = [2,2,1,1]
    
    if scale > 4:
        scale = 4
        print('Warning, scale was set higher than the maximum value of 4')

        
    registration_method.SetShrinkFactorsPerLevel(
            shrink_factors[(4-scale):])
    registration_method.SetSmoothingSigmasPerLevel(
            smoothing_sigmas[(4-scale):])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    transform = sitk.AffineTransform(2)    
    registration_method.SetInitialTransform(transform)

    # Connect all of the observers so that we can plot during registration.
    
    #animation = registration_plot
    
    #registration_method.AddCommand(sitk.sitkStartEvent, start_plot)
    #registration_method.AddCommand(sitk.sitkEndEvent, end_plot)
 #   registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent,
    #                               lambda: animation.update_scale) 
#    registration_method.AddCommand(
        #sitk.sitkIterationEvent,
        #lambda: animation.update_iteration(
        #   registration_method.GetMetricValue(),
        #   fixed_image, moving_image,
        #   transform))

    return (registration_method.Execute(fixed_image, moving_image),
            registration_method.GetMetricValue(),
            registration_method.GetOptimizerStopConditionDescription())


def query_good_registration(fixed_image, moving_image,
                            transform, metric, stop):
    
    moving_resampled = sitk.Resample(moving_image, fixed_image, transform, 
                                       sitk.sitkLinear, 0.0, 
                                       fixed_image.GetPixelIDValue()) 
                
    plt.imshow(proc.overlay_images(fixed_image, moving_resampled), cmap=plt.cm.gray)
    plt.show()
        
    print('Final metric value: {0}'.format(metric))
    print('Optimizer\'s stopping condition, {0}'.format(stop))
        
    transform_params = transform.GetParameters()
    matrix = np.array([transform_params[0:2], transform_params[2:4]])
    translation = np.array(transform_params[4:6])
    print('Transform Matrix: {0}'.format(matrix))
    print('Transform Translation: {0}'.format(translation))
        
    return util.yes_no('\n Is this registration good? [y/n] >>> ')


def supervised_register_images(fixed_path, moving_path,
                               iterations = 200, scale = 4):
    
    fixed_image = meta.setup_image(fixed_path)
    moving_image = meta.setup_image(moving_path, setup_origin = True)
    
    print('Registering ' + os.path.basename(moving_path) + ' to '
          + os.path.basename(fixed_path))
    
    while True:    
        moving_image.SetOrigin(meta.query_origin_change(fixed_image, moving_image))
        (transform, metric, stop) = affine_register(
                fixed_image, moving_image,
                iterations = iterations, scale = scale)
        
        if query_good_registration(fixed_image, moving_image,
                                   transform, metric, stop): break
       
    registered_image = sitk.Resample(moving_image, fixed_image,
                                     transform, sitk.sitkLinear,
                                     0.0, moving_image.GetPixelID())
       
    return registered_image, transform, metric, stop
    

def bulk_supervised_register_images(fixed_dir, moving_dir,
                                    output_dir, output_suffix,
                                    writeOutput = True, writeTransform = True,
                                    iterations = 200, scale = 4):
    
    (fixed_path_list, moving_path_list) = blk.find_shared_images(
            fixed_dir, moving_dir)
    
    for i in range(0, np.size(fixed_path_list)):
        registered_image, transform, metric, stop = supervised_register_images(
                fixed_path_list[i], moving_path_list[i],
                iterations = iterations, scale = scale)
        
        registered_path = blk.create_new_image_path(
                moving_path_list[i], output_dir, output_suffix)

        if writeOutput:
            sitk.WriteImage(registered_image, registered_path)
            meta.write_image_parameters(registered_path,
                                   registered_image.GetSpacing(),
                                   registered_image.GetOrigin())
            
        if writeTransform:
            tran.write_transform(registered_path, transform, metric, stop)

    
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
#    def update_iteration(self, new_metric_value,
#                            fixed_image, moving_image, transform):
#        metric_values.append(new_metric_value)                                       
#        
#        moving_image_transformed = sitk.Resample(
                            #moving_image, fixed_image, transform, 
#                                       sitk.sitkLinear, 0.0, 
#                                       moving_image.GetPixelIDValue()) 
#        
#        combined_array = overlay_images(fixed_image, moving_image_transformed)
#
#        self.ax[0].imshow(combined_array,cmap=plt.cm.gray)
#        self.ax[0].axis('off')
#        
#        self.ax[1].plot(self.metric_values, 'r')
#        self.ax[1].plot(self.multires_iterations,
#                        [self.metric_values[index] for index 
                        # in self.multires_iterations], 'b*')
#   
#        asp = np.diff(self.ax[1].get_xlim())[0] 
                        #/ np.diff(self.ax[1].get_ylim())[0]
#        self.ax[1].set_aspect(asp)        
#        
#    def update_scale(self):
#        self.multires_iterations.append(len(self.metric_values))  