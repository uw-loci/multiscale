import numpy as np
import SimpleITK as sitk
import multiscale.utility_functions as util
import tiffile as tif
from pathlib import Path
import multiscale.ultrasound.reconstruction as recon


def convert_oct_to_tif(mat_path: Path, output_folder, resolution, overwrite=False):
        """
        Convert a .mat OCT image file from LINK to
        :param mat_path:
        :param output_folder:
        :param resolution: numpy array of [x, y, z] resolution
        :param overwrite: Boolean.  True if you wish to overwrite pre-existing files, false if not
        :return:
        """

        output_path = Path(output_folder, mat_path.stem + '.tif')
        
        if output_path.is_file() and not overwrite:
                print('File already exists.  Skipping writing.')
                return
        
        oct_array = util.load_mat(mat_path, 'ropd_vol')
        bmode_array = recon.iq_to_db(oct_array)
        
        zyx_array = np.transpose(bmode_array, (2, 0, 1))
        
        
        ijstyle = zyx_array.astype(np.float32)
        shape = ijstyle.shape
        ijstyle.shape = 1, shape[0], 1, shape[1], shape[2], 1
        
        tif.imwrite(output_path, ijstyle, imagej=True,
                    resolution=(1./resolution[0], 1./resolution[1]),
                    metadata={'spacing': resolution[2], 'unit': 'um'})


def save_ijstyle_overlay(images_list: list, save_path: Path):
        """
        Save a list of images as a tif, with each image a channel
        :param images_list: List of SimpleITK images of the same shape, spacing, and dtype
        :param save_path: File path to save at
        :return:
        """
        spacing = images_list[0].GetSpacing()
        overlay = sitk_to_ijstyle_overlay(images_list)
        save_ijstyle(overlay, save_path, spacing)


def save_ijstyle(img, save_path, spacing, unit='um'):
        """
        Save an image with the ijstyle using tiffile
        :param img: numpy array in TZCYXS order
        :param save_path: File path to save it
        :param spacing: [x, y, z] spacing
        :param unit: Unit used for the spacing.  Default um for micrometers
        :return:
        """
        tif.imwrite(save_path, img, imagej=True,
                    resolution=(1. / spacing[0], 1. / spacing[1]),
                    metadata={'spacing': spacing[2], 'unit': unit})


def sitk_to_ijstyle_overlay(images_list):
        """
        Overlay a list of SimpleITK images into the ImageJ style, where each image is a channel
        :param images_list: List of SimpleITK images.
        :return: The ImageJ style overlay in TZCYXS order
        """
        arr_list = [sitk_to_ijstyle(img) for img in images_list]
        
        num_images = len(arr_list)
        
        shape = arr_list[0].shape
        dtype = arr_list[0].dtype
        spacing = images_list[0].GetSpacing()
        
        for idx in range(num_images):
                if shape != arr_list[idx].shape:
                        raise Exception(
                                'Image 0 and Image {} are not the same size.  They cannot be overlaid'.format(idx + 1))
                elif dtype != arr_list[idx].dtype:
                        raise Exception(
                                'Image 0 and Image {} do not have the same pixel type.  They cannot be overlaid'.format(idx + 1))
                elif spacing != images_list[idx].GetSpacing():
                        raise Exception(
                                'Image 0 and Image {} do not have the same spacing.  They cannot be overlaid'.format(idx + 1))

        overlay = np.zeros([shape[0], shape[1], num_images, shape[3], shape[4]], arr_list[0].dtype)
        for idx in range(num_images):
                overlay[:, :, idx, :, :] = np.squeeze(arr_list[idx][:, :, 0, :, :], 4)
        
        return overlay


def sitk_to_ijstyle(img):
        """
        Convert a SimpleITK image into an ijstyle array for saving with tiffile
        :param img: SimpleITK image
        :return: IJ style array in TZCXYS order.
        """
        arr = sitk.GetArrayFromImage(img)
        if arr.dtype != np.uint8:
                arr = arr.astype(np.float32)
        
        shape = arr.shape
        arr.shape = 1, shape[0], 1, shape[1], shape[2], 1
        
        return arr

