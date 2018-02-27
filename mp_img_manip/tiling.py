def getTileStartEndIndex(tileNumber, tileSize, tileOffset, tileStepSize = None):
    #Calculate the starting and ending index along a single dimension for a tile

    if not tileStepSize:
        tileStepSize = tileSize
            
    startIndex = ((tileNumber-1)*tileStepSize)+tileOffset
    endIndex = startIndex + tileSize
    
    return (startIndex, endIndex)