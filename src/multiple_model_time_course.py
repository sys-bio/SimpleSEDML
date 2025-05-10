'''Provides comparisons between multiple simulations.'''

import constants as cn # type: ignore
from simple_sedml_base import SimpleSEDMLBase  # type:ignore
from typing import Optional, List

SIM_ID = "sim1"


class MultipleModelTimeCourse(SimpleSEDMLBase):
    """Provides comparisons between multiple simulations."""

    def __init__(self, start:float=cn.D_START, end:float=cn.D_END, num_step:int=cn.D_NUM_STEP,
                num_point:int=cn.D_NUM_POINT, algorithm:str=cn.D_ALGORITHM):
        """_summary_

        Args:
            start (float, optional): simulation start time. Defaults to cn.D_START.
            end (float, optional): simulation end time. Defaults to cn.D_END.
            num_step (int, optional): Defaults to cn.D_NUM_STEP.
            num_point (int, optional): Defaults to cn.D_NUM_POINT.
            algorithm (str, optional): Simulation algorithm. Defaults to cn.D_ALGORITHM.

        Example:
            from multiple_model_time_course import MultipleModelTimeCourse
            mmtc = MultipleModelTimeCourse(start=0, end=10, num_step=100)
            mmtc.addModel("model1", ref_type="sbml_str", k1=0.1, k2=0.2)
            mmtc.addModel("model2", ref_type="sbml_str", k1=0.3, k2=0.4)
            mmtc.addReport("model1.A", "model1.B", "model2.A", "model2.C")
            mmtc.addPlot("time", ["model1.A", "model2.A"], title="Comparison of A")
            sedml_str = mmtc.getSEDMLString()
        """
        self.start = start
        self.end = end
        self.num_step = num_step
        self.num_point = num_point
        self.algorithm = algorithm
        #
        self.simple = SimpleSEDMLBase()

    @staticmethod
    def _makeTaskID(model_id:str, sim_id:str=SIM_ID)->str:
        """Make a task ID from the model ID and simulation ID.

        Args:
            model_id (str): model ID
            sim_id (str): simulation ID

        Returns:
            str: task ID
        """
        return f"{model_id}_{sim_id}"

    def __str__(self)->str:
        """Construct the PhraSED-ML string. This requires:
            1. Create simulation and task directives
            2. Changing the model and report
        
        Returns:
            str: _description_
        """
        # Add the simulation directive
        self.addSimulation(SIM_ID, "uniform", start=self.start, end=self.end, num_step=self.num_step,
                    num_point=self.num_point, algorithm=self.algorithm)
        # Add a task directive for each model
        for model_id in self.model_dct.keys():
            self.addTask(self._makeTaskID(model_id), model_id, SIM_ID)
        # Update variable scopes in the plot directive to use the task instead of the model
        for plot in self.plot_dct.values():
            for var_id in plot.variable_ids:
                splits = var_id.split(".")
                if len(splits) == 2:
                    model_id = splits[0]
                    task_id = self._makeTaskID(model_id)
                    plot.changeVariableScope(model_id, task_id)
        #
        return self.getSEDMLString()