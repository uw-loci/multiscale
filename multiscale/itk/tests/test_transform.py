import pytest
import SimpleITK as sitk
import multiscale.itk.transform as tran
from pathlib import Path
import numpy as np


class TestReadTransform(object):
        @pytest.mark.parametrize('transform', [
                (sitk.AffineTransform(2)), (sitk.Euler2DTransform())
        ])
        def test_gets_transform_types_correct(self, transform, tmpdir):
                temp_path = Path(tmpdir.join('transform.tfm'))
                sitk.WriteTransform(transform, str(temp_path))
                new_transform = tran.read_transform(Path(temp_path))
                
                assert type(transform) == type(new_transform)


class TestChangeTransformRotation(object):
        def test_change_affine2d_rotation(self):
                transform = sitk.AffineTransform(2)
                tran.change_transform_rotation(transform, 2)
                expected_params = (0.9993908270190958, 0.03489949670250097, -0.03489949670250097, 0.9993908270190958,
                                   0.0, 0.0)
                assert expected_params == transform.GetParameters()
                
        def test_change_euler2d_angle(self):
                rotation = 2
                deg_to_rad = 2 * np.pi / 360
                angle = rotation * deg_to_rad
                
                transform = sitk.Euler2DTransform()
                tran.change_transform_rotation(transform, rotation)
                assert angle == transform.GetAngle()
                

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


class TestGetTranslation(object):
        def test_affine2d(self):
                expected = (15, 40)
                transform = sitk.AffineTransform(2)
                transform.SetTranslation(expected)
                assert expected == tran.get_translation(transform)
                
        def test_euler2d(self):
                expected = (15, 40)
                transform = sitk.Euler2DTransform()
                transform.SetTranslation(expected)
                assert expected == tran.get_translation(transform)
                
        def test_not_implemented(self):
                with pytest.raises(NotImplementedError):
                        transform = sitk.BSplineTransform(2)
                        tran.get_translation(transform)


class TestSetTranslation(object):
        def test_affine2d(self):
                expected = (15, 40)
                transform = sitk.AffineTransform(2)
                tran.set_translation(transform, expected)
                assert expected == transform.GetTranslation()
        
        def test_euler2d(self):
                expected = (15, 40)
                transform = sitk.Euler2DTransform()
                tran.set_translation(transform, expected)
                assert expected == transform.GetTranslation()
        
        def test_not_implemented(self):
                with pytest.raises(NotImplementedError):
                        transform = sitk.BSplineTransform(2)
                        tran.get_translation(transform)
