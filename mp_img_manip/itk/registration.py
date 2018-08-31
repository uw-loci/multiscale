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
from mp_img_manip.itk.registration_plot import RegistrationPlot

import SimpleITK as sitk
import numpy as np
import os

from pathlib import Path

import matplotlib.pyplot as plt


def plot_overlay(fixed_image: sitk.Image, moving_image: sitk.Image, rotation: np.double):
    origin = moving_image.GetOrigin()

    transform = sitk.AffineTransform(2)
    deg_to_rad = 2 * np.pi / 360

    transform.Rotate(0, 1, rotation * deg_to_rad, pre=True)

    rotated_image = sitk.Resample(moving_image, fixed_image, transform,
                                  sitk.sitkLinear, 0.0,
                                  moving_image.GetPixelIDValue())

    fig, ax = plt.subplots()
    ax.set_title('Rotation = {}, Origin = {}'.format(rotation, origin))
    img = ax.imshow(proc.overlay_images(fixed_image, rotated_image))

    mng = plt.get_current_fig_manager()
    geom = mng.window.geometry().getRect()
    mng.window.setGeometry(-1800, 100, geom[2], geom[3])

    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.02)


def affine_register(fixed_image, moving_image, reg_plot: RegistrationPlot,
                    scale=3, iterations=10,
                    fixed_mask=None, moving_mask=None, rotation=0,
                    learning_rate=200, min_step=0.01, gradient_tolerance=1E-5):
    """Perform an affine registration using MI and RSGD over up to 4 scales
    
    Uses mutual information and regular step gradient descent
    
    Inputs:
    fixed_image -- The image that is registered to
    moving_image -- The image that is being registered
    scale -- how many resolution scales the function uses
    iterations -- Iterations per scale before the function stops
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

    transform = sitk.AffineTransform(2)
    deg_to_rad = 2*np.pi/360
    transform.Rotate(0, 1, rotation*deg_to_rad, pre=True)
    registration_method.SetInitialTransform(transform)

    registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, reg_plot.update_idx_resolution_switch)
    registration_method.AddCommand(sitk.sitkIterationEvent, lambda: reg_plot.update_plot(
        registration_method.GetMetricValue(), fixed_image, moving_image, transform))

    return (registration_method.Execute(fixed_image, moving_image),
            registration_method.GetMetricValue(),
            registration_method.GetOptimizerStopConditionDescription())


def query_good_registration(fixed_image, moving_image,
                            transform, metric, stop):

    print('\nFinal metric value: {0}'.format(metric))
    print('\n{0}'.format(stop))

    transform_params = transform.GetParameters()
    matrix = np.array([transform_params[0:2], transform_params[2:4]])
    translation = np.array(transform_params[4:6])
    print('\nTransform Matrix: \n{0}'.format(matrix))
    print('\nTransform Translation: \n{0}'.format(translation))

    return util.yes_no('Is this registration good? [y/n] >>> ')


def query_pre_rotation(fixed_image, moving_image, initial_rotation):
    """Ask if the user wants a new 2D ITK origin based on image overlay"""

    plot_overlay(fixed_image, moving_image, initial_rotation)

    change_rotation = util.yes_no('Do you want to change the rotation? [y/n] >>> ')

    rotation = initial_rotation

    if change_rotation:
        while True:
            rotation = util.query_float('Enter new rotation (degrees):')

            plot_overlay(fixed_image, moving_image, rotation)

            # bug: The image does not show up till after the question
            if util.yes_no('Is this rotation good? [y/n] >>> '): break

    return rotation


def query_origin_change(fixed_image, moving_image, rotation):
    """Ask if the user wants a new 2D ITK origin based on image overlay"""

    plot_overlay(fixed_image, moving_image, rotation)

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
            plot_overlay(fixed_image, moving_image, rotation)

            # bug: The image does not show up till after the question
            if util.yes_no('Is this origin good? [y/n] >>> '): break

        return new_origin
    else:
        return origin


def rgb_to_2d_img(moving_image):
    """Convert an RGB to grayscale image by extracting the average intensity, filtering out white light >230 avg"""
    array = sitk.GetArrayFromImage(moving_image)
    array_2d = np.average(array, 0)
    array_2d[array_2d > 230] = 0

    moving_image_2d = sitk.GetImageFromArray(array_2d)
    spacing_2d = moving_image.GetSpacing()[:2]
    moving_image_2d.SetSpacing(spacing_2d)

    origin_2d = moving_image.GetOrigin()[:2]
    moving_image_2d.SetOrigin(origin_2d)
    return moving_image_2d


def write_image(registered_image, registered_path, rotation):
    if registered_image.GetDimension() > 2:
        arr_rgb_wrong_idx = sitk.GetArrayFromImage(registered_image)
        arr_rotated_idx = np.swapaxes(arr_rgb_wrong_idx, 0, 2)
        arr_correct_idx = np.swapaxes(arr_rotated_idx, 0, 1)

        rgb_image = sitk.GetImageFromArray(arr_correct_idx, isVector=True)

        spacing_original = registered_image.GetSpacing()
        spacing_new = np.array([spacing_original[1], spacing_original[2]])
        rgb_image.SetSpacing(spacing_new)

        sitk.WriteImage(rgb_image)

    else:
        sitk.WriteImage(registered_image, str(registered_path))

    meta.write_image_parameters(registered_path,
                                registered_image.GetSpacing(),
                                registered_image.GetOrigin(),
                                rotation)


def supervised_register_images(fixed_path: Path, moving_path: Path,
                               iterations=200, scale=4, rotation=0):

    fixed_image = meta.setup_image(fixed_path)
    moving_image, rotation = meta.setup_image(moving_path, return_rotation=True)
    print('\nRegistering ' + os.path.basename(moving_path) + ' to '
          + os.path.basename(fixed_path))

    moving_image_is_rgb = np.size(moving_image.GetSpacing()) > 2
    if moving_image_is_rgb:
        moving_image_2d = rgb_to_2d_img(moving_image)
    else:
        moving_image_2d = moving_image

    while True:

        rotation = query_pre_rotation(fixed_image, moving_image_2d, rotation)
        moving_image_2d.SetOrigin(query_origin_change(fixed_image, moving_image_2d, rotation))

        reg_plot = RegistrationPlot(fixed_image, moving_image_2d)
        (transform, metric, stop) = affine_register(fixed_image, moving_image_2d, reg_plot,
                                                    iterations=iterations, scale=scale, rotation=rotation)

        if query_good_registration(fixed_image, moving_image_2d, transform, metric, stop):
            break

    origin = moving_image.GetOrigin()
    meta.write_image_parameters(moving_path, moving_image.GetSpacing(), origin, rotation)

    registered_image = sitk.Resample(moving_image, fixed_image,
                                     transform, sitk.sitkLinear,
                                     0.0, moving_image.GetPixelID())

    plt.close('all')

    return registered_image, origin, transform, metric, stop, rotation


def bulk_supervised_register_images(fixed_dir, moving_dir,
                                    output_dir, output_suffix,
                                    write_output=True, write_transform=True,
                                    iterations=100, scale=2,
                                    skip_existing_images=False):

    (fixed_path_list, moving_path_list) = blk.find_shared_images(
        fixed_dir, moving_dir)

    for i in range(0, np.size(fixed_path_list)):
        registered_path = blk.create_new_image_path(moving_path_list[i], output_dir, output_suffix)
        if registered_path.exists() and skip_existing_images:
            continue
        
        registered_image, origin, transform, metric, stop, rotation = \
            supervised_register_images(fixed_path_list[i], moving_path_list[i], iterations=iterations, scale=scale)

        if write_output:
            write_image(registered_image, registered_path, rotation)

        if write_transform:
            tran.write_transform(registered_path, origin, transform, metric, stop, rotation)




