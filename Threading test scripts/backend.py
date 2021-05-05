# -*- coding: utf-8 -*-
"""
Created on Wed May  5 18:30:52 2021

@author: tvdrb
"""

import numpy as np
from PyQt5 import QtCore
from PyQt5.Qt import QMutex


class AutomaticPatcher(QtCore.QObject):
    
    finished = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.parent = parent
        self.mutex  = QMutex()
        self.image = np.zeros((2048,2048))
        
    
    def take_snap(self):
        self.mutex.lock()
        print('snap!')
        self.image = np.random.rand(2048,2048)
        self.parent.canvas.setImage(self.image)
        self.finished.emit()
        self.mutex.unlock()
        