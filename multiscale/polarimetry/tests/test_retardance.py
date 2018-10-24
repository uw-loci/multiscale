# # -*- coding: utf-8 -*-
# """
# Created on Mon Mar  5 09:12:30 2018
#
# @author: mpinkert
# """
#
# import multiscale.polarimetry.retardance as retard
# import SimpleITK as sitk
# import unittest
# import numpy as np
# from numpy.testing import assert_array_equal
#
#
# class convertIntensityToRetardance_TestSuite(unittest.TestCase):
#
#         def test_nm_to_deg(self):
#                 inputValue = np.array([[100, 200],[563,843]], dtype='float32')
#                 inputImg = sitk.GetImageFromArray(inputValue)
#                 inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
#
#                 expected_value = inputValue * (35/65535) * (360/546)
#                 output_img = retard.convert_intensity_to_retardance(inputImg)
#                 output_value = sitk.GetArrayFromImage(output_img)
#
#                 assert_array_equal(expected_value, output_value)
#
#         def test_nm_to_deg_diff_wavelength(self):
#                 inputValue = np.array([[100, 200],[563,843]])
#                 inputImg = sitk.GetImageFromArray(inputValue)
#                 inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
#
#                 wl = 600
#
#                 outputValue = inputValue * (35/65535) * (360/600)
#                 outputImg = sitk.GetImageFromArray(outputValue)
#
#                 self.assertEqual(retard.convert_intensity_to_retardance(
#                         inputImg, wavelength=wl), outputImg)
#
#         def test_nm_to_deg_diff_ceiling(self):
#                 inputValue = np.array([[100, 200],[563,843]])
#                 inputImg = sitk.GetImageFromArray(inputValue)
#                 inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
#
#                 ceiling = 50
#
#                 outputValue = inputValue * (50/65535) * (360/546)
#                 outputImg = sitk.GetImageFromArray(outputValue)
#
#                 self.assertEqual(retard.convert_intensity_to_retardance(
#                         inputImg, ret_ceiling = ceiling), outputImg)
#
#         def test_nm_to_nm(self):
#                 inputValue = np.array([[100, 200],[563,843]])
#                 inputImg = sitk.GetImageFromArray(inputValue)
#                 inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
#
#                 outputValue = inputValue * (35/65535)
#                 outputImg = sitk.GetImageFromArray(outputValue)
#
#                 self.assertEqual(retard.convert_intensity_to_retardance(
#                         inputImg, deg_output=False), outputImg)
#
#         def test_deg_to_deg(self):
#                 inputValue = np.array([[100, 200],[563,843]])
#                 inputImg = sitk.GetImageFromArray(inputValue)
#                 inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
#
#                 outputValue = inputValue * (35/65535)
#                 outputImg = sitk.GetImageFromArray(outputValue)
#
#                 self.assertEqual(retard.convert_intensity_to_retardance(
#                         inputImg, nm_input=False), outputImg)
#
#         def test_deg_to_nm(self):
#                 inputValue = np.array([[100, 200],[563,843]])
#                 inputImg = sitk.GetImageFromArray(inputValue)
#                 inputImg = sitk.Cast(inputImg, sitk.sitkUInt16)
#
#                 outputValue = inputValue * (35/65535) * (546/360)
#                 outputImg = sitk.GetImageFromArray(outputValue)
#
#                 self.assertEqual(retard.convert_intensity_to_retardance(
#                         inputImg, deg_output = False, nm_input = False), outputImg)
#
# if __name__ == '__main__':
#         unittest.main(verbosity=2)