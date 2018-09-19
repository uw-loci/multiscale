import mp_img_manip.ultrasound.correlation as corr
from pathlib import Path
dir_rf = Path(r'C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-09-03\Rovyer_Close_14-5V\Run-6')
corr.calc_plot_corr_curves(dir_rf)