# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 10:49:06 2022

@author: tvdrb
"""

import os
import serial
import unittest


os.chdir("../..")
from PatchClamp.micromanipulator import ScientificaPatchStar
os.chdir("PatchClamp")



class MicromanipulatorTestCase(unittest.TestCase):
    
    def setUp(self):
        """ 
        The setup method only goes through set up files.
        """
        self.address = 'COM3'
        self.baud = 9600
        self.micromanipulator = ScientificaPatchStar(address=self.address, baud=self.baud)
    
    def tearDown(self):
        """
        This function will be executed after the unittests.
        """
        pass
        

#%% testcases

    def test_init_portname(self):
        name = self.micromanipulator.port
        self.assertEqual(name, self.address, 'Port name not set correctly')
    
    def test_init_baudrate(self):
        baud = self.micromanipulator.baudrate
        self.assertEqual(baud, self.baud, 'Baud rate not set correctly')
    
    def test_connection(self):
        device = serial.Serial(self.address, self.baud, timeout=3)
        status1 = device.isOpen()
        device.close()
        status2 = device.isOpen()
        self.assertEqual(status1, True, "COM-port did not open")
        self.assertEqual(status2, False, "COM-port did not close")
    
    def test_setZero_getPos(self):
        self.micromanipulator.setZero()
        x,y,z = self.micromanipulator.getPos()
        self.assertEqual([x,y,z], [0,0,0], 'SetZero or getPos not working correctly')
    
    def test_moveAbs(self):
        x1,y1,z1 = self.micromanipulator.getPos()
        self.micromanipulator.moveAbs(x=x1+10,y=y1+10,z=z1+10)
        x2,y2,z2 = self.micromanipulator.getPos()
        self.assertEqual([x2,y2,z2], [x1+10,y1+10,z1+10], 'moveAbs not working correctly')
    
    def test_moveRel(self):
        x1,y1,z1 = self.micromanipulator.getPos()
        self.micromanipulator.moveRel(dx=10,dy=10,dz=10)
        x2,y2,z2 = self.micromanipulator.getPos()
        self.assertEqual([x2,y2,z2], [x1+10,y1+10,z1+10], 'moveRel not working correctly')
    
    def test_stop(self):
        x1,y1,z1 = self.micromanipulator.getPos()
        self.micromanipulator.moveRel(dx=-20,dy=-20,dz=-20)
        self.micromanipulator.stop()
        x2,y2,z2 = self.micromanipulator.getPos()
        condition1 = x2 in range(int(x1-21),int(x1+1)+1)
        condition2 = y2 in range(int(y1-21),int(y1+1)+1)
        condition3 = z2 in range(int(z1-21),int(z1+1)+1)
        self.assertEqual([condition1,condition2,condition3], [True,True,True], 'Did not stay on trajectory')
        self.assertAmostEqual(x1, x2, 1, 'Stop did not work correctly')
        self.assertAmostEqual(y1, y2, 1, 'Stop did not work correctly')
        self.assertAmostEqual(z1, z2, 1, 'Stop did not work correctly')
        
        


#%% end of testcases



def suite():
    suite = unittest.TestSuite()
    suite.addTest(MicromanipulatorTestCase('test_init_portname'))
    suite.addTest(MicromanipulatorTestCase('test_init_baudrate'))
    suite.addTest(MicromanipulatorTestCase('test_connection'))
    suite.addTest(MicromanipulatorTestCase('test_setZero_getPos'))
    suite.addTest(MicromanipulatorTestCase('test_moveAbs'))
    suite.addTest(MicromanipulatorTestCase('test_moveRel'))
    suite.addTest(MicromanipulatorTestCase('test_stop'))
    return suite




if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
        
