'''Provides an programmatic interface to PhraSED-ML capabilities.'''

import constants as cn # type:ignore
from model import Model  # type:ignore
from simulation import Simulation  # type:ignore
from task import Task, RepeatedTask  # type:ignore
from plot import Plot  # type:ignore
from report import Report  # type:ignore

from collections import namedtuple
import pandas as pd # type: ignore
import phrasedml # type: ignore
import tellurium as te  # type: ignore
import warnings
from typing import Optional, List, Tuple, Union


ModelInfo = namedtuple("ModelInfo", ["model_id", "parameters", "floating_species"])

"""
PhraSED-ML is strctured as a series of sections, each of which specifies a Model, Simulation, Task or repeated task.

A model section contains one or more references to models. Some of these may be indirect in that they reference a reference.
A model section may contain changes to parameters, initial conditions or other model components.


Restrictions:
  - No local variables (because this is an API)
  - No formulas (because this is an API and python can do this)
"""


class SimpleSEDMLBase(object):
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
    
    def getPhraSEDML(self)->str:
        """Creates phrasedml string from composition of sections

        Returns:
            str: SED-ML string
        """
        sections = [
            *[m.getPhraSEDML() for m in self.model_dct.values()],
            *[s.getPhraSEDML() for s in self.simulation_dct.values()],
            *[t.getPhraSEDML() for t in self.task_dct.values()],
            *[rt.getPhraSEDML() for rt in self.repeated_task_dct.values()],
            *[r.getPhraSEDML() for r in self.report_dct.values()],
            *[p.getPhraSEDML() for p in self.plot_dct.values()],
        ]
        return "\n".join(sections)
    
    def __str__(self)->str:
        """
        Get the PhraSED-ML string representation of the script.

        Returns:
            str: PhraSED-ML string
        """
        return self.getPhraSEDML()
    
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
        sedml_str = phrasedml.convertString(self.getPhraSEDML())
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
            cn.MODEL: self.model_dct,
            cn.SIMULATION: self.simulation_dct,
            cn.TASK: self.task_dct,
            cn.REPEATED_TASK: self.repeated_task_dct,
            cn.REPORT: self.report_dct,
            cn.PLOT2D: self.plot_dct,
        }
        if id in TYPE_DCT[dict_type]:
            raise ValueError(f"Duplicate {dict_type} ID: {id}")

    def addModel(self, id:str, model_ref:Optional[str]=None, ref_type:Optional[str]=None,
            model_source_path:Optional[str]=None, is_overwrite:bool=False,
            **parameters)->str:
        """Adds a model to the script

        Args:
            id: ID of the model
            model_ref: reference to the model
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")
            model_source_path: path to the model source file
            is_overwrite: if True, overwrite the model if it already exists

        Returns:
            str: ID of the model
        """
        self._checkDuplicate(id, cn.MODEL)
        model_ids = list(self.model_dct.keys())
        model = Model(id, model_ref, ref_type=ref_type,
                model_source=model_source_path, is_overwrite=is_overwrite,
                existing_model_ids=model_ids, **parameters)
        self.model_dct[id] = model
        return model.id

    def addSimulation(self,
                    id:str,
                    simulation_type:str=cn.ST_UNIFORM,
                    start:float=cn.D_START,
                    end:float=cn.D_END,
                    num_step:Optional[int]=None,
                    num_point:Optional[int]=None,
                    algorithm:Optional[str]=None): 
        """Adds a simulation to the script

        Args:
            id (str): Simulation identifier
            start (float): start time for simulation
            end (float): end time for simulation 
        """
        if algorithm is None:
            if simulation_type == cn.ST_UNIFORM:
                algorithm = cn.D_SIM_UNIFORM_ALGORITHM
            elif simulation_type == cn.ST_UNIFORM_STOCHASTIC:
                algorithm = cn.D_SIM_UNIFORM_STOCHASTIC_ALGORITHM
        self._checkDuplicate(id, cn.SIMULATION)
        self.simulation_dct[id] = Simulation(id, simulation_type=simulation_type, start=start, end=end,
                num_point=num_point, num_step=num_step, algorithm=algorithm)  # type: ignore

    def addTask(self, id, model_id:str, simulation_id:str):
        """Adds a task to the script

        Args:
            id: ID of the task
            model: Model object
            simulation: Simulation object
        """
        self._checkDuplicate(id, cn.TASK)
        task = Task(id, model_id, simulation_id)
        self.task_dct[id] = task

    def addRepeatedTask(self, id:str, subtask_id:str, parameter_df:pd.DataFrame, reset:bool=True):
        """Adds a repeated task to the script

        Args:
            repeated_task: RepeatedTask object
        """
        self._checkDuplicate(id, cn.REPEATED_TASK)
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
    
    def getAllModelInformation(self, model_id:Optional[str]=None)->dict:
        """Returns a list of information about all models

        Args:
            model_id: ID of the model. If None, returns information for all models 

        Returns: List of dictionaries structured as follows:
            "task_id": str
            "parameters": list of parameters
            "species": list of species
        """
        model_information_dct = {}
        for id, model in self.model_dct.items():
            model_information_dct[id] = model.getInformation()
            model_information_dct[id].model_id = model.id
        return model_information_dct

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