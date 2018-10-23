# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 10:06:55 2018

@author: mpinkert
"""
import multiscale.bulk_img_processing as blk
import multiscale.utility_functions as util
import multiscale.itk.metadata as meta

import SimpleITK as sitk
import numpy as np
import os


def bulk_apply_mask(image_dir, mask_dir,
                    output_dir, output_suffix,
                    skip_existing_images=True):
        """Find corresponding images between dirs and apply the second as a mask
        
        Inputs:
        image_dir -- Directory of images to-be-masked
        mask_dir -- Directory of images that will be used as the mask
        output_dir -- Directory where the masked images will be saved
        ouptut_suffix -- Filename text after the core/sample name of the image file
        """
        
        (image_path_list, mask_path_list) = blk.find_shared_images(
                image_dir, mask_dir)
        
        for i in range(np.size(image_path_list)):
                
                masked_path = blk.create_new_image_path(
                        image_path_list[i], output_dir, output_suffix)
                if masked_path.exists() and skip_existing_images:
                        continue
                
                image = meta.setup_image(image_path_list[i])
                mask = meta.setup_image(mask_path_list[i]) > 0
                
                print('Masking ' + os.path.basename(image_path_list[i]) + ' with '
                      + os.path.basename(mask_path_list[i]))
                
                masked_image = sitk.Mask(image, mask)
                meta.copy_relevant_metadata(masked_image, image)
                
                meta.write_image(masked_image, masked_path)


def find_centroid(image: sitk.Image) -> list:
        """Find the centroid of the pixels in an image"""
        # calculate centroid


def apply_threshold(itk_image, image_name,
                    threshold=1, unit='degree'):
        """Apply an intensity based threshold to an image"""
        print('Thresholding {0} to {1} {2}'.format(image_name, threshold, unit))
        
        mask = itk_image > threshold
        thresh_image = sitk.Mask(itk_image, mask)
        
        return thresh_image


def bulk_threshold(input_dir, output_dir, output_suffix,
                   threshold=1,
                   skip_existing_images=False):
        """Apply intensity based thresholds to all images in folder"""
        path_list = util.list_filetype_in_dir(input_dir, '.tif')
        
        for i in range(len(path_list)):
                new_path = blk.create_new_image_path(path_list[i],
                                                     output_dir, output_suffix)
                if new_path.exists() and skip_existing_images:
                        continue
                
                original = meta.setup_image(path_list[i])
                new_image = apply_threshold(original, os.path.basename(path_list[i]), threshold=threshold)
                
                meta.copy_relevant_metadata(new_image, original)
                meta.write_image(new_image, new_path)


def convert_to_eightbit(itk_image, image_name):
        """Convert an itk image to 8 bit integer pixels"""
        
        print('Converting {0} to 8-bit grayscale'.format(image_name))
        return sitk.Cast(sitk.RescaleIntensity(itk_image), sitk.sitkUInt8)


def bulk_convert_to_eightbit(input_dir, output_dir, output_suffix):
        """Convert all tif images in a directory to 8bit and save in new directory
        
        Inputs:
        input_dir -- Directory of images to convert
        output_dir -- Directory to save converted images
        output_suffix -- Text in output image name after the core/sample name
        
        """
        
        path_list = util.list_filetype_in_dir(input_dir, '.tif')
        
        for i in range(len(path_list)):
                original = meta.setup_image(path_list[i])
                new_image = convert_to_eightbit(original,
                                                os.path.basename(path_list[i]))
                
                new_path = blk.create_new_image_path(path_list[i],
                                                     output_dir, output_suffix)
                
                meta.copy_relevant_metadata(new_image, original)
                meta.write_image(new_image, new_path)


def check_if_image_is_rgb(image: sitk.Image):
        
        components = image.GetNumberOfComponentsPerPixel()
        pixel_type = image.GetPixelIDTypeAsString()
        
        if components == 3 and pixel_type == 'vector of 8-bit unsigned integer':
                image_is_rgb = True
        else:
                image_is_rgb = False
        
        return image_is_rgb


def rgb_to_grayscale_img(image: sitk.Image, white_light_filter_value=0.9):
        """Convert an RGB to grayscale image by extracting the average intensity, filtering out white light >0.9 max"""
        array = sitk.GetArrayFromImage(image)
        dimension = image.GetDimension()
        
        grayscale_array = np.average(array, 2)
        grayscale_array[grayscale_array > white_light_filter_value*np.max(array)] = 0
        
        grayscale_image = sitk.GetImageFromArray(grayscale_array)
        grayscale_image.SetSpacing(image.GetSpacing())
        grayscale_image.SetOrigin(image.GetOrigin())
        
        return grayscale_image