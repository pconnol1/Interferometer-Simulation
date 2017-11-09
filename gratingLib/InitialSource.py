# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 21:39:05 2017

@author: joest
"""
import numpy as np
from math import sqrt, exp
from complexAmplitude import complexAmplitude

class InitialSource:
    """
    a class that represents the initial source(s) before waves enter the grating system
    """
    def __init__(self, xPosition, yPosition, waveType, initialAmplitude):
        self.xPosition = xPosition # expand this to include collections of point sources? let xPosition and yPosition be arrays?
        self.yPosition = yPosition
        self.waveType = waveType
        self.initialAmplitude = initialAmplitude
        
    def propogate(self, gratingX, pointSourceYs,waveNum, normalize=False):
        """
        will generate an array of amplitudes for each pointSourceY in pointSourceYs. Pass function? or what?
        """
        pointSourceYs = np.asarray(pointSourceYs)
        ampValues = np.zeros_like(pointSourceYs)
        ampPhases = np.zeros_like(pointSourceYs)
        rValues = np.zeros_like(pointSourceYs)
        
        if self.waveType == 'spherical':
            
            for i in range(0, len(rValues)):
                r = sqrt((gratingX-self.xPosition)**2 + (pointSourceYs[i]-self.yPosition)**2)
                ampValues[i] = complexAmplitude(self.initialAmplitude, waveNum, r)
                ampPhases[i] = exp(1j*waveNum*r)
        
        return None
    
testSource = InitialSource(1.0,2.0,'spherical',1.0)

val = testSource.propogate(2,[0,0,0,0,0], 2)

print(val)