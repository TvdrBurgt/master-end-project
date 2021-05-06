# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 10:37:51 2021

@author: tvdrb
"""

import sys
import numpy as np
import pyqtgraph as pg
from copy import copy
from PyQt5 import QtWidgets, QtCore
from PyQt5.Qt import QMutex


class DataGenerator(QtCore.QObject):

    newData  = QtCore.pyqtSignal(np.ndarray)
    
    def __init__(self,parent=None, delay=1000):
        QtCore.QObject.__init__(self)
        self.parent = parent
        self.delay  = delay
        self.mutex  = QMutex()        
        self.image  = np.zeros((2048,2048))
        self.run    = True    
        
    def generateData(self):
        while self.run:
            try:
                self.mutex.lock()            
                self.image = np.random.rand(2048,2048)
                self.mutex.unlock()
                self.newData.emit(self.image)
                QtCore.QThread.msleep(self.delay)
            except: pass

class MainWin(QtWidgets.QWidget):
    
    def __init__(self, camera_handle = None, motor_handle = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #======================================================================
        #---------------------------- Start of GUI ----------------------------
        #======================================================================
        #----------------------- General widget settings ----------------------
        self.setWindowTitle("Automatic Patchclamp")
        
        #---------------------------- Snapshot view ---------------------------
        snapshotContainer = QtWidgets.QGroupBox()
        snapshotContainer.setMinimumSize(600, 600)
        snapshotLayout = QtWidgets.QGridLayout()
        
        # Display to project snapshots
        self.snapshotWidget = pg.ImageView()
        self.canvas = self.snapshotWidget.getImageItem()
        self.canvas.setAutoDownsample(True)
        
        self.snapshotWidget.ui.roiBtn.hide()
        self.snapshotWidget.ui.menuBtn.hide()
        self.snapshotWidget.ui.histogram.hide()
        snapshotLayout.addWidget(self.snapshotWidget, 0, 0, 1, 3)
        
        # Button for automatic focussing a pipette
        request_autofocus_button = QtWidgets.QPushButton("Autofocus pipette")
        snapshotLayout.addWidget(request_autofocus_button, 1, 0, 1, 1)
        
        # Button for making a snapshot
        request_camera_image_button = QtWidgets.QPushButton("Snap image")
        request_camera_image_button.clicked.connect(self.snap)
        snapshotLayout.addWidget(request_camera_image_button, 1, 1, 1, 1)
        
        # Button for detecting pipette tip
        request_pipette_coordinates_button = QtWidgets.QPushButton("Detect pipette tip")
        snapshotLayout.addWidget(request_pipette_coordinates_button, 1, 2, 1, 1)
        
        snapshotContainer.setLayout(snapshotLayout)
        
        #-------------------------- Adding to master --------------------------
        master = QtWidgets.QGridLayout()
        master.addWidget(snapshotContainer, 0, 0, 1, 1)
        
        self.setLayout(master)
        
        #======================================================================
        #---------------------------- End of GUI ------------------------------
        #======================================================================
        
        self.thread = QtCore.QThread()
        self.dgen = DataGenerator(self, delay=1)
        self.dgen.moveToThread(self.thread)
        # self.dgen.newData.connect(self.update_plot)
        self.thread.started.connect(self.dgen.generateData)
        self.thread.start()
        
    def snap(self):
        self.dgen.newData.connect(self.update_plot)
    
    def update_plot(self,image):
        if self.dgen.mutex.tryLock(): 
            image = copy(image)
            self.dgen.mutex.unlock() 
            self.canvas.setImage(image)
    
    def closeEvent(self, event):
        QtWidgets.QApplication.quit()
        event.accept()


if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        pg.setConfigOptions(imageAxisOrder='row-major') #Transposes image in pg.ImageView()
        mainwin = MainWin()
        mainwin.show()
        app.exec_()
    run_app()
    