import SimpleSEDML.constants as cn # type: ignore
from SimpleSEDML.multiple_model_time_course import MultipleModelTimeCourse # type:ignore
from SimpleSEDML.make_omex import makeOMEX # type:ignore

import pandas as pd; # type: ignore
import os
import shutil  # type: ignore
import tellurium as te # type: ignore
import unittest
import zipfile


IGNORE_TEST = False
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
MODEL1_SBML = te.antimonyToSBML(MODEL_ANT)
MODEL2_SBML = te.antimonyToSBML(MODEL2_ANT)
OMEX_DIR = os.path.join(cn.TEST_DIR, "omex")
OMEX_PROJECT_DIR = os.path.join(cn.TEST_DIR, "project")
REMOVE_DIRS = [OMEX_DIR, OMEX_PROJECT_DIR]
DISPLAY_VARIABLES = ["S1", "S2"]
NUM_POINT = 100
MODEL_REFS = [MODEL1_SBML, MODEL2_SBML]
MMTC = MultipleModelTimeCourse(MODEL_REFS, start=0,
                end=10, num_point=NUM_POINT, k1=1.5,
                display_variables=DISPLAY_VARIABLES,
                is_plot=False)
SEDML_STR = MMTC.getSEDML()
SEDML_PATH = os.path.join(OMEX_PROJECT_DIR, "sedml.xml")


#############################


def assemble(*args):
        return "\n".join([str(arg) for arg in args])


#############################
# Tests
#############################
class TestMakeOmex(unittest.TestCase):

    def setUp(self):
        self.remove_files = []
        for directory in REMOVE_DIRS:
            os.makedirs(directory, exist_ok=True)
        self.makeSBMLFiles()
        with open(SEDML_PATH, "w") as f:
            f.write(SEDML_STR)

    def makeSBMLFiles(self):
        """Create SBML files from Antimony models"""
        # Create the SBML files
        for i, sbml_str in enumerate(MODEL_REFS):
            path = os.path.join(OMEX_PROJECT_DIR, f"model_{i}.xml")
            with open(path, "w") as f:
                f.write(sbml_str)
            self.remove_files.append(path)

    def tearDown(self):
        # Remove files if they exist
        self.remove()

    def remove(self):
        # Remove files if they exist
        for file in self.remove_files:
            if os.path.exists(file):
                os.remove(file)
        for directory in REMOVE_DIRS:
            if os.path.exists(directory):
                shutil.rmtree(directory)

    def testMakeOMEXFiles(self):
        """Test the makeOMEXFiles method"""
        if IGNORE_TEST:
            return
        makeOMEX(project_path=OMEX_PROJECT_DIR, omex_dir=OMEX_DIR)
        archive_path = os.path.join(OMEX_DIR, "project.omex")
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            ffiles = zipf.namelist()
        self.assertIn("metadata.rdf", ffiles)
        self.assertIn("manifest.xml", ffiles)
        self.assertIn("sedml.xml", ffiles)
        self.assertIn("model_0.xml", ffiles)
        self.assertIn("model_1.xml", ffiles)
        


if __name__ == '__main__':
    unittest.main()