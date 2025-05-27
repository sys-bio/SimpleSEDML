__version__ = "0.0.5"
from SimpleSEDML.single_model_time_course import SingleModelTimeCourse # type:ignore
from SimpleSEDML.multiple_model_time_course import MultipleModelTimeCourse # type:ignore
from SimpleSEDML.single_model_parameter_scan import SingleModelParameterScan # type:ignore
from SimpleSEDML.model_information import ModelInformation # type:ignore
import SimpleSEDML.constants as cn # type:ignore
getModelInformation = ModelInformation.get # type:ignore
# The following "make" functions all return objects that have the following methods:
#   - getSEDML(): returns the sedml for the task
#   - getPhraSEDML(): returns the phrasedml for the task
#   - execute(): executes the task
#   - makeOMEXFile(): creates an OMEX file (first return argument is the path to the OMEX file)
makeSingleModelTimeCourse = SingleModelTimeCourse # type:ignore
makeMultipleModelTimeCourse = MultipleModelTimeCourse # type:ignore
makeSingleModelParameterScan = SingleModelParameterScan # type:ignore