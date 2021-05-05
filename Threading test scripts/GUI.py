# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 10:37:51 2021

@author: tvdrb
"""

import sys
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore

from autopatch_example import AutomaticPatcher


class PatchClampUI(QtWidgets.QWidget):
    
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
        
        self.autopatch_instance = AutomaticPatcher(self)
        
        
        
        
    def snap(self):
        self.thread = QtCore.QThread()
        self.autopatch_instance.moveToThread(self.thread)
        self.thread.started.connect(self.autopatch_instance.take_snap)
        self.autopatch_instance.finished.connect(self.thread.quit)
        self.thread.start()
        
    
    def closeEvent(self, event):
        QtWidgets.QApplication.quit()
        event.accept()


if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        pg.setConfigOptions(imageAxisOrder='row-major') #Transposes image in pg.ImageView()
        mainwin = PatchClampUI()
        mainwin.show()
        app.exec_()
    run_app()
    