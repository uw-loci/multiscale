# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:40:25 2018

@author: mpinkert
"""

import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.utility_functions as util

import mp_img_manip.itk.process as proc

import SimpleITK as sitk
import os

import matplotlib.pyplot as plt


def setup_image(image_path,
                setup_origin = False,
                return_image = True, return_spacing = False,
                print_parameters = False):
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
    if print_parameters: 
        print('\n ' + image_parameters)
    
    
    spacing = [float(image_parameters['X Spacing']),
               float(image_parameters['Y Spacing'])]
    
    if setup_origin:
        origin = [float(image_parameters['X Origin']),
                  float(image_parameters['Y Origin'])]
    
    if return_image: 
        image = sitk.ReadImage(image_path)
        image.SetSpacing(spacing)
        if setup_origin: image.SetOrigin(origin)

        return image
    
    
    elif return_spacing:
        return spacing
    
    
def query_origin_change(fixed_image, moving_image):
    """Ask if the user wants a new 2D ITK origin based on image overlay"""
    
    plt.imshow(proc.overlay_images(fixed_image, moving_image), cmap=plt.cm.gray)
    plt.show()
    print('Current origin: ' + str(moving_image.GetOrigin()))
    change_origin = util.yes_no('Do you want to change the origin? [y/n] >>> ')
    origin = moving_image.GetOrigin()
    
    #todo: have it change the origin file too....  
    
    if change_origin:
        
        while True:
            print('Current origin: '+str(origin))
            new_origin_x = util.query_int('Enter new X origin: ')
            new_origin_y = util.query_int('Enter new Y origin: ')
            
            new_origin = (new_origin_x, new_origin_y)
            
            moving_image.SetOrigin(new_origin)
            plt.imshow(proc.overlay_images(fixed_image, moving_image),
                       cmap=plt.cm.gray)
            plt.show()
            
            #bug: The image does not show up till after the question
            if util.yes_no('Is this origin good? [y/n] >>> '): break
        
        return new_origin
    else:
        return origin


    
def write_image_parameters(image_path, spacing, origin):
    """Write down the spacing and origin of an image file to csv metadata"""
    
    (output_dir, image_name) = os.path.split(image_path)
    
    file_path = output_dir + '/Image Parameters.csv'
    
    column_labels = ['X Spacing', 'Y Spacing', 'X Origin', 'Y Origin']
    
    column_values = spacing + origin
    
    blk.write_pandas_row(file_path,image_name,column_values,
                         'Image',column_labels)    