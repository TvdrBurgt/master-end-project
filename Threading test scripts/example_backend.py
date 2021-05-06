# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 11:12:26 2021

@author: tvdrb
"""

import time
import numpy as np

from copy import copy

from PyQt5.QtCore import pyqtSignal, QObject


class AutomaticPatcher(QObject):
    newimage = pyqtSignal(np.ndarray)

    def __init__(
        self,
        camera_handle=None,
        motor_handle=None,
        micromanipulator_handle=None,
        *args,
        **kwargs
    ):
        """
        
        Parameters
        ----------
        camera_handle : TYPE, optional
            Handle to control Hamamatsu camera. The default is None.
        motor_handle : TYPE, optional
            Handle to control PI motor. The default is None.
        patchstar_handle : TYPE, optional
            Handle to control Scientifica PatchStar. Default is None.

        Returns
        -------
        None.
        
        """
        QObject.__init__(self, *args, **kwargs)
        
        self.lastview = np.random.rand(2048, 2048)

        # Static parameter settings
        self.exposure_time = 0.02  # camera exposure time (in seconds)

        # Variable paramater settings that methods will update
        self.manipulator_position_absolute = [0, 0, 0]  # x,y,z in micrometers
        self.manipulator_position_relative = [0, 0, 0]  # x,y,z in micrometers
        self.objective_position = 0  # z in micrometers/10

        """
        #====================== Connect hardware devices ======================
        # """
        # # Create a camera instance if the handle is not provided.
        # print('Connecting camera...')
        # if camera_handle == None:
        #     self.hamamatsu_cam_instance = CamActuator()
        #     self.hamamatsu_cam_instance.initializeCamera()
        # else:
        #     self.hamamatsu_cam_instance = camera_handle

        # # Create an objective motor instance if the handle is not provided.
        # print('Connecting objective motor...')
        # if motor_handle == None:
        #     self.pi_device_instance = PIMotor()
        # else:
        #     self.pi_device_instance = motor_handle

        # # Create a micromanipulator instance if the handle is not provided.
        # print('Connecting micromanipulator...')
        # if micromanipulator_handle == None:
        #     self.micromanipulator_instance = ScientificaPatchStar()
        # else:
        #     self.micromanipulator_instance = micromanipulator_handle

        """
        #==================== Get hardware device settings ====================
        """
        # self.manipulator_position_absolute = self.micromanipulator_instance.getPos()
        # self.objective_position = self.pi_device_instance.GetCurrentPos()

    def run(self):
        print("data acquisition started")
        while True:
            self.lastview = np.random.rand(2048, 2048)
            time.sleep(self.exposure_time)

    def snap_image(self):
        # Copy last camera view for display or image analysis
        snapped_image = copy(self.lastview)
        print("snap!")

        # Emit the newly snapped image for display in widget
        self.newimage.emit(snapped_image)

        return snapped_image


if __name__ == "__main__":
    instance = AutomaticPatcher()
