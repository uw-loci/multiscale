import mp_img_manip.ultrasound.correlation as corr
from pathlib import Path
import mp_img_manip.utility_functions as util

dir_mats = Path(r'C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-09-03\Rovyer_Close_14-5V\Run-6')

# if rf files are in dir, move them
rf_list = util.list_filetype_in_dir(dir_mats, 'RF.mat')
dir_new = Path(dir_mats, 'RF')
util.move_files_to_new_folder(rf_list, dir_new)

corr.calc_plot_corr_curves(dir_mats)
