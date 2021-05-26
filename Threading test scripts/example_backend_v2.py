# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 11:12:26 2021

@author: tvdrb
"""

import numpy as np

from copy import copy

from PyQt5.QtCore import pyqtSignal, QThread


class CameraThread(QThread):
    snapsignal = pyqtSignal(np.ndarray)
    livesignal = pyqtSignal(np.ndarray)
    
    def __init__(self):
        self.isrunning = True
        self.livecanvas = True
        self.exposure_time = 20
        self.get_frame = np.zeros((2048,2048))
        
        super().__init__()
        self.moveToThread(self)
        self.started.connect(self.acquire)
        
    def __del__(self):
        self.isrunning = False
        self.quit()
        self.wait()
    
    def acquire(self):
        print("data acquisition started")
        while self.isrunning:
            # Mutex lock here?
            self.get_frame = np.random.rand(2048, 2048)
            QThread.msleep(self.exposure_time)
            if self.livecanvas:
                self.livesignal.emit(self.get_frame)
            else:
                pass
        print("data acquisition stopped")
    
    def start_canvasupdates(self):
        self.livecanvas = True
        
    def stop_canvasupdates(self):
        self.livecanvas = False
        
    def snap(self):
        # Mutex lock here?
        last_view = copy(self.get_frame)
        print("snap!")
        self.snapsignal.emit(last_view)
        
        return last_view
        


class AutoPatchThread(QThread):

    def __init__(self, camera_handle):
        self.camera = camera_handle
        self.isrunning = True
        
        super().__init__()
        self.moveToThread(self)
        self.started.connect(self.get_cameraFOV)
        
    def __del__(self):
        self.isrunning = False
        self.quit()
        self.wait()

    def run(self):
        # Do something here
        pass

    def get_cameraFOV(self):
        while self.isrunning:
            QThread.msleep(1000)
            snapped_image = self.camera.snap()
        print('autopatcher stopped')


if __name__ == "__main__":
    instance = AutoPatchThread()
