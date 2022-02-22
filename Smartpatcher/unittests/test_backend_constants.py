# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 21:51:02 2021

@author: tvdrb
"""


import unittest

import os
import json

os.chdir("../..")
from PatchClamp.smartpatcher_frontend import PatchClampUI
os.chdir("PatchClamp")



class BackendConstantsTestCase(unittest.TestCase):

    def setUp(self):
        """ 
        The setup method only goes through set up files. Remember that we run
        every file of the smartpatcher_backend relative to Tupolev.py because
        the octoscope control software is not a standalone executable yet.
        """
        self.ui = PatchClampUI()
        with open("autopatch_configuration.txt", "r") as json_infile:
            self.constants = json.load(json_infile)
        with open("unittest-TestCase_autopatch_configuration.txt", "w") as json_outfile:
            json.dump(self.constants, json_outfile)
    
    def tearDown(self):
        """
        The autopatch_constants can be changed bust must be set back unaltered
        when tests are done.
        """
        with open("autopatch_configuration.txt", "w") as json_outfile:
            json.dump(self.constants, json_outfile)
        os.remove("unittest-TestCase_autopatch_configuration.txt")
            
#%% testcases
    def test_json_read(self):
        self.ui.backend.update_constants_from_JSON()
        for _, (attribute, constant) in enumerate(self.constants.items()):
            self.assertEqual(getattr(self.ui.backend,attribute), constant, 'JSON updater failed')
    
    def test_pixel_size(self):
        self.ui.backend.pixel_size = 1
        self.assertEqual(self.ui.backend.pixel_size, 1, 'pixel_size property damaged')
    
    def test_pipette_orientation(self):
        self.ui.backend.pipette_orientation = 1
        self.assertEqual(self.ui.backend.pipette_orientation , 1, 'pipette_orientation property damaged')
    
    def test_pipette_diameter(self):
        self.ui.backend.pipette_diameter = 1
        self.assertEqual(self.ui.backend.pipette_diameter, 1, 'pipette_diameter damaged')
        
    def test_rotation_angles(self):
        self.ui.backend.rotation_angles = [1,1,1]
        self.assertEqual(self.ui.backend.rotation_angles, [1,1,1], 'rotation_angles property damaged')
    
    def test_json_write(self):
        self.ui.backend.pixel_size = 2
        self.ui.backend.pipette_orientation = 2
        self.ui.backend.pipette_diameter = 2
        self.ui.backend.rotation_angles = [2,2,2]
        self.ui.backend.write_constants_to_JSON()
        with open("autopatch_configuration.txt", "r") as json_infile:
            constants = json.load(json_infile)
        for _, (attribute, constant) in enumerate(constants.items()):
            self.assertEqual(getattr(self.ui.backend,attribute), constant, 'JSON writer failed')
#%% end of testcases


def suite():
    suite = unittest.TestSuite()
    suite.addTest(BackendConstantsTestCase('test_json_read'))
    suite.addTest(BackendConstantsTestCase('test_pixel_size'))
    suite.addTest(BackendConstantsTestCase('test_pipette_orientation'))
    suite.addTest(BackendConstantsTestCase('test_pipette_diameter'))
    suite.addTest(BackendConstantsTestCase('test_rotation_angles'))
    suite.addTest(BackendConstantsTestCase('test_json_write'))
    return suite



if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())