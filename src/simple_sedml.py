from src.model import Model
from src.simulation import Simulation
from src.task import Task, RepeatedTask
from plot2d import Plot2D
from src.report import Report

import pandas as pd # type: ignore
import phrasedml # type: ignore
import tellurium as te  # type: ignore
import warnings
from typing import Optional, List, Tuple, Union

REPORT = "report"
MODEL = "model"
SIMULATION = "simulation"
TASK = "task"
REPEATED_TASK = "repeated_task"
PLOT2D = "plot2d"

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
            raise ValueError(phrasedml.getLastError())
        return sedml_str
    
    def _checkDuplicate(self, id:str, dict_type:str):
        """Checks if the ID already exists in the dictionary

        Args:
            id: ID of the model
            dict_type: type of the dictionary (model, simulation, task, repeated_task)

        Raises:
            ValueError: if the ID already exists in the dictionary
        """
        TYPE_DCT = {
            MODEL: self.model_dct,
            SIMULATION: self.simulation_dct,
            TASK: self.task_dct,
            REPEATED_TASK: self.repeated_task_dct,
            REPORT: self.report_dct,
            PLOT2D: self.plot2d_dct,
        }
        if id in TYPE_DCT[dict_type]:
            raise ValueError(f"Duplicate {dict_type} ID: {id}")

    def addModel(self, id:str, model_ref:str, ref_type:Optional[str]=None,
          model_source_path:Optional[str]=None, is_overwrite:bool=False, **parameters):
        """Adds a model to the script

        Args:
            id: ID of the model
            model_ref: reference to the model
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")
            model_source_path: path to the model source file
            is_overwrite: if True, overwrite the model if it already exists
        """
        self._checkDuplicate(id, MODEL)
        model = Model(id, model_ref, ref_type=ref_type,
              model_source=model_source_path, is_overwrite=is_overwrite, **parameters)
        self.model_dct[id] = model

    def addSimulation(self, id:str, simulation_type:str,
          start:float, end:float, steps:int, algorithm:Optional[str]=None): 
        """Adds a simulation to the script

        Args:
            simulation: Simulation object
        """
        self._checkDuplicate(id, SIMULATION)
        self.simulation_dct[id] = Simulation(id, simulation_type, start, end, steps, algorithm=algorithm)

    def addTask(self, id, model_id:str, simulation_id:str):
        """Adds a task to the script

        Args:
            id: ID of the task
            model: Model object
            simulation: Simulation object
        """
        self._checkDuplicate(id, TASK)
        task = Task(id, model_id, simulation_id)
        self.task_dct[id] = task

    def addRepeatedTask(self, id:str, subtask_id:str, parameter_df:pd.DataFrame, reset:bool=True):
        """Adds a repeated task to the script

        Args:
            repeated_task: RepeatedTask object
        """
        self._checkDuplicate(id, REPEATED_TASK)
        task = RepeatedTask(id, subtask_id, parameter_df, reset=reset)
        self.repeated_task_dct[id] = task

    def addPlot(self, plot2d:Plot2D):
        """Adds a plot to the script

        Args:
            plot2d: Plot2D object
        """
        #self.plot2d_dct.append(plot2d)
        raise NotImplementedError("Plot2D is not implemented yet.")

    def addReportVariables(self, *report_variables, metadata:Optional[dict]=None, title:Optional[str]=None):
        """Adds data to the report

        Args:
            report_variable: variable to be added to the report
            metadata: metadata for the report variable
            title: title for the report variable
        """
        if not REPORT in self.report_dct:
            self.report_dct[REPORT] = Report()
        if metadata is not None:
            self.report_dct[REPORT].metadata = metadata
        if title is not None:
            self.report_dct[REPORT].title = title
        self.report_dct[REPORT].addVariables(*report_variables)

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
        if (len(self.repeated_task_dct) > 0):
            is_repeated_task = True
        else:
            is_repeated_task = False
        if len(self.task_dct) > 1:
            is_more_than_one_task = True
        else:
            is_more_than_one_task = False
        if len(self.report_dct) > 0:
            if is_repeated_task:
                warnings.warn("Reports only generate data for the last repeated task.")
            if is_more_than_one_task:
                warnings.warn("Reports only generate data for the last task.")
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

