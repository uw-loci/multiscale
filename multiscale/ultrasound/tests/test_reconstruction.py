import pytest
import multiscale.ultrasound.reconstruction as recon
import multiscale.utility_functions as util
import scipy.io as sio
import numpy as np
from pathlib import Path


#
# @pytest.fixture(scope='module')
# def mat_dir_and_position_list(self, tmpdir):
#         mat_dir = tmpdir.mkdir('us_image_test')
#         im_one = np.array([[0, 0], [1, 1]])
#         im_two = np.array([[2, 2], [3, 3]])
#         im_three = np.array([[4, 4], [5, 5]])


@pytest.fixture()
def pos_text():
        def _pos_text(positions_xy, position_labels):
                sub_dict =[{'GRID_COL': 0, 'DEVICES':[
                        {'DEVICE': 'XYStage:XY:31', 'AXES': 2, 'Y': positions_xy[pos][1], 'X': positions_xy[pos][0], 'Z': 0}],
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


class TestUltrasoundImage(object):
        @pytest.fixture()
        def us_image(self, tmpdir):
                mats_dir = tmpdir.mkdir('recon_mats')
                pl_path = tmpdir.join('pos_list.pos')

                image = recon.UltrasoundImage(mats_dir, pl_path)

                return image

        def test_input_paths_set_correctly(self):
                mat_dir = Path('Test')
                pl_path = Path('This')

                image = recon.UltrasoundImage(mat_dir, pl_path)

                assert mat_dir == image.mat_dir
                assert pl_path == image.pl_path

        def test_position_list_is_read_correctly(self, pos_file, us_image):
                pos_list_exp = [[0, 0], [1, 1], [2, 2]]
                pos_labels = ['Pos-0', 'Pos-1', 'Pos-2']
                pos_file(us_image.pl_path, pos_list_exp, pos_labels)

                pos_list = us_image._read_position_list()
                assert pos_list == pos_list_exp




