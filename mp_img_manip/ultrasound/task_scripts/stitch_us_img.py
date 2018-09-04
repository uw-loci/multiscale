from pathlib import Path
import mp_img_manip.ultrasound.reconstruction as recon

dir_mats = Path("C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-09-03\\ProngPhantom-BrokenProng_11Volt\\Run-3")
path_pl = Path('C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-09-03\\ProngPhantomGrid.pos')
dir_output = Path('C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-09-03\\')
name_output = 'ProngPhantom3D_Y-fixed'
recon.stitch_us_image(dir_mats, path_pl, dir_output, name_output)