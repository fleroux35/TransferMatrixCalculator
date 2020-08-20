# -*- coding: utf-8 -*-

import resources
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

class AddLayerPopUp(QtWidgets.QWidget):
    
    def __init__(self, listMaterials):
        
        """Initialise"""
        super().__init__()
        
        self.setWindowIcon(QtGui.QIcon(":/TmIcon.png"));
        self.setWindowTitle("AddLayerPopUp")
        
        self.setFixedSize(350, 200)
        
        font = QtGui.QFont()
        font.setPointSize(8)
        self.setFont(font)
        self.setAutoFillBackground(False)
        self.setStyleSheet("border-color: rgb(206, 206, 206);")
        
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(10, 10, 330, 125))
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
        
        self.materialComboBox = QtWidgets.QComboBox(self.frame)
        self.materialComboBox.setObjectName("materialComboBox")
        self.materialComboBox.setGeometry(QtCore.QRect(120, 40, 200, 30))
        self.materialComboBox.setStyleSheet('background-color: rgb(255,255,255);')
        
        for material in listMaterials:
            self.materialComboBox.addItem(material)
        
        self.thicknessPrompt = QtWidgets.QTextEdit(self.frame)
        self.thicknessPrompt.setObjectName("thicknessPrompt")
        self.thicknessPrompt.setGeometry(QtCore.QRect(200, 85, 80, 30))
        self.thicknessPrompt.setText(str(100))
        
        self.materialText = QtWidgets.QLabel(self.frame)
        self.materialText.setFont(font)
        self.materialText.setObjectName("materialText")
        self.materialText.setGeometry(QtCore.QRect(20, 40, 80, 30))
        
        self.thicknessText = QtWidgets.QLabel(self.frame)
        self.thicknessText.setFont(font)
        self.thicknessText.setObjectName("thicknessText")
        self.thicknessText.setGeometry(QtCore.QRect(20, 85, 140, 30))
            
        self.materialText.raise_()
        self.label.raise_()
        self.targetAngleText.raise_()
        self.materialComboBox.raise_()
        self.thicknessPrompt.raise_()
        self.thicknessText.raise_()
        
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(90, 148, 180, 40))
        self.pushButton.setObjectName("pushButton")
        self.frame.raise_()
        self.pushButton.raise_()    
        
        self.materialText.setText("Material")
        self.targetAngleText.setText("Parameters")
        self.thicknessText.setText("Thickness (nm)")
        self.pushButton.setText("Add Layer")        
    
        self.show()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    PopUp = AddLayerPopUp()
    PopUp.show()
    sys.exit(app.exec_())

