# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:38:19 2018

@author: mpinkert
"""
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.utility_functions as util

import mp_img_manip.itk.metadata as meta
import mp_img_manip.itk.transform as tran
from mp_img_manip.itk.itk_plotting import RegistrationPlot
import mp_img_manip.itk.itk_plotting as itkplt

import SimpleITK as sitk
import numpy as np
import os

from pathlib import Path

import matplotlib.pyplot as plt

from mp_img_manip.itk.process import rgb_to_2d_img


def define_registration_method(scale: int=4, iterations: int=100, learning_rate: np.double=50,
                               min_step: np.double=0.01, gradient_tolerance: np.double=1E-5) \
            -> sitk.ImageRegistrationMethod:
        """
        Define the base metric, interpolator, and optimizer of a registration or series of registrations
    
        :param scale: How many times the method downsamples the resolution by 2x
        :param iterations: The number of times the method optimizes the metric before
        :param learning_rate:
        :param min_step:
        :param gradient_tolerance:
        :return:
        """
        registration_method = sitk.ImageRegistrationMethod()
        
        # Similarity metric settings.|
        registration_method.SetMetricAsMattesMutualInformation()
        registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
        registration_method.SetMetricSamplingPercentage(0.01)
        
        registration_method.SetInterpolator(sitk.sitkLinear)
        
        # Optimizer settings.
        registration_method.SetOptimizerAsRegularStepGradientDescent(learningRate=learning_rate, minStep=min_step,
                                                                     numberOfIterations=iterations,
                                                                     gradientMagnitudeTolerance=gradient_tolerance)
        
        registration_method.SetOptimizerScalesFromPhysicalShift()
        
        # Setup for the multi-resolution framework.
        shrink_factors = [8, 4, 2, 1]
        smoothing_sigmas = [2, 2, 1, 1]
        if scale > 4:
                scale = 4
                print('Warning, scale was set higher than the maximum value of 4')
        
        registration_method.SetShrinkFactorsPerLevel(shrink_factors[(4-scale):])
        registration_method.SetSmoothingSigmasPerLevel(smoothing_sigmas[(4-scale):])
        registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
        
        return registration_method


def register(fixed_image: sitk.Image, moving_image: sitk.Image, reg_plot: RegistrationPlot,
             registration_method: sitk.ImageRegistrationMethod=None,
             initial_transform: sitk.Transform=None,
             fixed_mask: sitk.Image=None, moving_mask: sitk.Image=None):
        """Perform an affine registration using MI and RSGD over up to 4 scales
        
        Uses mutual information and regular step gradient descent
        
        Inputs:
        fixed_image -- The image that is registered to
        moving_image -- The image that is being registered
        base_registration_method -- The pre-defined optimizer/metric/interpolator
        fixed_mask -- Forces calculations over part of the fixed image
        moving_mask -- Forces calculations over part of the moving image
        rotation -- Pre rotation in degrees, to assist in registration
        
        Outputs:
        initial_transform -- The calculated image initial_transform for registration
        metric -- The mutual information value at the stopping poin
        stop -- the stopping condition of the optimizer
        """
        
        fixed_image = sitk.Cast(fixed_image, sitk.sitkFloat32)
        moving_image = sitk.Cast(moving_image, sitk.sitkFloat32)
        
        if registration_method is None:
                registration_method = define_registration_method()
        
        if initial_transform is None:
                initial_transform = tran.define_transform()
        
        if fixed_mask:
                registration_method.SetMetricFixedMask(fixed_mask)
        
        if moving_mask:
                registration_method.SetMetricMovingMask(moving_mask)
        
        registration_method.SetInitialTransform(initial_transform)
        
        registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, reg_plot.update_idx_resolution_switch)
        registration_method.AddCommand(sitk.sitkIterationEvent,
                                       lambda: reg_plot.update_plot(registration_method.GetMetricValue(), initial_transform))
        registration_method.AddCommand(sitk.sitkEndEvent, lambda: reg_plot.plot_final_overlay(initial_transform))
        
        return (registration_method.Execute(fixed_image, moving_image),
                registration_method.GetMetricValue(),
                registration_method.GetOptimizerStopConditionDescription())


def query_good_registration(transform: sitk.Transform, metric, stop):
        
        print('\nFinal metric value: {0}'.format(metric))
        print('\n{0}'.format(stop))
        
        transform_params = transform.GetParameters()
        matrix = np.array([transform_params[0:2], transform_params[2:4]])
        translation = np.array(transform_params[4:6])
        print('\nTransform Matrix: \n{0}'.format(matrix))
        print('\nTransform Translation: \n{0}'.format(translation))
        
        plt.show()
        
        return util.yes_no('Is this registration good? [y/n] >>> ')


def query_pre_rotation(fixed_image: sitk.Image, moving_image: sitk.Image,
                       initial_transform: sitk.Transform):
        """Ask if the user wants a new 2D ITK origin based on image overlay"""
        
        itkplt.plot_overlay(fixed_image, moving_image, initial_transform)
        
        change_rotation = util.yes_no('Do you want to change the rotation? [y/n] >>> ')
        
        if change_rotation:
                while True:
                        rotation = util.query_float('Enter new rotation (degrees):')
                        tran.change_transform_rotation(initial_transform, rotation)
                        
                        itkplt.plot_overlay(fixed_image, moving_image, initial_transform, rotation)
                        
                        # bug: The image does not show up till after the question
                        if util.yes_no('Is this rotation good? [y/n] >>> '): break
        

def query_translation_change(fixed_image: sitk.Image, moving_image: sitk.Image,
                             transform: sitk.Transform):
        """Ask if the user wants a new 2D ITK translation based on image overlay"""
        
        change_origin = util.yes_no('Do you want to change the initial translation? [y/n] >>> ')
        translation = tran.get_translation(transform)
        
        if change_origin:
                while True:
                        print('Current translation: ' + str(translation))
                        new_translation = []
                        for dim in len(translation):
                                new_dim_translation = util.query_float(
                                        'Enter the new translation in dimension {0}'.format(str(dim)))
                                new_translation.append(new_dim_translation)
                        
                        tran.set_translation(transform, translation)
                        itkplt.plot_overlay(fixed_image, moving_image, transform)
                        
                        # bug: The image does not show up till after the question
                        if util.yes_no('Is this translation good? [y/n] >>> '): break


def supervised_register_images(fixed_image: sitk.Image, moving_image: sitk.Image,
                               registration_method: sitk.ImageRegistrationMethod=None,
                               initial_transform: sitk.Transform=None):
        """Register two images
    
        :param fixed_image: image that is being registered to
        :param moving_image: image that is being transformed and registered
        :param registration_method: the pre-defined optimizer/metric/interpolator
        :param initial_transform: the type of registration/transform, e.g. affine or euler
        :return:
        """
        
        moving_image_is_rgb = moving_image.GetNumberOfComponentsPerPixel() > 1
        if moving_image_is_rgb:
                moving_image_2d = rgb_to_2d_img(moving_image)
        else:
                moving_image_2d = moving_image
        
        while True:
                query_pre_rotation(fixed_image, moving_image_2d, initial_transform)
                query_translation_change(fixed_image, moving_image_2d, initial_transform)
                
                reg_plot = RegistrationPlot(fixed_image, moving_image_2d)
                (transform, metric, stop) = register(fixed_image, moving_image_2d, reg_plot,
                                                     registration_method=registration_method,
                                                     initial_transform=initial_transform)
                
                if query_good_registration(transform, metric, stop):
                        break
        
        origin = moving_image.GetOrigin()
        
        registered_image = sitk.Resample(moving_image, fixed_image,
                                         transform, sitk.sitkLinear,
                                         0.0, moving_image.GetPixelID())
        
        meta.copy_relevant_metadata(registered_image, moving_image)
        plt.close('all')
        
        return registered_image, origin, transform, metric, stop


def bulk_supervised_register_images(fixed_dir: Path, moving_dir: Path,
                                    output_dir: Path, output_suffix: str, write_output: bool=True,
                                    write_transform: bool=True, transform_type: type=sitk.AffineTransform,
                                    iterations: int=100, scale: int=3,
                                    skip_existing_images: bool=True):
        """Register two directories of images, matching based on the core name, the string before the first _
    
        :param fixed_dir: directory holding the images that are being registered to
        :param moving_dir: directory holding the images that will be registered
        :param output_dir: directory to save the output images
        :param output_suffix: base name of the output images
        :param write_output: whether or not to actually write the output image
        :param write_transform: whether or not to write down the transform that produced the output
        :param transform_type: what type of registration, e.g. affine or euler
        :param iterations: how many times will the algorithm calcluate the metric before switching resolutions/ending
        :param scale: how many resolution scales the algorithm measures at
        :param skip_existing_images: whether to skip images that already have a transform/output image
        :return:
        """
        
        (fixed_path_list, moving_path_list) = blk.find_shared_images(
                fixed_dir, moving_dir)
        
        for i in range(0, np.size(fixed_path_list)):
                registered_path = blk.create_new_image_path(moving_path_list[i], output_dir, output_suffix)
                if registered_path.exists() and skip_existing_images:
                        continue
                
                registration_method = define_registration_method(scale=scale, iterations=iterations)
                
                fixed_image = meta.setup_image(fixed_path_list[i])
                moving_image = meta.setup_image(moving_path_list[i])
                initial_transform = tran.read_initial_transform(moving_image, transform_type)
                
                print('\nRegistering ' + os.path.basename(moving_path_list[i]) + ' to '
                      + os.path.basename(fixed_path_list[i]))
                
                registered_image, origin, transform, metric, stop= \
                        supervised_register_images(fixed_image, moving_image, registration_method,
                                                   initial_transform)
                                
                if write_output:
                        sitk.WriteImage(registered_image, str(registered_path))
                
                if write_transform:
                        tran.write_transform(registered_path, transform)




