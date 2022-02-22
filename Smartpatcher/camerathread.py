# -*- coding: utf-8 -*-
"""
Created on Tue Aug 10 15:05:11 2021

@author: TvdrBurgt
"""


import time
import numpy as np
from copy import copy
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QMutex

from HamamatsuCam.HamamatsuActuator import CamActuator


class CameraThread(QThread):
    snapsignal = pyqtSignal(np.ndarray)
    livesignal = pyqtSignal(np.ndarray)
    
    def __init__(self, camerahandle=None):
        self.exposuretime = 0.02    # seconds
        self.GUIframerate = 25      # frames per second
        self.sleeptime = np.max([1/self.GUIframerate, self.exposuretime])
        self.frame = np.random.rand(2048, 2048)
        self.mutex = QMutex()
        
        # Camera attributes
        if camerahandle == None:
            self.camera = CamActuator()
            self.camera.initializeCamera()
        else:
            self.camera = camerahandle
        self.camera.hcam.setPropertyValue("exposure_time", self.exposuretime)
        
        # QThread attributes
        super().__init__()
        self.isrunning = False
        self.moveToThread(self)
        self.started.connect(self.live)
        
    def stop(self):
        self.isrunning = False
        self.quit()
        self.wait()
        
    def snap(self):
        time.sleep(self.sleeptime)
        snap = np.random.rand(2048, 2048)
        self.mutex.lock()
        snap = copy(self.frame)
        self.mutex.unlock()
        self.snapsignal.emit(snap)
        return snap
    
    @pyqtSlot()
    def live(self):
        print('camera thread started')
        
        self.camera.isLiving = True
        self.camera.hcam.acquisition_mode = "run_till_abort"
        
        # Wait a second for camera acquisition to start
        self.camera.hcam.startAcquisition()
        QThread.msleep(1000)
        
        # Emit and get frames from the camera at a rate of 1/sleeptime
        self.isrunning = True
        while self.isrunning:
            QThread.msleep(int(self.sleeptime *1000))
            try:
                [frames, dims] = self.camera.hcam.getFrames()
                self.mutex.lock()
                self.frame = np.resize(frames[-1].np_array, (dims[1], dims[0]))
                self.livesignal.emit(self.frame)
                self.mutex.unlock()
            except:
                pass
        
        self.camera.hcam.stopAcquisition()
        self.camera.isLiving = False
        self.camera.Exit()
        
        print('camera thread stopped')
    

# class CameraThread(QThread):
#     snapsignal = pyqtSignal(np.ndarray)
#     livesignal = pyqtSignal(np.ndarray)
    
#     def __init__(self, camerahandle=None):
#         self.exposuretime = 0.02    # seconds
#         self.GUIframerate = 25      # frames per second
#         self.sleeptime = np.max([1/self.GUIframerate, self.exposuretime])
#         self.frame = np.random.rand(2048, 2048)
#         self.mutex = QMutex()
        
#         # QThread attributes
#         super().__init__()
#         self.isrunning = False
#         self.moveToThread(self)
#         self.started.connect(self.live)
        
#     def stop(self):
#         self.isrunning = False
#         self.quit()
#         self.wait()
        
#     def snap(self):
#         time.sleep(self.sleeptime)
#         snap = np.ndarray
#         self.mutex.lock()
#         snap = copy(self.frame)
#         self.mutex.unlock()
#         self.snapsignal.emit(snap)
#         return snap
        
#     @pyqtSlot()
#     def live(self):
#         print('camera thread started')
        
#         self.isrunning = True
#         while self.isrunning:
#             QThread.msleep(int(self.sleeptime*1000))
#             try:
#                 self.mutex.lock()
#                 self.frame = np.random.rand(2048, 2048)
#                 self.livesignal.emit(self.frame)
#                 self.mutex.unlock()
#             except:
#                 pass
            
#         print('camera thread stopped')
