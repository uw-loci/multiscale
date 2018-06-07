from pathlib import Path
import mp_img_manip.curve_align as ca

input_dir = Path('F:\Box Sync\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 03 - Masked images\MLR_Large_Mask')
output_dir = Path('F:\Box Sync\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 05 - Tiling images\CHTC\MLR')

ca.create_batches_for_chtc(input_dir, output_dir)