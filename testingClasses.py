# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 12:53:59 2017

@author: joest
"""

from gratingLib import *
import matplotlib.pyplot as plt

testSource = InitialSource(xPosition = -1e7, yPosition = .500e7, waveType = 'spherical', initialAmplitude = 1.0)

testGrating = Grating(x=0, length=1e7,numberOfSlits=100,slitWidth=100, sourcesPerSlit=100)

val1Normalized, phases = testSource.propogate(5,testGrating.pointSourcePositions, 1, normalize=True)
val1Unnormalized, _ = testSource.propogate(5,testGrating.pointSourcePositions, 1, normalize=False)
#print(val1Normalized)

testGrating.addAmplitudes(val1Normalized)

print(phases)