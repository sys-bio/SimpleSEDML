'''API for SimpleSEDML'''

from simple_sedml_base import SimpleSEDMLBase  # type:ignore

import numpy as np  # type:ignore
import pandas as pd  # type:ignore
import tellurium as te  # type:ignore
from typing import Optional

TIME_COURSE = "time_course"


"""
PhraSED-ML is strctured as a series of sections, each of which specifies a Model, Simulation, Task or repeated task.

A model section contains one or more references to models. Some of these may be indirect in that they reference a reference.
A model section may contain changes to parameters, initial conditions or other model components.


Restrictions:
    - No local variables (because this is an API)
    - No formulas (because this is an API and python can do this)
"""

class SimpleSEDML(SimpleSEDMLBase):

    @classmethod
    def getModelInformation(cls, model_ref:str, ref_type:Optional[str]=None)->dict:
        """Get the model global parameters and floating species.

        Args:
            model_ref: reference to the model
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")

        Returns:
            str: SEDML
        """
        simple = cls()
        task_id = "task1"
        simple.addModel(task_id, model_ref, ref_type=ref_type, is_overwrite=True)
        return simple.getModelInfo(task_id)[0]

    @classmethod 
    def makeSingleModelTimeCourse(cls,
            model_ref:str,
            ref_type:Optional[str]=None,
            plot_variables:Optional[str]=None,
            start:float=0, end:float=5, num_step:int=50,
            time_course_id:Optional[str]=None,
            title:Optional[str]=None,
            algorithm:Optional[str]=None,
            **parameters)->str:
        """Creates a time course simulation

        Args:
            model_ref: reference to the model
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")
            plot_variables: variables to be plotted
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