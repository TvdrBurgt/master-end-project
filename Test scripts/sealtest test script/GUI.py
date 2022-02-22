# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 09:56:32 2021

@author: tvdrb
"""



import time
import sys
import numpy as np
import logging
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QDoubleSpinBox, QGroupBox, QLabel, QStackedWidget, QComboBox, QTabWidget, QSizePolicy
import pyqtgraph.exporters
import pyqtgraph as pg

sys.path.append('../')
from PatchClamp.smartpatcher_GUI import AutomaticPatchGUI
from PatchClamp.manualpatcher_GUI import ManualPatchGUI


class PatchClamp(QWidget):
    def __init__(self):
        super().__init__()
        """
        =======================================================================
        ----------------------------- Start of GUI ----------------------------
        =======================================================================
        """
        """
        ----------------------- General widget settings ----------------------
        """
        self.setWindowTitle("Patchclamp")
        
        """
        ------------------- Stack automatic/manual patchers -------------------
        """
        self.autopatch = AutomaticPatchGUI()
        self.manualpatch = ManualPatchGUI()
        
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.autopatch)
        self.stackedWidget.addWidget(self.manualpatch)
        
        """
        --------------------- Add widgets and set Layout  ---------------------
        """
        pageComboBox = QComboBox()
        pageComboBox.addItem(str("Automatic patcher"))
        pageComboBox.addItem(str("Manual patcher"))
        pageComboBox.activated.connect(self.stackedWidget.setCurrentIndex)
        pageComboBox.activated.connect(self.resize_QStack)
        pageComboBox.AdjustToContents = True
        
        layout = QGridLayout()
        layout.addWidget(pageComboBox, 0,0,1,1)
        layout.addWidget(self.stackedWidget, 1,0,1,1)
        
        self.setLayout(layout)
        
        """
        =======================================================================
        ----------------------------- End of GUI ------------------------------
        =======================================================================
        """
        
    
    def resize_QStack(self):
        activelayer = self.stackedWidget.currentIndex()
        if activelayer == 1:
            self.setFixedSize(400,800)
        else:
            self.setFixedSize(1800,800)
    
    
    def closeEvent(self, event):
        """ Close event
        This method is called when the GUI is shut down. First we need to stop
        the threads that are still running, then we disconnect all hardware to
        be reused in the main widget, only then we accept the close event.
        and quit the widget.
        """
        self.autopatch.closeEvent(event)
        self.manualpatch.closeEvent(event)
        
        event.accept()
        
        # Frees the console by quitting the application entirely
        QtWidgets.QApplication.quit() # remove when part of Tupolev!!




if __name__ == "__main__":
    
    def start_logger():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                # logging.FileHandler("autopatch.log"),   # uncomment to write to .log
                logging.StreamHandler()
            ]
        )
    
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        pg.setConfigOptions(
            imageAxisOrder="row-major"
        )  # Transposes image in pg.ImageView()
        mainwin = PatchClamp()
        mainwin.show()
        app.exec_()
        
    start_logger()
    run_app()
    