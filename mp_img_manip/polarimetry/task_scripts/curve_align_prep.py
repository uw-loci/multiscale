import mp_img_manip.curve_align as ca
import mp_img_manip.polarimetry.dir_dictionary as dird

dir_dict = dird.create_dictionary()

ca.create_batches_for_chtc(dir_dict['shg_large'], dir_dict['shg_tile'], 'SHG', batch_size=5)

# ca.create_batches_for_chtc(dir_dict['mlr_large_reg'], dir_dict['mlr_tile'], 'MLR')

# ca.create_batches_for_chtc(dir_dict['mhr_large_reg'], dir_dict['mhr_tile'], 'MHR')
#
# ca.create_batches_for_chtc(dir_dict['ps_large_reg'], dir_dict['ps_tile'], 'PS')
