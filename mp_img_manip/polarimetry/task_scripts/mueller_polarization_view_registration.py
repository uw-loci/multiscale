import javabridge
import bioformats as bf
import SimpleITK as sitk

javabridge.start_vm(class_path=bf.JARS)

path = r'C:\Users\mpinkert\Box\Research\Polarimetry\Polarimetry - Raw Data\2018.06.14_32x\1367 slide 5.czi'

with bf.ImageReader(path) as reader:
    test = reader.read()
    img = sitk.GetImageFromArray(test)
    print('hello')

javabridge.kill_vm()


