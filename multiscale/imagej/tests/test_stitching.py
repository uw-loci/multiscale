import multiscale.imagej.stitching as stitch
import numpy as np
from pathlib import Path
#from multiscale.imagej.tests.fixtures.imagej_fixture import imagej


class TestBigStitcher(object):
        def test_stitch_from_files(self):
                assert True

        def test_stitch_from_numpy(self, tmpdir, ij):
                outdir = tmpdir.mkdir('stitch')

                array = np.random.rand(9, 16, 16)
                args = {
                        'define_dataset': '[Automatic Loader (Bioformats based)]',
                        'project_filename': 'dataset.xml',
                        'exclude': '10',
                        'pattern_0': 'Tiles',
                        'modify_voxel_size?': '',
                        'voxel_size_x': '0.5',
                        'voxel_size_y': '0.5',
                        'voxel_size_z': '0.5',
                        'voxel_size_unit': '\u03bcm',
                        'move_tiles_to_grid_(per_angle)?': '[Move Tile to Grid (Macro-scriptable)]',
                        'grid_type': '[Right & Down             ]',
                        'tiles_x': 3,
                        'tiles_y': 3,
                        'tiles_z': 1,
                        'overlap_x_(%)': '10',
                        'overlap_y_(%)': '10',
                        'overlap_z_(%)': '10',
                        'keep_metadata_rotation': '',
                        'how_to_load_images': '[Re-save as multiresolution HDF5]',
                        'dataset_save_path': '.',
                        'subsampling_factors': '[{ {1,1,1}, {2,2,2}, {4,4,4} }]',
                        'hdf5_chunk_sizes': '[{ {16,16,16}, {16,16,16}, {16,16,16} }]',
                        'timepoints_per_partition': '1',
                        'setups_per_partition': '0',
                        'use_deflate_compression': '',
                        'export_path': str(outdir) + 'dataset'
                }

                stitcher = stitch.BigStitcher(ij)
                stitcher.stitch_from_numpy(array, args, {})

                dataset_path = Path(outdir, 'dataset.h5')

                assert dataset_path.is_file()

                #todo : Add fuse args and fuse testing
