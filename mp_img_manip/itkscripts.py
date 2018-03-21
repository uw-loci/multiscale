# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 09:04:51 2018

@author: mpinkert
"""
import mp_image_manip.bulk_image_processing as blk
import mp_image_manip.utility_functions as util


import SimpleITK as sitk
import numpy as np
import os
import math

# GUI components (sliders, dropdown...).
#from ipywidgets import interact

# Enable display of HTML.
from IPython.display import clear_output

#Set up our plotting environment
import matplotlib.pyplot as plt
#import matplotlib.animation as ani
#plt.ion()
#
#
#
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
    combined_array = overlay_images(fixed_image, moving_transformed)
    
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


def setup_image(image_path,
                setup_origin = False,
                return_image = True, return_spacing = False):
    """Set up the image spacing and optionally the registration origin
    
    This function is necessary because ITK cannot save in microns, making
    external metadata necessary.  It references, or creates, a csv file to
    handle this metadata
    
    Inputs:
    image_path -- The path to the image being setup
    setup_origin -- Set values for the origin or leaves at 0,0
    return_image -- Return the whole setup image
    return_scacing -- Return the spacing values
    
    Outputs:
    image -- The setup image if return_image is True
    spacing -- The spacing of the image if return_spacing is True
    
    """
    
    (image_dir, image_name) = os.path.split(image_path)
    file_path = image_dir + '/Image Parameters.csv'
    
    image_parameters = blk.read_write_pandas_row(
            file_path, image_name,
            'Image', ['X Spacing', 'Y Spacing', 'X Origin', 'Y Origin'])
    
    print(image_parameters)
    print('')
    
    spacing = [float(image_parameters['X Spacing']),
               float(image_parameters['Y Spacing'])]
    
    if setup_origin:
        origin = [float(image_parameters['X Origin']),
                  float(image_parameters['Y Origin'])]
    
    if return_image: 
        image = sitk.ReadImage(image_path)
        image.SetSpacing(spacing)
        image.SetOrigin(origin)

        return image
    
    
    elif return_spacing:
        return spacing
    


def overlay_images(fixed_image, moving_image, alpha = 0.7):
    """Create a numpy array that is an 8bit combination of two images
    
    Inputs:
    fixed_image -- Image one, using registration nomenclature
    moving_image -- Image two, using registration nomeclature
    alpha -- degree of weighting towards the moving image
    
    """
    
    fixed_array = sitk.GetArrayFromImage(fixed_image)
    fixed_normalized = (fixed_array - np.amin(fixed_array))/(
            np.amax(fixed_array) + np.amin(fixed_array))

    try: #Post-registration
        moving_array = sitk.GetArrayFromImage(moving_image)
        moving_normalized = (moving_array - np.amin(moving_array))/(
                np.amax(moving_array)+np.amin(moving_array))
        
        combined_array = ((1.0 - alpha)*fixed_normalized 
                          + alpha*moving_normalized)
        
        return combined_array
    
    except: #Pre-registration
        initial_transform = sitk.Similarity2DTransform()
        moving_resampled = sitk.Resample(moving_image, fixed_image, 
                                         initial_transform, sitk.sitkLinear,
                                         0.0, moving_image.GetPixelID())
        
        moving_array = sitk.GetArrayFromImage(moving_resampled)
        moving_normalized = (moving_array - np.amin(moving_array))/(
                np.amax(moving_array)+np.amin(moving_array))

        combined_array = ((1.0 - alpha)*fixed_normalized 
                          + alpha*moving_normalized)
        return combined_array
                 
    
    
def query_origin_change(fixed_image, moving_image):
    """Ask if the user wants a new 2D ITK origin based on image overlay"""
    
    plt.imshow(overlay_images(fixed_image, moving_image), cmap=plt.cm.gray)
    plt.show()
    change_origin = util.yes_no('Do you want to change the origin? [y/n] >>> ')
    origin = moving_image.GetOrigin()
    print(moving_image.GetOrigin())
    
    #todo: have it change the origin file too....  
    
    if change_origin:
        
        while True:
            print('Current origin: '+str(origin))
            new_origin_x = util.query_int('Enter new X origin: ')
            new_origin_y = util.query_int('Enter new Y origin: ')
            
            new_origin = (new_origin_x, new_origin_y)
            
            moving_image.SetOrigin(new_origin)
            plt.imshow(overlay_images(fixed_image, moving_image),
                       cmap=plt.cm.gray)
            plt.show()
            
            #bug: The image does not show up till after the question
            if util.yes_no('Is this origin good? [y/n] >>> '): break
        
        return new_origin
    else:
        return origin
    
    
def query_good_registration(fixed_image, moving_image,
                            transform, metric, stop):
    
    moving_resampled = sitk.Resample(moving_image, fixed_image, transform, 
                                       sitk.sitkLinear, 0.0, 
                                       moving_image.GetPixelIDValue()) 
                
    plt.imshow(overlay_images(fixed_image, moving_resampled), cmap=plt.cm.gray)
    plt.show()
        
    print('Final metric value: {0}'.format(metric))
    print('Optimizer\'s stopping condition, {0}'.format(stop))
        
    transform_params = transform.GetParameters()
    matrix = np.array([transform_params[0:2], transform_params[2:4]])
    translation = np.array(transform_params[4:6])
    print('Transform Matrix: {0}'.format(matrix))
    print('Transform Translation: {0}'.format(translation))
        
    return util.yes_no('Is this registration good? [y/n] >>> ')
    
def write_image_parameters(image_path, spacing, origin):
    """Write down the spacing and origin of an image file to csv metadata"""
    
    (output_dir, image_name) = os.path.split(image_path)
    
    file_path = output_dir + '/Image Parameters.csv'
    
    column_labels = ['X Spacing', 'Y Spacing', 'X Origin', 'Y Origin']
    
    column_values = spacing + origin
    
    blk.write_pandas_row(file_path,image_name,column_values,
                         'Image',column_labels)    
    

def write_transform(registered_path,transform, metric, stop):
    
    (output_dir, image_name) = os.path.split(registered_path)
    
    file_path = output_dir + '/Transforms.csv'
    
    column_labels = ('Matrix Top Left', 'Matrix Top Right',
                    'Matrix Bottom Left', 'Matrix Bottom Right',
                    'X Translation', 'Y Translation',
                    'Mutual Information', 'Stop Condition')
    
    column_values = transform.GetParameters()
    column_values.append(metric)
    column_values.append(stop)
    
    blk.write_pandas_row(file_path,image_name,column_values,
                         'Image',column_labels)
    
    
def read_transform(registered_path):
    (input_dir, image_name) = os.path.split(registered_path)
    
    transform = sitk.AffineTransform(2)
    
    file_name = 'Transforms.csv'
    file_path = os.path.join(input_dir,file_name)
    
    transform_params = blk.read_pandas_row(file_path,image_name,'Image')
    
    transform.SetMatrix(transform_params[:4])
    transform.SetTranslation(transform_params[4:6])

    return transform    


def supervised_register_images(fixed_path, moving_path,
                               iterations = 200, scale = 4):
    
    fixed_image = setup_image(fixed_path)
    moving_image = setup_image(moving_path, setup_origin = True)
    
    while True:    
        moving_image.SetOrigin(query_origin_change(fixed_image, moving_image))
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
    
    (fixed_image_path_list, moving_image_path_list) = blk.find_shared_images(
            fixed_dir, moving_dir)
    
    for i in range(0, np.size(fixed_image_path_list)):
        registered_image, transform, metric, stop = supervised_register_images(
                fixed_image_path_list[i], moving_image_path_list[i],
                iterations = iterations, scale = scale)
        
        registered_path = blk.create_new_image_path(
                moving_image_path_list[i], output_dir, output_suffix)

        if writeOutput:
            sitk.WriteImage(registered_image, registered_path)
            write_image_parameters(registered_path,
                                   registered_image.GetSpacing(),
                                   registered_image.GetOrigin())
            
        if writeTransform:
            write_transform(registered_path, transform, metric, stop)
            
            
            
def resize_image(image_path, output_suffix, current_spacing, target_spacing):
    itkImg = setup_image(image_path, return_image = True)
    
    scale = math.floor(target_spacing/current_spacing)
    endRes = current_spacing*scale
    
    if current_spacing < target_spacing:      
        shrunk = sitk.Shrink(itkImg,[scale,scale])
        shrunk.SetSpacing([endRes,endRes])
        return shrunk
    
    elif current_spacing > target_spacing:
        expand = sitk.Expand(itkImg,[scale,scale])
        expand.SetSpacing([endRes,endRes])
        return expand
    
    
def bulk_resize_image(fixed_dir, moving_dir, output_dir, output_suffix):
    (fixed_image_path_list, moving_image_path_list) = blk.find_shared_images(
            fixed_dir, moving_dir)
    
    for i in range(0, np.size(fixed_image_path_list)):
        current_spacing = setup_image(moving_image_path_list[i],
                                      return_image = False,
                                      return_spacing=True)[0]
        
        target_spacing = setup_image(fixed_image_path_list[i],
                                     return_image = False,
                                     return_spacing=True)[0]

        resized_image = resize_image(moving_image_path_list[i],
                                     output_suffix,
                                     current_spacing,target_spacing)
        
        resized_path = blk.create_new_image_path(moving_image_path_list[i],
                                                 output_dir, output_suffix)

        sitk.WriteImage(resized_image,resized_path)
        write_image_parameters(resized_path,
                               resized_image.GetSpacing(),
                               resized_image.GetOrigin())


def apply_transform(fixed_path, moving_path, transform):
    return

def bulk_apply_transform(fixed_dir, moving_dir, output_dir,
                         transform_dir,
                         output_suffix,):
    return