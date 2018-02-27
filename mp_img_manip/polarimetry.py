import mp_img_manip.tiling as til
import numpy as np
import imageio as io

def  calculateRetardanceOverArea(retardance, orientation):
    
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

    retImg = io.imread(retImgPath)
    orientImg = io.imread(orientImgPath)

    #if np.size(retImg) != np.size(orientImg):
     #   warn('The retardance and orientation image sizes do not match.  Please select inputs from the same image')    
      #  return

    #if (np.remainder(scalePixelFactor,1) != 0) or (np.remainder(simulatedResolutionFactor,1) != 0):
     #   warn('The scale factor(s) needs to be a positive integer, representing the number of pixels that compose the new pixel value')
      #  return
        #todo: allow non-integer resolution scaling
    
    imgSize = np.shape(retImg)
    
    (xPixelNum, xOffset) = til.calculateNumberOfTiles(imgSize[0], scalePixelFactor, simulatedResolutionFactor)
    (yPixelNum, yOffset) = til.calculateNumberOfTiles(imgSize[1], scalePixelFactor, simulatedResolutionFactor)
    
    downRet = np.zeros((xPixelNum, yPixelNum))
    downOrient = downRet

    for y in range(1,yPixelNum+1):
        for x in range(1, xPixelNum+1):
            
            (xStart, xEnd) = til.getTileStartEndIndex(x, scalePixelFactor, xOffset, simulatedResolutionFactor)
            (yStart, yEnd) = til.getTileStartEndIndex(y, scalePixelFactor, yOffset, simulatedResolutionFactor)

            retNeighborhood = retImg(range(xStart,xEnd+1),range(yStart,yEnd+1))
            orientNeighborhood = orientImg(range(xStart,xEnd+1),range(yStart,yEnd+1))
            
            (retPixel, orientPixel) = calculateRetardanceOverArea(retNeighborhood,orientNeighborhood)
           
            downRet[x,y] = retPixel
            downOrient[x,y] = orientPixel
            
    return (downRet, downOrient) 