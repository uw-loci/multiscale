import pytest
import multiscale.ultrasound.reconstruction as recon
import multiscale.utility_functions as util
import scipy.io as sio
import numpy as np
from pathlib import Path


#
# @pytest.fixture(scope='module')
# def populate_mat_dir(self, tmpdir):
#         def _populate_mat_dir(list_img_arrays, suffix='')
#                 mat_dir = tmpdir.mkdir('recon_mats')
#
#                 for idx in range(len(list_img_arrays)):
#                         save_path = Path(mat_dir, 'TestImg_It-{0}{1}.mat'.format(idx, suffix))
#                         sio.savemat()


@pytest.fixture()
def pos_text():
        def _pos_text(positions_xy, position_labels=None):
                if position_labels is None:
                        position_labels = ['']*len(positions_xy)
                        
                sub_dict =[{'GRID_COL': 0, 'DEVICES':[
                        {'DEVICE': 'XYStage:XY:31', 'AXES': 2, 'Y': float(positions_xy[pos][1]),
                         'X': float(positions_xy[pos][0]), 'Z': 0}],
                        'PROPERTIES': {}, 'DEFAULT_Z_STAGE': '', 'LABEL': position_labels[pos],
                        'GRID_ROW': 0, 'DEFAULT_XY_STAGE': ''} for pos in range(len(position_labels))]

                pos_text = {'VERSION': 3, 'ID': 'Micro-Manager XY-position list',
                            'POSITIONS': sub_dict}

                return pos_text

        return _pos_text


@pytest.fixture()
def pos_file(pos_text):
        def _pos_file(pos_path, positions_xy, position_labels):
                text = pos_text(positions_xy, position_labels)
                util.write_json(text, pos_path)

        return _pos_file


class TestUltrasoundImageAssembler(object):
        @pytest.fixture()
        def us_image(self, tmpdir):
                mats_dir = tmpdir.mkdir('recon_mats')
                pl_path = tmpdir.join('pos_list.pos')

                image = recon.UltrasoundImageAssembler(mats_dir, pl_path)

                return image

        def test_input_paths_set_correctly(self):
                mat_dir = Path('Test')
                pl_path = Path('This')

                image = recon.UltrasoundImageAssembler(mat_dir, pl_path)

                assert mat_dir == image.mat_dir
                assert pl_path == image.pl_path

        def test_position_list_is_read_correctly(self, pos_file, us_image):
                pos_list_exp = np.array([[0, 0], [1, 1], [2, 2]])
                pos_labels = ['Pos-0', 'Pos-1', 'Pos-2']
                pos_file(us_image.pl_path, pos_list_exp, pos_labels)

                pos_list = us_image._read_position_list()
                assert (pos_list == pos_list_exp).all()

        def test_count_unique_positions(self, us_image):
                pos_list = np.array([[0, 0], [1, 0], [2, 0], [0, 1]])
                us_image.pos_list = pos_list
                
                unique_0 = us_image._count_unique_positions(0)
                unique_1 = us_image._count_unique_positions(1)
                assert unique_0 == 3
                assert unique_1 == 2
                
        @pytest.mark.parametrize('pos_list, axis, expected', [
                (np.array([[0, 0], [1.5, 0], [0, 1], [1.5, 1]]), 0, 1.5),
                (np.array([[0, 0], [1.5, 0], [0, 1], [1.5, 1]]), 1, 1)
        ])
        def test_calculate_position_separation(self, us_image, pos_list, axis, expected):
                us_image.pos_list = pos_list
                sep = us_image._calculate_position_separation(axis)
                assert sep == expected

        def test_get_position_separation_raises_error_on_irregular_grid(self, us_image):
                pos_list = np.array([[0, 0], [1.5, 0], [2, 0]])
                us_image.pos_list = pos_list
                
                with pytest.raises(ValueError):
                        us_image._calculate_position_separation(0)
                        pass

        def test_read_sorted_list_mats(self, us_image, monkeypatch):
                unsorted = [Path('It-0.mat'), Path('It-1.mat'), Path('It-10.mat'), Path('It-2.mat')]
                monkeypatch.setattr('multiscale.utility_functions.list_filetype_in_dir', lambda x, y: unsorted)
                expected = [Path('It-0.mat'), Path('It-1.mat'), Path('It-2.mat'), Path('It-10.mat')]
                sorted = us_image._read_sorted_list_mats()
                
                assert sorted == expected
          
        @pytest.mark.parametrize('file_path, expected', [
                (Path('Test_Run-1_It-5.mat'), 4)
        ])
        def test_extract_iteration_from_path(self, us_image, file_path, expected):
                index = us_image.extract_iteration_from_path(file_path)
                assert index == expected

        @pytest.mark.parametrize('raw, var, expected',[
                ({'A': 4, 'B': 3}, 'A', 4),
                ({'C': {'A': 4, 'B': 3}, 'D': 5}, 'C', {'A': 4, 'B': 3}),
                pytest.param({'A': 4, 'B': 3, 'C': {'E': 1, 'F': 2}}, ['A', 'C'], {'A': 4, 'C':{'E': 1, 'F': 2}},
                             marks=pytest.mark.xfail)
        ])
        def test_read_variable(self, monkeypatch, us_image, raw, var, expected):
                monkeypatch.setattr('multiscale.utility_functions.load_mat', lambda x, variables: raw)
                output = us_image.read_variable(Path('test'), var)
                assert output == expected
                
        def test_read_parameters(self, monkeypatch, us_image):
                raw_params = {'lateral_resolution': 0.5, 'axial_resolution': 0.25, 'txFocus': 80, 'startDepth': 5,
                              'endDepth': 160, 'transducer_spacing': 1.014610389610390, 'wavelength_micron': 98.56,
                              'speed_of_sound': 1540}
                
                exp_params ={'lateral resolution': 49.28, 'axial resolution': 24.64, 'transmit focus': 7884.8,
                             'start depth':  492.8, 'end depth': 15769.6, 'transducer spacing': 100.00000000000004,
                             'sampling wavelength': 98.56, 'speed of sound': 1540}
                
                monkeypatch.setattr('multiscale.ultrasound.reconstruction.UltrasoundImageAssembler.read_variable',
                                    lambda x, y, z: raw_params)
                
                us_image._read_parameters(Path('Test'))
                
                assert us_image.acq_params == exp_params

        def test_mat_list_to_variable_list(self, monkeypatch, us_image):
                expected = [np.random.rand(5, 5), np.random.rand(5, 5), np.random.rand(5, 5)]
                generator = (expected[i] for i in range(3))
                
                monkeypatch.setattr('multiscale.ultrasound.reconstruction.UltrasoundImageAssembler.read_variable',
                                        lambda x, y, z: next(generator))
                
                us_image.mat_list = [1, 2, 3]
                output = us_image._mat_list_to_variable_list('Test')
                
                assert output == expected
                






