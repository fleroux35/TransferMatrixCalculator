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

class OscillatorGenerator():
    
          def __init__(self):
                    
                    self.eng = matlab.engine.start_matlab()
           
          #using notation from paper with pulses
          
          def generateLorentzianIsotropic(self, neff, gamma, gammapower, centralEnergy, go, gopower, minWavelength, maxWavelength, wvlResolution, materialName):
                    
                    wavelength, refractivendexReal, refractiveIndexComplex = self.generateLorentzian(self, neff, gamma, gammapower, centralEnergy, go, gopower, minWavelength, maxWavelength, wvlResolution)
                              
                    fig, ax1 = plt.subplots()
                    
                    color = 'tab:blue'
                    ax1.set_xlabel('Wavelength (nm)')
                    ax1.set_ylabel('Refractive Index (Real)', color=color)
                    ax1.plot(wavelength, refractiveIndexReal, color=color)
                    ax1.tick_params(axis='y', labelcolor=color)
                    
                    ax2 = ax1.twinx()
                    
                    color = 'tab:red'
                    ax2.set_ylabel('Refractive Index (Complex)', color=color)
                    ax2.plot(wavelength, refractiveIndexComplex, color=color)
                    ax2.tick_params(axis='y', labelcolor=color)
                    
                    fig.tight_layout()
                    plt.show()                    
        
                    myparser = csvparser()
                    
                    myparser.write('C:\\Users\\leroux\\Desktop\\Test.csv', wavelength, refractiveIndexReal, refractiveIndexComplex, False, False, False, False)
                    
          def generateLorentzian(self, neff, gamma, gammapower, centralEnergy, go, gopower, minWavelength, maxWavelength, wvlResolution):
          
                    numberOfWavelengths = int((maxWavelength-minWavelength)/wvlResolution) + 1
                    wavelength = np.linspace(minWavelength, maxWavelength, numberOfWavelengths)
                    
                    refractiveIndexReal = np.zeros_like(wavelength)
                    
                    refractiveIndexComplex = np.zeros_like(wavelength)
                    
                    try:
                    
                              wavelengthForMatlab = matlab.double(wavelength.tolist())
                              
                              centralEnergyForMatlab = centralEnergy
                              
                              gammaForMatlab = gamma
                              
                              neffForMatlab = neff
                              
                              goForMatlab = go
                    
                              PackedResult = self.eng.GenerateLorentzian(wavelengthForMatlab, centralEnergyForMatlab, gammaForMatlab, gammapower, neffForMatlab, goForMatlab, gopower)
                    
                              result = PackedResult._data
                    
                              refractiveIndexReal = np.asarray(result[0:numberOfWavelengths])
                    
                              refractiveIndexComplex = np.asarray(result[numberOfWavelengths:numberOfWavelengths*2])
                              
    
                    except RuntimeError:
                    
                              print('Matlab Engine Failure')                       
                              
                    return wavelength, refractiveIndexReal, refractiveIndexComplex
                    
          def generateCauchy(self, neff, minWavelength, maxWavelength, wvlResolution):
                    
                    numberOfWavelengths = int((maxWavelength-minWavelength)/wvlResolution) + 1
                    wavelength = np.linspace(minWavelength, maxWavelength, numberOfWavelengths)
                    
                    refractiveIndexReal = np.zeros_like(wavelength)
                    
                    refractiveIndexComplex = np.zeros_like(wavelength)
                    
                    for eltIdx, elt in enumerate(refractiveIndexReal):
                              
                              refractiveIndexReal[eltIdx] = neff
                              
                    return wavelength, refractiveIndexReal, refractiveIndexComplex
                      
                    
          def generateBiaxial(self, layerX, layerY, layerZ, minWavelength, maxWavelength, wvlResolution, materialName):
                    
                    #identify the type of layer first
                    
                    oscParametersX = layerX[1]                    
                    
                    if layerX[0] == 'Lorentzian':
                              
                              wavelength, refractiveIndexRealX, refractiveIndexComplexX = self.generateLorentzian(oscParametersX[0], oscParametersX[1], oscParametersX[2], oscParametersX[3], oscParametersX[4], oscParametersX[5], minWavelength, maxWavelength, wvlResolution)
                              
                    if layerX[0] == 'Cauchy':
                              
                              wavelength, refractiveIndexRealX, refractiveIndexComplexX = self.generateCauchy(oscParametersX[0], minWavelength, maxWavelength, wvlResolution)                   
                              
                    oscParametersY = layerY[1]                    
                              
                    if layerY[0] == 'Lorentzian':
                                        
                              wavelength, refractiveIndexRealY, refractiveIndexComplexY = self.generateLorentzian(oscParametersY[0], oscParametersY[1], oscParametersY[2], oscParametersY[3], oscParametersY[4], oscParametersY[5], minWavelength, maxWavelength, wvlResolution)
                                        
                    if layerY[0] == 'Cauchy':
                                        
                              wavelength, refractiveIndexRealY, refractiveIndexComplexY = self.generateCauchy(oscParametersY[0], minWavelength, maxWavelength, wvlResolution)
                                
                    oscParametersZ = layerZ[1]                    
                                        
                    if layerZ[0] == 'Lorentzian':
                                                  
                              wavelength, refractiveIndexRealZ, refractiveIndexComplexZ = self.generateLorentzian(oscParametersZ[0], oscParametersZ[1], oscParametersZ[2], oscParametersZ[3], oscParametersZ[4], oscParametersZ[5], minWavelength, maxWavelength, wvlResolution)
                                                  
                    if layerZ[0] == 'Cauchy':
                                                  
                              wavelength, refractiveIndexRealZ, refractiveIndexComplexZ = self.generateCauchy(oscParametersZ[0], minWavelength, maxWavelength, wvlResolution)                              
                                                
                    fig, ax1 = plt.subplots()
                    
                    colorX = 'tab:blue'
                    colorY = 'tab:red'
                    
                    energies = np.zeros_like(wavelength)
                    
                    for wvlIdx, wvl in enumerate(wavelength):
                    
                              energies[wvlIdx] = 1239.82/wvl
                              
                    
                    font = {'family': 'Calibri',
                          'color':  'black',
                              'weight': 'normal',
                              'size': 25,}  
                    
                    ax1.set_xlabel('Energy (eV)', fontdict = font)
                    ax1.set_ylabel('n', fontdict = font)
                    ax1.plot(energies, refractiveIndexRealX, color = 'blue', linestyle = 'dashed')
                    ax1.plot(energies, refractiveIndexRealY, color = 'red', linestyle = 'dashed')
                    ax1.tick_params(axis='y')
                    ax1.get_yaxis().get_major_formatter().set_useOffset(False)
                    plt.yticks(np.asarray([0.8,1.2,1.6,2.0,2.4]))
                    #plt.yticks(np.asarray([1.55,1.6,1.65]))
                    
                    for tick in ax1.xaxis.get_major_ticks():
                              tick.label.set_fontsize(15) 
          
                    for tick in ax1.yaxis.get_major_ticks():
                              tick.label.set_fontsize(15)                      
                    
                    plt.grid(True)
                    ax1.grid(color='gray', linestyle='dashed', linewidth=0.5)                    
                    
                    ax2 = ax1.twinx()
                    
                    ax2.set_ylabel('k', fontdict = font)
                    ax2.plot(energies, refractiveIndexComplexX, color = 'blue')
                    ax2.plot(energies, refractiveIndexComplexY, color = 'red')
                    ax2.tick_params(axis='y')
                    plt.yticks(np.asarray([0,0.7,1.4]))
                    #plt.yticks(np.asarray([0,0.055,0.11]))
                    ax2.ticklabel_format(axis='both',style='sci',scilimits = (0,2))
                    
                    for tick in ax2.xaxis.get_major_ticks():
                              tick.label.set_fontsize(15)                     
          
                    for tick in ax2.yaxis.get_major_ticks():
                              tick.label.set_fontsize(15)  
                              
                    for axis in ['top','bottom','left','right']:
          
                              ax1.spines[axis].set_linewidth(1.75)
                              ax2.spines[axis].set_linewidth(1.75)   
                    
                    plt.xlim(2.1,4.5)
                    #plt.xlim(3.1,3.4)
                    #plt.ylim(0, 0.11)  
                    plt.ylim(0, 1.4)                     
                    
                    fig.tight_layout()
                    
                    plt.savefig('Index', dpi=600, facecolor='w', edgecolor='w',
                              orientation='portrait', papertype=None, format=None,
                          transparent=False, bbox_inches=None, pad_inches=0.1,
                          frameon=None, metadata=None)
                    
                    plt.show()  
                                         
        
                    myparser = csvparser()
                    
                    myparser.write(str('C:\\Users\\leroux\\Desktop\\{}.csv'.format(materialName)), wavelength, refractiveIndexRealX, refractiveIndexComplexX, refractiveIndexRealY, refractiveIndexComplexY, refractiveIndexRealZ, refractiveIndexComplexZ)  
                    
          def threeLorentziansVisibility(self, wavelength, Lorentzian1, Lorentzian2, Lorentzian3):
                    
                    plt.plot(wavelength,Lorentzian1)
                    plt.plot(wavelength,Lorentzian2)
                    plt.plot(wavelength,Lorentzian3)
                    
                    sumLorentzians = np.zeros_like(Lorentzian1)
                    
                    for eltIdx, elt in enumerate(Lorentzian1):
                              
                              sumLorentzians[eltIdx] = Lorentzian1[eltIdx] + Lorentzian2[eltIdx] + Lorentzian3[eltIdx]
                              
                    plt.plot(wavelength,sumLorentzians)   
                    
                    plt.show()
                    
                    
if __name__ == "__main__":
    
          oscgen = OscillatorGenerator()
          
          neff = 1.6
          
          gamma = 4*10
          
          gammapower = 13
          
          centralEnergy = 3.25
          
          minWavelength = 200
          
          maxWavelength = 600
          
          wvlResolution = 0.01
          
          go = 10
          
          gopower = 14
          
          materialName = 'LCE3.25neff1.6Goe14Ga4e13'
          
          #oscgen.generateLorentzianIsotropic(neff, gamma, gammapower, centralEnergy, go, gopower, minWavelength, maxWavelength, wvlResolution, materialName)
          
          neffX = neff
          
          neffY = neff
          
          neffZ = neff
          
          gammaX = gamma
          
          gammapowerX = gammapower
          
          centralEnergyX = centralEnergy
          
          goX = go
          
          gopowerX = gopower
          
          LorentzianY = ['Lorentzian',[neffY, gammaX, gammapowerX, centralEnergyX, goX, gopowerX]]
          
          CauchyX = ['Cauchy',[neffX]]
          
          CauchyZ = ['Cauchy',[neffZ]]
          
          oscgen.generateBiaxial(CauchyX, LorentzianY, CauchyZ, minWavelength, maxWavelength, wvlResolution, materialName)
          
          Lorentzian2 = ['Lorentzian',[neffY, gammaX, gammapowerX, centralEnergyX, goX, gopowerX]]
          
          Lorentzian3 = ['Lorentzian',[neffY, gammaX, gammapowerX, centralEnergyX, goX, gopowerX]]
          
          #oscgen.threeLorentziansVisibility(LorentzianY, LorentzianY, LorentzianY)
          
    
   
