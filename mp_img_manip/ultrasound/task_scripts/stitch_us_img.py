from pathlib import Path
import mp_img_manip.ultrasound.reconstruction as recon

dir_mats = Path(r"C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-10-02\5Prong_7Angle_18deg\Run-2")
path_pl = Path(
        'C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-09-03\\ProngPhantomGrid.pos')
dir_output = Path(r'C:\Users\mpinkert\Box\Research\LINK\Ultrasound\Ultrasound Data\2018-10-02\5Prong_7Angle_18deg')
name_output = 'ProngPhantom_MultiAngle_NoPositionList_Env'

data_to_return = 'envelope'

# recon.stitch_elevational_image(dir_mats, path_pl, dir_output, name_output, data_to_return)
recon.stitch_image_without_positions(dir_mats, dir_output, name_output, data_to_return)
