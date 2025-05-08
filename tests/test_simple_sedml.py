import src.constants as cn
from src.simple_sedml import SimpleSEDML

import numpy as np # type: ignore
import os
import pandas as pd # type: ignore
import phrasedml # type: ignore
import unittest
import warnings
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

    def makeInitialSimpleSEDML(self,
          is_model:bool=True, 
          is_simulation:bool=True,
          is_task:bool=True,
          is_report:bool=True,
          is_plot:bool=True,
          )->SimpleSEDML:
        simple = SimpleSEDML()
        if is_model:
            simple.addModel(MODEL_NAME, MODEL_SBML, ref_type="sbml_str", k1=2.5, k2= 100, is_overwrite=True)
        if is_simulation:
            simple.addSimulation("sim1", "uniform", 0, 10, 100)
        if is_task:
            simple.addTask("task1", MODEL_NAME, "sim1")
        if is_plot:
            simple.addPlot("task1.time", ["task1.S1", "task1.S2"], title="test plot", is_plot=IS_PLOT)
        if is_report:
            simple.addReport("S1", "S2")
        return simple

    def testComposeSimpleReport(self):
        if IGNORE_TEST:
            return
        simple = self.makeInitialSimpleSEDML(is_plot=False)
        # Check if the model is added correctly
        self.assertEqual(len(simple.model_dct), 1)
        self.assertEqual(len(simple.simulation_dct), 1)
        self.assertEqual(len(simple.task_dct), 1)
        self.assertEqual(len(simple.report_dct["0"].variables), 2)
        #
        df = simple.execute()
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertGreater(len(df), 0)

    def testComposeMultipleReports(self):
        if IGNORE_TEST:
            return
        simple = self.makeInitialSimpleSEDML(is_plot=False)
        simple.addReport("S3")
        simple.addReport("S4")
        # Check if the model is added correctly
        self.assertEqual(len(simple.model_dct), 1)
        self.assertEqual(len(simple.simulation_dct), 1)
        self.assertEqual(len(simple.task_dct), 1)
        self.assertEqual(len(simple.report_dct), 3)
        #
        df = simple.execute()
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertGreater(len(df), 0)

    def testComposeRepeatedTask(self):
        if IGNORE_TEST:
            return
        NUM_SAMPLE = 100
        def makePHRASEDML()->SimpleSEDML:
            simple = SimpleSEDML()
            simple.addModel(MODEL_NAME, MODEL_SBML, ref_type="sbml_str", k1=2.5, k2= 100, is_overwrite=True)
            simple.addSimulation("sim1", "uniform", 0, 10, NUM_SAMPLE)
            simple.addTask("task1", MODEL_NAME, "sim1")
            return simple
        # Works without warning
        simple = makePHRASEDML()
        simple.addReport("task1.time", "task1.S1", "task1.S2")
        df = simple.execute()
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertLessEqual(np.abs(len(df) - NUM_SAMPLE), 2)
        # Check for warning
        simple = makePHRASEDML()
        simple.addRepeatedTask("repeat1", "task1", pd.DataFrame({"k2": [1, 3, 5], "k3": [0, 10, 3]}), reset=True)
        simple.addReport("repeat1.time", "repeat1.S1", "repeat1.S2")
        with self.assertWarns(UserWarning):
            df = simple.execute()
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertGreater(len(df), 0)

    def testComposeSimplePlot(self):
        if IGNORE_TEST:
            return
        simple = self.makeInitialSimpleSEDML()
        simple.addReport("S3")
        # Check if the model is added correctly
        self.assertEqual(len(simple.model_dct), 1)
        self.assertEqual(len(simple.simulation_dct), 1)
        self.assertEqual(len(simple.task_dct), 1)
        self.assertEqual(len(simple.report_dct), 2)
        #
        df = simple.execute()
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertGreater(len(df), 0)

    def testGetModelInfo(self):
        if IGNORE_TEST:
            return
        self.simple.addModel(MODEL_NAME, MODEL_ANT, ref_type="ant_str", k1=2.5, k2= 100, is_overwrite=True)
        self.simple.addModel(MODEL2_NAME, MODEL2_ANT, ref_type="ant_str", is_overwrite=True)
        results = self.simple.getModelInfo(MODEL_NAME)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['model_id'], MODEL_NAME)
        #
        results = self.simple.getModelInfo()
        self.assertEqual(len(results), 2)

    def testMakeTimeCourse(self):
        if IGNORE_TEST:
            return
        try:
            sedml_str = SimpleSEDML.makeTimeCourse(MODEL_ANT, ["time", "S1", "S2"], start=0, end=10, num_step=100)
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")
        try:
            sedml_str = SimpleSEDML.makeTimeCourse(MODEL_ANT, ref_type="ant_str", title="my plot")
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")
        try:
            sedml_str = SimpleSEDML.makeTimeCourse(WOLF_URL, ref_type="sbml_url", title="Wolf2000")
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")
        if IS_PLOT:
            SimpleSEDML.executeSEDML(sedml_str)


if __name__ == '__main__':
    unittest.main()