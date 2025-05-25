'''Evaluates multiple values of parameters on a single model.'''

"""
Produces a plot with a curve for each display variable and the x-axis are
the values of the scan parameters.
Produces a report.
"""

from SimpleSEDML.simple_sedml_base import SimpleSEDMLBase # type:ignore
from SimpleSEDML import constants as cn # type:ignore

import numpy as np # type:ignore
import pandas as pd # type:ignore
from typing import Optional, List


class SingleModelParameterScan(SimpleSEDMLBase):

    def __init__(self,
            model_ref:str,
            scan_parameter_dct:dict,
            project_id:Optional[str]=None,
            ref_type:Optional[str]=None,
            simulation_type:str=cn.ST_STEADYSTATE,
            project_dir:Optional[str]=None,
            display_variables:Optional[List[str]]=None,
            start:float=0,
            title:Optional[str]=None,
            algorithm:Optional[str]=None,
            model_parameter_dct:Optional[dict]=None,
            is_plot:bool=True,):

        """Creates a time course simulation

        Args:
            model_ref: reference to the model
            scan_parameter_dct: dictionary of parameters to scan over multiple values
                    Each key is a parameter name, and the value is a list of values to scan.
            project_id: ID of the project, if None, uses the default project ID
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")
            simulation_type: type of the simulation
                    (i.e., "steadystate", "onestep")
            project_dir: directory to save the files
            display_variables: variables to be plotted and included the report
            start: start time
            end: end time
            num_step: number of steps
            time_course_id: ID of the time course simulation
            algorithm: algorithm to use for the simulation
            title: title of the plot
            is_plot: if True, plot the results
            model_parameter_dct: dictionary of parameters whose values are changed

        Returns:
            SingleModelTimeCourse: a time course simulation object
        """
        # Ensure that scan parameters have the same number of values
        lengths = [len(v) for v in scan_parameter_dct.values()]
        if len(lengths) == 0:
            raise ValueError("Must provide at least one scan parameter.")
        if np.std(lengths) != 0:
            raise ValueError("All scan parameters must have the same number of values.")
        if not simulation_type in [cn.ST_STEADYSTATE, cn.ST_ONESTEP]:
            raise ValueError(f"Invalid simulation type: {simulation_type}. "
                    "Only 'steadystate' and 'onestep' are supported for parameter scans.")
        #
        super().__init__(project_dir=project_dir, project_id=project_id,
                display_variables=display_variables)
        # Construct the IDs
        self.model_id = f"m_{self.project_id}"
        self.sim_id = f"s_{self.project_id}"
        self.subtask_id = f"bt_{self.project_id}" # base task for the repeated task
        self.repeatedtask_id = f"rt_{self.project_id}" # repeated task
        self.report_id = f"r_{self.project_id}"   # type: ignore
        self.plot_id = f"p_{self.project_id}"  # type: ignore
        # Set the title
        self.is_plot = is_plot
        if title is None:
            title = ""
        self.scan_parameter_dct = scan_parameter_dct
        self.addModel(self.model_id, model_ref=model_ref, ref_type=ref_type,
                is_overwrite=True,
                parameter_dct=model_parameter_dct)
        self.addSimulation(self.sim_id, simulation_type=simulation_type,
                algorithm=algorithm, start=start)
        self.base_model = self.model_dct[self.model_id]
        # Parameter scan does not include time as a display variable
        if cn.TIME in self.display_variables:
            self._display_variables = self._display_variables.remove(cn.TIME)   # type:ignore
        self._addRepeatedTask()
        self._addReport()
        self._addPlot()

    def _addRepeatedTask(self):
        """Adds a repeated task for the parameter scan"""
        # Make the dataframe with the parameters to be scanned
        parameter_df = pd.DataFrame(self.scan_parameter_dct)
        # Create the repeated task
        self.addRepeatedTask(self.repeatedtask_id, subtask_id=self.subtask_id,
                parameter_df=parameter_df, reset=True)
        
    def _makeScopedVariables(self)->List[str]:
        """Makes the scoped variables for the scan parameters"""
        variables = list(self.scan_parameter_dct.keys())
        variables.extend(self.display_variables)
        scoped_scan_variables = [self.repeatedtask_id + cn.SCOPE_INDICATOR + k 
                for k in variables]
        return scoped_scan_variables
        
    def _addReport(self):
        """Adds a report for the parameter scan"""
        # Make the parameter variables
        scoped_variables = self._makeScopedVariables()
        # Add the report
        self.addReport(*scoped_variables, id=self.report_id,
                title=f"Parameter scan for {self.model_id}")
        
    def _addPlot(self):
        """Adds a plot for the parameter scan"""
        # Add the plot
        scoped_variables = self._makeScopedVariables()
        x_var = scoped_variables[0]
        y_vars = scoped_variables[1:]
        self.addPlot(x_var=x_var, y_var=y_vars,
                title=f"Parameter scan for {self.model_id}", is_plot=self.is_plot)