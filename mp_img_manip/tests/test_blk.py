# -*- coding: utf-8 -*-

import mp_img_manip.bulk_img_processing as blk
from pathlib import Path
import unittest


class get_core_file_name_TestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_multiple_underscores(self):
        testStr = 'This_name_has_multiple_underscores.extension'
        self.assertEqual(blk.get_core_file_name(testStr),'This')

    def test_no_underscores(self):
        testStr = 'TestStr.extension'
        self.assertEqual(blk.get_core_file_name(testStr),'TestStr')
        
    def test_single_underscore(self):
        testStr = 'Test_str.extension'
        self.assertEqual(blk.get_core_file_name(testStr),'Test')


#class dataframe_generator_excel_TestSuite(unittest.TestCast):
#    return
#    
    
class file_name_parts_TestSuite(unittest.TestCase):
    
    def test_multiple_underscores(self):
        testStr = 'This_name_has_multiple_underscores.extension'
        parts = ['This', 'name', 'has', 'multiple', 'underscores']
        self.assertEqual(blk.file_name_parts(testStr),parts)

    def test_no_underscores(self):
        testStr = 'TestStr.extension'
        self.assertEqual(blk.file_name_parts(testStr),['TestStr'])
        
    def test_single_underscore(self):
        testStr = 'Test_str.extension'
        parts = ['Test', 'str']
        self.assertEqual(blk.file_name_parts(testStr),parts)
    
    
class create_new_image_path_TestSuite(unittest.TestCase):
    
    def test_suffix_proivded(self):
        path = Path('C:\Test\Folder\Test.tif')
        output_dir = Path('C:\Output')
        suffix = 'Suffix'
        
        expected = Path('C:\Output\Test_Suffix.tif')
        
        new_path = blk.create_new_image_path(path, output_dir,
                                             output_suffix = suffix)
        self.assertEqual(new_path, expected)
    
    def test_empty_suffix(self):
        path = Path('C:\Test\Folder\Test.tif')
        output_dir = Path('C:\Output')
        expected = Path('C:\Output\Test.tif')
        
        new_path = blk.create_new_image_path(path, output_dir)
        
        #Modify to either Accept None Suffix, or to throw error for no bad suffix
        self.assertEqual(new_path, expected)
        
    def test_new_extension(self):
        path = Path('C:\Test\Folder\Test.tif')
        output_dir = Path('C:\Output')
        extension = '.test'
        expected = Path('C:\Output\Test.test')
        
        new_path = blk.create_new_image_path(path, output_dir,
                                             extension = extension)
        self.assertEqual(new_path, expected)

    
if __name__ == '__main__':
    unittest.main(verbosity=2)
