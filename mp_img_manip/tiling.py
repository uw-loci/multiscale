def getTileStartEndIndex(tileNumber, tileSize, tileOffset = None, tileStepSize = None):
    #Calculate the starting and ending index along a single dimension for a tile

    if not tileStepSize:
        tileStepSize = tileSize
        
    if not tileOffset:
        tileOffset = 0
            
    startIndex = ((tileNumber-1)*tileStepSize)+tileOffset
    endIndex = startIndex + tileSize
    
    return (startIndex, endIndex)