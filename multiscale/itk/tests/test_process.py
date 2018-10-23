import pytest
import multiscale.itk.process as proc
import SimpleITK as sitk


class TestCheckIfImageIsRGB(object):
        @pytest.mark.parametrize('image, expected', [
                (sitk.Image([5, 5], sitk.sitkVectorUInt8, 3), True),
                (sitk.Image(5, 5, sitk.sitkUInt8), False),
                (sitk.Image([5, 5], sitk.sitkVectorUInt8, 4), False),
                (sitk.Image([5, 5], sitk.sitkVectorFloat32, 3), False)
        ])
        def test_various_image_types(self, image, expected):
                image_is_rgb = proc.check_if_image_is_rgb(image)
                assert image_is_rgb == expected