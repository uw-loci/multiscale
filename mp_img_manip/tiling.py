import numpy as np

def getTileStartEndIndex(tileNumber, tileSize, tileOffset = None, tileStepSize = None):
    """Calculate the starting and ending index along a single dimension for a tile"""

    #todo: implement tests

    if not tileStepSize:
        tileStepSize = tileSize
        
    if not tileOffset:
        tileOffset = 0
            
    startIndex = ((tileNumber-1)*tileStepSize)+tileOffset - 1
    endIndex = startIndex + tileSize - 1
    
    return (startIndex, endIndex)



def calculateNumberOfTiles(sizeOfImageDimension, tileSize, tileStepSize = None):
    """Calculate the number of tiles that fit along an image dimension,
     given a certain tile size, and step size."""
    
    #todo: Implement tests.  e.g., tileSize 10, stepSize 9, number = 10, offset = 5
    
    border = 0
    
    if not tileStepSize:
        tileStepSize = tileSize
            
    if tileSize > tileStepSize:
        border = (tileSize - tileStepSize)

    idxRange = sizeOfImageDimension-2*border

    numberOfTiles = np.fix(idxRange/tileStepSize)
    remainder = np.remainder(idxRange,tileStepSize)  
    offset = np.fix(remainder/2) + border

    return (int(numberOfTiles), int(offset))

