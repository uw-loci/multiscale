from pathlib import Path
import mp_img_manip.ultrasound.reconstruction as recon

dir_mats = Path("C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-09-03\\ProngPhantom-BrokenProng_11Volt\\Run-3")
path_pl = Path('C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-09-03\\ProngPhantomGrid.pos')
dir_output = Path('C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-09-03\\')
name_output = 'ProngPhantom3D_Envelope_Test'
data_to_return = 'envelope'


#recon.stitch_bmode_image(dir_mats, path_pl, dir_output, name_output)
#recon.stitch_env_image(dir_mats, path_pl, dir_output, name_output)
recon.stitch_elevational_image(dir_mats, path_pl, dir_output, name_output, data_to_return)