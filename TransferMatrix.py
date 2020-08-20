# Author: Florian Le Roux
# -*- coding: utf-8 -*-

from ctypes import *
import numpy as np
import tempfile
import re
import os
import math
import time
import sys
import TransferMatrixGUI
import AddLayerPopUp
import PostProcessPopUp
import plotPopUp
from CalculationInfo import CalculationInfo
from FitInfo import FitInfo
from operatorTM import operatorTM
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import QObject, QSize, QThread, pyqtSignal, pyqtSlot, QRectF, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QLabel, QFileDialog
from plotData import plotData
from coupledOscillatorModel import coupledOscillators
import pickle
import matplotlib.pylab as plt

class TransferMatrix(TransferMatrixGUI.mainGUI):

    """TransferMatrix"""

    polarizationTE = 'TE'
    polarizationTM = 'TM'
    cavityFolder = 'C:\\Users\\leroux\\Google Drive\\Research\\MyPapers\\Aligned Cavities\\Tools\\TMM\\PostCalibration\\IdealCavities'

    ## Signals definitions for Qt threading ##

    sigUpdate = pyqtSignal(CalculationInfo)
    sigTriggerCalculation = pyqtSignal()
    sigUpdateFit = pyqtSignal(FitInfo)
    sigUpdateFitName = pyqtSignal(str)
    sigUpdatePolarizationTm = pyqtSignal(bool)
    sigTriggerFit = pyqtSignal()
    sigPlot = pyqtSignal(plotData,str, str, bool, float, float, float, float, bool, float, str) # send data computed for updating the graph

    def __init__(self,MainWindow):

        """Take GUI and initialize threads use."""

        super().__init__(MainWindow)

        self.__threads = []

        self.fitThreadName  = ''

        self.plotThreadName = ''

        self.currentHeight = 0

        self.structure = []

        self.params = {}  # for storing parameters

        self.Log = MainWindow.findChild(QTextEdit,"Log")

        self.layerPopUp = None

        #record text in the designer

        self.thicknessText = []
        self.layerText = []

        #record layers in the designer

        self.layerAdded = []

        # list all materials

        self.materials = []

        self.tmm_thread = [] 
        self.tmm_threadName = 'ToBeDefined'

        for root, dirs, files in os.walk("."):  
            for filename in files:
                if "Materials" in root:
                    self.materials.append((os.path.splitext(filename)[0]))  

        self.postProcessingCorrection = []

        for root, dirs, files in os.walk('C:\\Users\\leroux\\Google Drive\\Research\\MyPapers\\Aligned Cavities\\Tools\\TMM\\PostCalibration\\IdealCavities'):

            for dirname in dirs:

                if dirname is not 'H': 

                    if dirname is not 'V':

                        self.postProcessingCorrection.append(str(dirname + '\\H'))
                        self.postProcessingCorrection.append(str(dirname + '\\V'))

        # fit variables from GUI

        self.dataFileToFit = ''      
        self.nbOfLevels = ''
        self.nbOfResonances = 0
        self.Resonances = []
        self.lbO10 = 0
        self.ubO10 = 0
        self.lbO20 = 0
        self.ubO20 = 0
        self.lbneff = 0
        self.ubneff = 0
        self.lbE0 = 0
        self.ubE0 = 0

        self.setupConnections()

    def setupConnections(self):

        self.addLayerButton.clicked.connect(self.openAddLayerPopUp) 
        self.deleteLayerButton.clicked.connect(self.deleteTopLayer)
        self.clearDesignButton.clicked.connect(self.clearAll)
        self.calculateButton.clicked.connect(self.calculate)
        self.perfomFittingButton.clicked.connect(self.fitData)
        self.openDataFile.clicked.connect(self.openDataFileDialog)
        self.postCorrectionButton.clicked.connect(self.postProcessingPopUp)

        self.__threads = []
        plotThread = QThread()
        plotThread.setObjectName('plot_thread')
        self.plotThreadName = plotThread.objectName
        plotWorker = PlotWorker()
        plotWorker.moveToThread(plotThread)
        plotWorker.sig_msg.connect(self.react)
        self.sigPlot.connect(plotWorker.plotOrRefresh)

        plotThread.start()
        self.__threads.append((plotThread,plotWorker))          

    def openAddLayerPopUp(self):

        self.layerPopUp = AddLayerPopUp.AddLayerPopUp(self.materials) 
        self.layerPopUp.pushButton.clicked.connect(self.addLayerFromPopUp)

    def postProcessingPopUp(self):

        self.postProcessPopUp = PostProcessPopUp.PostProcessPopUp(self.postProcessingCorrection)
        self.postProcessPopUp.pushButton.clicked.connect(self.applypostProcessing)

    def applypostProcessing(self):

        self.posCorrectionText.setText(self.postProcessPopUp.cavityComboBox.currentText())
        self.postProcessPopUp.close()

    def addLayerFromPopUp(self):
        self.addLayer(self.layerPopUp.materialComboBox.currentText(),float(self.layerPopUp.thicknessPrompt.toPlainText()))

    def addLayer(self,LayerName:str,Thickness:float):

        self.layerAdded.append(self.Scenes.addRect(QRectF(0,-30 + self.currentHeight,200,30)))

        newLayerText = self.Scenes.addText(LayerName)        
        newLayerText.setPos(80,-30 + self.currentHeight)        
        self.layerText.append(newLayerText)

        textForThickness = str(Thickness) + 'nm'
        newThicknessText = self.Scenes.addText(textForThickness)
        newThicknessText.setPos(220,-30 + self.currentHeight)       
        self.thicknessText.append(newThicknessText)

        self.currentHeight = self.currentHeight - 30
        self.structure.append([LayerName,Thickness]) 

    def deleteTopLayer(self):

        if self.structure != []:

            lastLayer = self.structure.pop()        
            self.Scenes.removeItem(self.thicknessText.pop())
            self.Scenes.removeItem(self.layerAdded.pop())
            self.Scenes.removeItem(self.layerText.pop())

            self.currentHeight = self.currentHeight + 30

        else:

            self.Log.append("Nothing to delete")

    def clearAll(self):

        if self.structure == []:

            self.Log.append('The design is already empty')

        while self.structure != []:

            self.deleteTopLayer()

    def readPolarization(self):

        if self.sPolarCheck.isChecked():

            return self.polarizationTE

        if self.pPolarCheck.isChecked():

            return self.polarizationTM

    def readEnergy(self):

        if self.inEnergyCheck.isChecked():

            return True

        else:

            return False

    def calculate(self):

        ZminContent = self.ZminPrompt.toPlainText()

        ZmaxContent = self.ZmaxPrompt.toPlainText()

        if ZminContent == 'a':

            Zmin = Z.min()

        else:

            Zmin = float(ZminContent)

        if ZmaxContent == 'a':

            Zmax = Z.max()

        else:

            Zmax = float(ZmaxContent)

        tmm_threadExists = False      

        for threadAndWorker in self.__threads:

            thread, worker = threadAndWorker

            if thread.objectName == self.tmm_threadName:

                #print('I have found this thread')

                tmm_thread = thread

                tmm_worker = worker

                tmm_threadExists = True                

        if tmm_threadExists is False:

            self.azimAngles = self.formAzimAngles(self.minPhiAngle.toPlainText(),self.maxPhiAngle.toPlainText(),self.stepPhiAnglePrompt.toPlainText())
            calculationInfo = CalculationInfo(self.TCheck.isChecked(),self.minAngle.toPlainText(), self.maxAngle.toPlainText(), self.stepAnglePrompt.toPlainText(), self.minWavelength.toPlainText(), self.maxWavelength.toPlainText(), self.stepWvlPrompt.toPlainText(), self.structure, self.readPolarization(), self.azimAngles,self.readEnergy(), Zmin, Zmax)
            calculationThread = CalculationQThread(calculationInfo)
            calculationThread.setObjectName('tmm_thread')
            self.tmm_threadName = calculationThread.objectName
            calculationWorker = CalculationWorker()
            calculationWorker.moveToThread(calculationThread)    
            calculationThread.sigCalculation.connect(calculationWorker.performCalculation)

            self.sigUpdate.connect(calculationThread.updateCalculationInfo)
            self.sigTriggerCalculation.connect(calculationThread.triggerCalculation)

            calculationWorker.sig_msg.connect(self.react)
            calculationThread.sig_msg.connect(self.react)

            calculationThread.start()
            self.sigTriggerCalculation.emit()
            self.__threads.append((calculationThread, calculationWorker))

            plotThread, plotWorker = self.__threads[0]
            calculationWorker.sig_dataFit.connect(plotWorker.plotOrRefresh)
            calculationWorker.sig_azimPlot.connect(plotWorker.plotOffsetYAzim)
            calculationWorker.sig_azimPlotWithContrib.connect(plotWorker.plotOffsetYAzimWithContrib)

        else:

            self.azimAngles = self.formAzimAngles(self.minPhiAngle.toPlainText(),self.maxPhiAngle.toPlainText(),self.stepPhiAnglePrompt.toPlainText())
            self.sigUpdate.emit(CalculationInfo(self.TCheck.isChecked(),self.minAngle.toPlainText(), self.maxAngle.toPlainText(), self.stepAnglePrompt.toPlainText(), self.minWavelength.toPlainText(), self.maxWavelength.toPlainText(), self.stepWvlPrompt.toPlainText(), self.structure, self.readPolarization(), self.azimAngles,self.readEnergy(), Zmin, Zmax))
            self.sigTriggerCalculation.emit()

    def formAzimAngles(self, minPhiAngle, maxPhiAngle, stepPhiAngle):

        numberOfAngles = (float(maxPhiAngle) - float(minPhiAngle))/float(stepPhiAngle) + 1

        azimAngles = np.linspace(float(minPhiAngle), float(maxPhiAngle) , int(numberOfAngles))

        return azimAngles

    def openDataFileDialog(self):

        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():

            if self.dataFileToFit is not '':
                self.dataFileToFit = ''

            result = dlg.selectedFiles()  
            self.dataFileToFit = result[0]

        with open(self.dataFileToFit,'rb') as f:
            packed = pickle.load(f)

            X = packed[0]
            Y = packed[1]
            Z = packed[2] 

        #before messing around with the name, will save the original name
        self.dataFileToFitOriginal = self.dataFileToFit

        binSize = int(self.binPrompt.toPlainText())

        self.dataFilePrefix = self.dataFileToFit[:-9]

        self.forFitOrderName = self.dataFilePrefix[:-7]

        lastPosition = self.forFitOrderName.rfind('/')

        self.forFitOrderName = self.forFitOrderName[int(lastPosition+1):]

        #print('my order name is {}'.format(self.forFitOrderName))

        self.dataFileToFit = str(self.dataFilePrefix + '\\dataBin{}.txt'.format(binSize))

        orderName = str('PreviewFor' + 'dataBin{}'.format(binSize))        

        if binSize > 1:

            if os.path.exists(self.dataFileToFit):

                with open(self.dataFileToFit, 'rb') as f:

                    packed = pickle.load(f)

                    X = packed[0]
                    Y = packed[1]
                    Z = packed[2]  

                    Xbinned, Ybinned, Zbinned =  X, Y, Z

            else:

                Xbinned, Ybinned, Zbinned = self.binFile(binSize,X,Y,Z)

                with open(self.dataFileToFit, 'wb') as f:

                    packedData = Xbinned, Ybinned, Zbinned
                    pickle.dump(packedData, f)         

        else:

            Xbinned, Ybinned, Zbinned =  X, Y, Z        

        self.correctionText = self.posCorrectionText.text()   
        posCorrection = self.posCorrectionText.text() 

        if len(posCorrection) > 1:

            polaForCorrection = posCorrection[-1]    
            posCorrection = str(posCorrection[:-2] + polaForCorrection)            

            self.dataFilePrefix = self.dataFileToFit[:-4]

            #the dataFileToFit will now be the processed file 

            self.dataFileToFit = str(self.dataFilePrefix + 'ProcessedWth{}.txt'.format(posCorrection))   

            if os.path.exists(self.dataFileToFit):

                with open(self.dataFileToFit, 'rb') as f:

                    packed = pickle.load(f)

                    X = packed[0]
                    Y = packed[1]
                    Z = packed[2]  

                    Xbinned, Ybinned, Zbinned =  X, Y, Z            
            else:

                Xbinned, Ybinned, Zbinned = self.PostProcess(Xbinned, Ybinned, Zbinned)          

                with open(self.dataFileToFit, 'wb') as f:

                    packedData = Xbinned, Ybinned, Zbinned
                    pickle.dump(packedData, f)         

        fitData = plotData(Xbinned, Ybinned, Zbinned)

        self.Log.append('The file: {} will be fitted.'.format(self.dataFileToFit))
        self.Log.append('Please confirm parameters using Preview.')

        ZminContent = self.ZminPrompt.toPlainText()

        ZmaxContent = self.ZmaxPrompt.toPlainText()

        if ZminContent == 'a':

            Zmin = Z.min()

        else:

            Zmin = float(ZminContent)

        if ZmaxContent == 'a':

            Zmax = Z.max()

        else:

            Zmax = float(ZmaxContent)

            ZminContent = self.ZminPrompt.toPlainText()

            ZmaxContent = self.ZmaxPrompt.toPlainText()

            if ZminContent == 'a':

                Zmin = Z.min()

            else:

                Zmin = float(ZminContent)

            if ZmaxContent == 'a':

                Zmax = Z.max()

            else:

                Zmax = float(ZmaxContent) 

        EminContent = self.EminPrompt.toPlainText()

        EmaxContent = self.EmaxPrompt.toPlainText()

        if EminContent == 'a':

            Emin = Y.min()

        else:

            Emin = float(EminContent)

        if EmaxContent == 'a':

            Emax = Y.max()

        else:

            Emax = float(EmaxContent) 

        colormap = self.cMapPrompt.toPlainText()

        normalizeBy = 1.0

        if self.PLCheck.isChecked():

            isPL = True

            if self.NormalizePL.toPlainText() != '1.0':

                normalizeBy = float(self.NormalizePL.toPlainText())   

        if self.PLCheck.isChecked() == False:

            isPL = False

        self.sigPlot.emit(fitData, self.PolarizationE0Prompt.toPlainText(), orderName, True, Emin, Emax, Zmin, Zmax, isPL, normalizeBy, colormap)

    def binFile(self, binSize, X, Y, Z):

        #X remains untouched

        Xbinned = X

        #Y gets binned (energy or wavelength)

        Ybinned = self.binaction1D(binSize, Y)

        #Z gets binned

        numberOfColumns = Z.shape[1]

        #print('number of Z columns is {}'.format(numberOfColumns))

        Zbinned = self.binaction2D(binSize, numberOfColumns,  Z)

        self.spectraEFolder = str(self.dataFilePrefix[:-6] + 'SpectraE')

        return Xbinned, Ybinned, Zbinned

    def binaction1D(self, binSize, toBinarray):

        #only bin columns

        binSize = int(binSize)

        sizeYbinned = int((toBinarray.size - math.fmod(toBinarray.size, binSize))/binSize)

        sizeY = toBinarray.size

        #print(sizeY)

        #print(sizeYbinned)

        #print(toBinarray)

        Ybinned = np.zeros(sizeYbinned)

        isNotFull = True

        indices = np.linspace(0,binSize-1,binSize)

        for idx, element in enumerate(Ybinned):

            indices = np.linspace(idx * binSize, idx * binSize + 1, binSize)

            #for idxInd, element in enumerate(indices):

                #print('currentbinpack is:{}'.format(element))

            currentAvg = 0

            for idxI, element in enumerate(indices):

                currentAvg = currentAvg + toBinarray[int(element)]

                #print('currentbinningAvg is {}'.format(currentAvg))

            currentAvg = currentAvg/binSize

            Ybinned[idx] = currentAvg

            #print('bin final size is:{}'.format(Ybinned.size))

        return Ybinned

    def binaction2D(self, binSize, numberOfColumns, toBinarray):

        nbOfRows = toBinarray.shape[0]

        sizeZbinnedRows = int((nbOfRows - math.fmod(nbOfRows, binSize))/binSize)

        #print('number of binned Z rows is {}'.format(sizeZbinnedRows))

        Zbinned = np.zeros((sizeZbinnedRows,numberOfColumns))

        i = 0

        while i < numberOfColumns:

            Zbinned[:,i] = self.binaction1D(binSize, toBinarray[:,i])

            #print('Currently binning column {}'.format(i))

            i = i + 1

        return Zbinned        

    def PostProcess(self, X, Y, Z):

        self.refFolder = str(self.dataFilePrefix[:-8] + '\\Ref')

        #print('Looking for Ref in :{}'.format(self.refFolder))

        self.pathToCavity = str((self.cavityFolder) + '\\' + self.correctionText)

        #print('Looking for Cavity in :{}'.format(self.pathToCavity))

        rangeComparison = np.genfromtxt(str(self.pathToCavity + '\\Range.csv'), delimiter=",")

        #print('Looking for Comparison Range in :{}'.format(rangeComparison))

        lowerBoundForAverage = rangeComparison[0]

        #print('Lower Bound for Average is: {}'.format(lowerBoundForAverage))

        upperBoundForAverage = rangeComparison[1]

        #print('Upper Bound for Average is: {}'.format(upperBoundForAverage))

        #the bounds below are inverted since Y is in energy

        lowerBoundOnExperimental, upperBoundOnExperimental = self.findExperimentalBounds(lowerBoundForAverage, upperBoundForAverage, Y)

        #print('LowerBoundOnExperimental is: {} and UpperBoundOnExperimental is: {}'.format(lowerBoundOnExperimental, upperBoundOnExperimental))

        self.isRangeDecided = False

        self.isRangeExpDecided = False

        correctedZ = np.zeros_like(Z)

        #print('Attempting Full Correction Loop')

        for idx, angle in enumerate(X):

            currentColumn = Z[:,idx]

            correctedZ[:,idx] = self.compareRefMeasAndIdeal(angle, Y, currentColumn, lowerBoundForAverage, upperBoundForAverage, lowerBoundOnExperimental, upperBoundOnExperimental)

        return X, Y, correctedZ    

    def compareRefMeasAndIdeal(self, angle, Y, currentZ, lowerBoundForAverage, upperBoundForAverage, lowerBoundOnExperimental, upperBoundOnExperimental):

        idealCavity = np.genfromtxt(str(self.pathToCavity + '\\{}.csv'.format(angle)), delimiter=",")

        #form the correction ratio (average over the range taking half nm steps)

        wvlmin = idealCavity[:,0].min()

        #print('The wavelength min is:{}'.format(wvlmin))

        if self.isRangeDecided is not True:

            lwrIdx = int((lowerBoundForAverage-wvlmin.min())*2)
            upprIdx = int((upperBoundForAverage-wvlmin.min())*2)
            self.rangeProbed = np.linspace(lwrIdx,upprIdx,(upprIdx-lwrIdx)+1)

            #for element in (self.rangeProbed):

                #print('rangeProbed element:{}'.format(idealCavity[int(element),0]))    

        ratioAvg = 0

        for idx, indice in enumerate(self.rangeProbed): 

            ratioAvg = ratioAvg + idealCavity[int(indice),1]

        ratioAvg = ratioAvg/(self.rangeProbed.size)

        if self.isRangeExpDecided is not True:

            self.rangeExp = np.linspace(upperBoundOnExperimental, lowerBoundOnExperimental, (lowerBoundOnExperimental-upperBoundOnExperimental) + 1)

            #for element in (self.rangeExp):

                #print('rangeExpDecided element:{}'.format(Y[int(element)]))            

        ratioAvgExp = 0

        for idx, indice in enumerate(self.rangeExp): 

            ratioAvgExp = ratioAvgExp + currentZ[int(indice)]

        ratioAvgExp = ratioAvgExp/(self.rangeExp.size) 

        #find correction ratio

        correctionRatio = ratioAvg/ratioAvgExp

        #print('The Correction ratio is:{}'.format(correctionRatio))

        #apply the ratio to the currentColumn

        for idx, element in enumerate(currentZ):

            currentZ[idx] = currentZ[idx] * correctionRatio

        return currentZ

    def findExperimentalBounds(self, lowerboundForAverage, upperBoundForAverage, energiesOrderedIncreasing):

        lowerboundExp = 1

        upperboundExp = 1

        upperBoundHasBeenFound = False

        lowerBoundHasBeenFound = False

        for idx, element in enumerate(energiesOrderedIncreasing):

            if ((1239.82/element) <= upperBoundForAverage) and (upperBoundHasBeenFound is False):

                upperboundExp = idx

                upperBoundHasBeenFound = True

            if ((upperboundExp > 1) and ((1239.82/element) <= lowerboundForAverage)):

                lowerboundExp = idx - 1

                return lowerboundExp, upperboundExp

        #print('FAILURE')              

    def fitData(self):

        self.Resonances = [] 

        if self.OnelevelCheck.isChecked():

            self.nbOfResonances = 1
            self.Resonances.append(float(self.w1Prompt.toPlainText()))

        if self.TwolevelCheck.isChecked():

            self.nbOfResonances = 2
            self.Resonances.append(float(self.w1Prompt.toPlainText()))
            self.Resonances.append(float(self.w2Prompt.toPlainText()))

        self.lbLP = float(self.lbLPPrompt.toPlainText())
        self.ubLP = float(self.ubLPPrompt.toPlainText())
        self.lbMP = float(self.lbMPPrompt.toPlainText())
        self.ubMP = float(self.ubMPPrompt.toPlainText())
        self.lbUP = float(self.lbUPPrompt.toPlainText())
        self.ubUP = float(self.ubUPPrompt.toPlainText())        
        self.lbO10 = float(self.lbO10Prompt.toPlainText())
        self.ubO10 = float(self.ubO10Prompt.toPlainText())
        self.lbO20 = float(self.lbO20Prompt.toPlainText())
        self.ubO20 = float(self.ubO20Prompt.toPlainText())
        self.lbneff = float(self.lbneffPrompt.toPlainText())
        self.ubneff = float(self.ubneffPrompt.toPlainText())
        self.lbE0 = float(self.lbE0Prompt.toPlainText())
        self.ubE0 = float(self.ubE0Prompt.toPlainText())
        self.Emin = float(self.EminPrompt.toPlainText())
        self.Emax = float(self.EmaxPrompt.toPlainText())
        Zmin = float(self.ZminPrompt.toPlainText())
        Zmax = float(self.ZmaxPrompt.toPlainText())

        colormap = self.cMapPrompt.toPlainText()

        self.polarizationFit = self.PolarizationE0Prompt.toPlainText()

        lowerBounds = []
        upperBounds = []

        if self.nbOfResonances == 1:

            lowerBounds.append(self.lbLP)
            lowerBounds.append(-1)
            lowerBounds.append(self.lbUP)
            lowerBounds.append(self.lbO10)
            lowerBounds.append(-1)
            lowerBounds.append(self.lbneff)
            lowerBounds.append(self.lbE0)

            upperBounds.append(self.ubLP)
            upperBounds.append(-1)
            upperBounds.append(self.ubUP)
            upperBounds.append(self.ubO10)
            upperBounds.append(-1)
            upperBounds.append(self.ubneff)
            upperBounds.append(self.ubE0)

        if self.nbOfResonances == 2:

            lowerBounds.append(self.lbLP)
            lowerBounds.append(self.lbMP)
            lowerBounds.append(self.lbUP)
            lowerBounds.append(self.lbO10)
            lowerBounds.append(self.lbO20)
            lowerBounds.append(self.lbneff)
            lowerBounds.append(self.lbE0)

            upperBounds.append(self.ubLP)
            upperBounds.append(self.ubMP)
            upperBounds.append(self.ubUP)
            upperBounds.append(self.ubO10)
            upperBounds.append(self.ubO20)
            upperBounds.append(self.ubneff)
            upperBounds.append(self.ubE0)

        #print('I try to open: {}'.format(self.dataFileToFit))

        #print('If I can not find it I try to open: {}'.format(self.dataFileToFitOriginal))

        if os.path.exists(self.dataFileToFit):

            fitInfo = FitInfo(self.dataFileToFit, self.polarizationFit, self.nbOfResonances, self.Resonances, lowerBounds, upperBounds, self.Emin, self.Emax, Zmin, Zmax, colormap)

        else:

            fitInfo = FitInfo(self.dataFileToFitOriginal, self.polarizationFit, self.nbOfResonances, self.Resonances, lowerBounds, upperBounds, self.Emin, self.Emax, Zmin, Zmax, colormap)

        if self.tmCheck.isChecked():

            self.polarizationTM = True

        else:

            self.polarizationTM = False

        fitThreadExists = False

        for threadAndWorker in self.__threads:

            thread, worker = threadAndWorker

            if thread.objectName == self.fitThreadName:

                fit_thread, fit_worker = thread, worker

                fitThreadExists = True

            if thread.objectName == self.plotThreadName:

                plot_thread, plotWorker = thread, worker

        if fitThreadExists is False:

            fit_thread = []

        if fit_thread == []:

            fitThread = FitQThread(fitInfo)
            fitThread.setObjectName('fit_thread')
            self.fitThreadName = fitThread.objectName
            fitWorker = FitWorker()
            fitWorker.moveToThread(fitThread)    
            fitThread.sigFit.connect(fitWorker.performFit)

            self.sigUpdateFit.connect(fitThread.updateFitInfo)
            self.sigUpdateFitName.connect(fitThread.updateOrderName)
            self.sigUpdatePolarizationTm.connect(fitThread.updatePolarizationTM)
            self.sigTriggerFit.connect(fitThread.triggerFit)

            fitWorker.sig_msg.connect(self.react)
            fitThread.sig_msg.connect(self.react)

            fitThread.start()
            self.__threads.append((fitThread, fitWorker))

            fitWorker.sig_dataFit.connect(plotWorker.plotOrRefreshFit)

        else:

            self.sigUpdateFit.emit(fitInfo)

        self.sigUpdateFitName.emit(self.forFitOrderName)
        self.sigUpdatePolarizationTm.emit(self.polarizationTM)
        self.sigTriggerFit.emit()

    @pyqtSlot(str)   
    def react(self,string: str):

        self.Log.append(string)    

class CalculationQThread(QThread):

    sigCalculation = pyqtSignal(CalculationInfo)
    sig_msg = pyqtSignal(str)  # message to be shown to user

    def __init__(self, CalculationInfo):

        super().__init__()

        self.calculationInfo = CalculationInfo

    @pyqtSlot(CalculationInfo)
    def updateCalculationInfo(self,newCalculationInfo):

        self.calculationInfo = newCalculationInfo

    @pyqtSlot()    
    def triggerCalculation(self):

        self.sigCalculation.emit(self.calculationInfo)

class FitQThread(QThread):

    sigFit = pyqtSignal(FitInfo,str,bool)
    sig_msg = pyqtSignal(str)  # message to be shown to user

    def __init__(self, FitInfo):

        super().__init__()

        self.FitInfo = FitInfo
        self.orderName = 'default'
        self.polarizationtTM = False

    @pyqtSlot(FitInfo)
    def updateFitInfo(self,newFitInfo):

        self.FitInfo = newFitInfo

    @pyqtSlot(str)
    def updateOrderName(self,orderName):

        self.orderName = orderName

    @pyqtSlot(bool)
    def updatePolarizationTM(self,polarizationTM):

        self.polarizationTM = polarizationTM    

    @pyqtSlot()    
    def triggerFit(self):

        self.sigFit.emit(self.FitInfo, self.orderName, self.polarizationTM)


class CalculationWorker(QObject):

    sig_done = pyqtSignal(str)  # 
    sig_msg = pyqtSignal(str)  # message to be shown to user
    sig_dataFit = pyqtSignal(plotData,str,str,bool,float,float,float,float,bool, float, str)   # send data computed for updating the graph
    sig_azimPlot = pyqtSignal(plotData,float,float,float,float, float, str) #send data for creating the Y offset graph
    sig_azimPlotWithContrib = pyqtSignal(plotData, plotData, plotData, float,float,float,float, float, str) #send data for creating the Y offset graph

    def __init__(self):

        super().__init__()

    @pyqtSlot(CalculationInfo)    
    def performCalculation(self,calculationInfo):

        self.sig_msg.emit('Calculation Order received for {}'.format(os.path.splitext(calculationInfo.calculationOrderName)[0]))     

        temporaryZforAzimuthalStudy = []
        temporarycontribZxforAzimuthalStudy = []
        temporarycontribZyforAzimuthalStudy = []

        for azimAngle in calculationInfo.azimuthalAngles:

            tempCalculationInfo = CalculationInfo(calculationInfo.intransmission, calculationInfo.angleMin, calculationInfo.angleMax, calculationInfo.angleStep, calculationInfo.wavelengthMin, calculationInfo.wavelengthMax, calculationInfo.wavelengthStep, calculationInfo.structure, calculationInfo.polarization, azimAngle, calculationInfo.inEnergy, calculationInfo.Zmin, calculationInfo.Zmax) 

            local_operator = operatorTM(tempCalculationInfo)             

            if float(azimAngle) == 0.0:

                if calculationInfo.intransmission:

                    X, Y, Zs, Zp = local_operator.calculateTsAndTpForAllAngles() 

                    if calculationInfo.polarization == 'TE':

                        Z = Zs

                    if calculationInfo.polarization == 'TM':

                        Z = Zp

                    if np.size(calculationInfo.azimuthalAngles) == 1:

                        self.sig_dataFit.emit(plotData(X,Y,Z), calculationInfo.polarization,os.path.splitext(calculationInfo.calculationOrderName)[0], True, calculationInfo.EMin, calculationInfo.EMax, calculationInfo.Zmin, calculationInfo.Zmax, False, 1.0, 'RdBu')

                    else:

                        temporaryZforAzimuthalStudy.append(np.real(Z)) 
                        temporarycontribZxforAzimuthalStudy.append(np.zeros_like(np.real(Z)))
                        temporarycontribZyforAzimuthalStudy.append(np.real(Z))

                else:

                    X, Y, Zs, Zp = local_operator.calculateRsAndRpForAllAngles()

                    if calculationInfo.polarization == 'TE':

                        Z = Zs

                    if calculationInfo.polarization == 'TM':

                        Z = Zp

                    if np.size(calculationInfo.azimuthalAngles) == 1:

                        self.sig_dataFit.emit(plotData(X,Y,Z), calculationInfo.polarization,os.path.splitext(calculationInfo.calculationOrderName)[0], True, calculationInfo.EMin, calculationInfo.EMax, calculationInfo.Zmin, calculationInfo.Zmax, False, 1.0, 'RdBu')

                    else:

                        temporaryZforAzimuthalStudy.append(Z)                    


                self.sig_msg.emit('{} at Phi = {} was succesfully computed'.format(tempCalculationInfo.calculationOrderName,str(azimAngle))) 

            if float(azimAngle) > 0.0:

                #print('attempting OP with Phi {}'.format(azimAngle))

                if calculationInfo.intransmission:

                    X, Y, Zs, zss, zsp, zsx, zsy = local_operator.calculateTsAndTpForAllAngles()

                    if np.size(calculationInfo.azimuthalAngles) == 1:

                        self.sig_dataFit.emit(plotData(X,Y,Zs), calculationInfo.polarization,os.path.splitext(calculationInfo.calculationOrderName)[0], True, calculationInfo.EMin, calculationInfo.EMax, calculationInfo.Zmin, calculationInfo.Zmax, False, 1.0, 'RdBu')            

                    else:
                        
                        #print(zsx)
                        #print(zsy)
                        
                        #plt.plot(Y,zsx)
                        #plt.plot(Y,zsy)
                        #plt.show()
                        
                        temporaryZforAzimuthalStudy.append(Zs) 
                        temporarycontribZxforAzimuthalStudy.append(zsx)
                        temporarycontribZyforAzimuthalStudy.append(zsy)                        

                else:

                    X, Y, Zs = local_operator.calculateRsAndRpForAllAngles()

                    if np.size(calculationInfo.azimuthalAngles) == 1:

                        self.sig_dataFit.emit(plotData(X,Y,Zs), calculationInfo.polarization,os.path.splitext(calculationInfo.calculationOrderName)[0], True, calculationInfo.EMin, calculationInfo.EMax, calculationInfo.Zmin, calculationInfo.Zmax, False, 1.0, 'RdBu')            

                    else:

                        temporaryZforAzimuthalStudy.append(Zs)

                self.sig_msg.emit('{} at Phi = {} was succesfully computed'.format(tempCalculationInfo.calculationOrderName,str(azimAngle)))

        if np.size(calculationInfo.azimuthalAngles) > 1:

            if calculationInfo.intransmission is False:

                self.sig_azimPlot.emit(plotData(Y,calculationInfo.azimuthalAngles,temporaryZforAzimuthalStudy), calculationInfo.EMin, calculationInfo.EMax, calculationInfo.Zmin, calculationInfo.Zmax, 1.0, 'RdBu')

            else:

                self.sig_azimPlotWithContrib.emit(plotData(Y,calculationInfo.azimuthalAngles,temporaryZforAzimuthalStudy), plotData(Y,calculationInfo.azimuthalAngles,temporarycontribZxforAzimuthalStudy), plotData(Y,calculationInfo.azimuthalAngles,temporarycontribZyforAzimuthalStudy), calculationInfo.EMin, calculationInfo.EMax, calculationInfo.Zmin, calculationInfo.Zmax, 1.0, 'RdBu')

class FitWorker(QObject):

    sig_done = pyqtSignal(str)  # 
    sig_msg = pyqtSignal(str)  # message to be shown to user
    sig_dataFit = pyqtSignal(plotData, list, list, list, list, str,str,float,float,float,float,bool,float,str) # send data computed for updating the graph

    def __init__(self):

        super().__init__()

    @pyqtSlot(FitInfo,str,bool)    
    def performFit(self,fitInfo,orderName, polarizationTM):

        self.sig_msg.emit('Fit Order received for {}'.format(os.path.splitext(fitInfo.fitOrderName)[0]))

        #if os.path.exists(\\ComputedFittings):

            #self.sig_msg.emit('Previous Fit found')

            #with open(self.dataFileToFit, 'rb') as f:

                #packed = pickle.load(f)

                #X = packed[0]
                #Y = packed[1]
                #Z = packed[2]  

                #Xbinned, Ybinned, Zbinned =  X, Y, Z  

        #the following boolean is only used with simulated files to separate TE and TM
        if polarizationTM:

            with open(fitInfo.fitOrderName,'rb') as f:
                packed = pickle.load(f)

                X = packed[0]
                Y = packed[1]
                Z = packed[3]

                fitData = plotData(X,Y,Z)

        else:

            with open(fitInfo.fitOrderName,'rb') as f:
                packed = pickle.load(f)

                X = packed[0]
                Y = packed[1]
                Z = packed[2]

                fitData = plotData(X,Y,Z)            


        coupled = coupledOscillators(orderName, fitData, fitInfo.polarization, fitInfo.nbOfResonances, fitInfo.Resonances, fitInfo.lowerBounds, fitInfo.upperBounds)

        RabiEnergies, neff, E0, polaritonsExp, polaritonsFitted, excitonLines, cavityModesFitted  = coupled.fitData()

        if fitInfo.nbOfResonances == 1:

            O0 = RabiEnergies[0]

            #Display the Fitted Values in the Log

            str1 = 'O0 = {} eV\n'.format(RabiEnergies[0])
            str2 = 'neff = {}\n'.format(neff)
            str3 = 'E0 = {} eV\n'.format(E0)
            L = str(str1 + str2 + str3) 

            self.sig_msg.emit('Fitting complete, the fitting parameters obtained are:')
            self.sig_msg.emit(L)

        if fitInfo.nbOfResonances == 2:

            O10 = RabiEnergies[0]
            O20 = RabiEnergies[1]

            #Display the Fitted Values in the Log

            str1 = 'O10 = {} eV\n'.format(RabiEnergies[0])
            str2 = 'O20 = {} eV\n'.format(RabiEnergies[1])
            str3 = 'neff = {}\n'.format(neff)
            str4 = 'E0 = {} eV\n'.format(E0)
            L = str(str1 + str2 + str3 + str4)

            self.sig_msg.emit('Fitting complete, the fitting parameters obtained are:')
            self.sig_msg.emit(L)

        self.sig_dataFit.emit(plotData(X,Y,Z), polaritonsFitted, polaritonsExp, excitonLines, cavityModesFitted, fitInfo.polarization, orderName, fitInfo.Emin, fitInfo.Emax, fitInfo.Zmin, fitInfo.Zmax, False, 1.0, fitInfo.colormap)

class PlotWorker(QObject):

    sig_msg = pyqtSignal(str)  # message to be shown to user

    def __init__(self):  

        super().__init__()
        self.plotPopUp = plotPopUp.PlotPopUp()

    @pyqtSlot(plotData,str,str,bool,float,float,float,float,bool,float,str)    
    def plotOrRefresh(self,DataToPlot:plotData,polarization:str,orderName:str,inEnergy:bool, Ymin, Ymax, Zmin, Zmax, isPL, normalizeBy, colormap): 

        if inEnergy:

            self.plotPopUp.plotSurf(DataToPlot,False,False,False, False,polarization,str(orderName+'E'), inEnergy, Ymin, Ymax, Zmin, Zmax, isPL, normalizeBy, colormap)

        else:          

            self.plotPopUp.plotSurf(DataToPlot,False,False,False, False,polarization,orderName, inEnergy, Ymin, Ymax, Zmin, Zmax, isPL, normalizeBy, colormap)            

        self.sig_msg.emit('{} was saved in .eps, .pdf, .png formats'.format(orderName))

    @pyqtSlot(plotData,float,float,float,float,float,str)

    def plotOffsetYAzim(self,DataToPlot:plotData, Ymin, Ymax, Zmin, Zmax, normalizeBy, color): 

        self.plotPopUp.plotYOffset(DataToPlot, Ymin, Ymax, Zmin, Zmax, normalizeBy, color)

    @pyqtSlot(plotData,plotData,plotData,float,float,float,float,float,str)

    def plotOffsetYAzimWithContrib(self,DataToPlot:plotData,DataToPlotX:plotData,DataToPlotY:plotData, Ymin, Ymax, Zmin, Zmax, normalizeBy, color): 

        self.plotPopUp.plotYOffsetWithContributions(DataToPlot, DataToPlotX, DataToPlotY, Ymin, Ymax, Zmin, Zmax, normalizeBy, color)        

    @pyqtSlot(plotData, list, list, list, list, str,str,float,float,float,float,bool, float, str)

    def plotOrRefreshFit(self, DataToPlot:plotData, polaritonsFitted, polaritonsExp, cavityModesFitted, excitonLines, polarization:str, orderName:str, Emin:float, Emax:float, Zmin: float, Zmax: float,isPL: bool, normalizeBy: float, colormap: str):

        #this will not plot the polaritons Exp as the False is entered. You can put polaritonsExp instead to take a look at the minima
        self.plotPopUp.plotSurf(DataToPlot, polaritonsFitted, False, cavityModesFitted, excitonLines, polarization, orderName, True, Emin, Emax, Zmin, Zmax, isPL, 1.0, colormap)    

if __name__ == "__main__":

    app = QApplication(sys.argv)

    TMGUI = QMainWindow()
    ui = TransferMatrix(TMGUI)
    TMGUI.show()

    sys.exit(app.exec_())


