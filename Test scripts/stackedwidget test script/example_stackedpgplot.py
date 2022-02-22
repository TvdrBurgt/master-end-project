
import sys
import numpy as np

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QStackedWidget, QGridLayout, QComboBox
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
        
        # QWidget()
        algorithmWidget = pg.GraphicsLayoutWidget()
        algorithm = algorithmWidget.addPlot(1, 0, 1, 1)
        algorithm.setTitle('algorithm')
        algorithm.setLabel("left", units='a.u.')
        algorithm.setLabel("bottom", text="depth (um)")
        self.algorithm = algorithm.plot(pen=(1,3))
        
        # QWidget()
        currentWidget = pg.GraphicsLayoutWidget()
        current = currentWidget.addPlot(1, 0, 1, 1)
        current.setTitle('current')
        current.setLabel("left", units='I')
        current.setLabel("bottom", text="time (ms)")
        self.current = current.plot(pen=(2,3))
        
        # QWidget()
        pressureWidget = pg.GraphicsLayoutWidget()
        pressure = pressureWidget.addPlot(3, 0, 1, 1)
        pressure.setTitle('pressure')
        pressure.setLabel("left", units='mBar')
        pressure.setLabel("bottom", text="time (ms)")
        self.pressure = pressure.plot(pen=(3,3))
        
        # QStackedWidget = 3x QWidget()
        stackedWidget = QStackedWidget()
        stackedWidget.addWidget(algorithmWidget)
        stackedWidget.addWidget(currentWidget)
        stackedWidget.addWidget(pressureWidget)
        
        pageComboBox = QComboBox()
        pageComboBox.addItem(str("Algorithm"))
        pageComboBox.addItem(str("Current"))
        pageComboBox.addItem(str("Pressure"))
        pageComboBox.activated.connect(stackedWidget.setCurrentIndex)
        
        layout = QGridLayout()
        layout.addWidget(stackedWidget, 1,0,1,1)
        layout.addWidget(pageComboBox, 0,0,1,1)
        self.setLayout(layout)
        
        """
        =======================================================================
        ----------------------------- End of GUI ------------------------------
        =======================================================================
        """
        
        # algorithm thread
        self.algorithmthread = QThread()
        self.datagenerator1 = datagenerator()
        self.datagenerator1.moveToThread(self.algorithmthread)
        self.algorithmthread.started.connect(self.datagenerator1.measure)
        self.datagenerator1.finished.connect(self.algorithmthread.quit)
        self.datagenerator1.finished.connect(self.algorithmthread.wait)
        self.datagenerator1.measurement.connect(self.update_algorithmwindow)
        
        # current thread
        self.currentthread = QThread()
        self.datagenerator2 = datagenerator()
        self.datagenerator2.moveToThread(self.currentthread)
        self.currentthread.started.connect(self.datagenerator2.measure)
        self.datagenerator2.finished.connect(self.currentthread.quit)
        self.datagenerator2.finished.connect(self.currentthread.wait)
        self.datagenerator2.measurement.connect(self.update_currentwindow)
        
        # pressure thread
        self.pressurethread = QThread()
        self.datagenerator3 = datagenerator()
        self.datagenerator3.moveToThread(self.pressurethread)
        self.pressurethread.started.connect(self.datagenerator3.measure)
        self.datagenerator3.finished.connect(self.pressurethread.quit)
        self.datagenerator3.finished.connect(self.pressurethread.wait)
        self.datagenerator3.measurement.connect(self.update_pressurewindow)
        
        self.algorithmthread.start()
        self.currentthread.start()
        self.pressurethread.start()
    
    
    def update_algorithmwindow(self, xdata,ydata):
        n = 100
        self.algorithm.setData(xdata[-n:],ydata[-n:])
    
    def update_currentwindow(self, xdata,ydata):
        n = 100
        self.current.setData(xdata[-n:],ydata[-n:])
    
    def update_pressurewindow(self, xdata,ydata):
        n = 100
        self.pressure.setData(xdata[-n:],ydata[-n:])
        
    
    def closeEvent(self, event):
        self.datagenerator1.isrunning = False
        self.datagenerator2.isrunning = False
        self.datagenerator3.isrunning = False
        event.accept()
        QtWidgets.QApplication.quit()




class datagenerator(QThread):
    finished = pyqtSignal()
    measurement = pyqtSignal(np.ndarray,np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.isrunning = False
        self.xdata = np.array([0])
        self.ydata = np.array([0])
        
    def measure(self):
        self.isrunning = True
        while self.isrunning == True:
            self.xdata = np.append(self.xdata, self.xdata[-1]+1)
            self.ydata = np.append(self.ydata, np.random.rand(1))
            self.measurement.emit(self.xdata, self.ydata)
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