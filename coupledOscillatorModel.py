# -*- coding: utf-8 -*-

import sys
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
from os import walk

from scipy.optimize import  curve_fit

import numpy as np

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from matplotlib.backends.qt_compat import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import (FigureCanvasQT, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import pickle

import matlab.engine

class coupledOscillators(QObject):

	polarizationTE = 'TE'
	polarizationTM = 'TM'    

	def __init__(self, orderName, fitData, polarization, nbOfResonances, Resonances, lowerBounds, upperBounds):

		super().__init__()

		self.eng = matlab.engine.start_matlab()

		self.expValues = fitData.Z

		self.angles = fitData.X

		self.energies = fitData.Y

		self.nbOfResonances = nbOfResonances

		if nbOfResonances >= 1:

			self.w1 = Resonances[0]

		if nbOfResonances >= 2:

			self.w2 = Resonances[1]

		self.orderName = orderName		

		#bounds are to be entered as follows:

		# lb/ub [0] is for the lower polariton minima search
		# lb/ub [1] is for the middle polariton minima search
		# lb/ub [2] is for the upper polariton minima search
		# according to the model, put -1 when unused
		# lb/ub [3] is for the fitting, bounds on Omega 1
		# lb/ub [4] is for the fitting, bounds on Omega 2
		# lb/ub [5] is for the fitting, bounds on neff
		# lb/ub [6] is for the fitting, bounds on E0

		self.lowerBounds = lowerBounds

		self.upperBounds = upperBounds

		self.cavityModesFitted = []

		self.excitonLines = []

		self.polaritonsExp = []

		self.polaritonsFitted = []

	def extract2Minima(self):

		lowerPolariton = self.findMinima(self.lowerBounds[0],self.upperBounds[0])

		upperPolariton = self.findMinima(self.lowerBounds[2],self.upperBounds[2])

		self.polaritonsExp.append(lowerPolariton)

		self.polaritonsExp.append(upperPolariton)

	def extract3Minima(self):

		lowerPolariton = self.findMinima(self.lowerBounds[0],self.upperBounds[0])

		middlePolariton = self.findMinima(self.lowerBounds[1], self.upperBounds[1])

		upperPolariton = self.findMinima(self.lowerBounds[2],self.upperBounds[2])

		self.polaritonsExp.append(lowerPolariton)

		self.polaritonsExp.append(middlePolariton)

		self.polaritonsExp.append(upperPolariton)

	def findMinima(self,lowerBound,upperBound):

		minimaList = np.zeros_like(self.angles)

		boundedValues, startIndex = self.findValuesWithLowerAndUpperBound(lowerBound,upperBound)

		expValuesBounded = self.expValues[startIndex:(startIndex+len(boundedValues)),:]

		for i in range(0,expValuesBounded[1,:].size):

			currentValues = expValuesBounded[:,i]

			minimum = 2

			for p, ivalue in enumerate(currentValues):

				if ivalue <= minimum:

					minimum = ivalue
					minindex = p

			minimaList[i] = boundedValues[minindex]   

		return minimaList

	def findValuesWithLowerAndUpperBound(self, lowerBound, upperBound):

		boundedValues = []

		hasfoundStart = False

		startidx = 0

		for idx,value in enumerate(self.energies):

			if value > lowerBound and value < upperBound:

				if hasfoundStart != True:

					startidx = idx

					hasfoundStart = True

				boundedValues.append(value)

		return boundedValues, startidx

	def lineUp1Resonance(self, angles, wex, O0, neff, E0):

		lastdim = int(angles.size/2)

		realangles = angles[0:lastdim]

		lowerPolariton, upperPolariton = self.formPolaritons1Resonance(realangles, wex, O0, neff, E0)

		return np.append(lowerPolariton, upperPolariton)

	def lineUp2Resonances(self, angles, wex1, wex2, O10, O20, neff, E0):

		lastdim = int(angles.size/2)

		realangles = angles[0:lastdim]

		lowerPolariton, middlePolariton, upperPolariton = self.formPolaritons2Resonances(realangles, wex1, wex2, O10, O20, neff, E0)

		return np.append(lowerPolariton, upperPolariton)

	def fitDataOneResonance(self):

		self.extract2Minima()

		experimentalLowerPolariton = self.polaritonsExp[0]

		experimentalUpperPolariton = self.polaritonsExp[1]

		exlowerPolaritonMatlab = matlab.double(experimentalLowerPolariton.tolist())

		exupperPolaritonMatlab = matlab.double(experimentalUpperPolariton.tolist())

		anglesAsList = self.angles.tolist()

		anglesForMatlab = matlab.double(anglesAsList)		

		try:

			p_init = [self.w1, (self.lowerBounds[3]+self.upperBounds[3])/2, (self.lowerBounds[5]+self.upperBounds[5])/2, (self.lowerBounds[6]+self.upperBounds[6])/2]

			p_initForMatlab = matlab.double(p_init)

			PackedResult = self.eng.Fitting1Resonance(anglesForMatlab, exlowerPolaritonMatlab, exupperPolaritonMatlab, self.w1, self.lowerBounds[3], self.upperBounds[3], self.lowerBounds[5], self.upperBounds[5], self.lowerBounds[6], self.upperBounds[6], p_initForMatlab)

			result = PackedResult[0]

			O0 = result[1]

			neff = result[2]

			E0 = result[3]

		except RuntimeError:

			print('Matlab Engine Failure')

		lowerPolariton, upperPolariton = self.formPolaritons1Resonance(self.angles, self.w1, O0, neff, E0)

		self.polaritonsFitted.append(lowerPolariton)

		self.polaritonsFitted.append(upperPolariton)        

		cavityMode = self.photonDispersionModel(self.angles, E0, neff)

		self.cavityModesFitted.append(cavityMode)

		excitonLine = self.formExcitonLine(self.angles,self.w1)

		self.excitonLines.append(excitonLine)

		#plt.plot(self.angles,lowerPolariton, c='Red')
		#plt.plot(self.angles,upperPolariton, c='Blue')
		#plt.plot(self.angles,cavityMode, c='Green')
		#plt.plot(self.angles,excitonLine, c='Orange')

		#plt.show()

		RabiEnergies = []
		RabiEnergies.append(O0)

		return RabiEnergies, neff, E0, self.polaritonsExp, self.polaritonsFitted, self.excitonLines, self.cavityModesFitted

	def fitDataTwoResonances(self):

		self.extract3Minima()

		experimentalLowerPolariton = self.polaritonsExp[0]

		experimentalMiddlePolariton = self.polaritonsExp[1]

		experimentalUpperPolariton = self.polaritonsExp[2]

		exlowerPolaritonMatlab = matlab.double(experimentalLowerPolariton.tolist())

		exmiddlePolaritonMatlab = matlab.double(experimentalMiddlePolariton.tolist())

		exupperPolaritonMatlab = matlab.double(experimentalUpperPolariton.tolist())

		anglesAsList = self.angles.tolist()

		anglesForMatlab = matlab.double(anglesAsList)		

		try:

			p_init = [self.w1, self.w2,(self.lowerBounds[3]+self.upperBounds[3])/2, (self.lowerBounds[4]+self.upperBounds[4])/2, (self.lowerBounds[5]+self.upperBounds[5])/2, (self.lowerBounds[6]+self.upperBounds[6])/2]

			p_initForMatlab = matlab.double(p_init)

			PackedResult = self.eng.Fitting2Resonance(anglesForMatlab, exlowerPolaritonMatlab, exmiddlePolaritonMatlab, exupperPolaritonMatlab, self.w1, self.w2, self.lowerBounds[3], self.upperBounds[3], self.lowerBounds[4], self.upperBounds[4], self.lowerBounds[5], self.upperBounds[5], self.lowerBounds[6], self.upperBounds[6], p_initForMatlab)

			result = PackedResult[0]

			O10 = result[2]

			O20 = result[3]

			neff = result[4]

			E0 = result[5]

		except RuntimeError:

			print('Matlab Engine Failure')

		lowerPolariton, middlePolariton, upperPolariton = self.formPolaritons2Resonances(self.angles, self.w1, self.w2, O10, O20, neff, E0)

		self.polaritonsFitted.append(lowerPolariton)

		self.polaritonsFitted.append(middlePolariton)

		self.polaritonsFitted.append(upperPolariton)        

		cavityMode = self.photonDispersionModel(self.angles, E0, neff)

		self.cavityModesFitted.append(cavityMode)

		excitonLine1 = self.formExcitonLine(self.angles,self.w1)
		excitonLine2 = self.formExcitonLine(self.angles,self.w2)

		self.excitonLines.append(excitonLine1)
		self.excitonLines.append(excitonLine2)

		#plt.plot(self.angles,lowerPolariton, c='Red')
		#plt.plot(self.angles,middlePolariton, c ='Black')
		#plt.plot(self.angles,upperPolariton, c='Blue')
		#plt.plot(self.angles,cavityMode, c='Green')
		#plt.plot(self.angles,excitonLine1, c='Orange')
		#plt.plot(self.angles,excitonLine2, c='Orange')

		#plt.show()

		RabiEnergies = []

		RabiEnergies.append(O10)
		RabiEnergies.append(O20)

		return RabiEnergies, neff, E0, self.polaritonsExp, self.polaritonsFitted, self.excitonLines, self.cavityModesFitted

	def fitData(self):


		if self.nbOfResonances == 1:

			RabiEnergies, neff, E0, polaritonsExp, polaritonsFitted, excitonLines, cavityModesFitted = self.fitDataOneResonance()

			packedData = self.angles, self.w1, RabiEnergies, neff, E0, polaritonsExp, polaritonsFitted, excitonLines, cavityModesFitted

			RabiDisplay = round(RabiEnergies[0],3)

			with open('ComputedFittings\\{}Rabi1is{}eV'.format(self.orderName,RabiDisplay), 'wb') as f:
				pickle.dump(packedData,f)

			#Save the Fitted Values

			FittedParamFile = open('ComputedFittings\\{}Rabi1is{}eV.txt'.format(self.orderName,RabiDisplay),"w+") 
			str1 = 'O0 = {} eV\n'.format(RabiEnergies[0])
			str2 = 'neff = {}\n'.format(neff)
			str3 = 'E0 = {} eV\n'.format(E0)
			L = [str1, str2, str3] 
			FittedParamFile.writelines(L)

			return RabiEnergies, neff, E0, polaritonsExp, polaritonsFitted, excitonLines, cavityModesFitted

		if self.nbOfResonances == 2:

			RabiEnergies, neff, E0, self.polaritonsExp, self.polaritonsFitted, self.excitonLines, self.cavityModesFitted = self.fitDataTwoResonances()

			O10 = RabiEnergies[0]
			O20 = RabiEnergies[1]

			packedData = self.angles, self.w1, self.w2, O10, O20, neff, E0, self.polaritonsExp, self.polaritonsFitted, self.excitonLines, self.cavityModesFitted

			O10Display = round(O10,3)
			O20Display = round(O20,3)

			with open('ComputedFittings\{}Rabi1is{}eV&Rabi2is{}eV'.format(self.orderName,O10Display,O20Display), 'wb') as f:
				pickle.dump(packedData,f)

			#Save the Fitted Values

			FittedParamFile = open('ComputedFittings\\{}Rabi1is{}eV&Rabi2is{}eV.txt'.format(self.orderName,O10Display,O20Display),"w+") 
			str1 = 'O10 = {} eV\n'.format(RabiEnergies[0])
			str2 = 'O20 = {} eV\n'.format(RabiEnergies[1])
			str3 = 'neff = {}\n'.format(neff)
			str4 = 'E0 = {} eV\n'.format(E0)
			L = [str1, str2, str3, str4] 
			FittedParamFile.writelines(L)				

			return RabiEnergies, neff, E0, self.polaritonsExp, self.polaritonsFitted, self.excitonLines, self.cavityModesFitted


	def formPolaritons1Resonance(self, angles, wex, O0, neff, E0):

		lowerPolariton = []

		upperPolariton = []

		x = []

		x.append(wex)
		x.append(O0)
		x.append(neff)
		x.append(E0)

		anglesAsList = angles.tolist()

		xForMatlab = matlab.double(x)
		anglesForMatlab = matlab.double(anglesAsList)

		result = self.eng.OneResonanceEngine(xForMatlab,anglesForMatlab)

		lowerPolariton, upperPolariton = self.unpackMatlabResult2Polaritons(result)
		
		lowerPolaritonAsNp = np.asarray(lowerPolariton)
		
		upperPolaritonAsNp = np.asarray(upperPolariton)

		return lowerPolaritonAsNp, upperPolaritonAsNp	

	def formPolaritons2Resonances(self, angles, w1, w2, O10, O20, neff, E0):

		lowerPolariton = []

		middlePolariton = []

		upperPolariton = []

		x = []

		x.append(w1)
		x.append(w2)
		x.append(O10)
		x.append(O20)
		x.append(neff)
		x.append(E0)

		anglesAsList = angles.tolist()

		xForMatlab = matlab.double(x)
		anglesForMatlab = matlab.double(anglesAsList)

		result = self.eng.TwoResonanceEngine(xForMatlab,anglesForMatlab)

		lowerPolariton, middlePolariton, upperPolariton = self.unpackMatlabResult3Polaritons(result)

		return lowerPolariton, middlePolariton, upperPolariton	


	def photonDispersionModel(self,angles, E0, neff):

		wcavAll = np.zeros_like(angles)

		for iangle,angle in enumerate(angles):

			wcavAll[iangle] = E0*np.sqrt(1/(1-(np.square(np.sin((2*np.pi)*angles[iangle]/360)))/(np.square(neff))))    

		return wcavAll

	def formExcitonLine(self, angles, Eex):

		wEx = np.zeros_like(angles)

		for iangle,angle in enumerate(angles):

			wEx[iangle] = Eex   

		return wEx 
	
	def plotTestDataOneResonance(self, w1, O10, neff, E0):	

		lowerPolariton, upperPolariton = self.formPolaritons1Resonance(self.angles, w1, O10, neff, E0)

		self.polaritonsFitted.append(lowerPolariton)

		self.polaritonsFitted.append(upperPolariton)        

		cavityMode = self.photonDispersionModel(self.angles, E0, neff)

		self.cavityModesFitted.append(cavityMode)

		excitonLine1 = self.formExcitonLine(self.angles,w1)

		self.excitonLines.append(excitonLine1)

		plt.plot(self.angles,lowerPolariton, c='Red')
		plt.plot(self.angles,upperPolariton, c='Blue')
		plt.plot(self.angles,cavityMode, c='Green')
		plt.plot(self.angles,excitonLine1, c='Orange')

		plt.show()	

	def plotTestDataTwoResonances(self, w1, w2, O10, O20, neff, E0):	

		lowerPolariton, middlePolariton, upperPolariton = self.formPolaritons2Resonances(self.angles, w1, w2, O10, O20, neff, E0)

		self.polaritonsFitted.append(lowerPolariton)

		self.polaritonsFitted.append(middlePolariton)

		self.polaritonsFitted.append(upperPolariton)        

		cavityMode = self.photonDispersionModel(self.angles, E0, neff)

		self.cavityModesFitted.append(cavityMode)

		excitonLine1 = self.formExcitonLine(self.angles,w1)
		excitonLine2 = self.formExcitonLine(self.angles,w2)

		self.excitonLines.append(excitonLine1)
		self.excitonLines.append(excitonLine2)

		plt.plot(self.angles,lowerPolariton, c='Red')
		plt.plot(self.angles,middlePolariton, c ='Black')
		plt.plot(self.angles,upperPolariton, c='Blue')
		plt.plot(self.angles,cavityMode, c='Green')
		plt.plot(self.angles,excitonLine1, c='Orange')
		plt.plot(self.angles,excitonLine2, c='Orange')

		plt.show()

	def unpackMatlabResult3Polaritons(self,result):

		lowerPolariton = []
		middlePolariton = []
		upperPolariton = []

		for triplet in result:

			lowerPolariton.append(triplet[0])
			middlePolariton.append(triplet[1])
			upperPolariton.append(triplet[2])

		return lowerPolariton, middlePolariton, upperPolariton

	def unpackMatlabResult2Polaritons(self,result):

		lowerPolariton = []
		middlePolariton = []
		upperPolariton = []

		for doublet in result:

			lowerPolariton.append(doublet[0])
			upperPolariton.append(doublet[1])

		return lowerPolariton, upperPolariton		


if __name__ == "__main__":

	#fileName = 'C:\\Users\\leroux\\Google Drive\\Research\\MyPapers\\Aligned Cavities\\Project Data\\FullDataSets\\TestDataSet\\Pickle\\dataBin8ProcessedWthPFONAV.txt'

	fileName = 'C:\\Users\\leroux\\Google Drive\\Research\\MyPapers\\Aligned Cavities\\Analysis\\Polariton Fitting - Coupled Oscillators\\F8BT NA TE S1Exp12\\Pickle\\dataBin8ProcessedWthF8BTNAV.txt'
	
	with open(fileName,'rb') as f:
		packed = pickle.load(f)

		X = packed[0]
		Y = packed[1]
		Z = packed[2]

		fitData = plotData(X,Y,Z)

	#with open('ComputedSimulations\Al100.0AlignedPFOBeta80.0Al20.01070122060010E.txt','rb') as f:
		#packed = pickle.load(f)

		#X = packed[0]
		#Y = packed[1]
		#Zs = packed[2]
		#Zp = packed[3]  

		#fitData = plotData(X,Y,Zs,Zp)		


	#bounds are to be entered as follows:

	# lb/ub [0] is for the lower polariton minima search
	# lb/ub [1] is for the middle polariton minima search
	# lb/ub [2] is for the upper polariton minima search
	# according to the model, put -1 when unused
	# lb/ub [3] is for the fitting, bounds on Omega 1
	# lb/ub [4] is for the fitting, bounds on Omega 2
	# lb/ub [5] is for the fitting, bounds on neff
	# lb/ub [6] is for the fitting, bounds on E0

	#Example for beta phase cavity

	#lb = [2.5 , 2.87, 3.25, 0.8, 0.05, 1.5, 2.8]

	#ub = [2.87, 3.25, 4.8, 1.2, 0.3, 1.7, 3.5]

	#Example for glassy phase cavity

	#lb = [2.5 , -1, 3.25, 0.8, -1, 1.5, 2.8]

	#ub = [3.25, -1, 4.8, 1.2, -1, 1.7, 3.5]

	#lb = [2.5 , -1, 3.25, 0.8, -1, 1.5, 2.8]

	#ub = [3.25, -1, 4.8, 1.2, -1, 1.7, 3.5]

	#me = coupledOscillators('S3Exp12TE',fitData,'TE', 1, [3.25], lb, ub)

	#print('Eex:{},Rabi:{},neff:{},E0:{}'.format(Eex, ERabi, neff, E0))

	#RabiEnergies, neff, E0, polaritonsExp, polaritonsFitted, excitonLines, cavityModesFitted = me.fitData()

	#me.plotTestDataOneResonance( 3.25, RabiEnergies[0], neff, E0)
	
	#Test 2 resonances
	
	#Example for F8BT
	
	lb = [2.0 , 2.7, 3.7, 0.4, 0.4, 1.5, 2.0]

	ub = [2.5, 3.3, 4.2, 1.0, 1.0, 1.8, 4.0]
	
	me = coupledOscillators('S1Exp12TE',fitData,'TE', 2, [3.80, 2.68], lb, ub)
	
	RabiEnergies, neff, E0, polaritonsExp, polaritonsFitted, excitonLines, cavityModesFitted = me.fitData()

	me.plotTestDataTwoResonances(3.80, 2.68, RabiEnergies[0], RabiEnergies[1], neff, E0)


