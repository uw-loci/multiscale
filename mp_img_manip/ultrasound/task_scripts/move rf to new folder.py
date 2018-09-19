import os, shutil
import mp_img_manip.utility_functions as util
from pathlib import Path

dir_rf = Path(r'C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-09-03\Rovyer_Close_14-5V\Run-6')
rf_list = util.list_filetype_in_dir(dir_rf, 'RF.mat')
dir_new = Path(dir_rf, 'RF')

os.makedirs(dir_new, exist_ok=True)

for file in rf_list:
    new_path = Path(dir_new, file.name)
    shutil.move(file, new_path)

