import mp_img_manip.tiling as til
import mp_img_manip.bulk_img_processing as blk
import numpy as np
import SimpleITK as sitk

def calculateRetardanceOverArea(retardance, orientation):
    
    # This gives me the orientation in 360 degrees, doubled to calculate alignment.
    circularOrientation = (2*np.pi/180)*(orientation/100);
    complexOrientation = np.exp(1j*circularOrientation);
    
    retardanceWeightedByOrientation = retardance*complexOrientation;
    
    numPixels = np.size(retardance);
    
    averageRetardance = np.sum(retardanceWeightedByOrientation)/numPixels;
    
    retMag = np.absolute(averageRetardance);
    retAngle = np.angle(averageRetardance)/2; 

    return (retMag,retAngle)


def DownsampleRetardanceImage(retImgPath, orientImgPath, scalePixelFactor, simulatedResolutionFactor = None):

    if not simulatedResolutionFactor:
        simulatedResolutionFactor = scalePixelFactor

    retImgITK = sitk.ReadImage(retImgPath)
    orientImgITK = sitk.ReadImage(orientImgPath)

    retArray= sitk.GetArrayFromImage(retImgITK)
    orientArray = sitk.GetArrayFromImage(orientImgITK)


    #if np.size(retImg) != np.size(orientImg):
     #   warn('The retardance and orientation image sizes do not match.  Please select inputs from the same image')    
      #  return

    #if (np.remainder(scalePixelFactor,1) != 0) or (np.remainder(simulatedResolutionFactor,1) != 0):
     #   warn('The scale factor(s) needs to be a positive integer, representing the number of pixels that compose the new pixel value')
      #  return
        #todo: allow non-integer resolution scaling
    
    arraySize = np.shape(retArray)
    
    (xPixelNum, xOffset) = til.calculateNumberOfTiles(arraySize[0], scalePixelFactor, simulatedResolutionFactor)
    (yPixelNum, yOffset) = til.calculateNumberOfTiles(arraySize[1], scalePixelFactor, simulatedResolutionFactor)

    downRetArray = 
    downOrientArray = downRetArray

    for y in range(0,yPixelNum):
        for x in range(0, xPixelNum):
            
            (xStart, xEnd) = til.getTileStartEndIndex(x, scalePixelFactor, xOffset, simulatedResolutionFactor)
            (yStart, yEnd) = til.getTileStartEndIndex(y, scalePixelFactor, yOffset, simulatedResolutionFactor)

            retNeighborhood = retArray[range(xStart,xEnd+1),range(yStart,yEnd+1)]
            orientNeighborhood = orientArray[range(xStart,xEnd+1),range(yStart,yEnd+1)]
            
            (retPixel, orientPixel) = calculateRetardanceOverArea(retNeighborhood,orientNeighborhood)

            downRetArray[x,y] = 10
            downOrientArray[x,y] = orientPixel
            
            if x == 100 and y == 100:
                print(retPixel)
                print(downRetArray[x,y])
    
    
    downRetImg = sitk.GetImageFromArray(downRetArray)
    downOrientImg = sitk.GetImageFromArray(downOrientArray)
            
    return (downRetArray, downOrientArray) 

def BatchDownsampleRetardance(scaleFactor, retDir, orientDir, outputDir, simulatedResolutionFactor = None):
    outputSuffix = '_DownsampledBy-' + str(scaleFactor) + 'x'

    if simulatedResolutionFactor and simulatedResolutionFactor != scaleFactor:
        outputSuffix = outputSuffix + '_SimRes-' + str(simulatedResolutionFactor) + 'x'

    (retImgPathList, orientImgPathList) = blk.findSharedImages(retDir, orientDir)
    
    for i in range(0, np.size(retImgPathList)):
        (downRetImg, downOrientImg) = DownsampleRetardanceImage(retImgPathList[i], orientImgPathList[i], scaleFactor, simulatedResolutionFactor)
        
        downRetPath = blk.createNewImagePath(retImgPathList[i], outputDir, outputSuffix + '_Ret')
        downOrientPath = blk.createNewImagePath(orientImgPathList[i], outputDir, outputSuffix + '_SlowAxis')
        
        sitk.WriteImage(downRetImg, downRetPath)
        sitk.WriteImage(downOrientImg, downOrientPath)