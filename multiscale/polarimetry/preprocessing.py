import os
from pathlib import Path

import SimpleITK as sitk
import bioformats as bf

from multiscale import utility_functions as util
from multiscale.itk import itk_plotting as itkplot, registration as reg, transform as tran, metadata as meta


def plot_overlay_from_czi_timepoints(path_file, timepoint_one, timepoint_two):
        """
        Plot two timepoints from a czi image in a red/green overlay.  Warning: requires a running javabridge
        :param path_file: Path to the czi file
        :param timepoint_one: First timepoint
        :param timepoint_two: Second timepoint
        :return:
        """
        array_one = bf.load_image(str(path_file), t=timepoint_one)
        array_two = bf.load_image(str(path_file), t=timepoint_two)
        image_one = sitk.GetImageFromArray(array_one)
        image_two = sitk.GetImageFromArray(array_two)
        itkplot.plot_overlay(image_one, image_two, sitk.Transform(2, sitk.sitkIdentity), continuous_update=True,
                             downsample=False)


def czi_timepoint_to_sitk_image(path_file, position, resolution, resolution_unit='microns'):
        """
        Open a timepoint from a czi image and make it into an ITK image.  Warning: requires a running javabridge.
        
        :param path_file: Path to the czi file
        :param position: Timepoint to open
        :param resolution: Resolution of the czi image
        :param resolution_unit: The unit of measure (e.g. microns) of the czi image
        :return: A SimpleITK image made from the timepoint
        """
        array = bf.load_image(str(path_file), t=position)
        image = sitk.GetImageFromArray(array)
        image.SetSpacing([resolution, resolution])
        image.SetMetaData('Unit', resolution_unit)
        
        return image


def idx_dictionary():
        """Map the polarization state inputs and output states to the t slice from the channel"""
        idx_of_outputs = {
                'Hout': [0, 6, 9, 14],
                'Bout': [1, 7, 8, 15],
                'Pout': [2, 5, 10, 13],
                'Vout': [4, 3, 11, 12],
                'Rout': [18, 19, 20, 17],
                'Lout': [23, 22, 21, 16]}
        
        idx_of_inputs = {
                'Hin': [0, 1, 2, 3, 18, 23],
                'Pin': [6, 7, 5, 19, 22],
                'Vin': [9, 8, 10, 11, 20, 21],
                'Rin': [14, 15, 13, 12, 17, 16]
        }
        
        idx_dict = {'Outputs': idx_of_outputs, 'Inputs': idx_of_inputs}
        
        return idx_dict


def calculate_polarization_state_transforms(path_img: Path, resolution, transform_dir: Path, transform_prefix: str,
                                            skip_finished_transforms=True):
        """
        Register based on output polarization state, and save the resulting transform
        :param path_img: path to the image file being used to calculate the transforms
        :param resolution: resolution of the image file
        :param registration_method: itk construct holding registration parameters
        :param transform_dir: Directory that holds the transform files
        :param skip_finished_transforms: whether to skip finding transforms if they already exist or not
        :return:
        """
        idx_dict = idx_dictionary()
        keys = []
        
        fixed_img = czi_timepoint_to_sitk_image(path_img, 0, resolution)
        
        for idx in range(1, 24):
                
                registration_method = reg.define_registration_method(scale=1, learning_rate=1, iterations=300,
                                                                     min_step=0.001,
                                                                     metric_sampling_percentage=0.01)
                transform_path = Path(transform_dir, transform_prefix + '_' + str(idx + 1) + '.tfm')
                initial_transform = tran.read_initial_transform(transform_path, sitk.AffineTransform)
                
                if skip_finished_transforms:
                        if transform_path.is_file():
                                continue
                
                print('Registering {0} to 0'.format(idx))
                
                moving_img = czi_timepoint_to_sitk_image(path_img, idx, resolution)
                
                registered_img, transform, metric, stop = reg.supervised_register_images(
                        fixed_img, moving_img,
                        registration_method=registration_method,
                        initial_transform=initial_transform, moving_path=transform_path
                )
                
                tran.write_transform(transform_path, transform)


def apply_polarization_transforms(path_image, output_dir, transform_dir, transform_prefix, resolution,
                                  skip_existing_images=True):
        """
        Apply pre-calculated transforms onto a single mueller polarimetry image

        :param path_image: path to the image being processed
        :param output_dir: directory to save the image to
        :param resolution: resolution of the image file
        :return:
        """
        print('Applying transforms to {0}'.format(path_image.stem))
        
        fixed_image = czi_timepoint_to_sitk_image(path_image, 0, resolution)

        for num in range(24):
                output_path = Path(output_dir, path_image.stem + '_' + str(num + 1) + '.tif')
                if skip_existing_images and output_path.is_file():
                        continue

                moving_image = czi_timepoint_to_sitk_image(path_image, num, resolution)
                transform_path = Path(transform_dir, transform_prefix + '_' + str(num + 1) + '.tfm')
                
                if num == 0:
                        meta.write_image(fixed_image, output_path)
                else:
                        registered_image = tran.apply_transform(fixed_image, moving_image, str(transform_path))
                        meta.write_image(registered_image, output_path)


def bulk_apply_polarization_transforms(dir_input, dir_output, transform_dir, transform_prefix,
                                       resolution, skip_existing_images=True):
        """
        Apply pre-calculated transforms onto a whole directory of mueller polarimetry images

        :param dir_input: Directory holding both images and the transforms.csv file
        :param dir_output: Directory to write resulting images to
        :param resolution: Resolution of the image files
        :param skip_existing_images: Whether to skip applying the transform if files already exist
        :return:
        """
        file_list = util.list_filetype_in_dir(dir_input, 'czi')
        for file in file_list:
                dir_output_file = Path(dir_output, file.stem)
                os.makedirs(dir_output_file, exist_ok=True)
                
                apply_polarization_transforms(file, dir_output_file, transform_dir, transform_prefix, resolution,
                                              skip_existing_images=skip_existing_images)