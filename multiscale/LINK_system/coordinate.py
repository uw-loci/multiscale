"""
This module contains functions for mapping between the different image coordinate transforms

Copyright (c) 2018, Michael Pinkert
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Laboratory for Optical and Computational Instrumentation nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import SimpleITK as sitk
import numpy as np

import multiscale.itk.process as proc
import multiscale.microscopy.ome as ome
import multiscale.ultrasound.reconstruction as recon


def open_us(us_path, pl_path, params_path, dynamic_range, gauge_value):
        """
        Open the US image, window it to a dynamic range, and rotate it to microscope coordinate axes
        :param us_path: Path to the US image
        :param pl_path: Path to the position list for the US image
        :param params_path: Path to a .mat file with the P parameter struct
        :param dynamic_range: Window width in dB, measured from the maximum signal
        :param gauge_value: Indicator gauge value for the US image
        :return: SimpleITK US image with appropriate origin, direction, and spacing
        """
        # todo: Read in param.start depth to properly set the origin
        raw_image = sitk.ReadImage(str(us_path))
        windowed_image = proc.window_image(raw_image, dynamic_range)
        
        spacing = ome.get_spacing(us_path, order=['X', 'Z', 'Y'])
        
        params = recon.read_variable(params_path, 'P')
        origin_xy = recon.get_xy_origin(pl_path)
        origin_z = recon.get_z_origin(params, gauge_value)
        origin = [origin_xy[0], origin_xy[1], origin_z]
        
        us_image = rotate_axes_to_microscope(windowed_image)
        us_image.SetSpacing(spacing)
        us_image.SetOrigin(origin)
        us_image.SetDirection([1, 0, 0, 0, 1, 0, 0, 0, -1])
        return us_image


def open_microscopy(microscopy_path, microscopy_origin_path, downsample_factor=1):
        """
        Open the MPM image and set the direction to -1 in Z to mirror microscope convention
        :param microscopy_path: Path to the MPM image
        :param microscopy_origin_path: Path to the first saved tile of the MPM image, to extract the coordinates
        :param downsample_factor: The downsample factor in XY for the microscopy image.  Default to 1
        :return: SimpleITK MPM image with appropriate origin, direction, and spacing
        """
        positions = ome.get_positions(microscopy_origin_path)
        origin = np.min(positions, 0)
        
        spacing = ome.get_spacing(microscopy_origin_path)
        spacing[0] = spacing[0]*downsample_factor
        spacing[1] = spacing[1]*downsample_factor
        
        microscopy_image = sitk.ReadImage(str(microscopy_path))
        microscopy_image.SetSpacing(spacing)
        microscopy_image.SetOrigin(origin)
        microscopy_image.SetDirection([1, 0, 0, 0, 1, 0, 0, 0, -1])
        
        return microscopy_image


def rotate_axes_to_microscope(image):
        """
        Rotate the US axes to be along the microscope axes
        :param image: US image to rotate
        :return: Rotated image
        """
        arr = sitk.GetArrayFromImage(image)
        arr_rot = np.swapaxes(arr, 0, 1)
        arr_rot = np.flip(arr_rot, 0).astype(np.uint8)
        return sitk.GetImageFromArray(arr_rot)


def get_fiducial_stats(connected_img):
        """
        Get statistics for each object in a label image
        :param connected_img: A color image with each object a different color; taken from the connected component filter.
        :return: Object statistics for each unique object
        """
        stats = sitk.LabelShapeStatisticsImageFilter()
        stats.ComputeOrientedBoundingBoxOn()
        stats.ComputePerimeterOn()
        stats.Execute(connected_img)
        return stats


def filter_labels(stats):
        """
        Filter labels by property so you only get the fiducial circles
        :param stats: Object statistics for whole connected component image
        :return: Labels for the right objects
        """
        return [l for l in stats.GetLabels() if (stats.GetNumberOfPixels(l) < 300000
                                                 and stats.GetEquivalentEllipsoidDiameter(l)[1] > 2000)]


def get_leveled_centroid(stats, true_labels):
        """
        Get the leveled Z height, equivalent to the bottom of fiducial, for each label
        :param stats: Object statistics
        :param true_labels: Labels for the fiducial objects.
        :return: List of leveled Z heights
        """
        centroid = [stats.GetCentroid(l) for l in true_labels]
        level_center = []
        idx = 0
        for center in centroid:
                level_center.append(center[2] + np.floor((idx+3)/3)*1000)
        idx = idx+1
        return np.array(level_center)


def get_ellipsoid_radius(stats, true_labels):
        """Get the equivalent radius of objects in Z"""
        rad = [0.5*stats.GetEquivalentEllipsoidDiameter(l)[0] for l in true_labels]
        return rad


def calculate_centroid(us_image):
        """
        Get the leveled Z height (i.e., brought down to microscope plane at 0) location of each fiducial
        :param us_image: US image to calculate the fiducials from
        :return: list of Z heights
        """
        connected_image = connected_components(us_image)
        stats = get_fiducial_stats(connected_image)
        labels = filter_labels(stats)
        return get_leveled_centroid(stats, labels)


def connected_components(us_image):
    """Process the US image using Otsu thresholding and binary opening/closing to get the connected components"""
    thresh_filter = sitk.OtsuThresholdImageFilter()
    thresh_filter.SetInsideValue(0)
    thresh_filter.SetOutsideValue(1)
    thresh_img = thresh_filter.Execute(us_image)
    thresh_value = thresh_filter.GetThreshold()

    print("Threshold used: {}".format(thresh_value))

    cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(thresh_img, [4, 4, 2])
    cleaned_thresh_img = sitk.BinaryClosingByReconstruction(cleaned_thresh_img, [4, 4, 2])

    connected_img = sitk.ConnectedComponent(cleaned_thresh_img)
    return connected_img