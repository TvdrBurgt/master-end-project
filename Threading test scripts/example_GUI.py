# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 10:37:51 2021

@author: tvdrb
"""

import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QGroupBox
import pyqtgraph.exporters
import pyqtgraph as pg

from example_backend import CameraThread, AutoPatchThread


class PatchClampUI(QWidget):
    def __init__(self):
        super().__init__()

        # =====================================================================
        # ---------------------------- Start of GUI ---------------------------
        # =====================================================================
        # ----------------------- General widget settings ---------------------
        self.setWindowTitle("Automatic Patchclamp")

        # ---------------------------- Snapshot view --------------------------
        snapshotContainer = QGroupBox()
        snapshotContainer.setMinimumSize(1200, 600)
        snapshotLayout = QGridLayout()

        # Display to project live camera view
        self.liveWidget = pg.ImageView()
        self.canvaslive = self.liveWidget.getImageItem()
        self.canvaslive.setAutoDownsample(True)
        
        self.liveWidget.ui.roiBtn.hide()
        self.liveWidget.ui.menuBtn.hide()
        self.liveWidget.ui.histogram.hide()
        snapshotLayout.addWidget(self.liveWidget, 0, 0, 1, 2)
        
        # Display to project snapshots
        self.snapshotWidget = pg.ImageView()
        self.canvassnap = self.snapshotWidget.getImageItem()
        self.canvassnap.setAutoDownsample(True)
        
        self.snapshotWidget.ui.roiBtn.hide()
        self.snapshotWidget.ui.menuBtn.hide()
        self.snapshotWidget.ui.histogram.hide()
        snapshotLayout.addWidget(self.snapshotWidget, 0, 2, 1, 2)
        
        # Button for starting camera acquisition. This button is a property of
        # the container because we need its checkable state in a function.
        self.request_pause_button = QPushButton("Pause live")
        self.request_pause_button.setCheckable(True)
        self.request_pause_button.clicked.connect(self.toggle_live)
        snapshotLayout.addWidget(self.request_pause_button, 1, 0, 1, 1)

        # Button for making a snapshot
        request_camera_image_button = QPushButton("Snap image", clicked=self.request_snap)
        # request_camera_image_button.clicked.connect(self.request_snap)
        snapshotLayout.addWidget(request_camera_image_button, 1, 1, 1, 1)
        
        # Button for autofocus
        request_autofocus_button = QPushButton("Autofocus")
        request_autofocus_button.clicked.connect(self.request_autofocus)
        snapshotLayout.addWidget(request_autofocus_button, 1, 2, 1, 1)
        
        # Button for pipette detection
        request_detection_button = QPushButton("Detect pipette")
        request_detection_button.clicked.connect(self.request_detect)
        snapshotLayout.addWidget(request_detection_button, 1, 3, 1, 1)

        snapshotContainer.setLayout(snapshotLayout)
        
        # -------------------------- Adding to master -------------------------
        master = QGridLayout()
        master.addWidget(snapshotContainer, 0, 0, 1, 1)

        self.setLayout(master)

        # =====================================================================
        # ---------------------------- End of GUI -----------------------------
        # =====================================================================
        
        # Make a button for this
        self.connect_camera()
        
    def connect_micromanipulator(self):
        pass
        
    def connect_camera(self):
        self.camerathread = CameraThread()
        self.camerathread.livesignal.connect(self.update_canvaslive)
        self.camerathread.snapsignal.connect(self.update_canvassnap)
        self.camerathread.start()
        
    def toggle_live(self):
        # Request to pause or continue emitting frames from the camera thread
        if self.request_pause_button.isChecked():
            self.camerathread.livesignal.disconnect(self.update_canvaslive)
        else:
            self.camerathread.livesignal.connect(self.update_canvaslive)
    
    def request_snap(self):
        # Request a snapshot from the camera thread
        self.camerathread.snap()
        
    def request_autofocus(self):
        self.autopatchthread = AutoPatchThread('request autofocus', self.camerathread, None)
        # self.autopatchthread.started.connect(self.autopatchthread.autofocus)
        self.autopatchthread.start()
        
    def request_detect(self):
        self.autopatchthread = AutoPatchThread('request detect', self.camerathread, None)
        # self.autopatchthread.started.connect(self.autopatchthread.detect)
        self.autopatchthread.start()
        
    def update_canvaslive(self, image):
        # Update the live canvas with every new camera frame
        self.canvaslive.setImage(image)
        
    def update_canvassnap(self, image):
        # Update the snap canvas with the newest camera frame
        self.canvassnap.setImage(image)

    def closeEvent(self, event):
        self.camerathread.__del__()
        # self.autopatchthread.__del__()
        QtWidgets.QApplication.quit()
        event.accept()


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
