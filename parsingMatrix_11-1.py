#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 17:21:19 2017

@author: beverly
"""
import os
import numpy as np
from numba import jit, vectorize
import sys, math, time
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from gratingLib import *

screen_distance = 5e7 #nm
screen_length = 1e7
wavelength = .56 #nm
U_0 = 1 #?
wavenumber = 2 * np.pi / wavelength
numOfSlits = 100
numOfPointSources = 100
spacingType = 'uniform'
slitLength = 100
newSimulation = True

testGrating = Grating(0,screen_length,numOfSlits,[])
makeSlits(testGrating, slitLength, numOfPointSources)

for i in range(0,len(testGrating.slits)):
    makeSources(testGrating.slits[i],1,spacingType)

observingPositions = np.linspace(0,1e7,100000)

t0 = time.time()

@jit('c8[:,:](f4,f4,f8[:],f8[:],f8[:])')
def calcIntensitiesCUDA(x, waveNumber,y1Vals,y2Vals,y1Amps):
    
    
    #number of sections to divide y array into: N/x

    t0 = time.time()
    
    y1Vals = np.array(y1Vals)
    y2Vals = np.array(y2Vals)
    
    
    #print(y1Vals,y2Vals)
    
    """ Break y1 and y2 into sections """
    """ Need to change this yourself """
    numSections = 20
    
    
    
    #y1sections = np.array([np.array_split(y1Vals, numSections)])
    #y2sections = np.array([np.array_split(y2Vals, numSections)])
    

    
    y1secs = np.array_split(y1Vals, numSections)
    y2secs = np.array_split(y2Vals, numSections)
 
    #y1amps = 
    
    #Need to look through these later for more gratings
    y1AmpSecs = np.array_split(y1Amps, numSections)
    
    y1sections = np.array(y1secs)
    y2sections = np.array(y2secs)
    
    y1Amps = np.array(y1AmpSecs)
    

    ampInc = 0

    for y2section in y2sections:
        
        inc = 0
        
        ampColumns = [None]*numSections
    
        #ampColumns = [[0],[0],[0],[0]]

        # Make double for loop
        
        for y1section in y1sections:
            #print(y1section)
            #print(y2section)
            
            y1s, y2s = np.meshgrid(y1section, y2section)
            
            rArray = np.sqrt(x**2 + (y2s-y1s)**2)
    
            #rArray = np.transpose(rArray)
            waveNumArray = np.full(rArray.shape,waveNumber)
    
            
            #y1Amps = np.transpose(np.repeat(np.array([y1Amps]),rArray.shape[1],0))
            y1Amps = np.repeat(np.array([y1Amps[0]]),rArray.shape[0],0)
            
            ampComponentArray = np.zeros_like(rArray, dtype=complex)
    
            ampComponentArray[:,:] = complexAmplitudeCUDA(y1Amps[:,:], waveNumArray[:,:], rArray[:,:])
            
            
            Amps = ampComponentArray.sum(axis=1)
            
            ampColumns[inc] = Amps
            
    
            inc+=1
            
        ampColumns = np.array(ampColumns)
        summedAmps = ampColumns.sum(axis=0)
        #ampColumns[0] + ampColumns[1] + ampColumns[2] + ampColumns[3]
        
        ampInc += 1
        
        summedAmps = (summedAmps * np.conjugate(summedAmps)).real
 
        #print(summedAmps)
        sendSumAndSendTo("tempData.txt", summedAmps,'a')
        
    intensities = readFromFile("tempData.txt")
    
    return intensities

# preserve phase information k*r0
# returning phase is not recognized as a python object
@vectorize(["c8(f8,f8,f8)"], target='parallel')
def complexAmplitudeCUDA(U_0,k,r):
    U = U_0 * (np.cos(k*r) + 1j*np.sin(k*r)) / r
    return U

def readFromFile(fname):
    with open(fname, 'r') as f:
        data = f.readlines()
    os.remove(fname)
    return data

def sendSumAndSendTo(datafile, theList, option):
    with open(datafile, option) as f:
        for item in theList:
            f.write("%s\n" % item)

#t0 = time.time()
y2Array, y1Array, y1Amps = processInputForJobs(testGrating,observingPositions,1)
y2array = []
for i in y2Array[0]:
    y2array.append(i)

checkIntensity = calcIntensitiesCUDA(screen_distance,wavenumber,y1Array,y2array,y1Amps)

tf = time.time()

print(tf-t0)

plt.figure(figsize=(15,8))
plt.plot(observingPositions,checkIntensity,'r')
plt.savefig('dottedProfile.png', transparent=True)
plt.xlabel('Position on Observing Screen (microns)', fontsize = 25)
plt.ylabel('Normalized Intensity', fontsize = 25)
plt.title('Uniform Grating', fontsize = 30)
plt.show()