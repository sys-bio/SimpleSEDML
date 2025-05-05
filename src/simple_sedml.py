from src.model import Model
from src.simulation import Simulation
from src.task import Task, RepeatedTask
from plot2d import Plot2D
from src.report import Report

import pandas as pd # type: ignore
import phrasedml # type: ignore
import tellurium as te  # type: ignore
from typing import Optional, List, Tuple, Union

REPORT = "report"

"""
PhraSED-ML is strctured as a series of sections, each of which specifies a Model, Simulation, Task or repeated task.

A model section contains one or more references to models. Some of these may be indirect in that they reference a reference.
A model section may contain changes to parameters, initial conditions or other model components.


Restrictions:
  - No local variables (because this is an API)
  - No formulas (because this is an API and python can do this)
"""


class SimpleSBML(object):
    """A directive can consist of many sections each of which species a Model, Simulation, Task or repeated task,
    and an action (plot or report).

    Args:
        object (_type_): _description_
    """
    def __init__(self)->None:
        # Dictionary of script elements, indexed by their section ID
        self.model_dct:dict = {}
        self.simulation_dct:dict = {}
        self.task_dct:dict = {}
        self.repeated_task_dct:dict = {}
        self.report_dct:dict = {}
        self.plot2d_dct:dict = {}
    
    def __str__(self)->str:
        """Creates phrasedml string from composition of sections

        Returns:
            str: SED-ML string
        """
        sections = [
            *[str(m) for m in self.model_dct.values()],
            *[str(s) for s in self.simulation_dct.values()],
            *[str(t) for t in self.task_dct.values()],
            *[str(rt) for rt in self.repeated_task_dct.values()],
            *[str(r) for r in self.report_dct.values()],
            *[str(p) for p in self.plot2d_dct.values()],
        ]
        return "\n".join(sections)

    def getSEDML(self)->str:
        """Converts the script to a SED-ML string

        Returns:
            str: SED-ML string
        Raises:
            ValueError: if the conversion failsk
        """
        sedml_str = phrasedml.convertString(str(self))
        if sedml_str is None:
            raise ValueError(phrasedml.getLastPhrasedError())
        return sedml_str

    @property 
    def sedml_str(self)->str:
        """Converts the script to a SED-ML string

        Returns:
            str: SED-ML string
        """
        return phrasedml.convertString(str(self))

    def addModel(self, id:str, model_ref:str, ref_type:Optional[str]=None,
          model_source_path:Optional[str]=None, is_overwrite:bool=False):
        """Adds a model to the script

        Args:
            id: ID of the model
            model_ref: reference to the model
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")
            model_source_path: path to the model source file
            is_overwrite: if True, overwrite the model if it already exists
        """
        model = Model(id, model_ref, ref_type=ref_type,
              model_source=model_source_path, is_overwrite=is_overwrite)
        self.model_dct[id] = model

    def addSimulation(self, id:str, simulation_type:str,
          start:float, end:float, steps:int, algorithm:Optional[str]=None): 
        """Adds a simulation to the script

        Args:
            simulation: Simulation object
        """
        self.simulation_dct[id] = Simulation(id, simulation_type, start, end, steps, algorithm=algorithm)

    def addTask(self, id, model:Model, simulation:Simulation):
        """Adds a task to the script

        Args:
            id: ID of the task
            model: Model object
            simulation: Simulation object
        """
        task = Task(id, model, simulation)
        self.task_dct[id] = task

    def addRepeatedTask(self, id:str, subtask:Task, parameter_df:pd.DataFrame, reset:bool=True):
        """Adds a repeated task to the script

        Args:
            repeated_task: RepeatedTask object
        """
        task = RepeatedTask(id, subtask, parameter_df, reset=reset)
        self.repeated_task_dct[id] = task

    def addPlot(self, plot2d:Plot2D):
        """Adds a plot to the script

        Args:
            plot2d: Plot2D object
        """
        #self.plot2d_dct.append(plot2d)
        raise NotImplementedError("Plot2D is not implemented yet.")

    def addReportVariable(self, report_variable):
        """Adds data to the report

        Args:
            data: 
        """
        if len(self.report_dct) == 0:
            # Create a new report
            self.report_dct[REPORT] = report
        else:
        self.report_dct.append(report)
        raise NotImplementedError("Report is not implemented yet.")

    def getGlobalParameters(self)->List[str]:
        """Returns a list of global parameters
           For the models in the SimpleSBML.

        Returns:
            List[str]: list of global parameters
        """
        parameters = []
        for model in self.model_dct.values():
            if len(model.model_str) > 0:
                rr = te.loadSBMLModel(model.model_str)
                parameters.append(rr.getGlobalParameterIds())
        return parameters
    
    def execute(self)->pd.DataFrame:
        """Executes the script and returns the results as a DataFrame

        Returns:
            pd.DataFrame: DataFrame with the results
        """
        te.executeSEDML(self.getSEDML())
        return te.getLastReport()
    
    def validate(self):
        """
        Validates the script and returns a list of errors.
        Checks for:
        1. At least one model is defined.
        2. At least one simulation is defined.
        3. At least one task is defined.
        4. At least one output is defined.
        5. All referenced task IDs are defined.
        """
        raise NotImplementedError("Validation is not implemented yet.")

