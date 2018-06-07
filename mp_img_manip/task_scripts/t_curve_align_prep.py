from pathlib import Path
import mp_img_manip.curve_align as ca

image_path = Path('F:\Box Sync\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 03 - Masked images\MLR_Large_Mask', 'WP2_MLR_Large_Mask.tif')
output_dir = Path('F:\Box Sync\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 05 - Tiling images\MLR_Large_Tiles\WP2_MLR_CHTC')

ca.process_image_to_rois(image_path, output_dir)