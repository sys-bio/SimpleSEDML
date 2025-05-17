import SimpleSEDML.constants as cn # type: ignore
from SimpleSEDML.multiple_model_time_course import MultipleModelTimeCourse # type:ignore
from SimpleSEDML.simulation import Simulation # type:ignore
from SimpleSEDML.task import Task # type:ignore
from SimpleSEDML.model import Model # type:ignore
from SimpleSEDML.plot import Plot # type:ignore
from SimpleSEDML.report import Report # type:ignore

import pandas as pd; # type: ignore
import os
import phrasedml # type: ignore
import tellurium as te # type: ignore
import unittest


IGNORE_TEST = True
IS_PLOT = False
MODEL_ID = "model1"
MODEL2_ID = "model2"
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
MODEL2_ANT = """
model %s
    S1 -> S2; k1*S1
    S2 -> S3; k2*S2
    S3 -> S4; k3*S3
    S3 -> S1; k3*S3

    k1 = 0.1
    k2 = 0.2
    k3 = 0.3
    S1 = 10
    S2 = 0
    S3 = 0
    S4 = 0
end
""" % MODEL2_ID
MODEL_SBML = te.antimonyToSBML(MODEL_ANT)
SBML_FILE_PATH = os.path.join(cn.PROJECT_DIR, MODEL_ID)
WOLF_FILE = "Wolf2000_Glycolytic_Oscillations"
REMOVE_FILES = [SBML_FILE_PATH, WOLF_FILE]
DISPLAY_VARIABLES = ["S1", "S2"]
NUM_POINT = 100
MODEL_REFS = [MODEL_SBML, MODEL_ANT]


#############################


def assemble(*args):
        return "\n".join([str(arg) for arg in args])


#############################
# Tests
#############################
class TestMultipleModelTimeCourse(unittest.TestCase):

    def setUp(self):
        self.remove()
        self.model_refs = MODEL_REFS
        self.mmtc = MultipleModelTimeCourse(self.model_refs, start=0,
                end=10, num_point=NUM_POINT, k1=1.5,
                display_variables=DISPLAY_VARIABLES,
                is_plot=IS_PLOT)
        self.num_model = len(self.model_refs)

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
        model_refs = list(self.mmtc.model_ref_dct.keys())
        self.assertEqual(model_refs[0], MODEL_SBML)
        self.assertEqual(model_refs[1], MODEL_ANT)

    def testMakeSimulationObject(self):
        """Test the makeSimulationObject method"""
        if IGNORE_TEST:
            return
        self.mmtc._makeSimulationObject()
        simulation = list(self.mmtc.simulation_dct.values())[0]
        self.assertTrue(isinstance(simulation, Simulation))
        self.assertTrue(str(NUM_POINT-1) in simulation.getPhraSEDML())

    def testMakeTaskID(self):
        """Test the makeTaskID method"""
        if IGNORE_TEST:
            return
        task_id = self.mmtc._makeTaskID(MODEL_ID)
        self.assertEqual(task_id, "tmodel1")

    def testMakeModelObject(self):
        """Test the makeModelObject method"""
        if IGNORE_TEST:
            return
        self.mmtc._makeModelObjects()
        self.assertEqual(len(self.mmtc.model_dct), len(MODEL_REFS))
        trues = [m in ["model0", "model1"] for m in self.mmtc.model_dct.keys()]
        self.assertTrue(all(trues))

    def testMakeTaskObjects(self):
        """Test the makeTaskObject method"""
        if IGNORE_TEST:
            return
        self.mmtc._makeModelObjects()
        self.mmtc._makeTaskObjects()
        task = list(self.mmtc.task_dct.values())[0]
        self.assertTrue(isinstance(task, Task))
        self.assertTrue(task.id == "tmodel0")

    def testMakeVariables(self):
        """Test the makeTaskObject method"""
        if IGNORE_TEST:
            return
        self.mmtc._makeModelObjects()
        self.mmtc._makeVariables()
        self.assertEqual(self.mmtc.display_variables[0], "S1")
        self.assertEqual(self.mmtc.display_variables[1], "S2")
        #
        mmtc = MultipleModelTimeCourse(self.model_refs, is_plot=IS_PLOT)
        mmtc._makeModelObjects()
        mmtc._makeVariables()
        self.assertEqual(mmtc.display_variables[0], "S1")
        self.assertEqual(mmtc.display_variables[1], "S2")
        self.assertEqual(mmtc.display_variables[2], "S3")

    def testMakeReportObject(self):
        """Test the makeTaskObject method"""
        if IGNORE_TEST:
            return
        self.mmtc._makeModelObjects()
        self.mmtc._makeTaskObjects()
        self.mmtc._makeReportObject()
        report_directive = list(self.mmtc.report_dct.values())[0]
        self.assertEqual(str(report_directive).count("S1"), 2)
        self.assertEqual(str(report_directive).count("S2"), 2)

    def testMakePlotObject(self):
        """Test the makeTaskObject method"""
        if IGNORE_TEST:
            return
        self.mmtc._makeModelObjects()
        self.mmtc._makeTaskObjects()
        self.mmtc._makePlotObjects()
        for idx, plot in enumerate(self.mmtc.plot_dct.values()):
            directive = plot
            variable_name = "S" + str(idx + 1)
            self.assertTrue(variable_name in str(directive))

    def testGetPhraSEDML(self):
        if IGNORE_TEST:
            return
        self.evaluate(self.mmtc)

    def evaluate(self, mmtc:MultipleModelTimeCourse):
        """Evaluate the sedml_str and sbml_str

        Args:
            phrasedml_str (str): phraSED-ML string
        """
        phrasedml_str = mmtc.getPhraSEDML()
        sedml_str = phrasedml.convertString(phrasedml_str)
        self.assertIsNotNone(sedml_str, "SED-ML conversion failed\n" + phrasedml.getLastError())
        try:
            df = mmtc.executeSEDML(sedml_str)
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertTrue(df.shape[0] == NUM_POINT)
        except Exception as e:
            self.assertTrue(False, f"SED-ML execution failed: {e}")


if __name__ == '__main__':
    unittest.main()