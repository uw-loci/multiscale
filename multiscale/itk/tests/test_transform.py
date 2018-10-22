import pytest
import SimpleITK as sitk
import multiscale.itk.transform as tran
from pathlib import Path


class TestReadTransform(object):
        @pytest.mark.parametrize('transform', [
                (sitk.AffineTransform(2)), (sitk.Euler2DTransform())
        ])
        def test_gets_transform_types_correct(self, transform, tmpdir):
                temp_path = Path(tmpdir.join('transform.tfm'))
                sitk.WriteTransform(transform, str(temp_path))
                new_transform = tran.read_transform(Path(temp_path))
                
                assert type(transform) == type(new_transform)


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
