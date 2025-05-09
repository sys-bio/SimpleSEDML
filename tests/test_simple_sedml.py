import src.constants as cn
from src.simple_sedml import SimpleSEDML

import numpy as np # type: ignore
import os
import pandas as pd # type: ignore
import phrasedml # type: ignore
import unittest
import tellurium as te # type: ignore


IGNORE_TEST = True
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
MODEL2_NAME = "model2"
MODEL2_ANT = """
model %s
    S1 -> S2; k1*S1
    S2 -> S3; k2*S2
    S3 -> S4; k3*S3
    S4 -> S5; k4*S3

    k1 = 0.1
    k2 = 0.2
    k3 = 0.3
    k4 = 0.3
    S1 = 10
    S2 = 0
    S3 = 0
    S4 = 0
    S5 = 0
end
""" % MODEL2_NAME
MODEL_SBML = te.antimonyToSBML(MODEL_ANT)
SBML_FILE_PATH = os.path.join(cn.PROJECT_DIR, MODEL_NAME)
REMOVE_FILES = [SBML_FILE_PATH]
WOLF_URL = "https://www.ebi.ac.uk/biomodels/services/download/get-files/MODEL3352181362/3/BIOMD0000000206_url.xml"

#############################
# Tests
#############################
class TestSimpleSEDML(unittest.TestCase):

    def setUp(self):
        self.remove()
        self.simple = SimpleSEDML()

    def tearDown(self):
        # Remove files if they exist
        self.remove()

    def remove(self):
        # Remove files if they exist
        for file in REMOVE_FILES:
            if os.path.exists(file):
                os.remove(file)

    def evaluate(self, phrasedml_str:str):
        """Evaluate the sedml_str and sbml_str

        Args:
            phrasedml_str (str): phraSED-ML string
        """
        sedml_str = phrasedml.convertString(phrasedml_str)
        try:
            te.executeSEDML(sedml_str)
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")

    def testGetModelInformation(self):
        #if IGNORE_TEST:
        #    return
        info_dct = SimpleSEDML.getModelInformation(MODEL_ANT)
        self.assertEqual(len(info_dct), 3)
        self.assertTrue(all([k in info_dct for k in ["parameters", "floating_species", "model_id"]]))

    def testMakeTimeCourse(self):
        if IGNORE_TEST:
            return
        try:
            sedml_str = SimpleSEDML.makeSingleModelTimeCourse(MODEL_ANT)
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")
        try:
            sedml_str = SimpleSEDML.makeSingleModelTimeCourse(MODEL_ANT,
                    plot_variables=["time", "S1", "S2"], start=0, end=10, num_step=100)
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")
        try:
            sedml_str = SimpleSEDML.makeSingleModelTimeCourse(MODEL_ANT, title="my plot")
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")
        try:
            sedml_str = SimpleSEDML.makeSingleModelTimeCourse(WOLF_URL, title="Wolf2000")
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")
        try:
            sedml_str = SimpleSEDML.makeSingleModelTimeCourse(WOLF_URL, ref_type="sbml_url", title="Wolf2000")
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")
        if IS_PLOT:
            SimpleSEDML.executeSEDML(sedml_str)


if __name__ == '__main__':
    unittest.main()