# -*- coding: utf-8 -*-

import resources
import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal


class mainGUI(QtCore.QObject):
    
    def __init__(self, MainWindow):
        
        """Initialise mainwindow."""
        super().__init__()
        self.setupUi(MainWindow)
        
    def setupUi(self, MainWindow):
        
        MainWindow.setWindowIcon(QtGui.QIcon(":/TmIcon.png"));
        MainWindow.setWindowTitle("Analysis Algorithms")
        
        MainWindow.setFixedSize(1050, 1000)        
        
        font = QtGui.QFont()
        font.setPointSize(8)
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("border-color: rgb(206, 206, 206);")
        
        #Font for menu
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)        
        
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 685, 0))
        self.menuBar.setObjectName("menuBar")
        self.menuBar.setStyleSheet("background-color: rgb(245, 245, 245);")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuBar.setFont(font)
        self.menuFile.setObjectName("menuFile")    
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionClose)
        self.menuBar.addAction(self.menuFile.menuAction())       
        
        self.GraphicsViewDesign = QtWidgets.QGraphicsView(self.centralWidget)
        self.GraphicsViewDesign.setGeometry(QtCore.QRect(10, 10, 340, 400))
        self.GraphicsViewDesign.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.GraphicsViewDesign.setFrameShape(QtWidgets.QFrame.Panel)
        self.GraphicsViewDesign.setLineWidth(2)
        self.GraphicsViewDesign.setObjectName("GraphicsViewDesign") 
        self.GraphicsViewDesign.setAlignment(QtCore.Qt.AlignCenter)
        
        self.GraphicsViewDesign.show()
        self.Scenes = QtWidgets.QGraphicsScene(self.GraphicsViewDesign)
        self.GraphicsViewDesign.setScene(self.Scenes)
        
        
        #Font for substrate
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)               
        
        SubstrateText = self.Scenes.addText('Substrate',font)

        SubstrateRectangle = self.Scenes.addRect(QtCore.QRectF(0, 0, 200, 40))
        
        SubstrateText.setPos(50,5)
        SubstrateRectangle.setPos(0,0)
        
        self.currentHeight = 0
        self.structure = [{'Substrate',200,40,None}]
    
        self.frameDesigner = QtWidgets.QFrame(self.centralWidget)
        self.frameDesigner.setGeometry(QtCore.QRect(360, 10, 230, 400))
        self.frameDesigner.setAutoFillBackground(True)
        self.frameDesigner.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.frameDesigner.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameDesigner.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameDesigner.setLineWidth(2)
        self.frameDesigner.setObjectName("frameDesigner")
        
        self.DesignerLabel = QtWidgets.QLabel(self.frameDesigner)
        self.DesignerLabel.setFont(font)
        self.DesignerLabel.setGeometry(QtCore.QRect(80,-30,100,100))      
                
        self.frame = QtWidgets.QFrame(self.centralWidget)
        self.frame.setGeometry(QtCore.QRect(10, 425, 580, 230))
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(2)
        self.frame.setObjectName("frame")

        self.frameMicrocavity = QtWidgets.QFrame(self.centralWidget)
        self.frameMicrocavity.setGeometry(QtCore.QRect(605, 10, 430, 920))
        self.frameMicrocavity.setAutoFillBackground(True)
        self.frameMicrocavity.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.frameMicrocavity.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameMicrocavity.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMicrocavity.setLineWidth(2)
        self.frameMicrocavity.setObjectName("frameMicrocavity") 
        
        self.MicrocavityLabel = QtWidgets.QLabel(self.frameMicrocavity)
        self.MicrocavityLabel.setFont(font)
        self.MicrocavityLabel.setGeometry(QtCore.QRect(100,-30,300,100)) 
        
        fontCheckBoxes = font
        fontCheckBoxes.setBold(False)

        self.EminText = QtWidgets.QLabel(self.frameMicrocavity)
        self.EminText.setFont(font)
        self.EminText.setText('Emin (eV)')
        self.EminText.setGeometry(QtCore.QRect(20, 120, 300,100))
        
        self.EminPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.EminPrompt.setGeometry(QtCore.QRect(120, 155, 60, 30))            
        
        self.EmaxText = QtWidgets.QLabel(self.frameMicrocavity)
        self.EmaxText.setFont(font)
        self.EmaxText.setText('Emax (eV)')
        self.EmaxText.setGeometry(QtCore.QRect(200, 120, 300,100)) 
        
        self.EmaxPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.EmaxPrompt.setGeometry(QtCore.QRect(310, 155, 60, 30))         
        
        self.OnelevelText = QtWidgets.QLabel(self.frameMicrocavity)
        self.OnelevelText.setGeometry(QtCore.QRect(20,180,100,100))
        self.OnelevelText.setFont(fontCheckBoxes)
        self.OnelevelText.setObjectName("OnelevelText") 
        
        self.OnelevelCheck = QtWidgets.QCheckBox(self.frameMicrocavity)
        self.OnelevelCheck.setGeometry(QtCore.QRect(110,180,100,100))
        
        self.w1Text = QtWidgets.QLabel(self.frameMicrocavity)
        self.w1Text.setGeometry(QtCore.QRect(20,230,100,100))
        self.w1Text.setFont(fontCheckBoxes)
        self.w1Text.setObjectName("E1")
              
        self.w1Prompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.w1Prompt.setGeometry(QtCore.QRect(130,265,100,30))             
        
        self.w2Text = QtWidgets.QLabel(self.frameMicrocavity)
        self.w2Text.setGeometry(QtCore.QRect(20,280,100,100))
        self.w2Text.setFont(fontCheckBoxes)
        self.w2Text.setObjectName("E2")
        self.w2Text.setText('E2 (in eV)')
        
        self.w2Prompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.w2Prompt.setGeometry(QtCore.QRect(130,315,100,30))        
        
        self.lbO10Text = QtWidgets.QLabel(self.frameMicrocavity)
        self.lbO10Text.setGeometry(QtCore.QRect(20,330,150,100))
        self.lbO10Text.setFont(fontCheckBoxes)
        self.lbO10Text.setObjectName("lbO10")
        self.lbO10Text.setText('lbO10 (in eV)')
        
        self.lbO10Prompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.lbO10Prompt.setGeometry(QtCore.QRect(150,365,60,30))           
        
        self.ubO10Text = QtWidgets.QLabel(self.frameMicrocavity)
        self.ubO10Text.setGeometry(QtCore.QRect(230,330,150,100))
        self.ubO10Text.setFont(fontCheckBoxes)
        self.ubO10Text.setObjectName("ubO10")
        self.ubO10Text.setText('ubO10 (in eV)') 
        
        self.ubO10Prompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.ubO10Prompt.setGeometry(QtCore.QRect(360,365,60,30))        
        
        self.lbO20Text = QtWidgets.QLabel(self.frameMicrocavity)
        self.lbO20Text.setGeometry(QtCore.QRect(20,380,150,100))
        self.lbO20Text.setFont(fontCheckBoxes)
        self.lbO20Text.setObjectName("lbO20")
        self.lbO20Text.setText('lbO20 (in eV)')  
        
        self.lbO20Prompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.lbO20Prompt.setGeometry(QtCore.QRect(150,415,60,30))        
        
        self.ubO20Text = QtWidgets.QLabel(self.frameMicrocavity)
        self.ubO20Text.setGeometry(QtCore.QRect(230,385,150,100))
        self.ubO20Text.setFont(fontCheckBoxes)
        self.ubO20Text.setObjectName("ubO20")
        self.ubO20Text.setText('ubO20 (in eV)')
        
        self.ubO20Prompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.ubO20Prompt.setGeometry(QtCore.QRect(360,415,60,30)) 
        
        self.lbneffText = QtWidgets.QLabel(self.frameMicrocavity)
        self.lbneffText.setGeometry(QtCore.QRect(20,430,150,100))
        self.lbneffText.setFont(fontCheckBoxes)
        self.lbneffText.setObjectName("lbneff")
        self.lbneffText.setText('lbneff') 
        
        self.lbneffPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.lbneffPrompt.setGeometry(QtCore.QRect(150,465,60,30))         
        
        self.ubneffText = QtWidgets.QLabel(self.frameMicrocavity)
        self.ubneffText.setGeometry(QtCore.QRect(230,430,150,100))
        self.ubneffText.setFont(fontCheckBoxes)
        self.ubneffText.setObjectName("ubneff")
        self.ubneffText.setText('ubneff') 
        
        self.ubneffPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.ubneffPrompt.setGeometry(QtCore.QRect(360,465,60,30))  
        
        self.lbE0Text = QtWidgets.QLabel(self.frameMicrocavity)
        self.lbE0Text.setGeometry(QtCore.QRect(20,480,150,100))
        self.lbE0Text.setFont(fontCheckBoxes)
        self.lbE0Text.setObjectName("lbE0")
        self.lbE0Text.setText('lbE0')  
        
        self.lbE0Prompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.lbE0Prompt.setGeometry(QtCore.QRect(150,515,60,30)) 
        
        self.lbLPText = QtWidgets.QLabel(self.frameMicrocavity)
        self.lbLPText.setGeometry(QtCore.QRect(20,530,150,100))
        self.lbLPText.setFont(fontCheckBoxes)
        self.lbLPText.setObjectName("lbLP")
        self.lbLPText.setText('lbLP (in eV)')  
        
        self.lbLPPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.lbLPPrompt.setGeometry(QtCore.QRect(150,565,60,30))
        
        self.ubLPText = QtWidgets.QLabel(self.frameMicrocavity)
        self.ubLPText.setGeometry(QtCore.QRect(230,530,150,100))
        self.ubLPText.setFont(fontCheckBoxes)
        self.ubLPText.setObjectName("ubLP (in eV)")
        self.ubLPText.setText("ubLP (in eV)")  
        
        self.ubLPPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.ubLPPrompt.setGeometry(QtCore.QRect(360,565,60,30))   
        
        self.lbMPText = QtWidgets.QLabel(self.frameMicrocavity)
        self.lbMPText.setGeometry(QtCore.QRect(20,580,150,100))
        self.lbMPText.setFont(fontCheckBoxes)
        self.lbMPText.setObjectName("lbMP")
        self.lbMPText.setText('lbMP (in eV)')  
        
        self.lbMPPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.lbMPPrompt.setGeometry(QtCore.QRect(150,615,60,30))
        
        self.ubMPText = QtWidgets.QLabel(self.frameMicrocavity)
        self.ubMPText.setGeometry(QtCore.QRect(230,580,150,100))
        self.ubMPText.setFont(fontCheckBoxes)
        self.ubMPText.setObjectName("ubMP (in eV)")
        self.ubMPText.setText("ubMP (in eV)")  
        
        self.ubMPPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.ubMPPrompt.setGeometry(QtCore.QRect(360,615,60,30)) 
        
        self.lbuPText = QtWidgets.QLabel(self.frameMicrocavity)
        self.lbuPText.setGeometry(QtCore.QRect(20,630,150,100))
        self.lbuPText.setFont(fontCheckBoxes)
        self.lbuPText.setObjectName("lbUP")
        self.lbuPText.setText('lbUP (in eV)')  
        
        self.lbUPPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.lbUPPrompt.setGeometry(QtCore.QRect(150,665,60,30))
        
        self.ubUPText = QtWidgets.QLabel(self.frameMicrocavity)
        self.ubUPText.setGeometry(QtCore.QRect(230,630,150,100))
        self.ubUPText.setFont(fontCheckBoxes)
        self.ubUPText.setObjectName("ubUP (in eV)")
        self.ubUPText.setText("ubUP (in eV)")  
        
        self.ubUPPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.ubUPPrompt.setGeometry(QtCore.QRect(360,665,60,30)) 
        
        self.ZminText = QtWidgets.QLabel(self.frameMicrocavity)
        self.ZminText.setGeometry(QtCore.QRect(20,675,150,100))
        self.ZminText.setFont(fontCheckBoxes)
        self.ZminText.setObjectName("Z min")
        self.ZminText.setText("Z min")        
        
        self.ZminPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.ZminPrompt.setGeometry(QtCore.QRect(150,710,60,30))   
        
        self.ZmaxText = QtWidgets.QLabel(self.frameMicrocavity)
        self.ZmaxText.setGeometry(QtCore.QRect(230,675,150,100))
        self.ZmaxText.setFont(fontCheckBoxes)
        self.ZmaxText.setObjectName("Z max")
        self.ZmaxText.setText("Z max")  
        
        self.ZmaxPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.ZmaxPrompt.setGeometry(QtCore.QRect(360,710,60,30))                   
        
        self.PolarizationFitText = QtWidgets.QLabel(self.frameMicrocavity)
        self.PolarizationFitText.setGeometry(QtCore.QRect(20,730,150,100))
        self.PolarizationFitText.setFont(fontCheckBoxes)
        self.PolarizationFitText.setObjectName("Polarization")
        self.PolarizationFitText.setText('Polarization')  
        
        self.PolarizationE0Prompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.PolarizationE0Prompt.setGeometry(QtCore.QRect(150,765,60,30)) 
        
        self.cMapText = QtWidgets.QLabel(self.frameMicrocavity)
        self.cMapText.setGeometry(QtCore.QRect(230,730,150,100))
        self.cMapText.setFont(fontCheckBoxes)
        self.cMapText.setObjectName("CMap")
        self.cMapText.setText('CMap')  
        
        self.cMapPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.cMapPrompt.setGeometry(QtCore.QRect(360,765,60,30))         
        
        self.ubE0Text = QtWidgets.QLabel(self.frameMicrocavity)
        self.ubE0Text.setGeometry(QtCore.QRect(230,480,150,100))
        self.ubE0Text.setFont(fontCheckBoxes)
        self.ubE0Text.setObjectName("ubE0")
        self.ubE0Text.setText('ubE0')
        
        self.ubE0Prompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.ubE0Prompt.setGeometry(QtCore.QRect(360,515,60,30))  
                    
        self.TwolevelText = QtWidgets.QLabel(self.frameMicrocavity)
        self.TwolevelText.setGeometry(QtCore.QRect(150,180,150,100))
        self.TwolevelText.setFont(fontCheckBoxes)
        self.TwolevelText.setObjectName("TwolevelText") 
        
        self.TwolevelCheck = QtWidgets.QCheckBox(self.frameMicrocavity)
        self.TwolevelCheck.setGeometry(QtCore.QRect(230,180,150,100))
        
        self.ThreelevelText = QtWidgets.QLabel(self.frameMicrocavity)
        self.ThreelevelText.setGeometry(QtCore.QRect(270,180,150,100))
        self.ThreelevelText.setFont(fontCheckBoxes)
        self.ThreelevelText.setObjectName("ThreelevelText") 
        
        self.ThreelevelCheck = QtWidgets.QCheckBox(self.frameMicrocavity)
        self.ThreelevelCheck.setGeometry(QtCore.QRect(350,180,150,100))         
                  
        self.frameLog = QtWidgets.QFrame(self.centralWidget)
        self.frameLog.setGeometry(QtCore.QRect(10, 750, 580, 285))
        self.frameLog.setAutoFillBackground(True)
        self.frameLog.setStyleSheet("border-color: rgb(142, 231, 255);background-color: rgb(255, 255, 255);")
        self.frameLog.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameLog.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frameLog.setLineWidth(4)
        self.frameLog.setObjectName("frameLog")
        
        self.Log = QtWidgets.QTextEdit(self.frameLog)
        self.Log.setGeometry(QtCore.QRect(7, 7, 566, 180))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.Log.setFont(font)
        self.Log.setFrameStyle(0)
        self.Log.setObjectName("Log") 
        
        self.label = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        
        self.TransmissionText = QtWidgets.QLabel(self.frame)
        self.TransmissionText.setGeometry(QtCore.QRect(20, -30, 150, 100))        
        self.TransmissionText.setFont(font)
        self.TransmissionText.setObjectName("TransmissionText")
        
        self.TransmissionText.setText('Transmission')
        self.TCheck = QtWidgets.QCheckBox(self.frame)
        self.TCheck.setGeometry(QtCore.QRect(130, -30, 150, 100))
        self.TCheck.setChecked(True)
        self.TCheck.raise_()
        
        self.minText = QtWidgets.QLabel(self.frame)
        self.minText.setGeometry(QtCore.QRect(250, -30, 150, 100))        
        self.minText.setFont(font)
        self.minText.setObjectName("minText") 
        
        self.maxText = QtWidgets.QLabel(self.frame)
        self.maxText.setGeometry(QtCore.QRect(370, -30, 150, 100))        
        self.maxText.setFont(font)
        self.maxText.setObjectName("maxText") 
        
        self.stepText = QtWidgets.QLabel(self.frame)
        self.stepText.setGeometry(QtCore.QRect(490, -30, 150, 100))        
        self.stepText.setFont(font)
        self.stepText.setObjectName("stepText")  
        
        self.sPolarText = QtWidgets.QLabel(self.frame)
        self.sPolarText.setGeometry(QtCore.QRect(200,155,100,100))
        self.sPolarText.setFont(font)
        self.sPolarText.setObjectName("sPolarText")
        
        self.pPolarText = QtWidgets.QLabel(self.frame)
        self.pPolarText.setGeometry(QtCore.QRect(280,155,100,100))
        self.pPolarText.setFont(font)
        self.pPolarText.setObjectName("pPolarText") 
        
        self.sPolarCheck = QtWidgets.QCheckBox(self.frame)
        self.sPolarCheck.setGeometry(QtCore.QRect(220,155,100,100))
        self.sPolarCheck.setChecked(True)
        
        self.binText = QtWidgets.QLabel(self.frameMicrocavity)
        self.binText.setText('Bin:')
        self.binText.setGeometry(QtCore.QRect(280, 40, 220, 50))
        
        self.binPrompt = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.binPrompt.setGeometry(QtCore.QRect(320, 50, 30, 30)) 
        self.binPrompt.setText('8')    
        
        self.tmText = QtWidgets.QLabel(self.frameMicrocavity)
        self.tmText.setText('TM:')
        self.tmText.setGeometry(QtCore.QRect(280, 90, 220, 50))
        
        self.tmCheck = QtWidgets.QCheckBox(self.centralWidget)        
        self.tmCheck.setGeometry(QtCore.QRect(925, 75, 100, 100))   
        
        self.PLText = QtWidgets.QLabel(self.frameMicrocavity)
        self.PLText.setText('PL')
        self.PLText.setGeometry(QtCore.QRect(280, 250, 220, 50))
        
        self.PLCheck = QtWidgets.QCheckBox(self.frameMicrocavity)
        self.PLCheck.setGeometry(QtCore.QRect(320, 225, 100, 100))     
        self.PLCheck.raise_()
        
        self.NormalizePLLabel = QtWidgets.QLabel(self.frameMicrocavity)
        self.NormalizePLLabel.setGeometry(QtCore.QRect(260, 315, 80, 30)) 
        self.NormalizePLLabel.setText('NormBy')
        
        self.NormalizePL = QtWidgets.QTextEdit(self.frameMicrocavity)
        self.NormalizePL.setGeometry(QtCore.QRect(320, 315, 50, 30))
        self.NormalizePL.setText('1.0')
        
        self.pPolarCheck = QtWidgets.QCheckBox(self.frame)
        self.pPolarCheck.setGeometry(QtCore.QRect(300,155,100,100))
        
        self.inEnergyText = QtWidgets.QLabel(self.frame)
        self.inEnergyText.setGeometry(QtCore.QRect(350,155,200,100))
        self.inEnergyText.setFont(font)
        self.inEnergyText.setObjectName("inEnergyText")         
        
        self.inEnergyCheck = QtWidgets.QCheckBox(self.frame)
        self.inEnergyCheck.setGeometry(QtCore.QRect(510,155,100,100))
        
        self.inEnergyCheck.setChecked(True)
        
        self.minWavelength = QtWidgets.QTextEdit(self.frame)   
        self.minWavelength.setObjectName('minWavelength')
        self.minWavelength.setGeometry(QtCore.QRect(225, 45, 80, 35))
        self.minWavelength.setText('365')
        
        self.minAngle = QtWidgets.QTextEdit(self.frame)        
        self.minAngle.setObjectName('minAngle')
        self.minAngle.setGeometry(QtCore.QRect(225, 90, 80, 35))
        self.minAngle.setText('30')
        
        self.minPhiAngle = QtWidgets.QTextEdit(self.frame)        
        self.minPhiAngle.setObjectName('minPhiAngle')
        self.minPhiAngle.setGeometry(QtCore.QRect(225, 140, 80, 35))
        self.minPhiAngle.setText('0')        
                  
        self.maxWavelength = QtWidgets.QTextEdit(self.frame)
        self.maxWavelength.setObjectName("maxWavelength")
        self.maxWavelength.setGeometry(QtCore.QRect(350, 45, 80, 35))
        self.maxWavelength.setText('400')
        
        self.maxAngle = QtWidgets.QTextEdit(self.frame)
        self.maxAngle.setObjectName("maxAngle")
        self.maxAngle.setGeometry(QtCore.QRect(350, 90, 80, 35))
        self.maxAngle.setText('30')
        
        self.maxPhiAngle = QtWidgets.QTextEdit(self.frame)
        self.maxPhiAngle.setObjectName("maxPhiAngle")
        self.maxPhiAngle.setGeometry(QtCore.QRect(350, 140, 80, 35))
        self.maxPhiAngle.setText('90')        

        self.stepWvlPrompt = QtWidgets.QTextEdit(self.frame)
        self.stepWvlPrompt.setObjectName("stepWavelength")
        self.stepWvlPrompt.setGeometry(QtCore.QRect(475, 45, 80, 35))
        self.stepWvlPrompt.setText('0.2')
        
        self.cMapPrompt.setText('RdBu')
        
        self.stepAnglePrompt = QtWidgets.QTextEdit(self.frame)
        self.stepAnglePrompt.setObjectName("stepAngle")
        self.stepAnglePrompt.setGeometry(QtCore.QRect(475, 90, 80, 35)) 
        self.stepAnglePrompt.setText('1')
        
        self.stepPhiAnglePrompt = QtWidgets.QTextEdit(self.frame)
        self.stepPhiAnglePrompt.setObjectName("stepPhiAngle")
        self.stepPhiAnglePrompt.setGeometry(QtCore.QRect(475, 140, 80, 35)) 
        self.stepPhiAnglePrompt.setText('15')        
    
        self.wavelengthText = QtWidgets.QLabel(self.frame)
        self.wavelengthText.setFont(font)
        self.wavelengthText.setObjectName("wavelengthText")
        self.wavelengthText.setGeometry(QtCore.QRect(20, 50, 170, 40))
        
        self.angleText = QtWidgets.QLabel(self.frame)
        self.angleText.setFont(font)
        self.angleText.setObjectName("angleText")
        self.angleText.setGeometry(QtCore.QRect(20, 95, 150, 40))
        
        self.phiAngleText = QtWidgets.QLabel(self.frame)
        self.phiAngleText.setFont(font)
        self.phiAngleText.setObjectName("PhiangleText")
        self.phiAngleText.setGeometry(QtCore.QRect(20, 140, 150, 40))
        
        self.polarizationText = QtWidgets.QLabel(self.frame)
        self.polarizationText.setFont(font)
        self.polarizationText.setObjectName("polarizationText")
        self.polarizationText.setGeometry(QtCore.QRect(20, 185, 170, 40)) 
        
        self.deleteLayerButton = QtWidgets.QPushButton(self.frameDesigner)
        self.deleteLayerButton.setGeometry(QtCore.QRect(20, 120, 200, 50))
        self.deleteLayerButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.deleteLayerButton.setObjectName("deleteLayerButton")
        self.deleteLayerButton.setText("Delete Layer")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(8)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(False)
        fontapplyButton.setWeight(75)
        self.deleteLayerButton.setFont(fontapplyButton) 
        
        self.clearDesignButton = QtWidgets.QPushButton(self.frameDesigner)
        self.clearDesignButton.setGeometry(QtCore.QRect(20, 190, 200, 50))
        self.clearDesignButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.clearDesignButton.setObjectName("clearDesignButton")
        self.clearDesignButton.setText("Clear Design")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(8)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(False)
        fontapplyButton.setWeight(75)
        self.clearDesignButton.setFont(fontapplyButton)          
        
        self.addLayerButton = QtWidgets.QPushButton(self.frameDesigner)
        self.addLayerButton.setGeometry(QtCore.QRect(20, 50, 200, 50))
        self.addLayerButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.addLayerButton.setObjectName("addLayerButton")
        self.addLayerButton.setText("Add Layer")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(8)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(False)
        fontapplyButton.setWeight(75)
        self.addLayerButton.setFont(fontapplyButton)          
        
        self.calculateButton = QtWidgets.QPushButton(self.centralWidget)
        self.calculateButton.setGeometry(QtCore.QRect(10, 680, 280, 50))
        self.calculateButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.calculateButton.setObjectName("calculateButton")
        self.calculateButton.setText("Calculate")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(12)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(False)
        fontapplyButton.setWeight(75)
        self.calculateButton.setFont(fontapplyButton)
        
        self.saveButton = QtWidgets.QPushButton(self.centralWidget)
        self.saveButton.setGeometry(QtCore.QRect(300, 680, 280, 50))
        self.saveButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setText("Save Project")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(12)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(False)
        fontapplyButton.setWeight(75)
        self.saveButton.setFont(fontapplyButton) 
        
        self.openDataFile = QtWidgets.QPushButton(self.frameMicrocavity)
        self.openDataFile.setGeometry(QtCore.QRect(30, 45, 220, 40))
        self.openDataFile.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.openDataFile.setObjectName("openDataFile")
        self.openDataFile.setText("Open Data File")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(8)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(False)
        fontapplyButton.setWeight(75)
        self.openDataFile.setFont(fontapplyButton) 
        
        self.postCorrectionButton = QtWidgets.QPushButton(self.frameMicrocavity)
        self.postCorrectionButton.setGeometry(QtCore.QRect(30, 95, 220, 40))
        self.postCorrectionButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.postCorrectionButton.setObjectName("openDataFile")
        self.postCorrectionButton.setText("Apply Post Correction")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(8)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(False)
        fontapplyButton.setWeight(75)
        self.postCorrectionButton.setFont(fontapplyButton)
        
        self.posCorrectionText = QtWidgets.QLabel(self.frameMicrocavity)
        self.posCorrectionText.setGeometry(QtCore.QRect(280, 95, 220, 40))
        #self.posCorrectionText.setText('PFONA\\V')
        
        self.perfomFittingButton = QtWidgets.QPushButton(self.frameMicrocavity)
        self.perfomFittingButton.setGeometry(QtCore.QRect(100, 830, 240, 70))
        self.perfomFittingButton.setStyleSheet("background-color: rgb(255, 255, 255);")        
        self.perfomFittingButton.setObjectName("perfomFittingButton")
        self.perfomFittingButton.setText("Perfom Fitting")
        fontapplyButton = QtGui.QFont()
        fontapplyButton.setFamily("Verdana")
        fontapplyButton.setPointSize(11)
        fontapplyButton.setItalic(False)
        fontapplyButton.setBold(True)
        fontapplyButton.setWeight(75)
        self.perfomFittingButton.setFont(fontapplyButton)        
        
        self.frame.raise_()
        self.maxText.raise_()
        self.saveButton.raise_()
        self.calculateButton.raise_()
        self.wavelengthText.raise_()
        self.label.raise_()
        self.minText.raise_()
        self.maxWavelength.raise_()
        self.maxAngle.raise_()
        self.polarizationText.raise_() 
        self.minAngle.raise_()
        self.minWavelength.raise_()
        self.stepWvlPrompt.raise_()
        
        self.tmCheck.raise_()        

        self.inEnergyText.setText("Show in Energy")
        self.phiAngleText.setText("Azim Angle (°)")        
        self.minText.setText("Min")
        self.maxText.setText("Max")
        self.sPolarText.setText("s")
        self.pPolarText.setText("p")
        self.wavelengthText.setText("Wavelength Range (nm)")
        self.angleText.setText("Angle Range (°)")
        self.stepText.setText("Step")
        self.polarizationText.setText("Polarization") 
        self.DesignerLabel.setText("Designer")        
        self.menuFile.setTitle("File")
        self.actionLoad.setText("Load")
        self.actionClose.setText("Close")
        self.MicrocavityLabel.setText("Coupled Oscillator Model")
        self.OnelevelText.setText("1-level")
        self.TwolevelText.setText("2-levels")
        self.ThreelevelText.setText("3-levels")
        self.w1Text.setText('E1 (in eV)')
        
        MainWindow.setCentralWidget(self.centralWidget)
        
        #TestParamSet
        
        self.EminPrompt.setText('2.6')
        self.EmaxPrompt.setText('4.4')
        self.OnelevelCheck.setChecked(True)
        self.w1Prompt.setText('3.25')
        self.w2Prompt.setText('2.84')
        self.lbO10Prompt.setText('0.7')
        self.ubO10Prompt.setText('1.4')
        self.lbO20Prompt.setText('0.05')
        self.ubO20Prompt.setText('0.5')
        self.lbneffPrompt.setText('1.4')
        self.ubneffPrompt.setText('1.8')
        self.lbE0Prompt.setText('2.5')
        self.ubE0Prompt.setText('4')
        self.lbLPPrompt.setText('2.65')
        self.ubLPPrompt.setText('3.1')
        self.lbMPPrompt.setText('2.86')
        self.ubMPPrompt.setText('3.20')
        self.lbUPPrompt.setText('3.5')
        self.ubUPPrompt.setText('4.4')
        self.ZminPrompt.setText('0.6')
        self.ZmaxPrompt.setText('0.95')
        
        
        #Default Values to speed up analysis
        self.PolarizationE0Prompt.setText('TE')
        
        
                
        
if __name__ == "__main__":
        
        import sys
        app = QtWidgets.QApplication(sys.argv)
        TransferMatrixGUI = QtWidgets.QMainWindow()
        ui = mainGUI(TransferMatrixGUI)
        TransferMatrixGUI.show()
        sys.exit(app.exec_())
        
            
        # The code below has been generated from reading ui file 'UI_RsGUI.ui'

