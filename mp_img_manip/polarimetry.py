def  calculateRetardanceOverArea(retardance, orientation)
    
    # This gives me the orientation in 360 degrees, doubled to calculate alignment.
    circularOrientation = (2*pi/180)*(orientation/100);
    complexOrientation = exp(1i*circularOrientation);
    
    retardanceWeightedByOrientation = retardance*complexOrientation;
    
    numPixels = np.size(retardance);
    
    averageRetardance = np.sum(retardanceWeightedByOrientation)/numPixels;
    
    retMag = np.absolute(averageRetardance);
    retAngle = np.angle(averageRetardance)/2; 

    return (retMag,retAngle)

