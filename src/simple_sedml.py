from src.model import Model, ANT_STR
from src.simulation import Simulation
from src.task import Task, RepeatedTask
from plot import Plot
from src.report import Report

from collections import namedtuple
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
TIME_COURSE = "time_course"

ModelInfo = namedtuple("ModelInfo", ["model_id", "parameters", "floating_species"])

"""
PhraSED-ML is strctured as a series of sections, each of which specifies a Model, Simulation, Task or repeated task.

A model section contains one or more references to models. Some of these may be indirect in that they reference a reference.
A model section may contain changes to parameters, initial conditions or other model components.


Restrictions:
  - No local variables (because this is an API)
  - No formulas (because this is an API and python can do this)
"""


class SimpleSEDML(object):
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
        self.plot_dct:dict = {}
        #
        self.report_id = 0
        self.plot_id = 0
        self.time_course_id = 0
    
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
            *[str(p) for p in self.plot_dct.values()],
        ]
        return "\n".join(sections)
    
    def antimonyToSBML(antimony_str)->str:
        """Converts an Antimony string to SBML

        Args:
            antimony_str: Antimony string

        Returns:
            str: SBML string
        """
        return te.antimonyToSBML(antimony_str)

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
            PLOT2D: self.plot_dct,
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
          start:float, end:float, num_step:int, algorithm:Optional[str]=None): 
        """Adds a simulation to the script

        Args:
            simulation: Simulation object
        """
        self._checkDuplicate(id, SIMULATION)
        self.simulation_dct[id] = Simulation(id, simulation_type, start, end, num_step, algorithm=algorithm)

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

    def addPlot(self, x_var:str, y_var:Union[str, List[str]], z_var:Optional[str]=None, title:Optional[str]=None,
                id:Optional[str]=None,
                is_plot:bool=True)->None:  
        """
        Plot class to represent a plot in the script.
        Args:
            x_var (str): x variable
            y_var (str): y variable or list of y variables
            z_var (str, optional): z variable. Defaults to None.
            title (str, optional): title of the plot. Defaults to None.
            id (str, optional): ID of the plot. Defaults to None.
            is_plot (bool, optional): if True, plot the data. Defaults to True.
        """
        if id is None:
            id = str(self.plot_id)
            self.plot_id += 1
        plot = Plot(x_var, y_var, z_var=z_var, title=title, is_plot=is_plot)
        self.plot_dct[id] = plot
    
    def addReport(self, *report_variables, id:Optional[str]=None,
          metadata:Optional[dict]=None, title:str=""):
        """Adds data to the report

        Args:
            id: ID of the report
            report_variable: variable to be added to the report
            metadata: metadata for the report variable
            title: title for the report variable
        """
        if id is None:
            id = str(self.report_id)
            self.report_id += 1
        if not id in self.report_dct.keys():
            if len(title) == 0:
                title = f"Report {id}"
            self.report_dct[id] = Report(metadata=metadata, title=title)
        if metadata is not None:
            self.report_dct[id].metadata = metadata
        if title is not None:
            self.report_dct[id].title = title
        self.report_dct[id].addVariables(*report_variables)

    def _getModelInfo(self, model_id)->ModelInfo:
        """Returns information about model ID, parameters, floating species and fixed species.

        Args:
            model_id (str):

        Returns: ModelInfo
        """
        if model_id not in self.model_dct:
            raise ValueError(f"Model ID {model_id} not found.")
        model = self.model_dct[model_id]
        rr = te.loadSBMLModel(model.sbml_str)
        model_info = ModelInfo(
            model_id=model.id,
            parameters=rr.getGlobalParameterIds(),
            floating_species=rr.getFloatingSpeciesIds(),
        )
        return model_info
    
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
    
    def getModelInfo(self, model_id:Optional[str]=None)->List[dict]:
        """Returns a dictionary with the model information

        Args:
            model_id: ID of the model. If None, returns information for all models 

        Returns: List of dictionaries structured as follows:
            "task_id": str
            "parameters": list of parameters
            "species": list of species
        """
        info_dcts:list = []
        for model in self.model_dct.values():
            if (model_id is not None) and (model.id != model_id):
                continue
            model_info = self._getModelInfo(model.id)
            info_dct = dict(
                  model_id=model_info.model_id,
                  parameters=model_info.parameters,
                  floating_species=model_info.floating_species
            ) 
            info_dcts.append(info_dct)
        return info_dcts

    @classmethod 
    def makeTimeCourse(cls,
         model_ref:str,
         plot_variables:Optional[str]=None,
         ref_type:str=ANT_STR,
         start:float=0, end:float=5, num_step:int=50,
         time_course_id:Optional[str]=None,
         title:Optional[str]=None,
         algorithm:Optional[str]=None,
         **parameters)->str:
        """Creates a time course simulation

        Args:
            model_ref: reference to the model
            plot_variables: variables to be plotted
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")
            start: start time
            end: end time
            num_step: number of steps
            time_course_id: ID of the time course simulation
            algorithm: algorithm to use for the simulation
            title: title of the plot
            parameters: parameters to be passed to the model

        Returns:
            str: SEDML
        """
        if time_course_id is None:
            time_course_id = TIME_COURSE
        model_id = f"{time_course_id}_model"
        sim_id = f"{time_course_id}_sim"
        task_id = f"{time_course_id}_task"
        if title is None:
            title = ""
        #
        simple = cls()
        simple.addModel(model_id, model_ref, ref_type=ref_type, is_overwrite=True, **parameters)
        if plot_variables is None:
            variable_dct = simple.getModelInfo(model_id)[0]
            plot_variables = variable_dct['floating_species']
            plot_variables.insert(0, "time")   # type: ignore
        simple.addSimulation(sim_id, "uniform", start, end, num_step, algorithm=algorithm)
        simple.addTask(task_id, model_id, sim_id)
        x1_var = plot_variables[0]
        y_vars = plot_variables[1:]
        simple.addPlot(x1_var, y_vars, title=title)
        return simple.getSEDML()
    
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

    @classmethod
    def executeSEDML(cls, sedml_str:str)->Union[None, pd.DataFrame]:
        """Executes the SED-ML string and returns the results as a DataFrame

        Args:
            sedml_str: SED-ML string

        Returns:
            pd.DataFrame: DataFrame with the results
        """
        try:
            te.executeSEDML(sedml_str)
        except Exception as e:
            raise RuntimeError(f"SED-ML execution failed: {e}")
        # Return a DataFrame if there is a report
        num_report = sedml_str.count("<report id=")
        if num_report > 1:
            warnings.warn("Only generate data for the last report.")
        if num_report >= 1:
            df = te.getLastReport()
            if df is None:
                raise ValueError("No report found.")
            return df
        else:
            return None
