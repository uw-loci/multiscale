import pytest
import numpy
import multiscale.imagej.bigdata as bd


class TestWriteDatasetXML(object):
        def test_two_position_translation(self, tmpdir):
                pos_1 = {'position': [0, 0, 0], 'id': 'pos-0', 'size': [5, 5, 5],
                         'unit': 'micron', 'spacing': [1, 1, 1]}
                pos_2 = {'position': [5, 0, 0], 'id': 'pos-0', 'size': [5, 5, 5],
                         'unit': 'micron', 'spacing': [1, 1, 1]}
                position_list_with_metadata = [pos_1, pos_2]
                output_dir = tmpdir.mkdir('bigdata')
                output_name = 'test.xml'
                
                assert True
                