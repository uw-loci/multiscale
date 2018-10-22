import multiscale.tiling as til
import multiscale.bulk_img_processing as blk
import multiscale.itk.metadata as meta
import multiscale.utility_functions as util

import scipy.stats as st
import numpy as np
import SimpleITK as sitk
import os

import csv


def calculate_retardance_over_area(retardance, orientation, ret_thresh=0):
        """Calculate the average retardance in an neighborhood
        
        Retardance has a directional component, so it has to be weighted by
        the slow-axis orientation.  This function performs that weighting by
        doubling the orientation angle, and then turning it into a complex
        number which holds both magnitude and angle
        
        Inputs:
        Equally sized retardance and orientation neighborhoods holding
        corresponding pixels.
        
        Both units are degrees.
        """
        
        # Orientation doubled to calculate alignment.
        circular_orientation = (2 * np.pi / 180) * orientation
        complex_orientation = np.exp(-1j * circular_orientation)
        
        retardance_weighted_by_orientation = retardance * complex_orientation
        
        num_pixels = np.size(retardance)
        
        average_retardance = np.sum(retardance_weighted_by_orientation) / num_pixels
        
        ret_mag = np.absolute(average_retardance)
        ret_base_angle = np.angle(average_retardance, deg=True)
        
        ret_base_angle += 180
        
        #    if ret_base_angle < 0:
        #        ret_base_angle += 360
        
        ret_angle = ret_base_angle / 2
        
        # bug: ret_angle does not give right value.
        if ret_mag < ret_thresh:
                ret_mag = np.nan
                ret_angle = np.nan
        
        return ret_mag, ret_angle


def calculate_alignment(orient_tile):
        nonzero_orient = orient_tile > 0
        orient_rad = orient_tile[nonzero_orient] * 2 * np.pi / 180  # 180 is range of possible angles
        complex_angles = np.exp(-1j * orient_rad)
        
        size = np.size(orient_rad)
        
        if size is 0:
                return np.nan
        
        r = np.sum(complex_angles) / size
        alignment = np.abs(r)
        
        return alignment


def process_orientation_alignment(ret_image_path, orient_image_path,
                                  output_path,
                                  tile_size, tile_separation=None,
                                  roi_size=None,
                                  intensity_thresh=1, number_thresh=10):
        """
        Calculate the average retardance, orientation, and alignment through retardance and orientation images
        
        :param ret_image_path: Path to the retardance image
        :param orient_image_path:  path to the orientaiton image
        :param output_path: Path to save the output csv file
        :param tile_size: Size in pixels of the tile
        :param tile_separation: Distance between tiles, defaults to 0
        :param roi_size: Size of regions of interest within tiles
        :param intensity_thresh:
        :param number_thresh:
        :return:
        """
        
        modality = blk.file_name_parts(ret_image_path)[1] + '-O'
        
        ret_image = sitk.ReadImage(str(ret_image_path))
        ret_array = sitk.GetArrayFromImage(ret_image)
        ret_max = np.max(ret_array)
        
        orient_image = sitk.ReadImage(str(orient_image_path))
        orient_array = sitk.GetArrayFromImage(orient_image)
        
        array_shape = np.shape(orient_array)
        
        pixel_num, offset = til.calculate_number_of_tiles(
                array_shape, tile_size, tile_separation)
        
        if roi_size is None:
                with open(output_path, 'w', newline='') as csvfile:
                        print('\nWriting average retardance file for {} at tile size {}'.format(
                                output_path.name, tile_size[0]))
                        writer = csv.writer(csvfile)
                        writer.writerow(['Mouse', 'Slide', 'Modality', 'Tile',
                                         'Retardance', 'Orientation', 'Alignment'])
                        
                        for start, end, tile_number in til.generate_tile_start_end_index(
                                    pixel_num, tile_size, tile_offset=offset,
                                    tile_separation=tile_separation):
                                
                                ret_tile = ret_array[start[0]:end[0],
                                           start[1]:end[1]]
                                
                                orient_tile = orient_array[start[0]:end[0],
                                              start[1]:end[1]]
                                
                                retardance, orientation = calculate_retardance_over_area(
                                        ret_tile, orient_tile)
                                
                                if retardance is np.nan:
                                        continue
                                
                                alignment = calculate_alignment(orient_tile)
                                
                                sample = blk.get_core_file_name(output_path)
                                mouse, slide = sample.split('-')
                                
                                tile = str(tile_number[0]) + 'x-' + str(tile_number[1]) + 'y'
                                
                                writer.writerow([mouse, slide, modality, tile,
                                                 retardance, orientation, alignment])
        
        else:
                num_rois, roi_offset = til.calculate_number_of_tiles(tile_size, roi_size)
                
                with open(output_path, 'w', newline='') as csvfile:
                        print('\nWriting average retardance file for {} at tile size {} and roi size {}'.format(
                                output_path.name, tile_size[0], roi_size[0]))
                        writer = csv.writer(csvfile)
                        writer.writerow(['Mouse', 'Slide', 'Modality', 'Tile', 'ROI',
                                         'Retardance', 'Orientation', 'Alignment'])
                        
                        for start, end, tile_number in til.generate_tile_start_end_index(
                                    pixel_num, tile_size, tile_offset=offset,
                                    tile_separation=tile_separation):
                                
                                ret_tile = ret_array[start[0]:end[0],
                                           start[1]:end[1]]
                                
                                orient_tile = orient_array[start[0]:end[0],
                                              start[1]:end[1]]
                                
                                tile = str(tile_number[0]) + 'x-' + str(tile_number[1]) + 'y'
                                
                                for start_roi, end_roi, roi_number in til.generate_tile_start_end_index(
                                            num_rois, roi_size, tile_offset=roi_offset):
                                        
                                        ret_roi = ret_tile[start_roi[0]:end_roi[0],
                                                  start_roi[1]:end_roi[1]]
                                        
                                        orient_roi = orient_tile[start_roi[0]:end_roi[0],
                                                     start_roi[1]:end_roi[1]]
                                        
                                        retardance, orientation = calculate_retardance_over_area(
                                                ret_roi, orient_roi)
                                        
                                        if retardance is np.nan:
                                                continue
                                        
                                        alignment = calculate_alignment(orient_roi)
                                        
                                        sample = blk.get_core_file_name(output_path)
                                        mouse, slide = sample.split('-')
                                        
                                        roi = 'ROI' + str(roi_number[0]) + 'x' + str(roi_number[1]) + 'y'
                                        
                                        writer.writerow([mouse, slide, modality, tile, roi,
                                                         retardance, orientation, alignment])


def bulk_process_orientation_alignment(
            ret_dir, orient_dir, output_dir, output_suffix,
            tile_size,
            tile_separation=None, skip_existing_images=True,
            roi_size=None):
        """Calculate average retardance images
        """
        # todo: add ROI capability
        
        output_suffix_with_tilenum = output_suffix + '_' + str(tile_size[0])
        
        if roi_size is not None:
                output_suffix_with_tilenum = output_suffix_with_tilenum + '_' + str(roi_size[0])
        
        if (tile_separation
                    and tile_separation != tile_size):
                output_suffix = (output_suffix + '_SimRes-'
                                 + str(tile_separation) + 'x')
        
        ret_image_path_list, orient_image_path_list = blk.find_shared_images(
                ret_dir, orient_dir)
        
        for i in range(0, np.size(ret_image_path_list)):
                
                output_path = blk.create_new_image_path(
                        orient_image_path_list[i], output_dir,
                        output_suffix_with_tilenum,
                        extension='.csv')
                
                if output_path.exists() and skip_existing_images:
                        continue
                
                process_orientation_alignment(ret_image_path_list[i],
                                              orient_image_path_list[i],
                                              output_path,
                                              tile_size,
                                              tile_separation=tile_separation,
                                              roi_size=roi_size)


def convert_intensity_to_retardance(itk_image,
                                    ret_ceiling=35, wavelength=549,
                                    nm_input=True, deg_output=True):
        """Convert retardance intensities that are scaled to the image input
        (e.g., 16 bit int) into to actual retardance values.
        
        :param itk_image: The image being converted, as an ITK _image object
        :param ret_ceiling:  The retardance value corresponding to max intensity
        :param wavelength:  The wavelength of light used to image, for converting between degrees and retardance.
        :param nm_input:  The input ret_ceiling is in nm if true, degrees if false
        :param deg_output:  The output is in degrees if true, nm if false
        :return A new ITK image with retardance values either in degrees or in nm
        """
        
        input_array = sitk.GetArrayFromImage(itk_image)
        
        # todo: implement a check for pixel type
        
        pixel_type_factor = ret_ceiling / 65535
        
        if nm_input and deg_output:
                wavelength_factor = 360 / wavelength
        elif nm_input is False and deg_output is False:
                wavelength_factor = wavelength / 360
        else:
                wavelength_factor = 1
        
        output_array = input_array * pixel_type_factor * wavelength_factor
        
        output_image = sitk.GetImageFromArray(output_array)
        output_image = sitk.Cast(output_image, sitk.sitkFloat32)
        output_image.SetMetaData(itk_image.GetMetaData())
        
        return output_image


def bulk_intensity_to_retardance(input_dir, output_dir, output_suffix,
                                 skip_existing_images=False):
        path_list = util.list_filetype_in_dir(input_dir, '.tif')
        
        for i in range(len(path_list)):
                output_path = blk.create_new_image_path(
                        path_list[i], output_dir, output_suffix)
                if output_path.exists() and skip_existing_images:
                        continue
                
                int_image = meta.setup_image(path_list[i])
                ret_image = convert_intensity_to_retardance(int_image)

                meta.write_image(ret_image, output_path)


def downsample_retardance_image(ret_image_path, orient_image_path,
                                tile_size,
                                tile_separation=None):
        if not tile_separation:
                tile_separation = tile_size
        
        ret_image = sitk.ReadImage(ret_image_path)
        orient_image = sitk.ReadImage(orient_image_path)
        
        ret_array = sitk.GetArrayFromImage(ret_image)
        orient_array = sitk.GetArrayFromImage(orient_image)
        
        array_size = np.shape(ret_array)
        
        pixel_num, offset = til.calculate_number_of_tiles(
                array_size, tile_size, tile_separation)
        
        down_ret_array = np.zeros(pixel_num)
        down_orient_array = np.zeros(pixel_num)
        
        for start, end, tile_number in til.generate_tile_start_end_index(
                    pixel_num, tile_size, tile_offset=offset,
                    tile_separation=tile_separation):
                ret_tile = ret_array[range(start[0], end[0]),
                                     range(start[1], end[1])]
                
                orient_tile = orient_array[range(start[0], end[0]),
                                           range(start[1], end[1])]
                
                ret_pixel, orient_pixel = calculate_retardance_over_area(
                        ret_tile, orient_tile)
                
                down_ret_array[tile_number[0], tile_number[1]] = ret_pixel
                down_orient_array[tile_number[0], tile_number[1]] = orient_pixel
        
        down_ret_image = sitk.GetImageFromArray(down_ret_array)
        down_ret_image = sitk.Cast(down_ret_image, ret_image.GetPixelID())
        down_ret_image.SetMetaData(ret_image.GetMetaData())
        
        down_orient_image = sitk.GetImageFromArray(down_orient_array)
        down_orient_image = sitk.Cast(down_orient_image, orient_image.GetPixelID())
        down_orient_image.GetMetaData(orient_image.GetMetaData())
        
        return down_ret_image, down_orient_image


def batch_downsample_retardance(ret_dir, orient_dir, output_dir,
                                scale_factor,
                                simulated_resolution_factor=None):
        output_suffix = 'DownSample-' + str(scale_factor) + 'x'
        
        if (simulated_resolution_factor
                    and simulated_resolution_factor != scale_factor):
                output_suffix = (output_suffix + '_SimRes-'
                                 + str(simulated_resolution_factor) + 'x')
        
        (ret_image_path_list, orient_image_path_list) = blk.find_shared_images(
                ret_dir, orient_dir)
        
        for i in range(0, np.size(ret_image_path_list)):
                (down_ret_image, down_orient_image) = downsample_retardance_image(
                        ret_image_path_list[i], orient_image_path_list[i],
                        scale_factor, simulated_resolution_factor)
                
                down_ret_dir = os.path.join(output_dir, output_suffix, '_ret', )
                down_orient_dir = os.path.join(output_dir, output_suffix, 'SlowAxis', )
                
                down_ret_path = blk.create_new_image_path(ret_image_path_list[i],
                                                          down_ret_dir,
                                                          '__ret_' + output_suffix)
                
                down_orient_path = blk.create_new_image_path(
                        orient_image_path_list[i],
                        down_orient_dir,
                        '_SlowAxis_' + output_suffix)
                
                meta.write_image(down_ret_image, down_ret_path)
                meta.write_image(down_orient_image, down_orient_path)
