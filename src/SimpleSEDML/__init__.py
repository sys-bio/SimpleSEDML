__version__ = "0.0.5"
from SimpleSEDML.simple_sedml import SimpleSEDML # type:ignore
import SimpleSEDML.constants as cn # type:ignore
getModelInformation = SimpleSEDML.getModelInformation # type:ignore
# The following "make" functions all return objects that have the following methods:
#   - getSEDML(): returns the sedml for the task
#   - getPhraSEDML(): returns the phrasedml for the task
#   - execute(): executes the task
#   - makeOMEXFile(): creates an OMEX file (first return argument is the path to the OMEX file)
makeSingleModelTimeCourse = SimpleSEDML.makeSingleModelTimeCourse # type:ignore
makeMultipleModelTimeCourse = SimpleSEDML.makeMultipleModelTimeCourse # type:ignore
