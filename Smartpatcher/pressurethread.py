# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 10:03:29 2021

@author: TvdrBurgt
"""


import time
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread

from pressurecontroller import PressureController


class PressureThread(QThread):
    """ Pressure control through serial communication
    This class is for controlling the Pressure Controller.
    """
    measurement = pyqtSignal(np.ndarray)
    
    def __init__(self, pressurecontroller_handle=None):
        self.parent = None
        self.waveform = None
        
        # Pressure controller attributes
        if pressurecontroller_handle == None:
            self.pressurecontroller = PressureController(address='COM21', baud=9600)
        else:
            self.pressurecontroller = pressurecontroller_handle
        
        # QThread attributes
        super().__init__()
        self.isrunning = False
        self.isrecording = False
        self.moveToThread(self)
        self.started.connect(self.measure)
    
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, parent):
        self._parent = parent
    
    @property
    def waveform(self):
        return self._waveform
    
    @waveform.setter
    def waveform(self, function_handle):
        self._waveform = function_handle
    
    @waveform.deleter
    def waveform(self):
        self._waveform = None
        
    
    def stop(self):
        self.isrecording = False
        self.isrunning = False
        self.quit()
        self.wait()
    
    def set_pressure_stop_waveform(self, pressure):
        del self.waveform
        self.pressurecontroller.setPres(pressure)
    
    def set_pressure_hold_stop_waveform(self, pressure):
        del self.waveform
        self.pressurecontroller.setPresHold(pressure)
    
    def set_pulse_stop_waveform(self, magnitude):
        del self.waveform
        self.pressurecontroller.doPulse(magnitude)
    
    def set_waveform(self, high, low, high_T, low_T):
        """
        This function writes a lambda function P(t) to the waveform attribute.
        The pre-set wave is a square wave denoted by a high pressure with
        duration high_T, and a low pressure with a duration low_T. Note that
        P(t) can be any function handle you desire, but note that the pressure-
        controller has its high-, low-, and cooldown limit.
        """
        P = lambda t: high*(np.heaviside(t%(high_T+low_T),1) - np.heaviside(t%(high_T+low_T)-high_T,1)) + \
            low*(np.heaviside(t%(high_T+low_T)-high_T,1) - np.heaviside(t%(high_T+low_T)-high_T-low_T,1))
        
        self.waveform = P
        
        
    @pyqtSlot()
    def measure(self):
        print('pressure thread started')
        
        self.isrunning = True
        start = time.time()
        old_pressure = 0
        while self.isrunning:
        
            # get time into the measurement
            timestamp = time.time() - start
            
            # Read pressure controller and emit pressure measurements
            response = self.pressurecontroller.readFlush()
            response = response.split()
            if len(response) > 0:
                if response[0] == "PS":
                    try:
                        PS1 = float(response[1])
                        self.measurement.emit(np.array([PS1, timestamp]))
                    except ValueError or IndexError:
                        pass
            
            # Write waveform if active
            if self.waveform is not None:
                new_pressure = self.waveform(timestamp)
                if new_pressure != old_pressure:
                    self.pressurecontroller.setPres(new_pressure)
                    old_pressure = new_pressure
                
                # Enter the record function
                if not self.isrecording:
                    QThread.msleep(10)
                else:
                    # pass on start time to make the GUI graph continuous
                    self.record(start)
        
        # Set pressure back to ATM and close the serial port
        self.pressurecontroller.setPres(0)
        self.pressurecontroller.goIdle()
        time.sleep(0.1)
        self.pressurecontroller.close()
        
        print('pressure thread stopped')
    
    
    def record(self, start):
        print("pressure recording started")
        
        save_directory = self._parent.save_directory
        
        PS1 = []
        timing = []
        start = time.time()
        while self.isrecording:
            
            # Read pressure controller and emit pressure measurements
            timestamp = time.time() - start
            response = self.pressurecontroller.readFlush()
            response = response.split()
            if len(response) > 0:
                if response[0] == "PS":
                    try:
                        PS1.append(float(response[1]))
                        timing.append(timestamp)
                        self.measurement.emit(np.array([PS1[-1], timestamp]))
                    except ValueError:
                        pass
            
            # Determines the sampling rate
            QThread.msleep(5)
        
        # Save measurements and close the serial port
        np.save(save_directory+'pressure_recording_sensor1', PS1)
        np.save(save_directory+'pressure_recording_timing', timing)
            
        print('pressure recording stopped')



# class PressureThread(QThread):
#     """ Pressure control dummy
#     This class is for simulating output of the pressure controller.
#     """
#     measurement = pyqtSignal(np.ndarray)
    
#     def __init__(self, pressurecontroller_handle=None):
#         self.parent = None
#         self.waveform = None
#         self.pressure_offset = 0
        
#         # QThread attributes
#         super().__init__()
#         self.isrunning = False
#         self.isrecording = False
#         self.moveToThread(self)
#         self.started.connect(self.measure)
    
#     @property
#     def parent(self):
#         return self._parent
    
#     @parent.setter
#     def parent(self, parent):
#         self._parent = parent
    
#     @property
#     def waveform(self):
#         return self._waveform
    
#     @waveform.setter
#     def waveform(self, function_handle):
#         self._waveform = function_handle
    
#     @waveform.deleter
#     def waveform(self):
#         self._waveform = None
    
#     def stop(self):
#         self.isrecording = False
#         self.isrunning = False
#         self.quit()
#         self.wait()

#     def set_pressure_stop_waveform(self, pressure):
#         del self.waveform
#         self.pressure_offset = pressure
    
#     def set_pressure_hold_stop_waveform(self, pressure):
#         del self.waveform
#         self.pressure_offset = pressure
    
#     def set_pulse_stop_waveform(self, magnitude):
#         del self.waveform
#         self.pressure_offset = magnitude
#         time.sleep(0.05)
#         self.pressure_offset = 0
    
#     def set_waveform(self, high, low, high_T, low_T):
#         P = lambda t: high*(np.heaviside(t%(high_T+low_T),1) - np.heaviside(t%(high_T+low_T)-high_T,1)) + \
#             low*(np.heaviside(t%(high_T+low_T)-high_T,1) - np.heaviside(t%(high_T+low_T)-high_T-low_T,1))
#         self.waveform = P
    
#     @pyqtSlot()
#     def measure(self):
#         print('pressure thread started')
#         self.set_waveform(-100, -200, 1, 1)
#         self.isrunning = True
#         start = time.time()
#         old_pressure = 0
#         while self.isrunning:
#             timestamp = time.time()-start
#             output = self.pressure_offset + np.random.rand(2)*10-5
#             self.measurement.emit(np.array([output[0], timestamp]))
#             if self.waveform is not None:
#                 new_pressure = self.waveform(timestamp)
#                 if new_pressure != old_pressure:
#                     self.pressure_offset = new_pressure
#                     old_pressure = new_pressure
#             if not self.isrecording:
#                 QThread.msleep(10)
#             else:
#                 self.record(start)
#         self.pressure_offset = 0
#         print('pressure thread stopped')
    
#     def record(self,start):
#         print("pressure recording started")
#         PS1 = []
#         timing = []
#         while self.isrecording:
#             output = self.pressure_offset + np.random.rand(2)*10-5
#             timestamp = time.time() - start
#             PS1.append(output[0])
#             timing.append(timestamp)
#             self.measurement.emit(np.array([PS1[-1], timestamp]))
#             QThread.msleep(5)
#         print('pressure recording stopped')
