'''Provides comparisons between multiple simulations.'''

"""
This module provides a class for comparing multiple models with common variables
for the same time course. The class allows for the simulation of a collection of models
with the same variables and generates plots and reports for the comparisons.
The class is designed to be used with the PhraSED-ML format and provides methods
for creating simulation directives, task directives, report directives, and plot directives.

The generation of PhraSED-ML strings is done through the `getPhrasedml` method,
which constructs the string by adding the necessary directives based on the provided
model references, simulation parameters, and display variables. This "late generation" approach
allows for flexibility in model definitions since the definitions in the constructor
can reference other model definitions that occur later on.
"""

import constants as cn # type: ignore
from simple_sedml_base import SimpleSEDMLBase  # type:ignore
from typing import Optional, List

SIM_ID = "sim1"


class MultipleModelTimeCourse(SimpleSEDMLBase):
    """Provides comparisons between multiple simulations."""

    def __init__(self,
                    model_refs:List[str],
                    start:float=cn.D_START,
                    end:float=cn.D_END,
                    num_step:Optional[int]=None,
                    num_point:Optional[int]=None,
                    algorithm:str=cn.D_ALGORITHM,
                    time_course_id:Optional[str]=None,
                    display_variables:Optional[List[str]]=None,
                    **parameter_dct,
                    ):
        """Simulates a collection of models with common variables for the same time course.
        All models have the compared_variables. The outputs are:
            - plots comparing the models for each exposed variable
            - a report with the values of each variable for each model

        Args:
            start (float, optional): simulation start time. Defaults to cn.D_START.
            end (float, optional): simulation end time. Defaults to cn.D_END.
            num_step (int, optional): Defaults to cn.D_NUM_STEP.
            num_point (int, optional): Defaults to cn.D_NUM_POINT.
            algorithm (str, optional): Simulation algorithm. Defaults to cn.D_ALGORITHM.
            models (Optional[List[str]], optional): List of model references. Defaults to None.
            variables (Optional[List[str]], optional): List of variables to be compared. Defaults to None.
                if not provided, all variables in the model are used.
            parameters (Optional[dict], optional): Dictionary of parameters whose values are changed

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
        # Error checks
        if len(model_refs) == 0:
            raise ValueError("No models have been added to the simulation.")
        #
        super().__init__()
        #
        self.start = start
        self.end = end
        self.num_step = num_step
        self.num_point = num_point
        self.algorithm = algorithm
        self.model_refs = model_refs
        self.time_course_id = time_course_id
        if display_variables is None:
            display_variables = []
        self.display_variables = display_variables
        self.parameter_dct = parameter_dct
    
    def _makeSimulationDirective(self):
        self.addSimulation(SIM_ID, "uniform", start=self.start, end=self.end, num_step=self.num_step,
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

    def _makeTaskDirectives(self):
        """Make the task directives for the compared variables.

        Returns:
            str: task directives
        """
        if len(self.model_dct) == 0:
            raise ValueError("No models have been added to the simulation.")
        #
        for model_id in self.model_refs:
            task_id = self._makeTaskID(model_id)
            self.addTask(task_id, model_id, SIM_ID)

    def _makeScopePrefix(self, model_id:str)->str:
        """Makes the scoping prefix for the compared variables.

        Args:
            model_id (str): model ID

        Returns:
            str: task name
        """
        return self._makeTaskID(model_id) + "."
    
    def _makeVariables(self):
        # Creates variables if it's None
        if self.display_variables is None:
            first_model_id = list(self.model_dct.keys())[0]
            self.display_variables = list(self.model_dct[first_model_id].getInformation().floating_species_dct.keys())

    def _makeReportDirective(self, task_ids:List[str]):
        """Make the report directive for the compared variables.

        Args:
            task_ids: list of task ids

        Returns:
            str: report directives
        """
        # Calculate the task ids to consider
        # Handle the case where no variables are provided
        self._makeVariables()
        #
        report_variables = []
        for variable in self.display_variables:
            new_report_variables = [self._makeScopePrefix(m) + variable for m in task_ids]
            report_variables.extend(new_report_variables)
        self.addReport(*report_variables)

    def _makePlotDirective(self, task_ids:List[str]):
        """Make the report directive for the compared variables.
        There is one plot for each variable that plots comparisons of the models.

        Args:
            task_ids: list of task ids

        Returns:
            str: report directives
        """
        #
        self._makeVariables()
        for variable in self.display_variables:
            plot_variables = [self._makeScopePrefix(m) + variable for m in task_ids]
            self.addPlot(*plot_variables, title=variable)

    def getPhraSEDML(self)->str:
        """Construct the PhraSED-ML string. This requires:
            1. Create simulation and task directives
            2. Changing the model and report
        
        Returns:
            str: Phrased-ML string
        """
        # Add the models specified in the constructors
        exclude_ids = list(self.model_dct.keys())
        for idx, model_ref in enumerate(self.model_refs):
            model_id = f"model{idx}"
            self.addModel(model_id, model_ref, is_overwrite=True, **self.parameter_dct)
        # Calculate the task ids to consider
        task_ids = list(set(self.model_dct.keys()) - set(exclude_ids))
        # Add the other directives
        self._makeSimulationDirective()
        self._makeTaskDirectives()
        self._makeReportDirective(task_ids)
        self._makePlotDirectives(task_ids)
        #
        return self.self.super().getPhrasedml()
    
    def __str__(self)->str:
        """Return PhraSED-ML string.
        
        Returns:
            str:
        """
        return self.getPhraSEDML()