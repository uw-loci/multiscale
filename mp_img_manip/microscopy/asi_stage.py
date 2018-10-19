import os
environ = os.environ
for key, value in environ.items():
        print(key + ': ' + value)
import imagej

ij = imagej.init(r'C:\Users\mpinkert\Desktop\Fiji.app')

# Import an image with scikit-image.
import skimage
from skimage import io
# NB: Blood vessel image from: https://www.fi.edu/heart/blood-vessels
img = io.imread('https://www.fi.edu/sites/fi.live.franklinds.webair.com/files/styles/featured_large/public/General_EduRes_Heart_BloodVessels_0.jpg')
import numpy as np
img = np.mean(img, axis=2)

# Invoke ImageJ's Frangi vesselness op.
vessels = np.zeros(img.shape, dtype=img.dtype)
import imglyb
ij.op().filter().frangiVesselness(imglyb.to_imglib(vessels), imglyb.to_imglib(img), [1, 1], 20)