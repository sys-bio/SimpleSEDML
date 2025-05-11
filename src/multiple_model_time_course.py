'''Provides comparisons between multiple simulations.'''

import constants as cn # type: ignore
from simple_sedml_base import SimpleSEDMLBase  # type:ignore
from typing import Optional, List

SIM_ID = "sim1"


class MultipleModelTimeCourse(SimpleSEDMLBase):
    """Provides comparisons between multiple simulations."""

    def __init__(self, start:float=cn.D_START, end:float=cn.D_END, num_step:int=cn.D_NUM_STEP,
                    num_point:int=cn.D_NUM_POINT, algorithm:str=cn.D_ALGORITHM,
                    model_refs:Optional[List[str]]=None,
                    compare_variables:Optional[List[str]]=None,
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
        self.start = start
        self.end = end
        self.num_step = num_step
        self.num_point = num_point
        self.algorithm = algorithm
        if model_refs is not None:
            for model_ref in model_refs:
                self.addModel(model_ref)
        self.model_refs = model_refs
        if compare_variables is None:
            compare_variables = []
        self.compared_variables = compare_variables

    def _makeSimulationDirective(self):
        self.addSimulation(SIM_ID, "uniform", start=self.start, end=self.end, num_step=self.num_step,
                    num_point=self.num_point, algorithm=self.algorithm)

    def _makeTaskDirectives(self):
        """Make the task directives for the compared variables.

        Returns:
            str: task directives
        """
        if len(self.model_dct) == 0:
            raise ValueError("No models have been added to the simulation.")
        #
        for model_id in self.model_dct.keys():
            task_id = self._makeTaskID(model_id)
            self.addTask(task_id, model_id, SIM_ID)

    def _makeReportDirective(self):
        """Make the report directive for the compared variables.

        Returns:
            str: report directives
        """
        if self.compared_variables is None:
            first_model_id = list(self.model_dct.keys())[0]
            self.compared_variables = list(self.model_dct[first_model_id].getInformation().floating_species_dct.keys())
        #
        report_variables = []
        for model_id in self.model_dct.keys():
            task_prefix = self._makeTaskID(model_id) + "."
            new_report_variable = [task_prefix + v for v in self.compared_variables]
            report_variables.extend(new_report_variable)
        self.addReport(*report_variables)

    def _makeVariables(self):
        # Creates variables if it's None
        if self.compared_variables is None:
            first_model_id = list(self.model_dct.keys())[0]
            self.compared_variables = list(self.model_dct[first_model_id].getInformation().floating_species_dct.keys())

    def _makePlotDirectives(self):
        """Make the plot directives for the compared variables.

        Returns:
            str: plot directives
        """
        #
        self._makeVariables()
        for variable in self.compared_variables:
            plot_variables = []
            for model_id in self.model_dct.keys():
                task_prefix = self._makeTaskID(model_id) + "."
                plot_variables.append(task_prefix + variable)
            self.addPlot(*plot_variables, title=variable)

    @staticmethod
    def _makeTaskID(model_id:str)->str:
        """Make a task ID from the model ID and simulation ID.

        Args:
            model_id (str): model ID

        Returns:
            str: task ID
        """
        return f"t{model_id}"

    def getPhrasedml(self)->str:
        """Construct the PhraSED-ML string. This requires:
            1. Create simulation and task directives
            2. Changing the model and report
        
        Returns:
            str: _description_
        """
        ##
        # Add the simulation directive
        self.addSimulation(SIM_ID, "uniform", start=self.start, end=self.end, num_step=self.num_step,
                    num_point=self.num_point, algorithm=self.algorithm)
        # Add a task directive for each model
        for model_id in self.model_dct.keys():
            task_id = self._makeTaskID(model_id)
            self.addTask(task_id, model_id, SIM_ID)
            for plot in self.plot_dct.values():
                plot.changeVariableScope(model_id, task_id)
            # FIXME: do variable change for report
        #
        return self.self.super().getPhrasedml()
    
    def __str__(self)->str:
        """Return PhraSED-ML string.
        
        Returns:
            str:
        """
        return self.getPhrasedml()