# -*- coding: utf-8 -*-

import sys
import os
import time
import resources
from plotData import plotData

# matplotlib inline plots
import matplotlib.pylab as plt
import matplotlib.pyplot as pyplt
from matplotlib import colors
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib import cm

import numpy as np

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from matplotlib.backends.qt_compat import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import (FigureCanvasQT, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import pickle

import seaborn as sns
import pandas as pd

import coupledOscillatorModel as com

from mpl_toolkits.mplot3d import Axes3D


class PlotPopUp(QObject):

    polarizationTE = 'TE'
    polarizationTM = 'TM'
    
    def __init__(self):
        
        super().__init__() 
        self.CurvesHaveBeenAdded = False
        
    def plotLineAtAngle(self,X,Y,Z,polarizationName, angle):
        
        nearest_angle = X.flat[np.abs(X - angle).argmin()]
        AnglePosition = (X.tolist()).index(nearest_angle)
        
        valuesAtAngle = []
        
        for iy,y in enumerate(Y):
            
            valuesAtAngle.append(Z[iy][AnglePosition])
        
        self.plotLine(Y, valuesAtAngle, polarizationName) 
              
    def plotSurf(self, DataBackground, PolaritonsFitted, PolaritonsExp, CavityModes, ExcitonLines, polarizationName, orderName, inEnergy, XMin, XMax, Zmin, Zmax, isPL, normalizeBy, colormap):
        
        X = DataBackground.X
        Y = DataBackground.Y
        Z = DataBackground.Z
        
        if normalizeBy != 1.0:
            
            self.normalizeByValue(Z,normalizeBy)
                    
        f_size = 10
        
        if PolaritonsFitted is not False:
            
            self.CurvesHaveBeenAdded = True
            
            for polariton in PolaritonsFitted:
                
                plt.plot(X, polariton,'--', c='Black')                        
                   
        if CavityModes is not False:
            
            self.CurvesHaveBeenAdded = True
            
            for cavityMode in CavityModes:
                
                plt.plot(X, cavityMode, c='White') 
                
        if ExcitonLines is not False:
            
            self.CurvesHaveBeenAdded = True
            
            for excitonLine in ExcitonLines:
                
                plt.plot(X, excitonLine, c='White')  
        
        if inEnergy:
                       
            surf = plt.pcolormesh(X, Y, Z, cmap= colormap, vmin= Zmin, vmax= Zmax)
            
            plt.axis([X.min(), X.max(), XMin, XMax])
            
            cb = plt.colorbar(surf, aspect = 10)          
            
            plt.ylabel('Energy (eV)', fontsize = 20) 
            
        else:
            
            surf = plt.pcolormesh(X, Y, Z, cmap= colormap, vmin= Zmin, vmax= Zmax)
            
            plt.axis([X.min(), X.max(), XMin, XMax])
            
            cb = plt.colorbar(surf, aspect=10)
            
            plt.ylabel('Wavelength (nm)', fontsize = 20)
            
        plt.xlabel('Angles (°)', fontsize = 20)
        
        ax = plt.gca()
        
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(14) 
            
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(14)
        
        if isPL is False:
            
            cb.ax.tick_params(labelsize=14)
            cb.set_label(str('{} Reflectivity'.format(polarizationName)), fontsize = 20)
            
        else:
            
            cb.ax.tick_params(labelsize=14)
            cb.set_label('Normalized Intensity (a.u.)', fontsize = 20)            
        
        if PolaritonsExp is not False:
            
            self.CurvesHaveBeenAdded = True
            
            for polaritonExp in PolaritonsExp:
                
                currentscatter = plt.scatter(X, polaritonExp, s = 6, c = 'Grey')
        
        if self.CurvesHaveBeenAdded is False:
            
            if inEnergy:
                suffix = 'E'
        
                plt.savefig(str('ComputedSimulations\{}{}{}.eps' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True) 
                plt.savefig(str('ComputedSimulations\{}{}{}.pdf' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True) 
                plt.savefig(str('ComputedSimulations\{}{}{}.png' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True, dpi = 600)
        
            else:
                suffix = 'W'
            
                plt.savefig(str('ComputedSimulations\{}{}{}.eps' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True) 
                plt.savefig(str('ComputedSimulations\{}{}{}.pdf' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True) 
                plt.savefig(str('ComputedSimulations\{}{}{}.png' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True, dpi = 600)
        else:
            
            if inEnergy:
                suffix = 'E'
        
                plt.savefig(str('ComputedSimulations\{}{}{}Mod.eps' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True) 
                plt.savefig(str('ComputedSimulations\{}{}{}Mod.pdf' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True) 
                plt.savefig(str('ComputedSimulations\{}{}{}Mod.png' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True, dpi = 600)
        
            else:
                suffix = 'W'
            
                plt.savefig(str('ComputedSimulations\{}{}{}Mod.eps' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True) 
                plt.savefig(str('ComputedSimulations\{}{}{}Mod.pdf' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True) 
                plt.savefig(str('ComputedSimulations\{}{}{}Mod.png' .format(orderName,suffix,polarizationName)), bbox_inches='tight', transparent = True, dpi = 600)
            
            
        plt.show()
        
    def plotLine(self,X,Y,polarizationName):
    
        colorscale = cm.RdBu
        line = pyplt.plot(X,Y)
        
        pyplt.show()
        
        
    def normalizeByValue(self, Z, normalizeBy):
        
        for cidx, column in enumerate(Z[0,:]):
            
            for vidx, values in enumerate(Z[:,cidx]):
                
                Z[vidx,cidx] = values/normalizeBy   
                
        return Z
    
    def plotYOffset(self, plotData, Ymin, Ymax, Zmin, Zmax, normalizeBy, color):
        
        #X is energy, Z intensities corresponding to the azimuthal Angles
        x = plotData.X
        z = plotData.Z
        
        np.savetxt('C:\\Users\\leroux\\Desktop\\Controversy Article\\Curves\\CurrentX.csv', x, delimiter=',')
        
        counter = 0
        
        currentMax = 0
        
        printcounter = 0
        
        for zcolumn in z:
            
            np.savetxt('C:\\Users\\leroux\\Desktop\\Controversy Article\\Curves\\CurrentY{}.csv'.format(printcounter), zcolumn, delimiter=',')
            printcounter = printcounter + 1            
            
            for zeltIdx, zelt in enumerate(zcolumn):
            
                zcolumn[zeltIdx] = zelt + counter
                
            plt.plot(x, zcolumn, color = 'black')
            
            if currentMax == 0:
                
                currentMax = np.max(zcolumn) * 0.75
            
            #counter = counter + 0.15
            counter = counter + currentMax
          
        #plt.xlim(3.10,3.40)  
        #plt.ylim(0.69, 1.85)
        plt.show()
        
    def plotYOffsetWithContributions(self, plotData, plotDataX, plotDataY, Ymin, Ymax, Zmin, Zmax, normalizeBy, color):
        
        #X is energy, Z intensities corresponding to the azimuthal Angles
        x = plotData.X
        z = plotData.Z
        
        zX = plotDataX.Z
        zY = plotDataY.Z
        
        zYcolumn = np.zeros_like(z[0])
        zSumCheck = np.zeros_like(z[0])
        
        counter = 0
        basecounter = 0
        
        currentMax = 0
        
        tickpositions = []
        
        tickpositions.append(0)
        
        printcounter = 0                  
        
        for zidx, zcolumn in enumerate(z):
            
            np.savetxt('C:\\Users\\leroux\\Desktop\\Controversy Article\\Curves\\CurrentYBT{}.csv'.format(printcounter), zcolumn, delimiter=',')          
            
            printcounter = printcounter + 1
            
            for zeltIdx, zelt in enumerate(zcolumn):
            
                zcolumn[zeltIdx] = zelt + counter
                
            plt.plot(x, zcolumn, color = 'black')
            
            if currentMax == 0:
                
                currentMax = np.max(zcolumn) * 1.25
                basecounter = currentMax

            counter = counter + currentMax
            
            tickpositions.append(counter)
            
        counter = 0
        
        printcounter = 0      
            
        for zXidx, zXcolumn in enumerate(zX):
            
            zYcolumn = zY[zXidx]
            
            np.savetxt('C:\\Users\\leroux\\Desktop\\Controversy Article\\Curves\\CurrentYXT{}.csv'.format(printcounter), zXcolumn, delimiter=',')          
            np.savetxt('C:\\Users\\leroux\\Desktop\\Controversy Article\\Curves\\CurrentYYT{}.csv'.format(printcounter), zYcolumn, delimiter=',') 
            
            printcounter = printcounter + 1            
            
            for zXeltIdx, zXelt in enumerate(zXcolumn):
            
                zXcolumn[zXeltIdx] = zXelt + counter 
                zYcolumn[zXeltIdx] = zYcolumn[zXeltIdx] + counter  
                zSumCheck[zXeltIdx] = zXcolumn[zXeltIdx] + zYcolumn[zXeltIdx] - counter
            
            plt.plot(x, zXcolumn, color = 'blue', linestyle='dashed')  
            plt.plot(x, zYcolumn, color = 'red', linestyle='dashed')  
            #plt.plot(x, zSumCheck, color = 'green', linestyle = 'dashed')
            
            counter = counter + basecounter
            
        print(tickpositions)
        
        plt.yticks(np.asarray(tickpositions))
          
        #plt.xlim(3.10,3.40)  
        #plt.ylim(0.69, 1.85)
        
        plt.show()
        
    
if __name__ == "__main__":
    
    popup = PlotPopUp()
    
    # Test 1 Resonance Glassy PFO
    
    #orderName = 'Al100.0PFO90.0Al30.01070121060010'
    
    #with open(str('ComputedSimulations\Al100.0PFO90.0Al30.01070121060010E'+'.txt'), 'rb') as f:
        #packed = pickle.load(f)

        #X = packed[0]
        #Ye = packed[1]
        #Zs = packed[2]
        #Zp = packed[3]                
     
    ##popup.plotSurf(plotData(X,Ye,Zs,Zp), False, False, False, False,'TE',orderName,True)     
    
    #fitData = plotData(X,Ye,Zs,Zp)
    
    #lb = [2.5 , -1, 3.25, 0.8, -1, 1.5, 2.8]

    #ub = [3.25, -1, 4.8, 1.2, -1, 1.7, 3.5]

    #co = com.coupledOscillators(orderName, fitData,'TE', 1, [3.25], lb, ub)
    
    #ERabi, neff, E0, polaritonsExp, polaritonsFitted, excitonLines, cavityModesFitted = co.fitData()
    
    #print('Rabi:{},neff:{},E0:{}'.format(ERabi, neff, E0))
    
    #popup.plotSurf(plotData(X,Ye,Zs,Zp), polaritonsFitted, polaritonsExp, cavityModesFitted, excitonLines,'TE',orderName,True, 2.5, 4.8)
    
    # Test 2 Resonances Beta PFO
    
    #orderName = 'Al100.0PFO15890.0Al25.01070121060010'
    
    #with open(str('ComputedSimulations\Al100.0PFO15890.0Al25.01070121060010E'+'.txt'), 'rb') as f:
        #packed = pickle.load(f)

        #X = packed[0]
        #Ye = packed[1]
        #Z = packed[2]
        
        ##pick TE
    
    #print(X.size)
    #print(Ye.size)            
    #print(Z.size)
    #fitData = plotData(X,Ye,Z)
    
    #lb = [2.0 , 2.84, 3.25, 0.7, 0.05, 1.5, 2.8]

    #ub = [2.84, 3.25, 4.8, 1.3, 0.3, 1.8, 3.5]

    #co = com.coupledOscillators(orderName, fitData,'TE', 2, [3.25, 2.84], lb, ub)
    
    #RabiEnergies, neff, E0, polaritonsExp, polaritonsFitted, excitonLines, cavityModesFitted = co.fitData()
    
    #print('Rabi1:{},Rabi2:{},neff:{},E0:{}'.format(RabiEnergies[0], RabiEnergies[1], neff, E0))
    
    #popup.plotSurf(plotData(X,Ye,Z), polaritonsFitted, polaritonsExp, cavityModesFitted, excitonLines,'TE',orderName,True, 2.5, 4.8)
    
    # Test PFO
    
    fileName = 'C:\\Users\\leroux\\Google Drive\\Research\\MyPapers\\Aligned Cavities\\Project Data\\FullDataSets\\TestDataSet\\Pickle\\dataBin8ProcessedWthPFONAV.txt'

    with open(fileName,'rb') as f:
        packed = pickle.load(f)

        X = packed[0]
        Y = packed[1]
        Z = packed[2]

        fitData = plotData(X,Y,Z)

    lb = [2.5 , -1, 3.25, 0.8, -1, 1.5, 2.8]

    ub = [3.25, -1, 4.8, 1.2, -1, 1.7, 3.5]

    me = com.coupledOscillators('S3Exp12TE',fitData,'TE', 1, [3.25], lb, ub)

    #print('Eex:{},Rabi:{},neff:{},E0:{}'.format(Eex, ERabi, neff, E0))

    RabiEnergies, neff, E0, polaritonsExp, polaritonsFitted, excitonLines, cavityModesFitted = me.fitData()
    
    popup.plotSurf(fitData, polaritonsFitted, False, cavityModesFitted, excitonLines,'TE', 'S3Exp12',True, 2.5, 4.5, 0.6, 0.95, 'RdBu')

    #me.plotTestDataOneResonance( 3.25, RabiEnergies[0], neff, E0)