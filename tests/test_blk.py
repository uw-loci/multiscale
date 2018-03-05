# -*- coding: utf-8 -*-

import mp_img_manip.bulk_img_processing as blk

import unittest


class getBaseFileName_TestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_multiple_underscores(self):
        testStr = 'This_name_has_multiple_underscores.extension'
        self.assertEqual(blk.getBaseFileName(testStr),'This')

    def test_no_underscores(self):
        testStr = 'TestStr.extension'
        self.assertEqual(blk.getBaseFileName(testStr),'TestStr')
        
    def test_single_underscore(self):
        testStr = 'Test_str.extension'
        self.assertEqual(blk.getBaseFileName(testStr),'Test')

class createNewImagePath_TestSuite(unittest.Testcase):
    
    def test_what(self):
        test = True
        self.assertTrue(test)
    
#lass findSharedImages_TestSuite(unittest.TestCase):


if __name__ == '__main__':
    unittest.main(verbosity=2)
