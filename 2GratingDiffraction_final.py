#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 17:21:19 2017

"""

import os #Used in file saving function
import numpy as np
from numba import jit, vectorize, cuda
import sys, math, cmath, time
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from gratingLib import *

#Select which GPU to use in vectorized function
#'1' is Tesla K40 (faster)
#'0' is Nvidia graphics card (slower)

#if calculationTarget == 'cuda':
#    cuda.close()
#    cuda.select_device(1)

# This function is compiled with numba
# This function calculates the diffraction information between two gratings or a grating and an observing screen
# x: distance between two gratings or distance from last grating to observing screen
# waveNumber: 2Pi/lambda
# y1Vals: array of positions of point source in grating
# y2vals: array of positions of observing positions at next grating or screen
# y1Amps: initial amplitude U0 of the wave at first grating's point sources
# previousPhase: phase information wat first grating's point sources
#
# returns the resulting intensities, amplitudes, and phases at the next grating/screen

calculationTarget = 'parallel'

@jit('c8[:,:](f4,f4,f8[:],f8[:],f8[:],c8[:])')
def calcIntensitiesCUDA(x, waveNumber,y1Vals,y2Vals,y1Amps, previousPhase):
    
    #number of sections to divide y array into: N/x
    y1Vals = np.array(y1Vals)
    y2Vals = np.array(y2Vals)
    previousPhase = np.array(previousPhase)
    
    
    """ Break y1 and y2 into sections """
    """ Need to change this yourself """
    numSections = 10
    
    
    # np.array_split parses initial array in sections
    y1secs = np.array_split(y1Vals, numSections)
    y2secs = np.array_split(y2Vals, numSections)
    
    y1AmpSecs = np.array_split(y1Amps, numSections)
    phaseSections = np.array_split(previousPhase, numSections)
    
    # These arrays of arrays parts need to be numpy arrays
    y1secs = np.array(y1secs) #change names?
    y2secs = np.array(y2secs)
    y1Amps = np.array(y1AmpSecs)
    y1Phase = np.array(phaseSections)
    
    # start increment for amplitude summing later
    ampInc = 0

    outerLoopTime = 0
    innerLoopTime = 0
    checkTime = 0
    
    # Loop through each section of positions on next grating/screen

    for y2section in y2secs:
        inc = 0
        
        # Must have space allocated for amplitude and phases sums
        # Numba does allow for empty arrays '[]'
        ampColumns = [None]*numSections
        preservePhase = ampColumns
    
        # Need to loop through respective first grating point source position, phase information, 
        #       and initial amplitude sections.
        
        for section in range(0, len(y1secs)):
            # np.meshgrid creates repeating rows of first argument and repeating columns of second
            #       argument to create two NxN matrics of the same size. This is done so that these matrices
            #       can be shipped off the the GPU later
            
            y1s, y2s = np.meshgrid(y1secs[section], y2section)
            
            # rArray is a matrix of the respective distances between each point sources and observing point
            
            rArray = np.sqrt(x**2 + (y2s-y1s)**2)
            
            # waveNumArray must a matrix to send to vectorized function
            # this is matrix with every element equal to the wavenumber
            
            waveNumArray = np.full(rArray.shape,waveNumber)
            
            # Make matrix of repeating vectors of initial point source amplitudes to send to vectorized function
            
            y1AmpsMatrix = np.repeat(np.array([y1Amps[section]],dtype=np.float64),rArray.shape[0],0)
            
            
            # Make a matrix of repeating vectors of the phase from the previous propogation
           
            previousPhaseMatrix = np.repeat(np.array([y1Phase[section]],dtype=np.complex128),rArray.shape[0],0)
        
            # Preserve phase information for possible NEXT propagation
            preservePhase[inc] = wavePhase(waveNumArray, rArray)

            # Make a matrix to store the results of the vectorized function
            # Type must be specified as whatever vectorized function expects to return
            # Numba does allow for empty arrays '[]'
            
            ampComponentArray = np.zeros_like(rArray, dtype=np.complex128)
            
            # Calculate the phase information on second grating from the current propagation
            
            currentPhaseMatrix = wavePhase(waveNumArray, rArray)
            
            currentPhaseMatrix = np.array(currentPhaseMatrix, dtype=np.complex128)
            
            # Must separate real and imaginary parts of the current propagations phase and the initial phase
            #       in order to send to vectorized function
            
            prevPhaseMatrixReal = previousPhaseMatrix.real
            prevPhaseMatrixImag = previousPhaseMatrix.imag
            currentPhaseMatrixReal = currentPhaseMatrix.real
            currentPhaseMatrixImag = currentPhaseMatrix.imag
            
            # All of these must be numpy array with specified type
            
            prevPhaseMatrixReal = np.array(prevPhaseMatrixReal, dtype=np.float64)
            prevPhaseMatrixImag = np.array(prevPhaseMatrixImag, dtype=np.float64)
            currentPhaseMatrixReal = np.array(currentPhaseMatrixReal, dtype=np.float64)
            currentPhaseMatrixImag = np.array(currentPhaseMatrixImag, dtype=np.float64)
            
            
            
            
            # Call the vectorized function 'complexAmplitudeCUDA' to calculate the complex amplitudes at
            #       next grating/screen
            
            ampComponentArray = complexAmplitudeCUDA(y1AmpsMatrix, rArray, prevPhaseMatrixReal, prevPhaseMatrixImag, currentPhaseMatrixReal, currentPhaseMatrixImag)
            
            # Sum the columns in the resulting matrix to get the amplitude contribution at each observing point
            #       from all of the point sources in this point source position SECTION
            # Amps is a vector
            
            Amps = ampComponentArray.sum(axis=1)
            
            # This sum is an element of ampColumns to be added to the ampltiude contributions of the other point
            #       source sections later
            
            ampColumns[inc] = Amps
    
            inc+=1
            
        # For each section of observing point positions, the phase contributions are summed
    
        preservePhase = np.array(preservePhase)
        summedPhase = preservePhase.sum(axis=0)


        # For each section of observing point positions, the amplitude contributions are summed
        ampColumns = np.array(ampColumns)
        summedAmps = ampColumns.sum(axis=0)
        
        
        ampInc += 1
        
        # The resulting intensity at this section of observing point positions is found by calculating the modulus of
        #       the amplitudes at these observing points
        # The complex part of the intensity is zero, so we just take the real portion
        summedIntensity = (summedAmps * np.conjugate(summedAmps)).real
        preserveAmplitude = np.sqrt(summedIntensity)

        # Send this information to files so that we don't need to store this information in memory for the next
        #   observing point section
        # Each section of observing points appends information to these files
        

        sendSumAndSendTo("tempData.txt", summedIntensity,'a')
        sendSumAndSendTo("phaseInfo.txt", summedPhase, 'a')
        sendSumAndSendTo("amplitudeInfo.txt", preserveAmplitude, 'a')
    

    # Read the final intensities, phases, and amplitudes from the files to return
    # These files are then destroyed
    # Don't worry, the information is all saved together in files later
    
    intensities = readFromFile("tempData.txt", float)
    phases = readFromFile("phaseInfo.txt", complex)
    amplitudes = readFromFile("amplitudeInfo.txt", float)

    
    return intensities, amplitudes, phases



# preserve phase information k*r0
@vectorize(["c8(f8,f8,f8,f8,f8,f8)"], target=calculationTarget)
def complexAmplitudeCUDA(U_0, r, prevPhaseReal, prevPhaseImag, currentPhaseReal, currentPhaseImag):
    U = U_0 * (currentPhaseReal + 1j*currentPhaseImag) * (prevPhaseReal + 1j*prevPhaseImag) / r
    return U

# calculate phase from current grating
@vectorize(["c8(f8,f8)"], target=calculationTarget)
def wavePhase(k,r):
    phase = cmath.exp(1j*k*r)
    return phase
   
def readFromFile(fname, dataType):
    data = np.loadtxt(fname, dtype = dataType)
    os.remove(fname)
    return data

def sendSumAndSendTo(datafile, theList, option):
    with open(datafile, option) as f:
        for item in theList:
            f.write("%s\n" % item)

#Define initial parameters #################################################################################
screen_distance = 5e7 #nm
screen_length = 1e7
second_grating_distance = 5e7 #nm
wavelength = .56 #nm
U_0 = 1 #?
wavenumber = 2 * np.pi / wavelength
numOfSlits = 200 # number of slits in each grating
numOfPointSources = 100  # number of point sources in each slit
numObsPoints = 1000    # number of observing points on the screen
spacingType = 'uniform'
slitLength = 50 #nm
newSimulation = False
runNum = 1 #Used to dynamically name files. Change every time you run a simulation. Otherwise it will write
            # over old data
            
############################################################################################################

# Observing screen size
#center of screen will automatically be at 0.5e7 nm
# Change this based on size of gratings
screenStart = 0e7
screenEnd = 1e7

#create array of positions that represent an observing screen
observingPositions = np.linspace(screenStart,screenEnd,numObsPoints)

# Build gratings and fill with point sources
firstGrating = Grating(x=0, length=screen_length, numberOfSlits=numOfSlits, slitWidth=slitLength, sourcesPerSlit = numOfPointSources)

# Build second grating and fill with point sources
secondGrating = Grating(x=second_grating_distance, length=screen_length, numberOfSlits=numOfSlits, slitWidth=slitLength, sourcesPerSlit = numOfPointSources)

# Define initial source
# Options are 'spherical' and 'plane'
# Initial source position is -(distance from first grating in nm)
initSource = InitialSource(xPosition= -1e7, yPosition=screen_length/2, waveType='plane', initialAmplitude=1.0)

# generate source amplitudes and phases based on the initial source and the first gratings point source positions
sourceAmps, sourcePhase = initSource.propogate(firstGrating.x, firstGrating.pointSourcePositions, wavenumber, normalize=True)

# add these amplitudes to the first grating's point sources
firstGrating.addAmplitudes(sourceAmps, sourcePhase)

#calculate information from firstGrating propagating to secondGrating
intensities, amplitudes, phases = calcIntensitiesCUDA(screen_distance, wavenumber, firstGrating.pointSourcePositions, secondGrating.pointSourcePositions, firstGrating.pointSourceAmplitudes, firstGrating.pointSourcePhases)

#add necessary results to secondGrating's point sources
print('Populating grating 2\n')
secondGrating.addAmplitudes(amplitudes, phases)

#calculate information from secondGrating propagation to observingPositions
print('Grating 2 to Screen:\n')
intensities2, amplitudes2, phases2 = calcIntensitiesCUDA(screen_distance, wavenumber, secondGrating.pointSourcePositions, observingPositions, secondGrating.pointSourceAmplitudes, secondGrating.pointSourcePhases)


if newSimulation:     
    with open("onSecondGratingResults_%s_run00%s.txt" %(initSource.waveType,runNum), 'w') as f:
        f.write("#source wave type: %s, time taken: %s\n" %(initSource.waveType,tf1-t01))
        f.write("#Intensity\tAmplitudes\t\tPhase\t\t\t\tPosition\n")
        for i, a, p, o in zip(intensities, amplitudes, phases, secondGrating.pointSourcePositions):
            f.write("%s\t%s\t%s\t%s\n" %(i, a, p, o))
            
    with open("onScreenResults_%s_run00%s.txt" %(initSource.waveType,runNum), 'w') as f:
        f.write("#source wave type: %s, time taken: %s" %(initSource.waveType,tf2-t02))
        f.write("#Intensity\tAmplitudes\t\tPhase\t\t\t\tPosition\n")
        for i, a, p, o in zip(intensities2, amplitudes2, phases2, observingPositions):
            f.write("%s\t%s\t%s\t%s\n" %(i, a, p, o))
        
cuda.close()

# quickly plot data to see if results are reasonable
plt.figure(figsize=(15,8))
plt.plot(firstGrating.pointSourcePositions,firstGrating.pointSourceAmplitudes,'.r')
plt.savefig('dottedProfile.png', transparent=True)
plt.xlabel('Position on First Grating (nm)', fontsize = 25)
plt.ylabel('Amplitude', fontsize = 25)
plt.title('Incident on First Grating', fontsize = 30)
plt.show()


plt.figure(figsize=(15,8))
plt.plot(secondGrating.pointSourcePositions,intensities,'.r')
plt.savefig('dottedProfile.png', transparent=True)
plt.xlabel('Position on Second Grating (nm)', fontsize = 25)
plt.ylabel('Normalized Intensity', fontsize = 25)
plt.title('Incident on Second Grating', fontsize = 30)
plt.show()

maxIntensities2 = max(intensities2)
intensities2 = [i/maxIntensities2 for i in intensities2]

obsPositionsMicrons = [i/1000 for i in observingPositions]

plt.figure(figsize=(15,8))
plt.plot(obsPositionsMicrons,intensities2,'r')
plt.savefig('dottedProfile.png', transparent=True)
plt.xlabel('Position on Observing Screen (nm)', fontsize = 25)
plt.ylabel('Normalized Intensity', fontsize = 25)
plt.title('Uniform Grating', fontsize = 30)
plt.show()
