import pytest
import SimpleITK as sitk
import mp_img_manip.itk.transform as tran


class TestGetTransformTypeStr(object):
        def test_affine2d(self):
                expected = 'AffineTransform<double,2>'
                transform = sitk.AffineTransform(2)
                assert expected == tran.get_transform_type_str(transform)
                
        def test_Euler(self):
                expected = 'Euler2DTransform<double>'
                transform = sitk.Euler2DTransform()
                assert expected == tran.get_transform_type_str(transform)
        
        def test_BSpline2DOrder3(self):
                expected = 'BSplineTransform<double,2,3>'
                transform = sitk.BSplineTransform(2)
                assert expected == tran.get_transform_type_str(transform)
        