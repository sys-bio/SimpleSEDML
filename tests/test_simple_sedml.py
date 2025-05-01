from src.simple_sedml import SimpleSBML

import os
import time
import numpy as np
import unittest
import tellurium as te # type: ignore


IGNORE_TEST = False
IS_PLOT = False
MODEL_NAME = "model1"
MODEL_ANT = """
model %s
    S1 -> S2; k1*S1
    S2 -> S3; k2*S2
    S3 -> S4; k3*S3

    k1 = 0.1
    k2 = 0.2
    k3 = 0.3
    S1 = 10
    S2 = 0
    S3 = 0
    S4 = 0
end
""" % MODEL_NAME
MODEL_SBML = te.antimonyToSBML(MODEL_ANT)

#############################
# Tests
#############################
class TestSimpleSEDML(unittest.TestCase):

    def setUp(self):
        self.simple = SimpleSBML()

    # Define the model
    def testBuild(self):
        self.simple.addModel(MODEL_NAME, MODEL_SBML, ref_type="sbml_str", is_overwrite=True)
        self.simple.addSimulation("sim1", 0, 10, 100)
        self.simple.addTask("task1", MODEL_NAME, "sim1")
        #self.simple.addRepeatedTask("outer_scan", "model1.ps_a", "task1")
        self.simple.addPlot("plot1")

        # Check if the model is added correctly
        self.assertEqual(len(self.simple.models), 1)
        self.assertEqual(self.simple.models[0].id, MODEL_NAME)
        self.assertEqual(self.simple.models[0].id, MODEL_NAME)
        #
        sedml_str = self.simple.toSEDML()



if __name__ == '__main__':
    unittest.main()