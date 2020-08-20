# Author: Florian Le Roux
# -*- coding: utf-8 -*-
import numpy as np
import tempfile
import re
import os
import math
import time
import sys

import matlab.engine

from csvparser import csvparser
import matplotlib.pyplot as plt

import pickle

class MaximaSearch():

    def __init__(self, anglesToSearch, onlyBlack, midIndex):

        self.onlyBlack = onlyBlack
        self.anglesToSearch = anglesToSearch
        self.eng = matlab.engine.start_matlab()
        self.midIndex = midIndex

    def findMaxima(self):
        
        maximaIntensity = np.zeros((np.size(anglesToSearch),5)) 
                
        currentX = np.genfromtxt(str(os.getcwd()+'\\CurrentX.csv'))
        
        for eltX in currentX:
            
            print(eltX)     

        for idxAngle, angle in enumerate(anglesToSearch):
        
            currentCurve = np.genfromtxt(str(self.searchFolder + '\\CurrentYBT{}.csv'.format(int(angle))))
            
            for elt in currentCurve:
                
                print('startingCurve')
                
                print(elt)                 
            
            try:
    
                PackedResult = self.eng.computeMaximum(matlab.double(currentX.tolist()),matlab.double(currentCurve.tolist()), self.midIndex)
    
                result = PackedResult._data
    
            except RuntimeError:
    
                print('Matlab Engine Failure')             
            
            maximaIntensity[idxAngle,0] = (result1)
            
            maximaIntensity[idxAngle,1] = (result2)
            
            if self.onlyBlack is False:
                
                currentCurveX = np.genfromtxt(str(self.searchFolder + '\\CurrentYXT{}.csv'.format(int(angle))))
            
                firstMaximumCurveX = currentCurveX[:int(self.midIndex)]
            
                secondMaximumCurveX = currentCurveX[int(self.midIndex):]
            
                maximaIntensity[idxAngle,4] = (currentX[np.argmax(firstMaximumCurveX)])
                
                currentCurveY = np.genfromtxt(str(self.searchFolder + '\\CurrentYYT{}.csv'.format(int(angle))))
            
                firstMaximumCurveY = currentCurveY[:int(self.midIndex)]
            
                secondMaximumCurveY = currentCurveY[int(self.midIndex):]
            
                maximaIntensity[idxAngle,2] = (currentX[np.argmax(firstMaximumCurveY)])
            
                maximaIntensity[idxAngle,3] = (currentX[np.argmax(secondMaximumCurveY)])
            
        return maximaIntensity

if __name__ == "__main__":
    
    anglesToSearch = np.linspace(0,90,91)
    
    onlyBlack = True
    
    midIndex = 408

    maxSearch = MaximaSearch(anglesToSearch, onlyBlack, midIndex)
    
    maxIntensity = maxSearch.findMaxima() 

    plt.plot(anglesToSearch, maxIntensity[:,0], color = 'black')   
    plt.plot(anglesToSearch, maxIntensity[:,1], color = 'black')
    
    if onlyBlack is False:
    
        plt.plot(anglesToSearch, maxIntensity[:,2], color = 'red')
        plt.plot(anglesToSearch, maxIntensity[:,3], color = 'red')
    
        plt.plot(anglesToSearch, maxIntensity[:,4], color = 'blue')
    
    plt.show()

    myparser = csvparser()

    np.savetxt(str(os.getcwd()+'\\Maxima.csv'), maxIntensity)    