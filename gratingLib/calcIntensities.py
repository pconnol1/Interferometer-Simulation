def calcIntensities(observingPositions,pointSourcePositions,xDistance,pointSourceAmplitudes,waveNumber):
        
    # this is the functional form of the inner loop that looked at each point source position and each observing position
    # changes include simply using arrays rather than maneuvering through the classes, as they are just used for the initial
    # set up
    
    sumArray = []
    
    #rTestArray = [] # REMOVE THIS WHEN DONE TESTING
    
    for y1 in observingPositions:
        
        thisSum = 0
        
        # zip just conveniently loops through both our observing positions and amplitudes in one go
        
        for y2, a in zip(pointSourcePositions,pointSourceAmplitudes):
            
            
            yDistance = y2-y1
            
            r0 = math.sqrt(xDistance**2 + yDistance**2)

            thisSum += complexAmplitude(a, waveNumber,r0)
            
            #rTestArray.append(r0) #REMOVE THIS WHEN DONE TESTING

        thisSum = math.sqrt(thisSum * (numpy.conj(thisSum))).real
        
        sumArray.append(thisSum)
    
    return sumArray#, rTestArray # CHANGE RETURN STATEMENT WHEN DONE TESTING