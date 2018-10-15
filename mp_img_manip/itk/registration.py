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


def define_transform(type_of_transform: str='affine', rotation: np.double=0) -> sitk.Transform:
        
        deg_to_rad = 2*np.pi/360
        angle = rotation*deg_to_rad
        
        if type_of_transform == 'euler':
                transform = sitk.Euler2DTransform()
                transform.SetAngle(angle)
        elif type_of_transform == 'affine':
                transform = sitk.AffineTransform(2)
                transform.Rotate(0, 1, angle, pre=True)
        else:
                raise('{0} registration has not been implemented yet'.format(type_of_transform))
        
        return transform


def register(fixed_image: sitk.Image, moving_image: sitk.Image, reg_plot: RegistrationPlot,
             registration_method: sitk.ImageRegistrationMethod=None,
             transform: sitk.Transform=None,
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
        transform -- The calculated image transform for registration
        metric -- The mutual information value at the stopping poin
        stop -- the stopping condition of the optimizer
        """
        
        fixed_image = sitk.Cast(fixed_image, sitk.sitkFloat32)
        moving_image = sitk.Cast(moving_image, sitk.sitkFloat32)
        
        if registration_method is None:
                registration_method = define_registration_method()
        
        if transform is None:
                transform = define_transform()
        
        if fixed_mask:
                registration_method.SetMetricFixedMask(fixed_mask)
        
        if moving_mask:
                registration_method.SetMetricMovingMask(moving_mask)
        
        registration_method.SetInitialTransform(transform)
        
        registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, reg_plot.update_idx_resolution_switch)
        registration_method.AddCommand(sitk.sitkIterationEvent,
                                       lambda: reg_plot.update_plot(registration_method.GetMetricValue(), transform))
        registration_method.AddCommand(sitk.sitkEndEvent, lambda: reg_plot.plot_final_overlay(transform))
        
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
                       initial_rotation: np.double, type_of_transform: str):
        """Ask if the user wants a new 2D ITK origin based on image overlay"""
        
        transform = define_transform(type_of_transform, rotation=initial_rotation)
        
        itkplt.plot_overlay(fixed_image, moving_image, transform, initial_rotation)
        
        change_rotation = util.yes_no('Do you want to change the rotation? [y/n] >>> ')
        
        rotation = initial_rotation
        
        if change_rotation:
                while True:
                        rotation = util.query_float('Enter new rotation (degrees):')
                        transform = define_transform(type_of_transform, rotation=rotation)
                        
                        itkplt.plot_overlay(fixed_image, moving_image, transform, rotation)
                        
                        # bug: The image does not show up till after the question
                        if util.yes_no('Is this rotation good? [y/n] >>> '): break
        
        return transform, rotation


def query_origin_change(fixed_image: sitk.Image, moving_image: sitk.Image,
                        transform: sitk.Transform, rotation: np.double):
        """Ask if the user wants a new 2D ITK origin based on image overlay"""
        
        change_origin = util.yes_no('Do you want to change the origin? [y/n] >>> ')
        origin = moving_image.GetOrigin()
        
        # todo: have it change the origin file too....
        
        if change_origin:
                while True:
                        print('Current origin: ' + str(origin))
                        new_origin_x = util.query_int('Enter new X origin: ')
                        new_origin_y = util.query_int('Enter new Y origin: ')
                        
                        new_origin = (new_origin_x, new_origin_y)
                        
                        moving_image.SetOrigin(new_origin)
                        itkplt.plot_overlay(fixed_image, moving_image, transform, rotation)
                        
                        # bug: The image does not show up till after the question
                        if util.yes_no('Is this origin good? [y/n] >>> '): break
                
                return new_origin
        else:
                return origin


def write_image(registered_image: sitk.Image, registered_path: Path, rotation: np.double):
        """Save an itk image and output parameters
    
        :param registered_image: the final registered image
        :param registered_path: the path to save the registered image to
        :param rotation: rotation of the final image, typically 0
        :return:
        """
        sitk.WriteImage(registered_image, str(registered_path))
        
        meta.write_image_parameters(registered_path,
                                    registered_image.GetSpacing(),
                                    registered_image.GetOrigin(),
                                    rotation)


def supervised_register_images(fixed_image: sitk.Image, moving_image: sitk.Image,
                               registration_method: sitk.ImageRegistrationMethod=None,
                               type_of_transform: str='affine', rotation: np.double=0):
        """Register two images
    
        :param fixed_image: image that is being registered to
        :param moving_image: image that is being transformed and registered
        :param registration_method: the pre-defined optimizer/metric/interpolator
        :param type_of_transform: the type of registration/transform, e.g. affine or euler
        :return:
        """
        
        moving_image_is_rgb = moving_image.GetNumberOfComponentsPerPixel() > 1
        if moving_image_is_rgb:
                moving_image_2d = rgb_to_2d_img(moving_image)
        else:
                moving_image_2d = moving_image
        
        while True:
                transform, rotation = query_pre_rotation(fixed_image, moving_image_2d, rotation, type_of_transform)
                moving_origin = query_origin_change(fixed_image, moving_image_2d, transform, rotation)
                moving_image_2d.SetOrigin(moving_origin)
                
                reg_plot = RegistrationPlot(fixed_image, moving_image_2d)
                (transform, metric, stop) = register(fixed_image, moving_image_2d, reg_plot,
                                                     registration_method=registration_method, transform=transform)
                
                if query_good_registration(transform, metric, stop):
                        break
        
        origin = moving_image.GetOrigin()
        
        registered_image = sitk.Resample(moving_image, fixed_image,
                                         transform, sitk.sitkLinear,
                                         0.0, moving_image.GetPixelID())
        
        plt.close('all')
        
        return registered_image, origin, transform, metric, stop, rotation


def bulk_supervised_register_images(fixed_dir: Path, moving_dir: Path,
                                    output_dir: Path, output_suffix: str, write_output: bool=True,
                                    write_transform: bool=True, type_of_transform: str='affine',
                                    iterations: int=100, scale: int=3,
                                    skip_existing_images: bool=True):
        """Register two directories of images, matching based on the core name, the string before the first _
    
        :param fixed_dir: directory holding the images that are being registered to
        :param moving_dir: directory holding the images that will be registered
        :param output_dir: directory to save the output images
        :param output_suffix: base name of the output images
        :param write_output: whether or not to actually write the output image
        :param write_transform: whether or not to write down the transform that produced the output
        :param type_of_transform: what type of registration, e.g. affine or euler
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
                
                fixed_image = meta.setup_image(fixed_path_list[i], change_origin=False)
                moving_image, rotation = meta.setup_image(moving_path_list[i], return_rotation=True)
                print('\nRegistering ' + os.path.basename(moving_path_list[i]) + ' to '
                      + os.path.basename(fixed_path_list[i]))
                
                registered_image, origin, transform, metric, stop, rotation = \
                        supervised_register_images(fixed_image, moving_image, registration_method,
                                                   type_of_transform=type_of_transform)
                
                meta.write_image_parameters(moving_path_list[i], moving_image.GetSpacing(), origin, rotation)
                
                if write_output:
                        write_image(registered_image, registered_path, rotation)
                
                if write_transform:
                        tran.write_transform_pandas(registered_path, origin, transform, metric, stop, rotation)




