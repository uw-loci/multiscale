import pytest
import SimpleITK as sitk
from pathlib import Path
import multiscale.itk.metadata as meta
import numpy as np


@pytest.fixture()
def generic_tif(tmpdir):
        im_array = np.array([[4, 2, 0], [1, 3, 5]])
        img = sitk.GetImageFromArray(im_array)
        img = sitk.Cast(img, sitk.sitkUInt8)
        img_path = Path(tmpdir.join('test_img.tif'))
        sitk.WriteImage(img, str(img_path))
        
        return img_path


class TestUnitToFactor(object):
        def test_known_inputs(self):
                return
        
        
class TestThreeDToRGB(object):
        def test_regular_3channel(self):
                return
        
        def test_3channel_duplicated_in_4channels(self):
                return
        
        
class TestCopyRelevantMetadata(object):
        def test_default_key(self):
                return
        
        def test_unique_key(self):
                return
        
        def test_missing_key(self):
                return
        
        def test_no_keys(self):
                return
        
        
class TestConvertSpacingUnits(object):
        def test_millimeter_to_micron(self):
                return
        
        def test_invalid_unit(self):
                return
        
        def test_micron_to_millimeter(self):
                return
        

class TestSetupImage(object):
        def test_image_with_metadata(self):
                return
        
        def test_image_without_metadata(self):
                return
        
        def test_rgb_regular_3channel(self):
                return
        
        def test_rgb_duplicated_4channel(self):
                return
        

class TestWriteMetadata(object):
        def test_writes_file(self):
                return
        
        def test_output_correct(self):
                return
        

class TestReadMetadata(object):
        def test_read_file(self):
                return
        
        def test_read_correct(self):
                return
        

class TestWriteImage(object):
        def test_writes_image(self):
                return


class TestGetImageSizeFromPath(object):
        def test_gets_size_from_sitk_written_image(self, generic_tif):
                expected = (3, 2)
                size = meta.get_image_size_from_path(generic_tif)
                assert size == expected