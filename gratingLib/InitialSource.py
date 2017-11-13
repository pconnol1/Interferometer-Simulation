# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 21:39:05 2017

@author: joest
"""
import numpy as np
from .complexAmplitude import complexAmplitude

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
        will generate an array of amplitudes for each pointSourceY in pointSourceYs.
        """
        pointSourceYs = np.asarray(pointSourceYs)
        ampValues = np.zeros_like(pointSourceYs)
        ampPhases = np.zeros_like(pointSourceYs, dtype=complex)
        rValues = np.zeros_like(pointSourceYs)
        
        if self.waveType.lower() == 'plane':
            
            ampValues = np.ones_like(pointSourceYs)
            ampPhases = np.ones_like(pointSourceYs)
        
        
        if self.waveType.lower() == 'spherical':
            
            for i in range(0, len(rValues)):
                
                r = np.sqrt((gratingX-self.xPosition)**2 + (pointSourceYs[i]-self.yPosition)**2)
                ampValues[i] = (complexAmplitude(self.initialAmplitude, waveNum, r, 0)).real
                ampPhases[i] = np.exp(1j*waveNum*r)
                
            if normalize == True:
                maxAmp = np.amax(ampValues)
                ampValues = [amp/maxAmp for amp in ampValues]
        
        return ampValues, ampPhases