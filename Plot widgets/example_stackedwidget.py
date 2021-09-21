
import sys

from PyQt5 import QtWidgets
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
        pageComboBox.addItem(str("Page 1"))
        pageComboBox.addItem(str("Page 2"))
        pageComboBox.addItem(str("Page 3"))
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
        
    def closeEvent(self, event):
        event.accept()
        QtWidgets.QApplication.quit()

    

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