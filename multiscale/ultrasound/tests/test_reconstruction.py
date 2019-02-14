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


@pytest.fixture()
def us_files(tmpdir, pos_file):
        images = np.random.rand(9, 128, 128)+1j*np.random.rand(9, 128, 128)

        mat_dir = tmpdir.mkdir('us_files')
        pos_path = Path(mat_dir, 'Pos.pos')
        positions_xy = [[0, 0],
                        [0, 100],
                        [0, 200],
                        [100, 0],
                        [100, 100],
                        [100, 200],
                        [200, 0],
                        [200, 100],
                        [200, 200]]
        pos_labels = None
        pos_file(pos_path, positions_xy, pos_labels)

        P = {'wavelength_micron': 1,
             'lateral_resolution': 1,
             'axial_resolution': 1,
             'txFocus': 1,
             'startDepth': 5,
             'endDepth': 128,
             'transducer_spacing': 0.1,
             'speed_of_sound': 1540,
             'numRays': 128
             }

        for idx in range(len(images)):
                file_path = Path(mat_dir, 'Image_It-{}.mat'.format(idx))
                sio.savemat(file_path, {'IQData': images[idx], 'P': P})

        return mat_dir, pos_path


class TestUltrasoundImageAssembler(object):
        @pytest.fixture()
        def us_assembler(self, tmpdir, ij, us_files):
                mats_dir, pl_path = us_files
                output_dir = tmpdir.mkdir('recon')

                image = recon.UltrasoundImageAssembler(mats_dir, output_dir, ij, pl_path)

                return image

        def test_assemble_image(self, us_assembler):
                us_assembler._assemble_image()
                output_file = Path(us_assembler.output_dir, 'dataset.xml')
                tif_file = Path(us_assembler.output_dir, 'fused_tp_0_ch_0.tif')
                assert output_file.is_file()
                assert tif_file.is_file()

        def test_position_list_is_read_correctly(self, pos_file, us_assembler):
                pos_list_exp = np.array([[0, 0], [1, 1], [2, 2]])
                pos_labels = ['Pos-0', 'Pos-1', 'Pos-2']
                pos_file(us_assembler.pl_path, pos_list_exp, pos_labels)

                pos_list = us_assembler._read_position_list()
                assert (pos_list == pos_list_exp).all()

        def test_count_unique_positions(self, us_assembler):
                pos_list = np.array([[0, 0], [1, 0], [2, 0], [0, 1]])
                us_assembler.pos_list = pos_list
                
                unique_0 = us_assembler._count_unique_positions(0)
                unique_1 = us_assembler._count_unique_positions(1)
                assert unique_0 == 3
                assert unique_1 == 2
                
        def test_get_spacing(self, us_assembler):
                us_assembler.params = {'axial resolution': 5, 'lateral resolution': 4}
                us_assembler.pos_list = np.array([[0, 1], [0, 2]])
                us_assembler._get_spacing()
                
                output = us_assembler._get_spacing()
                expected = [4, 5, 1]
                
                assert output == expected
                
        @pytest.mark.parametrize('pos_list, axis, expected', [
                (np.array([[0, 0], [1.5, 0], [0, 1], [1.5, 1]]), 0, 1.5),
                (np.array([[0, 0], [1.5, 0], [0, 1], [1.5, 1]]), 1, 1)
        ])
        def test_calculate_position_separation(self, us_assembler, pos_list, axis, expected):
                us_assembler.pos_list = pos_list
                sep = us_assembler._calculate_position_separation(axis)
                assert sep == expected

        def test_get_position_separation_raises_error_on_irregular_grid(self, us_assembler):
                pos_list = np.array([[0, 0], [1.5, 0], [2, 0]])
                us_assembler.pos_list = pos_list
                
                with pytest.raises(ValueError):
                        us_assembler._calculate_position_separation(0)
                        pass

        def test_read_sorted_list_mats(self, us_assembler, monkeypatch):
                unsorted = [Path('It-0.mat'), Path('It-1.mat'), Path('It-10.mat'), Path('It-2.mat')]
                monkeypatch.setattr('multiscale.utility_functions.list_filetype_in_dir', lambda x, y: unsorted)
                expected = [Path('It-0.mat'), Path('It-1.mat'), Path('It-2.mat'), Path('It-10.mat')]
                sorted = us_assembler._read_sorted_list_mats()
                
                assert sorted == expected
          
        @pytest.mark.parametrize('file_path, expected', [
                (Path('Test_Run-1_It-5.mat'), 4)
        ])
        def test_extract_iteration_from_path(self, file_path, expected):
                index = recon.extract_iteration_from_path(file_path)
                assert index == expected

        @pytest.mark.parametrize('raw, var, expected', [
                ({'A': 4, 'B': 3}, 'A', 4),
                ({'C': {'A': 4, 'B': 3}, 'D': 5}, 'C', {'A': 4, 'B': 3}),
                pytest.param({'A': 4, 'B': 3, 'C': {'E': 1, 'F': 2}}, ['A', 'C'], {'A': 4, 'C':{'E': 1, 'F': 2}},
                             marks=pytest.mark.xfail)
        ])
        def test_read_variable(self, monkeypatch, raw, var, expected):
                monkeypatch.setattr('multiscale.utility_functions.load_mat', lambda x, variables: raw)
                output = recon.read_variable(Path('test'), var)
                assert output == expected
                
        def test_read_parameters(self, monkeypatch, us_assembler):
                raw_params = {'lateral_resolution': 0.5, 'axial_resolution': 0.25, 'txFocus': 80, 'startDepth': 5,
                              'endDepth': 160, 'transducer_spacing': 1.014610389610390, 'wavelength_micron': 98.56,
                              'speed_of_sound': 1540}
                
                exp_params ={'lateral resolution': 49.28, 'axial resolution': 24.64, 'transmit focus': 7884.8,
                             'start depth':  492.8, 'end depth': 15769.6, 'transducer spacing': 100.00000000000004,
                             'sampling wavelength': 98.56, 'speed of sound': 1540E6}
                
                monkeypatch.setattr('multiscale.ultrasound.reconstruction.read_variable',
                                    lambda x, y: raw_params)
                
                params = recon.read_parameters(Path('Test'))
                
                assert params == exp_params

        def test_mat_list_to_variable_list(self, monkeypatch, us_assembler):
                expected = [np.random.rand(5, 5), np.random.rand(5, 5), np.random.rand(5, 5)]
                generator = (expected[i] for i in range(3))
                
                monkeypatch.setattr('multiscale.ultrasound.reconstruction.read_variable',
                                        lambda x, y: next(generator))
                
                us_assembler.mat_list = [1, 2, 3]
                output = us_assembler._mat_list_to_variable_list('Test')
                
                assert output == expected
                
        def test_image_list_to_laterally_separate_3d_images(self, us_assembler):
                image_list_array = np.random.rand(6, 5, 5)
                
                expected = np.reshape(image_list_array, [3, 2, 5, 5])
                
                us_assembler.pos_list = np.array([[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]])
                image_list_2d = [image_list_array[i] for i in range(6)]
                
                output = us_assembler._image_list_to_laterally_separate_3d_images(image_list_2d)
                
                assert (output == expected).all()
