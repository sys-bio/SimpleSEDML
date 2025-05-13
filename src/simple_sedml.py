'''API for SimpleSEDML'''

import constants as cn  # type: ignore
from simple_sedml_base import SimpleSEDMLBase  # type:ignore
from single_model_time_course import SingleModelTimeCourse  # type:ignore
import model  # type:ignore

import numpy as np  # type:ignore
import pandas as pd  # type:ignore
import tellurium as te  # type:ignore
from typing import Optional, List, Union



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
    def getModelInformation(cls, model_ref:str,
            ref_type:Optional[str]=None)->Union[List, model.ModelInformation]:
        """Get the model global parameters and floating species.

        Args:
            model_ref: reference to the model (cannot be a model ID)
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")

        Returns:
            model.ModelInformation: named tuple with the following fields:
                - model_name: name of the model
                - parameters: list of global parameters
                - floating_species: list of floating species
                - boundary_species: list of boundary species
                - num_reaction: number of reactions
                - num_species: number of species
        """
        a_model = model.Model("dummy", model_ref, ref_type=ref_type,
                is_overwrite=True)
        return a_model.getInformation()

    @classmethod 
    def makeSingleModelTimeCourse(cls,
            model_ref:str,
            ref_type:Optional[str]=None,
            plot_variables:Optional[List[str]]=None,
            start:float=cn.D_START,
            end:float=cn.D_END,
            num_step:Optional[int]=None,
            num_point:Optional[int]=None,
            time_course_id:Optional[str]=None,
            title:Optional[str]=None,
            algorithm:Optional[str]=None,
            is_plot:bool=True,
            **parameters)->SingleModelTimeCourse:
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
            is_plot: if True, plot the results
            parameters: parameters to be passed to the model

        Returns:
            SingleModelTimeCourse: a time course simulation object
        """
        smtc = SingleModelTimeCourse(
            model_ref=model_ref,
            ref_type=ref_type,
            display_variables=plot_variables,
            start=start,
            end=end,
            num_step=num_step,
            num_point=num_point,
            time_course_id=time_course_id,
            title=title,
            algorithm=algorithm,
            is_plot=is_plot,
            **parameters
        )
        return smtc