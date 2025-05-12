import constants as cn # type: ignore
from multiple_model_time_course import MultipleModelTimeCourse # type:ignore
from simulation import Simulation # type:ignore

import pandas as pd; # type: ignore
import os
import phrasedml # type: ignore
import tellurium as te # type: ignore
import unittest


IGNORE_TEST = False
IS_PLOT = False
MODEL_ID = "model1"
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
""" % MODEL_ID
MODEL_SBML = te.antimonyToSBML(MODEL_ANT)
SBML_FILE_PATH = os.path.join(cn.PROJECT_DIR, MODEL_ID)
WOLF_FILE = "Wolf2000_Glycolytic_Oscillations"
REMOVE_FILES = [SBML_FILE_PATH, WOLF_FILE]
DISPLAY_VARIABLES = ["S1", "S2"]
NUM_POINT = 100


#############################
def evaluate(phrasedml_str:str):
    """Evaluate the sedml_str and sbml_str

    Args:
        phrasedml_str (str): phraSED-ML string
    """
    sedml_str = phrasedml.convertString(phrasedml_str)
    try:
        te.executeSEDML(sedml_str)
        return True, ""
    except Exception as e:
        return False, f"SED-ML execution failed: {e}"

def assemble(*args):
        return "\n".join([str(arg) for arg in args])


#############################
# Tests
#############################
class TestMultipleModelTimeCourse(unittest.TestCase):

    def setUp(self):
        self.mmtc = MultipleModelTimeCourse([MODEL_ANT, MODEL_SBML], start=0, end=10, num_point=NUM_POINT, k1=1.5,
                display_variables=DISPLAY_VARIABLES)
        self.remove()

    def tearDown(self):
        # Remove files if they exist
        self.remove()

    def remove(self):
        # Remove files if they exist
        for file in REMOVE_FILES:
            if os.path.exists(file):
                os.remove(file)

    def testConstructor(self):
        """Test the constructor of MultipleModelTimeCourse"""
        if IGNORE_TEST:
            return
        self.assertEqual(self.mmtc.start, 0)
        self.assertEqual(self.mmtc.end, 10)
        self.assertEqual(self.mmtc.num_point, 100)
        self.assertEqual(self.mmtc.model_refs[0], MODEL_ANT)
        self.assertEqual(self.mmtc.model_refs[1], MODEL_SBML)

    def testMakeSimulationDirective(self):
        """Test the makeSimulationDirective method"""
        if IGNORE_TEST:
            return
        self.mmtc._makeSimulationDirective()
        simulation = list(self.mmtc.simulation_dct.values())[0]
        self.assertTrue(isinstance(simulation, Simulation))
        self.assertTrue(str(NUM_POINT-1) in simulation.getPhraSEDML())


if __name__ == '__main__':
    unittest.main()