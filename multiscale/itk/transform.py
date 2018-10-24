# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:39:34 2018

@author: mpinkert
"""
import multiscale.bulk_img_processing as blk
import multiscale.itk.metadata as meta

import SimpleITK as sitk
import numpy as np
import os
import math
from pathlib import Path


def write_transform(registered_path, transform):
        transform_path = Path(registered_path.parent, registered_path.stem + '.tfm')
        sitk.WriteTransform(transform, str(transform_path))
        

def read_transform(transform_path: Path):
        """
        Read in a transform and set the type correctly, as it is generic with default SimpleITK
        
        :param transform_path: path to the transform.tfm file
        :return: the transform
        """
        generic_transform = sitk.ReadTransform(str(transform_path))
        generic_parameters = generic_transform.GetParameters()
        
        transform_type_str = get_transform_type_str(generic_transform)
        
        if transform_type_str == 'AffineTransform' and len(generic_parameters) == 6:
                transform = sitk.AffineTransform(2)
        
        elif transform_type_str == 'Euler2DTransform':
                transform = sitk.Euler2DTransform()
                
        else:
                raise NotImplementedError('This transform type has not been implemented yet')
                
        transform.SetParameters(generic_parameters)
        return transform
        

def apply_transform(fixed_image: sitk.Image, moving_image: sitk.Image, transform_path):
        transform = sitk.ReadTransform(str(transform_path))
        registered_image = sitk.Resample(moving_image, fixed_image, transform,
                                         sitk.sitkLinear, 0.0, moving_image.GetPixelID())
        
        meta.copy_relevant_metadata(registered_image, moving_image)
        
        return registered_image
        

def write_transform_pandas(registered_path, origin, transform, metric, stop, rotation):
        """Write affine transform parameters to a csv file"""
        (output_dir, image_name) = os.path.split(registered_path)
        
        file_path = output_dir + '/Transforms.csv'
        
        column_labels = ('Matrix Top Left', 'Matrix Top Right',
                         'Matrix Bottom Left', 'Matrix Bottom Right',
                         'X Translation', 'Y Translation',
                         'Mutual Information', 'Stop Condition',
                         'X Origin', 'Y Origin', 'Rotation')
        
        column_values = list(transform.GetParameters())
        column_values.append(metric)
        column_values.append(stop)
        column_values.append(origin[0])
        column_values.append(origin[1])
        column_values.append(rotation)
        
        blk.write_pandas_row(file_path, image_name, column_values,
                             'Image', column_labels)


def apply_transform_pandas(fixed_image: sitk.Image, moving_image: sitk.Image, reference_path, index=None):
        
        transform_path = os.path.join(reference_path.parent, 'Transforms.csv')
        
        if index is None:
                transform_params = blk.read_pandas_row(transform_path, reference_path.name, 'Image')
        else:
                transform_params = blk.read_pandas_row(transform_path, index, 'Image')
        
        transform = sitk.AffineTransform(2)
        
        transform.Rotate(0, 1, transform_params['Rotation'], pre=True)
        
        matrix = [transform_params['Matrix Top Left'],
                  transform_params['Matrix Top Right'],
                  transform_params['Matrix Bottom Left'],
                  transform_params['Matrix Bottom Right']]
        
        transform.SetMatrix(matrix)
        transform.SetTranslation([transform_params['X Translation'],
                                  transform_params['Y Translation']])
        
        origin = (int(transform_params['X Origin']),
                  int(transform_params['Y Origin']))
        moving_image.SetOrigin(origin)
        
        return sitk.Resample(moving_image, fixed_image, transform,
                             sitk.sitkLinear, 0.0, moving_image.GetPixelID())


def bulk_apply_transform(fixed_dir, moving_dir, transform_dir,
                         output_dir, output_suffix,
                         skip_existing_images=False):
        
        fixed_paths, moving_paths, transform_paths = blk.find_bulk_shared_images(
                [fixed_dir, moving_dir, transform_dir])
        
        for i in range(0, np.size(fixed_paths)):
                registered_path = blk.create_new_image_path(moving_paths[i],
                                                            output_dir,
                                                            output_suffix)
                
                if registered_path.exists() and skip_existing_images:
                        continue
                
                fixed_image = meta.setup_image(fixed_paths[i])
                moving_image = meta.setup_image(moving_paths[i])
                
                print('\nApplying transform onto {0} based on transform on {1}'.format(
                        str(moving_paths[i].name),
                        str(transform_paths[i].name)))
                
                transform_path = Path(transform_paths[i].parent, transform_paths[i].stem + '.tfm')
                registered_image = apply_transform(fixed_image, moving_image, transform_path)
                
                meta.write_image(registered_image, registered_path)
                write_transform(registered_path, sitk.ReadTransform(str(transform_path)))
        
        return


def resize_image(itk_image, current_spacing, target_spacing):
        """Resize an image by an integer factor towards target spacing"""
        
        if current_spacing < target_spacing:
                scale = math.floor(target_spacing/current_spacing)
                end_res = current_spacing*scale
                
                resized_image = sitk.Shrink(itk_image, [scale, scale])
                resized_image.SetSpacing([end_res, end_res])
                resized_image.SetOrigin(itk_image.GetOrigin())
        
        elif current_spacing > target_spacing:
                scale = math.floor(current_spacing/target_spacing)
                end_res = current_spacing/scale
                
                resized_image = sitk.Expand(itk_image,[scale, scale])
                resized_image.SetSpacing([end_res, end_res])
                resized_image.SetOrigin(itk_image.GetOrigin())
                
        else:
                resized_image = itk_image
        
        meta.copy_relevant_metadata(resized_image, itk_image)
        
        return resized_image


def bulk_resize_image(fixed_dir, moving_dir, output_dir, output_suffix,
                      skip_existing_images=False):
        """Resize multiple images to corresponding reference size"""
        (fixed_image_path_list, moving_image_path_list) = blk.find_shared_images(
                fixed_dir, moving_dir)
        
        for i in range(0, np.size(fixed_image_path_list)):
                resized_path = blk.create_new_image_path(moving_image_path_list[i],
                                                         output_dir, output_suffix)
                if resized_path.exists() and skip_existing_images:
                        continue
                
                current_spacing = meta.get_image_parameters(
                        moving_image_path_list[i],
                        return_origin=True,
                        return_spacing=True)[0]
                
                target_spacing = meta.get_image_parameters(
                        fixed_image_path_list[i],
                        return_origin=True,
                        return_spacing=True)[0]
                
                moving_image = sitk.ReadImage(str(moving_image_path_list[i]))
                resized_image = resize_image(moving_image_path_list[i],
                                             current_spacing, target_spacing)

                meta.write_image(resized_image, resized_path)


def bulk_resize_to_target(image_dir, output_dir, output_suffix,
                          target_spacing,
                          skip_existing_images=False):
        
        image_name_list = [
                Path(f) for f in os.listdir(image_dir) if f.endswith('.tif')]
        
        for i in range(0, np.size(image_name_list)):
                image_path = Path(image_dir, image_name_list[i])
                
                resized_path = blk.create_new_image_path(image_path,
                                                         output_dir, output_suffix)
                if resized_path.exists() and skip_existing_images:
                        continue
                
                current_spacing = meta.get_image_parameters(image_path, return_origin=False, return_spacing=True)[0][0]
                itk_image = meta.setup_image(image_path)
                image_name = os.path.basename(image_path)
                print('\nResizing ' + image_name + ' from '
                      + str(current_spacing) + ' to target spacing ' + str(target_spacing) + ')')
                
                resized_image = resize_image(itk_image,
                                             current_spacing, target_spacing)

                meta.write_image(resized_image, resized_path)


def define_transform(transform_type: type=sitk.AffineTransform, rotation: np.double=0) -> sitk.Transform:
        implemented_transforms = [sitk.AffineTransform, sitk.Euler2DTransform]
        
        if transform_type == sitk.Euler2DTransform:
                transform = sitk.Euler2DTransform()
                set_transform_rotation(transform, rotation)
                
        if transform_type == sitk.AffineTransform:
                transform = sitk.AffineTransform(2)
                set_transform_rotation(transform, rotation)
        
        if transform_type not in implemented_transforms:
                raise('{0} transform has not been implemented yet'.format(transform_type))
        
        return transform


def set_transform_rotation(transform, rotation):
        """
        Change the initial rotation of a transform matrix to the specified angle, ignoring previous angles
        
        :param transform: The transform to change
        :param rotation: The angle in degrees for the transform rotation to be
        :return:
        """
        deg_to_rad = 2*np.pi/360
        angle = rotation*deg_to_rad
        
        if type(transform) == sitk.Euler2DTransform:
                transform.SetAngle(angle)
        
        if type(transform) == sitk.AffineTransform and len(transform.GetTranslation()) == 2:
                generic_affine = sitk.AffineTransform(2)
                generic_affine.SetTranslation(transform.GetTranslation())
                generic_affine.Rotate(0, 1, angle)
                transform.SetParameters(generic_affine.GetParameters())
                
        if type(transform) == sitk.Transform:
                print('This transform is of generic type, it has no rotation parameter.')
                

def read_initial_transform(path_image: Path, transform_type: type):
        """
        Find the initial transform that sets up an image for registration, used for remembering good initializations
        :param path_image: Path to the image in question.
        :param transform_type: Type of transform, writes down a blank initial transform file if this none are found
        :return: The initial transform
        """
        path_transform = Path(path_image.parent, path_image.stem + '_initial.tfm')
        
        if path_transform.is_file():
                transform = read_transform(path_transform)
        else:
                print('No transform found.  Writing blank transform for {0}'.format(path_image.name))
                transform = define_transform(transform_type)
                sitk.WriteTransform(transform, str(path_transform))
        
        return transform


def write_initial_transform(path_image: Path, transform: sitk.Transform):
        """Write a transform with the suffix _initial, meant for registration initialization"""
        path_transform = Path(path_image.parent, path_image.stem + '_initial.tfm')
        sitk.WriteTransform(transform, str(path_transform))
        

def get_translation(transform: sitk.Transform):
        """
        Get the translation from a transform
        :param transform: the transform in question
        :return: list of the translation
        """
        parameters = transform.GetParameters()
        transform_type = type(transform)
        
        if transform_type == sitk.AffineTransform and len(parameters) == 6:
                translation = parameters[4:]
                
        elif transform_type == sitk.Euler2DTransform:
                translation = parameters[1:]
        
        else:
                raise NotImplementedError('This transform type is not implemented yet')
                
        return translation


def implemented_transform_type(transform_type: type):
        """Check if functions can use this transform type"""
        implemented_types = [sitk.AffineTransform, sitk.Euler2DTransform]
        
        if transform_type in implemented_types:
                return True
        
        else:
                return False


def set_translation(transform, translation):
        """
        Set the translation in a SimpleITK transform, for implemented types of transforms
        
        :param transform: transform in question
        :param translation: new translation to set the transform to
        :return: Change the transform using set method.  No return.
        """
        parameters = list(transform.GetParameters())
        transform_type = type(transform)
        
        if transform_type == sitk.AffineTransform and len(parameters) == 6:
                parameters[4:] = translation
        
        elif transform_type == sitk.Euler2DTransform:
                parameters[1:] = translation
                
        else:
                raise NotImplementedError('This transform type is not implemented yet')
        
        transform.SetParameters(parameters)
        

def get_transform_type_str(transform):
        class_line = str(transform).split('\n')[2]
        full_transform_type = class_line.split('itk::')[1]
        transform_type_str = full_transform_type.split('<')[0]
        
        return transform_type_str



        