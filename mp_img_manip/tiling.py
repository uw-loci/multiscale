import numpy as np

def getTileStartEndIndex(tileNumber, tileSize, tileOffset = None, tileStepSize = None):
    #Calculate the starting and ending index along a single dimension for a tile

    if not tileStepSize:
        tileStepSize = tileSize
        
    if not tileOffset:
        tileOffset = 0
            
    startIndex = ((tileNumber-1)*tileStepSize)+tileOffset
    endIndex = startIndex + tileSize
    
    return (startIndex, endIndex)


def calculateNumberOfTiles(sizeOfImageDimension, tileSize, tileStepSize = None):
    border = 0
    
    if not tileStepSize:
        tileStepSize = tileSize
            
    if tileSize > tileStepSize:
        border = (tileSize - tileStepSize)

    idxRange = sizeOfImageDimension-2*border

    numberOfTiles = np.fix(idxRange/tileStepSize)
    remainder = np.remainder(idxRange,tileStepSize)  
    offset = np.fix(remainder/2) + border

    return (numberOfTiles, offset)