# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 11:12:26 2021

@author: tvdrb
"""

import numpy as np

from copy import copy

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread


class CameraThread(QThread):
    snapsignal = pyqtSignal(np.ndarray)
    livesignal = pyqtSignal(np.ndarray)
    
    def __init__(self):
        self.isrunning = True
        self.exposure_time = 20
        self.get_frame = np.zeros((2048,2048))
        
        super().__init__()
        self.moveToThread(self)
        self.started.connect(self.acquire)
        
    def __del__(self):
        self.isrunning = False
        self.quit()
        self.wait()
    
    @pyqtSlot()
    def acquire(self):
        print("data acquisition started")
        while self.isrunning:
            # Mutex lock here?
            self.get_frame = np.random.rand(2048, 2048)
            QThread.msleep(self.exposure_time)
            self.livesignal.emit(self.get_frame)
        print("data acquisition stopped")
        
    def snap(self):
        # Mutex lock here?
        last_view = copy(self.get_frame)
        print("snap!")
        self.snapsignal.emit(last_view)
        
        return last_view
        


class AutoPatchThread(QThread):

    def __init__(self, method, camera_handle, manipulator_handle=None):
        self.camera = camera_handle
        self.micromanipulator = manipulator_handle
        self.isrunning = True
        
        super().__init__()
        self.moveToThread(self)
        if method == 'request autofocus':
            self.started.connect(self.autofocus)
        elif method == 'request detect':
            self.started.connect(self.detect)
        else:
            pass
        
    def __del__(self):
        self.isrunning = False
        self.quit()
        self.wait()
        
        
    def autofocus(self):
        print("autofocus started")
        loopcount = -1
        while self.isrunning:
            loopcount += 1
            QThread.msleep(1000)
            print(loopcount)
            if loopcount == 10:
                self.isrunning = False
        print("autofocus stopped")
        # self.__del__()
    
    def detect(self):
        print("pipette detection started")
        loopcount = -1
        while self.isrunning:
            loopcount += 1
            QThread.msleep(1000)
            print(loopcount)
            if loopcount == 10:
                self.isrunning = False
        print("pipette detection stopped")
        # self.__del__()


if __name__ == "__main__":
    instance = AutoPatchThread()
