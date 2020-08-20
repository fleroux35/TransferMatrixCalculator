# -*- coding: utf-8 -*-

import resources
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

class PostProcessPopUp(QtWidgets.QWidget):
    
    def __init__(self, cavityMaterials):
        
        """Initialise"""
        super().__init__()
        
        self.setWindowIcon(QtGui.QIcon(":/TmIcon.png"));
        self.setWindowTitle("PostProcessPopUp")
        
        self.setFixedSize(350, 150)
        
        font = QtGui.QFont()
        font.setPointSize(8)
        self.setFont(font)
        self.setAutoFillBackground(False)
        self.setStyleSheet("border-color: rgb(206, 206, 206);")
        
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(10, 10, 330, 80))
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("border-color: rgb(142, 231, 255);")
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(2)
        self.frame.setObjectName("frame")
        
        self.label = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        self.targetAngleText = QtWidgets.QLabel(self.frame)
        self.targetAngleText.setGeometry(QtCore.QRect(170, -30, 150, 100))
        
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        
        self.targetAngleText.setFont(font)
        self.targetAngleText.setObjectName("targetAngleText")        
        
        self.cavityComboBox = QtWidgets.QComboBox(self.frame)
        self.cavityComboBox.setObjectName("cavityComboBox")
        self.cavityComboBox.setGeometry(QtCore.QRect(120, 40, 200, 30))
        self.cavityComboBox.setStyleSheet('background-color: rgb(255,255,255);')
        
        for cavity in cavityMaterials:
            self.cavityComboBox.addItem(cavity)
        
        self.cavitiesText = QtWidgets.QLabel(self.frame)
        self.cavitiesText.setFont(font)
        self.cavitiesText.setObjectName("cavitiesText")
        self.cavitiesText.setGeometry(QtCore.QRect(20, 40, 80, 30))
        
        self.cavitiesText.raise_()
        self.label.raise_()
        self.targetAngleText.raise_()
        self.cavityComboBox.raise_()
        
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(90, 100, 180, 40))
        self.pushButton.setObjectName("pushButton")
        self.frame.raise_()
        self.pushButton.raise_()    
        
        self.cavitiesText.setText("Material")
        self.targetAngleText.setText("Parameters")
        self.pushButton.setText("Apply")        
    
        self.show()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    PopUp = PostProcessPopUp(['dicks','dicksdicks'])
    PopUp.show()
    sys.exit(app.exec_())

