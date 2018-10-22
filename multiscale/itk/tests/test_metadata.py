import pytest
import multiscale.itk.metadata as meta

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


        