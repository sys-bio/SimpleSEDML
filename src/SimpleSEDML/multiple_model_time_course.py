'''Provides comparisons between multiple simulations.'''

"""
This module provides a class for comparing multiple models with common variables
for the same time course. The class allows for the simulation of a collection of models
with the same variables and generates plots and reports for the comparisons.
The class is designed to be used with the PhraSED-ML format and provides methods
for creating simulation objects, task objects, report objects, and plot objects.

The generation of PhraSED-ML strings is done through the `getPhrasedml` method,
which constructs the string by adding the necessary directives based on the provided
model references, simulation parameters, and display variables. This "late generation" approach
allows for flexibility in model definitions since the definitions in the constructor
can reference other model definitions that occur later on.
"""

import SimpleSEDML.constants as cn # type: ignore
from SimpleSEDML.simple_sedml import SimpleSEDML  # type:ignore

import pandas as pd # type:ignore
from typing import Optional, List, Union

SIM_ID = "sim1"


class MultipleModelTimeCourse(SimpleSEDML):
    """Provides comparisons between multiple simulations."""

    def __init__(self,
                    model_refs:List[str],
                    project_id:Optional[str]=None,
                    simulation_type:str=cn.ST_UNIFORM,
                    project_dir:Optional[str]=None,
                    start:float=cn.D_START,
                    end:float=cn.D_END,
                    num_step:Optional[int]=None,
                    num_point:Optional[int]=None,
                    algorithm:Optional[str]=None,
                    display_variables:Optional[List[str]]=None,
                    is_plot:bool=True,
                    model_parameter_dct:Optional[dict]=None,
                    ):
        """Simulates a collection of models with common variables for the same time course.
        All models have the compared_variables. The outputs are:
            - plots comparing the models for each exposed variable
            - a report with the values of each variable for each model

        Args:
            project_dir (Optional[str], optional): Directory to save the files. Defaults to None.
            project_id (Optional[str], optional): Project ID. Defaults to None.
            simulation_type: type of the simulation
                    (e.g., "uniform", "uniform_stochastic", "steadystate", "onestep")
            start (float, optional): simulation start time. Defaults to cn.D_START.
            end (float, optional): simulation end time. Defaults to cn.D_END.
            num_step (int, optional): Defaults to cn.D_NUM_STEP.
            num_point (int, optional): Defaults to cn.D_NUM_POINT.
            algorithm (str, optional): Simulation algorithm. Defaults to cn.D_ALGORITHM.
            models (Optional[List[str]], optional): List of model references. Defaults to None.
            variables (Optional[List[str]], optional): List of variables to be compared. Defaults to None.
                if not provided, all variables in the model are used.
            is_plot (bool, optional): Whether to plot the results. Defaults to True.
            model_parameter_dct (Optional[dict], optional): Dictionary of model parameters whose values are changed

        Example 1: Compare two models with the same variables
            mmtc = MultipleModelTimeCourse(start=0, end=10, num_step=100,
                model_refs=[model1_file, model2_file])
            sedml_str = mmtc.getSEDMLString()

        Example 2: Compare parameterizations of the same model
            mmtc = MultipleModelTimeCourse(start=0, end=10, num_step=100,
                compared_variables=["S1", "S2", "S3"])
            mmtc.addModel(model1_str, k1=0.1, k2=0.2)
            mmtc.addModel(model1_str, k1=0.2, k2=0.2)
            mmtc.addModel(model1_str, k1=0.1, k2=0.4)
            mmtc.addModel(model1_str, k1=0.2, k2=0.4)
            sedml_str = mmtc.getSEDMLString()
        """
        #
        super().__init__(project_dir=project_dir, 
                project_id=project_id, display_variables=display_variables)
        #
        self.simulation_type = simulation_type
        self.start = start
        self.end = end
        self.num_step = num_step
        self.num_point = num_point
        self.algorithm = algorithm
        self.model_ref_dct:dict = {m: None for m in model_refs}  # type:ignore
        self.model_parameter_dct = model_parameter_dct
        self.is_plot = is_plot
        # Calculated
        self.task_ids:list = []

    @property
    def model_ids(self)->List[Union[str, None]]: 
        return list(self.model_ref_dct.values())

    def _makeSimulationObject(self):
        if not SIM_ID in self.simulation_dct:
            # Create the simulation object
            self.addSimulation(SIM_ID,
                    simulation_type=self.simulation_type,
                    start=self.start, end=self.end, num_step=self.num_step,
                    num_point=self.num_point, algorithm=self.algorithm)
    
    @staticmethod
    def _makeTaskID(model_id:str)->str:
        """Make a task ID from the model ID and simulation ID.

        Args:
            model_id (str): model ID

        Returns:
            str: task ID
        """
        return f"t{model_id}"
    
    def _makeModelObjects(self):
        for model_ref, model_id in self.model_ref_dct.items():
            if model_id is None:
                model_id = self.addModel(model_ref, is_overwrite=True,
                        parameter_dct=self.model_parameter_dct)
                self.model_ref_dct[model_ref] = model_id

    def _makeTaskObjects(self):
        """Make the task objects for the compared variables.

        Returns:
            str: task ids
        """
        if len(self.model_ids) == 0:
            raise ValueError("No models have been added to the simulation.")
        #
        for model_id in self.model_ids:
            if model_id is None:
                continue
            task_id = self._makeTaskID(model_id)
            if not task_id in self.task_dct:
                self.addTask(task_id, model_id, SIM_ID)
                self.task_ids.append(task_id)

    def _getScopedTime(self)->str:
        """Get the first scoped time variable.

        Returns:
            str: first task ID
        """
        if len(self.task_ids) == 0:
            raise ValueError("No tasks have been created. Call _makeTaskObjects() first.")
        return self.task_ids[0] + cn.SCOPE_INDICATOR + cn.TIME

    def _makeReportObject(self):
        """Make the report objects for the compared variables.
        """
        # Calculate the task ids to consider
        #
        report_variables = self.variable_collection.getScopedVariables(
                self.task_ids, is_time=False, is_parameters=True,
                is_display_variables=True).lst
        report_variables.insert(0, self._getScopedTime())
        self.addReport(*report_variables)

    def _makePlotObjects(self):
        """Make the report objects for the compared variables.
        There is one plot for each variable that plots comparisons of the models.
        """
        display_variables = list(set(self.variable_collection.display_variables) - set([cn.TIME]))
        for variable in display_variables:
            plot_id = "_".join([variable + "-" + m for m in self.task_ids])
            if not plot_id in self.plot_dct:
                variables = [m + cn.SCOPE_INDICATOR + variable for m in self.task_ids]
                self.addPlot(x_var=self._getScopedTime(), y_var=variables,
                    title=variable, id=plot_id, is_plot=self.is_plot)

    def getPhraSEDML(self, is_basename_source:bool=False)->str:
        """Construct the PhraSED-ML string. This requires:
            1. Create simulation and task directives
            2. Changing the model and report
        
        Returns:
            str: Phrased-ML string
        """
        # Make the objects if they have not been created yet
        if None in self.model_ref_dct.values():
            self._makeModelObjects()
            self._makeSimulationObject()
            self._makeTaskObjects()
            self._makeReportObject()
            self._makePlotObjects()
        #
        return super().getPhraSEDML(is_basename_source=is_basename_source)
    
    def __str__(self)->str:
        """Return PhraSED-ML string.
        
        Returns:
            str:
        """
        return self.getPhraSEDML()
    
    def execute(self, scope_str:Optional[str]=None)->pd.DataFrame:
        """Executes the script and returns the results as a DataFrame

        Args:
            scope_str: string used to scope variables. If None, uses the default scope.

        Returns:
            pd.DataFrame: DataFrame with the results
        """
        _ = self.getPhraSEDML()  # Ensure that objects have been created
        return super().execute(scope_str=scope_str)