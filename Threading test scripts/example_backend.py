# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 11:12:26 2021

@author: tvdrb
"""

import logging
import numpy as np

from copy import copy

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QMutex


class CameraThread(QThread):
    snapsignal = pyqtSignal(np.ndarray)
    livesignal = pyqtSignal(np.ndarray)

    def __init__(self):
        self.exposure_time = 20
        self.frame = np.random.rand(2048, 2048)

        super().__init__()
        self.isrunning = False
        self.mutex = QMutex()
        self.moveToThread(self)
        self.started.connect(self.acquire)

    def __del__(self):
        self.isrunning = False
        self.quit()
        self.wait()

    @pyqtSlot()
    def acquire(self):
        self.isrunning = True
        logging.info("data acquisition started")
        while self.isrunning:
            self.mutex.lock()
            self.frame = np.random.rand(2048, 2048)
            QThread.msleep(self.exposure_time)
            self.livesignal.emit(self.frame)
            self.mutex.unlock()
        logging.info("data acquisition stopped")

    def snap(self):
        # Mutex lock makes code execute in order. Code continues when unlocked,
        # so it acts as a que.
        self.mutex.lock()
        snapshot = copy(self.frame)
        self.mutex.unlock()
        logging.info("snap!")
        self.snapsignal.emit(snapshot)

        return snapshot


class AutoPatchThread(QThread):
    finished = pyqtSignal()

    def __init__(self, camera_handle=None, manipulator_handle=None, objective_handle=None):
        self.camera_handle = camera_handle
        self.micromanipulator_handle = manipulator_handle
        self.objective_handle = objective_handle

        super().__init__()
        self.isrunning = False
        self.moveToThread(self)
        self.finished.connect(self.__del__)
        self.started.connect(self.__del__)

    def __del__(self):
        self.isrunning = False
        self.quit()
        self.wait()
        
    def request(self, slot):
        self.started.disconnect()
        if slot == "autofocus":
            self.started.connect(self.autofocus)
        elif slot == "detect":
            self.started.connect(self.detect)
        self.isrunning = True
        self.start()
        
    @pyqtSlot()
    def autofocus(self):
        logging.info("autofocus started")
        loopcount = -1
        while self.isrunning:
            loopcount += 1
            QThread.msleep(1000)
            print(loopcount)
            if loopcount == 5:
                self.isrunning = False
        logging.info("autofocus stopped")
        self.finished.emit()

    @pyqtSlot()
    def detect(self):
        logging.info("pipette detection started")
        loopcount = -1
        while self.isrunning:
            loopcount += 1
            QThread.msleep(1000)
            print(loopcount)
            if loopcount == 10:
                self.isrunning = False
        logging.info("pipette detection stopped")
        self.finished.emit()

