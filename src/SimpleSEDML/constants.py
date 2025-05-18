import os

PROJECT_DIR = os.path.dirname(__file__)
for _ in range(2):
    PROJECT_DIR = os.path.dirname(PROJECT_DIR)
SRC_DIR = os.path.join(PROJECT_DIR, "src")
TEST_DIR = os.path.join(SRC_DIR, "tests")
# Reference types
SBML_STR = "sbml_str"
ANT_STR = "ant_str"
SBML_FILE = "sbml_file"
ANT_FILE = "ant_file"
SBML_URL = "sbml_url"
MODEL_ID = "model_id"
MODEL_REF_TYPES = [SBML_STR, ANT_STR, SBML_FILE, ANT_FILE, SBML_URL, MODEL_ID]
#
REPORT = "report"
MODEL = "model"
SIMULATION = "simulation"
TASK = "task"
TIME = "time"
REPEATED_TASK = "repeated_task"
PLOT2D = "plot2d"
TIME_COURSE = "time_course"
# Simulation parameters
ST_UNIFORM = "uniform"
ST_STEADY_STATE = "steady_state"
ST_UNIFORM_STOCHASTIC = "uniform_stochastic"
# Default values
D_ALGORITHM = "CVODE"
D_END = 5
D_NUM_STEP = 10
D_NUM_POINT = D_NUM_STEP + 1
D_REF_TYPE = ANT_STR
D_SIM_TYPE  = ST_UNIFORM
D_SIM_UNIFORM_ALGORITHM = "CVODE"
D_SIM_UNIFORM_STOCHASTIC_ALGORITHM = "gillespie"
D_START = 0
# File extensions
ANT_EXT = ".ant"
XML_EXT = ".xml"