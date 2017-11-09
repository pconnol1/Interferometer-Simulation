# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 19:40:59 2017

@author: joest
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

class PlotBuddy:
    
    def __init__(self, dataArg, plotTitle, xLabel, yLabel):
        
        """
        Creating an instance of PlotBuddy requires...
        
            dataArg: either an array with [xData, yData] or a string of a .txt file name with a column of xData and yData
                        in that order. Comments in the text file are the same as python comments (#). If it is a grating
                        output file, it will also retrieve the parameters we print by finding the tag "GratingFile"
                        in the first line of the .txt. It then parses the file and finds the parameters of each grating
                        and saved them to a parameter array.
                    
            plotTitle: a string that will be the plot title
            
            xLabel: a string that will become the label of the x axis
            
            yLabel: a string that will become the label of the y axis
        """
        
        # if given a list of arrays, use these initializers
        if isinstance(dataArg, list):
            self.xData = dataArg[0]
            self.yData = dataArg[1]
            self.numberOfGratings = None
            self.paramList = None
            
        # if given the name of the file to load, use these initializers
        if isinstance(dataArg, str):
            
            isGratingFile = False
            # find the tag "GratingFile" in line 1 of the file
            with open(dataArg) as f:
                for word in f.readline().split():
                    if word == 'GratingFile':
                        isGratingFile = True
                       
            # if we find the GratingFile tag, we grab each parameter from the headers
            if isGratingFile:
                
                parameterData = []
                
                with open(dataArg) as f:
                    counter = 0
                    
                    for word in f.readline().split():
                        try:
                            gratingNum = int(word)
                        except ValueError:
                            _ = None
                            
                    if gratingNum > 5:
                        print('PlotBuddy Initialization Error: Check file headers for number of gratings. Found %d gratings.' %gratingNum)
                        
                        return None

                    for line in f:
                        for word in line.split():
                            try:
                                parameterData.append(float(word))
                            except ValueError:
                                _ = None
                        counter+=1

                        if counter >(2+gratingNum):
                            break
                            
                    if len(parameterData) < 5 or len(parameterData) > 10:
                        print('PlotBuddy Initialization Error: Check file headers in data file. Found %d parameters.' %len(parameterData))
                        return None
                        
                    
                self.numberOfGratings = gratingNum
                self.paramList = parameterData
                
                xdata, ydata = np.loadtxt(dataArg, unpack=True)
                
                self.xData = xdata
                self.yData = ydata
                
            else:
                xdata, ydata = np.loadtxt(dataArg, unpack=True)
                self.xData = xdata
                self.yData = ydata
                self.numberOfGratings = None
                self.paramList = None
                
        self.plotTitle = plotTitle
        self.xLabel = xLabel
        self.yLabel = yLabel
        
    def plot(self, newPlotTitle = None, newXLabel = None, newYLabel = None,
             figSize = None, paramLoc = None, markerStyle = None,minFontSize=15, saveFigAs = None):
        """
        
        Inputs:
        
            - plotTitle: A string the user provides that will be the title of the plot
            
            - xLabel/yLabels: A string the user provides that will label the x/y axes respectively.
            
        """

        
        if isinstance(figSize, tuple):
            fig=plt.figure(figsize=figSize)
        else:
            fig = plt.figure(figsize=(12,10))
        
        if type(newPlotTitle) is str:
            plt.title(newPlotTitle,fontsize=minFontSize+10)
            self.plotTitle = newPlotTitle
            
        else:
            plt.title(self.plotTitle, fontsize=minFontSize+10)
        
        if type(newXLabel) is str:
            plt.xlabel(newXLabel, fontsize=minFontSize+5)
            self.xLabel = newXLabel
            
        else:
            plt.xlabel(self.xLabel, fontsize=minFontSize+5)
            
        if type(newYLabel) is str:
            plt.ylabel(newYLabel, fontsize=minFontSize+5)
            self.yLabel = newYLabel
            
        else:
            plt.ylabel(self.yLabel, fontsize=minFontSize+5)
        
        ax = fig.add_subplot(111)
        
        if type(markerStyle) is str:
            ax.plot(self.xData, self.yData, markerStyle, markersize=15.0)
        
        else:
            ax.plot(self.xData, self.yData, '-', markersize=15.0)
        #ax.plot(calcs,fittedTime,label='Linear fit')
        
        ax.xaxis.set_major_locator(tkr.MaxNLocator())
        ax.yaxis.set_major_locator(tkr.MaxNLocator())
        ax.xaxis.set_minor_locator(tkr.AutoMinorLocator())
        ax.yaxis.set_minor_locator(tkr.AutoMinorLocator())
        
        
        for x in ax.xaxis.get_major_ticks():
            x.label.set_fontsize(minFontSize)
        
        for y in ax.yaxis.get_major_ticks():
            y.label.set_fontsize(minFontSize)
            
        if isinstance(self.numberOfGratings,int) and isinstance(paramLoc,tuple):
            
            if paramLoc[0]>1 or paramLoc[1]>1 or paramLoc[0]<0.0 or paramLoc[1]<0.0:
                print('Error: paramLocs must be floats between 0.0 and 1.0, stopping plot.')
                return None
            # first build a parameter string based on the paramList we grabbed
            paramStrings = ''
            
            for grating in range(0,self.numberOfGratings):
                paramStrings = paramStrings + 'Grating %i parameters: %d Slits, %d Sources per Slit\n' %(grating+1,self.paramList[grating*2], self.paramList[grating*2+1])
            paramStrings = paramStrings + r'%0.3f $\mu$m wavelength, %d cm distance' %(self.paramList[-3],self.paramList[-2])
            paramStrings = paramStrings + '\ntime taken: %.4f s' %self.paramList[-1]
                 
            size = plt.gcf().get_size_inches()*fig.dpi # size of plot in pixels
            ax.annotate(paramStrings, xy=(size[0]*paramLoc[0],size[1]*paramLoc[1]), xycoords='figure points', fontsize=14)    
        
        ax.grid(which='both')
        ax.grid(which='minor', alpha=0.2)                                                
        ax.grid(which='major', alpha=0.5)
        
        plt.show()
        
        if isinstance(saveFigAs, str):
            plt.savefig(saveFigAs)
        
    def addText(self):
        print('this will add text!')