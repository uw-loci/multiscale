import mp_img_manip.itk.registration as reg
import mp_img_manip.itk.transform as trans
import mp_img_manip.itk.process as proc
import mp_img_manip.dir_dictionary as dird
import mp_img_manip.polarimetry as pol


"""
Pseudo code:

Read in multiple images, of different polarizations but same general location.

Register them all to a single base image

Acquire the transforms

Mass application of transforms based on image type.

Calculate the transform

Bulk apply it to images.  

"""