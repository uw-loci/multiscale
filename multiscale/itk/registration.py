# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:38:19 2018

@author: mpinkert
"""
import multiscale.bulk_img_processing as blk
import multiscale.utility_functions as util

import multiscale.itk.metadata as meta
import multiscale.itk.transform as tran
from multiscale.itk.itk_plotting import RegistrationPlot
import multiscale.itk.itk_plotting as itkplt

import SimpleITK as sitk
import numpy as np
import os

from pathlib import Path

import matplotlib.pyplot as plt

from multiscale.itk.process import rgb_to_grayscale_img


class RegistrationHelper(object):
        """
        A registration interface that works with Jupyter notebooks
        """
        def __init__(self, fixed_image: sitk.Image, moving_image: sitk.Image,
                     output_dir=None, registration_params=None):
                self._fixed_image = fixed_image
                self._moving_image = moving_image
                self._output_dir = output_dir
                self._registration_params = registration_params
                self._registered_image = None

        def setup_registration(self):
                return
        
        def perform_registration(self):
                return
        
        
        


def _setup_smoothing_sigmas(scale: int=1):
        """Setup the smoothing sigmas array for registration"""
        smoothing_sigmas = [0]
        if scale > 1:
                for idx in range(1, scale, 1):
                        smoothing_sigmas.insert(0, 2**(idx - 1))
                print('No smoothing sigmas given, setting to {}'.format(smoothing_sigmas))
        
        return smoothing_sigmas


def _setup_shrink_factors(scale: int=1):
        """Setup the smoothing sigmas array for registration"""
        shrink_factors = [1]
        if scale > 1:
                for idx in range(1, scale, 1):
                        shrink_factors.insert(0, 2**idx)
                print('No shrink factors given, setting to {}'.format(shrink_factors))
                
        return shrink_factors


def setup_registration_parameters(scale: int=1, smoothing_sigmas: list=None, shrink_factors: list=None,
                                  iterations: int=100, learning_rate: float=3,
                                  min_step: float=0.01, gradient_tolerance: float=1E-6,
                                  sampling_percentage: float=0.01):
        """
        Define the registration parameters and convert it into a dictionary for easy passing through functions
        :param scale: How many times the method performs registration, downsampling based on the shrink factor
        :param smoothing_sigmas: Gaussian smoothing operation at scales. Default [0], then factor of 2 e.g. [4, 2, 1, 0]
        :param shrink_factors: Downsampling for each registration.  Default factors of 2, e.g. [8, 4, 2, 1]
        :param iterations: The number of times the method optimizes the metric before
        :param learning_rate: How far is each move in the gradient descent.
        :param min_step: The minimum learning rate, as the algorithm /2 every time metric moves in opposite directions
        :param gradient_tolerance: If the gradient is below this size, stop the algorithm
        :param sampling_percentage: How many pixels are used in the metric evaluation
        :return:
        """
        
        if smoothing_sigmas is None:
                smoothing_sigmas = _setup_smoothing_sigmas(scale)
        elif len(smoothing_sigmas) != scale:
                raise ValueError('The smoothing sigmas list is not the same size as the scale')
        
        if shrink_factors is None:
                shrink_factors = _setup_shrink_factors(scale)
        elif len(shrink_factors) != scale:
                raise ValueError('The shrink factors list is not the same size as the scale')
                
        parameters = {
                'scale': scale,
                'iterations': iterations,
                'learning_rate': learning_rate,
                'min_step': min_step,
                'gradient_tolerance': gradient_tolerance,
                'sampling_percentage': sampling_percentage,
                'smoothing_sigmas': smoothing_sigmas,
                'shrink_factors': shrink_factors
        }
        return parameters
        
        
def define_registration_method(parameters: dict) -> sitk.ImageRegistrationMethod:
        """
        Define the base metric, interpolator, and optimizer of a registration or series of registrations
    
        :param parameters: A dictionary of parameter key/value pairs defined by setup_registration_parameters
        """
        # todo: Make this run off of kwargs
        
        if parameters is None:
                parameters = setup_registration_parameters()
        
        registration_method = sitk.ImageRegistrationMethod()
        
        # Similarity metric settings.|
        registration_method.SetMetricAsMattesMutualInformation()
        registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
        registration_method.SetMetricSamplingPercentage(parameters['sampling_percentage'])
        
        registration_method.SetInterpolator(sitk.sitkLinear)
        
        # Optimizer settings.
        registration_method.SetOptimizerAsRegularStepGradientDescent(
                learningRate=parameters['learning_rate'], minStep=parameters['min_step'],
                numberOfIterations=parameters['iterations'],
                gradientMagnitudeTolerance=parameters['gradient_tolerance'])
        
        registration_method.SetOptimizerScalesFromPhysicalShift()
        
        #Set up for multi-resolution framework
        registration_method.SetShrinkFactorsPerLevel(parameters['shrink_factors'])
        registration_method.SetSmoothingSigmasPerLevel(parameters['smoothing_sigmas'])
        registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOff()
        
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
        
        final_transform = registration_method.Execute(fixed_image, moving_image)
        final_metric = registration_method.GetMetricValue()
        stop_condition = registration_method.GetOptimizerStopConditionDescription()
        
        return (final_transform, final_metric, stop_condition)


def query_good_registration(transform: sitk.Transform, metric, stop):

        print('\nFinal metric value: {0}'.format(metric))
        print('\n{0}'.format(stop))
        
        transform_params = transform.GetParameters()
        matrix = np.array([transform_params[0:2], transform_params[2:4]])
        translation = np.array(transform_params[4:6])
        print('\nTransform Matrix: \n{0}'.format(matrix))
        print('\nTransform Translation: \n{0}'.format(translation))
        
        return util.query_yes_no('Is this registration good? [y/n] >>> ')


def query_rotation_change(fixed_image: sitk.Image, moving_image: sitk.Image,
                          initial_transform: sitk.Transform):
        """Ask if the user wants a new 2D ITK origin based on image overlay"""
        
        itkplt.plot_overlay(fixed_image, moving_image, initial_transform)
        
        change_rotation = util.query_yes_no('Do you want to change the rotation? [y/n] >> ')
        
        if change_rotation:
                while True:
                        rotation = util.query_float('Enter new rotation (degrees): ')
                        tran.set_transform_rotation(initial_transform, rotation)
                        
                        itkplt.plot_overlay(fixed_image, moving_image, initial_transform, rotation)
                        
                        # bug: The image does not show up till after the question
                        if util.query_yes_no('Is this rotation good? [y/n] >> '): break
        

def query_translation_change(fixed_image: sitk.Image, moving_image: sitk.Image,
                             transform: sitk.Transform):
        """Ask if the user wants a new 2D ITK translation based on image overlay"""
        
        change_origin = util.query_yes_no('Do you want to change the initial translation? [y/n] >> ')
        translation = tran.get_translation(transform)
        
        if change_origin:
                while True:
                        print('Current physical shift: ' + str(-1*np.array(translation)))
                        new_translation = []
                        for dim in range(len(translation)):
                                new_dim_translation = -1*util.query_float(
                                        'Enter the new shift in dimension {0} >> '.format(str(dim)))
                                new_translation.append(new_dim_translation)
                        
                        tran.set_translation(transform, new_translation)
                        itkplt.plot_overlay(fixed_image, moving_image, transform)
                        
                        # bug: The image does not show up till after the question
                        if util.query_yes_no('Is this translation good? [y/n] >>> '): break


def get_region_size_origin_indices(size, origin, spacing):
        """
        Convert the size and origin indices from physical dimensions to integer index
        :param size: Size of a region in physical space
        :param origin: Origin of a region in physical space
        :param spacing: Physical spacing of pixels
        :return:
        """
        dimensions = len(spacing)
        integer_size = [int(np.floor(size / spacing[i])) for i in range(dimensions)]
        integer_index = [int(np.floor(origin[i] / spacing[i])) for i in range(dimensions)]
        return integer_size, integer_index


def extract_region(image: sitk.Image, size, origin, transform=None):
        """
        Extract a region from a SimpleITK image
        :param image: The SimpleITK image
        :param size: The size of the region in physical space
        :param origin: The origin of the region in physical space
        :param transform: Image transform to apply before extracting the region
        :return: A SimpleITK image that corresponds to the region
        """
        if transform is not None:
                translation = tran.get_translation(transform)
                origin = origin + translation
        
        size_array, index = get_region_size_origin_indices(size, origin, image.GetSpacing())
        region = sitk.Extract(image, size_array, index)
        meta.copy_relevant_metadata(region, image)
        return region
        

def query_registration_sampling_change(registration_method: sitk.ImageRegistrationMethod):
        """
        Ask the user if they want to change the registration sampling rate, and to what if they do.
        :param registration_method: The registration method being used in the registration algorithm
        :return:
        """
        do_change = util.query_yes_no('Do you wish to change the registration sampling rate (default 0.01)? [y/n] >> ')
        if do_change:
                while True:
                        new_rate = util.query_float('Please enter a rate >0 and <= 1 >> ')
                        if new_rate > 0 and new_rate <= 1:
                                break
                        print('{0} is an invalid rate'.format(new_rate))
                registration_method.SetMetricSamplingPercentage(new_rate)


def query_extract_region(fixed_image: sitk.Image, moving_image: sitk.Image, transform: sitk.Transform,
                         registration_method: sitk.ImageRegistrationMethod):
        do_extract = util.query_yes_no('Do you wish to extract a sub-region to register based on? [y/n] >> ')

        if do_extract:
                itkplt.plot_overlay(fixed_image, moving_image, transform=transform)
                
                size = util.query_int('Enter the region size >> ')
                
                origin = []
                for dim in range(len(fixed_image.GetSpacing())):
                        origin_in_dim = util.query_float('Enter the origin in dimension {0} >> '.format(dim))
                        origin.append(origin_in_dim)
                origin = np.array(origin)

                fixed_region = extract_region(fixed_image, size, origin)
                moving_region = extract_region(moving_image, size*1.1, origin-0.05*size, transform)
                
                query_registration_sampling_change(registration_method)
                
                return fixed_region, moving_region, do_extract
                
        else:
                return fixed_image, moving_image, do_extract


def query_for_changes(fixed_image: sitk.Image, moving_image: sitk.Image, initial_transform: sitk.Transform,
                      registration_method: sitk.ImageRegistrationMethod, moving_path: Path=None):
        """
        Ask the user if they want to change initial conditions before registration
        :param fixed_image: Image being registered to
        :param moving_image: Image that is being transformed
        :param initial_transform: The pre-registration transform setup
        :param registration_method: The container for the image registration
        :param moving_path: Path to the moving image to save the initial transform
        :return:
        """
        query_rotation_change(fixed_image, moving_image, initial_transform)
        query_translation_change(fixed_image, moving_image, initial_transform)
        if moving_path is not None:
                tran.write_initial_transform(moving_path, initial_transform)
        
        fixed_final, moving_final, region_extracted = query_extract_region(fixed_image, moving_image,
                                                                           initial_transform,
                                                                           registration_method)

        return fixed_final, moving_final, region_extracted


def supervised_register_images(fixed_image: sitk.Image, moving_image: sitk.Image,
                               initial_transform: sitk.Transform=None, moving_path=None,
                               registration_parameters: dict=None):
        """Register two images
    
        :param fixed_image: image that is being registered to
        :param moving_image: image that is being transformed and registered
        :param initial_transform: the type of registration/transform, e.g. affine or euler
        :param registration_parameters: dictionary of registration key/value arguments
        :return: Registered image, corresponding transform, metric, and stop
        """
        
        # todo: Re-enable registering for RGB images
        
        while True:
                registration_method = define_registration_method(registration_parameters)
                fixed_final, moving_final, region_extracted = query_for_changes(fixed_image, moving_image,
                                                                                initial_transform, registration_method,
                                                                                moving_path)
                reg_plot = RegistrationPlot(fixed_final, moving_final)
                
                (transform, metric, stop) = register(fixed_final, moving_final, reg_plot,
                                                     registration_method=registration_method,
                                                     initial_transform=initial_transform)
                
                if region_extracted:
                        itkplt.plot_overlay(fixed_image, moving_image, transform, downsample=False)
                        
                if query_good_registration(transform, metric, stop):
                        break
                # todo: change registration method query here
                
        registered_image = sitk.Resample(moving_image, fixed_image, transform,
                                         sitk.sitkLinear, 0.0, moving_image.GetPixelID())
        
        meta.copy_relevant_metadata(registered_image, moving_image)
        plt.close('all')
        
        return registered_image, transform, metric, stop


def bulk_supervised_register_images(fixed_dir: Path, moving_dir: Path,
                                    output_dir: Path, output_suffix: str, write_output: bool=True,
                                    write_transform: bool=True, transform_type: type=sitk.AffineTransform,
                                    registration_parameters: dict=None, skip_existing_images=True):
        """Register two directories of images, matching based on the core name, the string before the first _
    
        :param fixed_dir: directory holding the images that are being registered to
        :param moving_dir: directory holding the images that will be registered
        :param output_dir: directory to save the output images
        :param output_suffix: base name of the output images
        :param write_output: whether or not to actually write the output image
        :param write_transform: whether or not to write down the transform that produced the output
        :param transform_type: what type of registration, e.g. affine or euler
        :param registration_parameters: dictionary of registration key/value arguments
        :param skip_existing_images: whether to skip images that already have a transform/output image
        :return:
        """
        
        (fixed_path_list, moving_path_list) = blk.find_shared_images(
                fixed_dir, moving_dir)
        
        for i in range(0, np.size(fixed_path_list)):
                registered_path = blk.create_new_image_path(moving_path_list[i], output_dir, output_suffix)
                if registered_path.exists() and skip_existing_images:
                        continue
                        
                fixed_image = meta.setup_image(fixed_path_list[i])
                moving_image = meta.setup_image(moving_path_list[i])
                initial_transform = tran.read_initial_transform(moving_path_list[i], transform_type)
                
                print('\nRegistering ' + os.path.basename(moving_path_list[i]) + ' to '
                      + os.path.basename(fixed_path_list[i]))
                
                registered_image, transform, metric, stop = \
                        supervised_register_images(fixed_image, moving_image, initial_transform,
                                                   moving_path_list[i], registration_parameters)
                                
                if write_output:
                        meta.write_image(registered_image, registered_path)
                
                if write_transform:
                        tran.write_transform(registered_path, transform)
