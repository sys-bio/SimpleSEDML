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
MODEL0_ID = "model0"
MODEL1_ID = "model1"
MODEL0_ANT = """
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
""" % MODEL0_ID
MODEL1_ANT = """
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
""" % MODEL1_ID
MODEL0_SBML = te.antimonyToSBML(MODEL0_ANT)
MODEL1_SBML = te.antimonyToSBML(MODEL1_ANT)
OMEX_DIR = os.path.join(cn.TEST_DIR, "omex")
OMEX_PROJECT_DIR = os.path.join(cn.TEST_DIR, "project")
REMOVE_DIRS = [OMEX_DIR, OMEX_PROJECT_DIR]
DISPLAY_VARIABLES = ["S1", "S2"]
NUM_POINT = 100
MODEL_REFS = [MODEL0_SBML, MODEL1_SBML]
SEDML_PATH = os.path.join(OMEX_PROJECT_DIR, "project.sedml")


#############################


def assemble(*args):
        return "\n".join([str(arg) for arg in args])


#############################
# Tests
#############################
class TestMakeOmex(unittest.TestCase):

    def setUp(self):
        mmtc = MultipleModelTimeCourse(MODEL_REFS, start=0,
                end=10, num_point=NUM_POINT, k1=1.5,
                display_variables=DISPLAY_VARIABLES,
                is_plot=False)
        sedml_str = mmtc.getSEDML(is_basename_source=True)
        self.remove_files = mmtc.model_sources
        for directory in REMOVE_DIRS:
            os.makedirs(directory, exist_ok=True)
        self.makeSBMLFiles()
        with open(SEDML_PATH, "w") as f:
            f.write(sedml_str)

    def makeSBMLFiles(self):
        """Create SBML files from Antimony models"""
        # Create the SBML files
        for i, sbml_str in enumerate(MODEL_REFS):
            path = os.path.join(OMEX_PROJECT_DIR, f"model{i}.xml")
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
        validation_result = makeOMEX(project_path=OMEX_PROJECT_DIR, omex_dir=OMEX_DIR)
        archive_path = os.path.join(OMEX_DIR, "project.omex")
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            ffiles = zipf.namelist()
        self.assertIn("metadata.rdf", ffiles)
        self.assertIn("manifest.xml", ffiles)
        self.assertIn("project.sedml", ffiles)
        self.assertIn("model0.xml", ffiles)
        self.assertIn("model1.xml", ffiles)
        


if __name__ == '__main__':
    unittest.main()