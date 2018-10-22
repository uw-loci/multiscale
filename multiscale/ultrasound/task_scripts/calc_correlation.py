import multiscale.ultrasound.correlation as corr
from pathlib import Path
import multiscale.utility_functions as util

list_dirs = [
        Path(r'C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-09-03\Rovyer_Close_14-5V\Run-6'),
        Path(r'C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-09-03\Rovyer_Close_14-5V\Run-5'),
        Path(r'C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-09-03\Lavarello_Close_14-5V\Run-3'),
        Path(r'C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-09-03\Lavarello_Close_14-5V\Run-4')]

dir_output = Path(r'C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-09-03')

for dir_mats in list_dirs:
        output_suffix = str(dir_mats.relative_to(dir_output).parent) + '_' + str(dir_mats.stem)
        
        # if rf files are in dir, move them
        rf_list = util.list_filetype_in_dir(dir_mats, 'RF.mat')
        dir_new = Path(dir_mats, 'RF')
        util.move_files_to_new_folder(rf_list, dir_new)
        
        corr.calc_plot_corr_curves(dir_mats, dir_output, output_suffix)
