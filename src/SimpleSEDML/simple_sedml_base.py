'''Provides an programmatic interface to PhraSED-ML capabilities.'''

import SimpleSEDML.constants as cn # type:ignore
from SimpleSEDML.model import Model  # type:ignore
from SimpleSEDML.simulation import Simulation  # type:ignore
from SimpleSEDML.task import Task, RepeatedTask  # type:ignore
from SimpleSEDML.plot import Plot  # type:ignore
from SimpleSEDML.report import Report  # type:ignore
from SimpleSEDML.omex_maker import OMEXMaker  # type:ignore

from collections import namedtuple
import os
import pandas as pd # type: ignore
import phrasedml # type: ignore
import tellurium as te  # type: ignore
import tempfile # type: ignore
from typing import Optional, List, Tuple, Union
import warnings


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
    def __init__(self, 
                    project_id:Optional[str]=None,
                    project_dir:Optional[str]=None):
        """
        Args:
            project_id (Optional[str]): ID of the project. Default is "project".
            project_dir (Optional[str]): Directory where project files are stored.
                Default is current directory.
        """
        # Initializations
        if project_id is None:
            project_id = cn.D_PROJECT_ID
        #
        self.project_id = project_id
        self.project_dir = self._makeDefaultProjectDir(project_dir)
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

    @property
    def model_sources(self)->List[str]:
        """Returns a list of model sources

        Returns:
            List[str]: list of model sources
        """
        return [m.source for m in self.model_dct.values()]
    
    def getPhraSEDML(self, is_basename_source:bool=False)->str:
        """Creates phrasedml string from composition of sections

        Returns:
            str: SED-ML string
        """
        sections = [
            *[m.getPhraSEDML(is_basename_source=is_basename_source)
                    for m in self.model_dct.values()],
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

    @staticmethod 
    def antimonyToSBML(antimony_str)->str:
        """Converts an Antimony string to SBML

        Args:
            antimony_str: Antimony string

        Returns:
            str: SBML string
        """
        return te.antimonyToSBML(antimony_str)

    def getSEDML(self, is_basename_source:bool=False)->str:
        """Converts the script to a SED-ML string

        Returns:
            str: SED-ML string
        Raises:
            ValueError: if the conversion failsk
        """
        phrasedml.setWorkingDirectory(self.project_dir)
        sedml_str = phrasedml.convertString(
            self.getPhraSEDML(is_basename_source=is_basename_source))
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

    def addModel(self,
                    id:str,
                    model_ref:Optional[str]=None,
                    ref_type:Optional[str]=None,
                    model_source_path:Optional[str]=None,
                    is_overwrite:bool=False,
                    parameter_dct:Optional[dict]=None)->str:
        """Adds a model to the script

        Args:
            id: ID of the model
            model_ref: reference to the model
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")
            model_source_path: path to the model source file
            is_overwrite: if True, overwrite the model if it already exists
            parameters: changes in parameter values for the model

        Returns:
            str: ID of the model
        """
        model_ids = list(self.model_dct.keys())
        model = Model(id, model_ref=model_ref, ref_type=ref_type,
                source=model_source_path, is_overwrite=is_overwrite,
                project_dir=self.project_dir,
                existing_model_ids=model_ids, parameter_dct=parameter_dct)
        self._checkDuplicate(model.id, cn.MODEL)
        self.model_dct[model.id] = model
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
        if not is_plot:
            return
        #
        if id is None:
            id = str(self.plot_id)
            self.plot_id += 1
        plot = Plot(x_var, y_var, z_var=z_var, title=title, is_plot=is_plot)
        self.plot_dct[id] = plot
    
    def addReport(self, *report_variables, id:Optional[str]=None, is_plot:bool=True,
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
            self.report_dct[id] = Report(metadata=metadata, title=title)
        if metadata is not None:
            self.report_dct[id].metadata = metadata
        if len(title) > 0:
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
        if len(self.report_dct) > 0:
            if is_repeated_task:
                warnings.warn("Reports only generate data for the last repeated task.")
        if len(self.report_dct) > 1:
            warnings.warn("Reports only generate data for the last task.")
        te.executeSEDML(self.getSEDML())
        return te.getLastReport()   # type: ignore
    
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
    def executeSEDML(cls, sedml_str:str)->pd.DataFrame:
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
            return pd.DataFrame()
        
    def makeOMEXFile(self,
                omex_path:Optional[str]=None,
                is_write_omex:bool=True,
                sbml_master = None,
                surname:str="Anon",
                firstname:str="Anon",
                email:str="anon@nowhere.com",
                organization:str="unknown",
                url:str="http://www.unknown.com",
                description:str="Generated by SimpleSEDML",
                date:Optional[str]=None)->Tuple[str, OMEXMaker]:
        """
        Process a project directory to create a Combine archive and write it to an OMEX file.
        Args:
            project_id (str): The ID of the project. Default is "project".
            omex_path (str): Where the OMEX file will be written.
                            Default is ./<self.projec_id>.omex
            is_write_omex (bool): Whether to write the OMEX file or not.
                            Default is True.
            sbml_master (str): The path to the SBML master file.
                            Default is None.
            surname (str): The surname of the creator.
                            Default is "Anon".
            firstname (str): The first name of the creator.
                            Default is "Anon".
            email (str): The email of the creator.
                            Default is "anon@nowhere.com"
            organization (str): The organization of the creator.
                            Default is "unknown".
            url (str): The URL of the creator.
                            Default is "http://www.unknown.com".
            description (str): The description of the project.
                            Default is "Generated by SimpleSEDML".  
            date (str): The date of the project.

        Returns:
            path to the OMEX file (str): The path to the OMEX file.
            OMEXMaker: An instance of the OMEXMaker class.
                validateOMEX() method can be used to validate the OMEX file.
                cleanUp() method can be used to remove the temporary files.
        """
        # Initializations
        if omex_path is None:
            omex_dir = os.getcwd()
            omex_dir = os.path.join(omex_dir, self.project_id + ".omex")
        # Create the SEDML File
        sedml_str = self.getSEDML(is_basename_source=True)
        sedml_path = os.path.join(self.project_dir, self.project_id + ".sedml")
        with open(sedml_path, "w") as f:
            f.write(sedml_str)
        # Create the OMEX file
        maker = OMEXMaker(project_id=self.project_id, omex_path=omex_path,
                    project_path=self.project_dir)
        maker.make(is_write_omex=is_write_omex,
                sbml_master=sbml_master, surname=surname,
                firstname=firstname, email=email,
                organization=organization, url=url,
                description=description, date=date)
        return maker.omex_path, maker
    
    @staticmethod
    def _makeDefaultProjectDir(project_dir:Union[str, None])->str:
        """Creates a default project directory in a temporary location

        Args:
            project_dir: path to the project directory. If None, a temporary directory is created.

        Returns:
            str: path to the project directory
        """
        if project_dir is not None:
            new_project_dir = str(project_dir)
        else:
            new_project_dir = tempfile.mkdtemp()
        return new_project_dir