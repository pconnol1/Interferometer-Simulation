#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 17:21:19 2017

@author: beverly
"""
import os #Used in file saving
import numpy as np
from numba import jit, vectorize, cuda
import sys, math, time
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from gratingLib import *

screen_distance = 5e7 #nm
screen_length = 1e7
wavelength = .56 #nm
U_0 = 1 #?
wavenumber = 2 * np.pi / wavelength
numOfSlits = 1
numOfPointSources = 10
numObsPoints = 10
spacingType = 'uniform'
slitLength = 100
newSimulation = True

cuda.close()
cuda.select_device(0)

testGrating = Grating(x=0, length=screen_length,numberOfSlits=numOfSlits,slitWidth=slitLength, sourcesPerSlit=numOfPointSources)

testSource = InitialSource(xPosition = -1e7, yPosition = .500e7, waveType = 'plane', initialAmplitude = 1.0)

sourceAmps, sourcePhases = testSource.propogate(testGrating.x, testGrating.pointSourcePositions, wavenumber, normalize=True)

testGrating.addAmplitudes(sourceAmps, sourcePhases)

observingPositions = np.linspace(0,1e7,numObsPoints)

@jit('c8[:,:](f4,f4,f8[:],f8[:],f8[:],f8[:])')
def calcIntensitiesCUDA(x, waveNumber,y1Vals,y2Vals,y1Amps,phase):
    
    
    #number of sections to divide y array into: N/x
    
    y1Vals = np.array(y1Vals)
    y2Vals = np.array(y2Vals)
    phase = np.array(phase)
    
    
    """ Break y1 and y2 into sections """
    """ Need to change this yourself """
    numSections = 2
    
    y1secs = np.array_split(y1Vals, numSections)
    y2secs = np.array_split(y2Vals, numSections)
 
    #y1amps = 
    
    #Need to look through these later for more gratings
    y1AmpSecs = np.array_split(y1Amps, numSections)
    
    #Grab phase information from last propagation
    phaseSections = np.array_split(phase, numSections)
    
    
    y1sections = np.array(y1secs)
    y2sections = np.array(y2secs)
    
    y1Amps = np.array(y1AmpSecs) ##CHECK
    y1Phase = np.array(phaseSections)
    
    ampInc = 0

    #print(len(y1sections), len(y1Amps))
    
    for y2section in y2sections:
        
        inc = 0
        
        ampColumns = [None]*numSections

        preservePhase = ampColumns
    
        #Need to loop through sections in y1Amps, phase, and y1Sections
        for section in range(0, len(y1sections)):
            
            
            y1s, y2s = np.meshgrid(y1sections[section], y2section)
            
            rArray = np.sqrt(x**2 + (y2s-y1s)**2)
            #print(y1s)
            
    
            #rArray = np.transpose(rArray)
            waveNumArray = np.full(rArray.shape,waveNumber)
            
            #print(y1Amps[section])
            #print(y1Phase[section])
            #print(rArray.shape[0])
            y1AmpsMatrix = np.repeat(np.array([y1Amps[section]],dtype=np.float64),rArray.shape[0],0)
            phaseArray = np.repeat(np.array([y1Phase[section]],dtype=np.float64),rArray.shape[0],0)
            ampComponentArray = np.zeros_like(rArray, dtype=np.complex128)
            
            #rint(y1AmpsMatrix)
            #rint(phaseArray)
            
            ampComponentArray = complexAmplitudeCUDA(y1AmpsMatrix, waveNumArray, rArray, phaseArray)
            
            #Preserve phase information for NEXT propagation
            preservePhase[inc] = np.exp(1j * waveNumber * rArray.sum(axis=1))
            
            #print(len(y1Amps))
            #rint(y1Amps)
            Amps = ampComponentArray.sum(axis=1)
            #print(Amps)
            
            ampColumns[inc] = Amps
            
    
            inc+=1
        
        preservePhase = np.array(preservePhase)
        #print(preservePhase)
        summedPhase = preservePhase.sum(axis=0)
        
        ampColumns = np.array(ampColumns)
        #print(len(ampColumns[1]))
        #print(ampColumns)
        summedAmps = ampColumns.sum(axis=0)
        
        
        ampInc += 1
        
        summedAmps = (summedAmps * np.conjugate(summedAmps)).real
        #print(summedAmps)
        
        A = [1,2,3,4]
 
        #print(summedAmps)
        sendSumAndSendTo("tempData.txt", summedAmps,'a')
        sendSumAndSendTo("phaseInfo.txt", summedPhase, 'a')
        
    intensities = readFromFile("tempData.txt", float)
    phases = readFromFile("phaseInfo.txt", complex)
    
    return intensities, phases

# preserve phase information k*r0
# returning phase is not recognized as a python object
@vectorize(["c8(f8,f8,f8,f8)"], target='parallel')
def complexAmplitudeCUDA(U_0,k,r, phase):
    U = U_0 * phase * (math.cos(k*r) + 1j*math.sin(k*r)) / r
    return U

def readFromFile(fname, dataType):
    
    data = np.loadtxt(fname, dtype = dataType)
    
    os.remove(fname)
    return data

def sendSumAndSendTo(datafile, theList, option):
    with open(datafile, option) as f:
        for item in theList:
            f.write("%s\n" % item)

#t0 = time.time()

numRuns = 1
times = np.zeros(numRuns)

for run in range(0,numRuns):
    t0 = time.time()
    checkIntensity, phases = calcIntensitiesCUDA(screen_distance,wavenumber,testGrating.pointSourcePositions,observingPositions,testGrating.pointSourceAmplitudes, sourcePhases)
    tf = time.time()
    times[run] = tf-t0

    if run==0:
        print(tf-t0)

print(phases)
    
print("Average time: ", np.mean(times))
print("Standard dev.: ", np.std(times))

#cuda.close()
print(len(observingPositions), len(checkIntensity))

plt.figure(figsize=(15,8))
plt.plot(observingPositions,checkIntensity,'r')
plt.savefig('dottedProfile.png', transparent=True)
plt.xlabel('Position on Observing Screen (microns)', fontsize = 25)
plt.ylabel('Normalized Intensity', fontsize = 25)
plt.title('Uniform Grating', fontsize = 30)
plt.show()