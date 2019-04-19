import multiscale.ultrasound.correlation as corr
from pathlib import Path
import multiscale.utility_functions as util

list_dirs = [Path(r'F:\Research\LINK\Phantom Trials\2018-12-19\Lavarello 1gperL TGC_1 V_5-1\Run-2')]

dir_output = Path(r'F:\Research\LINK\Phantom Trials\2018-12-19\Lavarello 1gperL TGC_1 V_5-1')

for dir_mats in list_dirs:
        output_suffix = str(dir_mats.relative_to(dir_output).parent) + '_' + str(dir_mats.stem)
        
        # if rf files are in dir, move them
        rf_list = util.list_filetype_in_dir(dir_mats, 'RF.mat')
        dir_new = Path(dir_mats, 'RF')
        util.move_files_to_new_folder(rf_list, dir_new)
        
        corr.calc_plot_corr_curves(dir_mats, dir_output, output_suffix, elevation_res=0.02)
