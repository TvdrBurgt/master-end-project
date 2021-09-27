# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 13:01:03 2021

@author: tvdrb
"""

import sys
import numpy as np

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox
import pyqtgraph.exporters
import pyqtgraph as pg


class PatchClampUI(QWidget):
    def __init__(self):
        super().__init__()
        """
        =======================================================================
        ----------------------------- Start of GUI ----------------------------
        =======================================================================
        """
        """
        # ---------------------- General widget settings ---------------------
        """
        self.setWindowTitle("Automatic Patchclamp")

        """
        -------------------------- Sensory output display -------------------------
        """
        sensorContainer = QGroupBox()
        sensorContainer.setMinimumSize(400,600)
        sensorLayout = QGridLayout()
        
        sensorWidget = pg.GraphicsLayoutWidget()
        algorithm = sensorWidget.addPlot(1, 0, 1, 1)
        algorithm.setTitle('algorithm')
        algorithm.setLabel("left", units='a.u.')
        algorithm.setLabel("bottom", text="depth (um)")
        self.algorithm = algorithm.plot(pen=(1,3))
        current = sensorWidget.addPlot(2, 0, 1, 1)
        current.setTitle('current')
        current.setLabel("left", units='I')
        current.setLabel("bottom", text="time (ms)")
        self.current = current.plot(pen=(2,3))
        pressure = sensorWidget.addPlot(3, 0, 1, 1)
        pressure.setTitle('pressure')
        pressure.setLabel("left", units='mBar')
        pressure.setLabel("bottom", text="time (ms)")
        self.pressure = pressure.plot(pen=(3,3))
        
        sensorLayout.addWidget(sensorWidget)
        sensorContainer.setLayout(sensorLayout)

        """
        --------------------------- Adding to master --------------------------
        """
        master = QGridLayout()
        master.addWidget(sensorContainer, 0, 0, 1, 1)

        self.setLayout(master)

        """
        =======================================================================
        ----------------------------- End of GUI ------------------------------
        =======================================================================
        """
        
        self.algorithmthread = QThread()
        self.currentthread = QThread()
        self.pressurethread = QThread()
        
        self.datagenerator1 = datagenerator()
        self.datagenerator2 = datagenerator()
        self.datagenerator3 = datagenerator()
        
        self.datagenerator1.moveToThread(self.algorithmthread)
        self.datagenerator2.moveToThread(self.currentthread)
        self.datagenerator3.moveToThread(self.pressurethread)
        
        self.algorithmthread.started.connect(self.datagenerator1.measure)
        self.currentthread.started.connect(self.datagenerator2.measure)
        self.pressurethread.started.connect(self.datagenerator3.measure)
        
        self.datagenerator1.finished.connect(self.algorithmthread.quit)
        self.datagenerator2.finished.connect(self.currentthread.quit)
        self.datagenerator3.finished.connect(self.pressurethread.quit)
        
        self.datagenerator1.finished.connect(self.algorithmthread.wait)
        self.datagenerator2.finished.connect(self.currentthread.wait)
        self.datagenerator3.finished.connect(self.pressurethread.wait)
        
        self.datagenerator1.data.connect(self.algorithm.setData)
        self.datagenerator2.data.connect(self.current.setData)
        self.datagenerator3.data.connect(self.pressure.setData)
        
        self.algorithmthread.start()
        self.currentthread.start()
        self.pressurethread.start()
        
    
    
    def closeEvent(self, event):
        self.datagenerator1.isrunning = False
        self.datagenerator2.isrunning = False
        self.datagenerator3.isrunning = False
        event.accept()
        QtWidgets.QApplication.quit()



class datagenerator(QThread):
    finished = pyqtSignal()
    data = pyqtSignal(np.ndarray,np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.isrunning = False
        
    def measure(self):
        x = np.array([0])
        y = np.array([0])
        self.isrunning = True
        while self.isrunning == True:
            x = np.append(x, x[-1]+1)
            y = np.append(y, np.random.rand(1))
            self.data.emit(x, y)
            QThread.msleep(int(np.random.rand(1)*100+50))
        self.finished.emit()
    

if __name__ == "__main__":
    
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        pg.setConfigOptions(
            imageAxisOrder="row-major"
        )  # Transposes image in pg.ImageView()
        mainwin = PatchClampUI()
        mainwin.show()
        app.exec_()
        
    run_app()

