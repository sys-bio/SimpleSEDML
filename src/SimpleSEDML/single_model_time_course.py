from SimpleSEDML.simple_sedml_base import SimpleSEDMLBase # type:ignore

from typing import Optional, List


TIME_COURSE = "time_course"

class SingleModelTimeCourse(SimpleSEDMLBase):
    """Class to create a time course simulation for a single model"""

    def __init__(self,
            model_ref:str,
            ref_type:Optional[str]=None,
            display_variables:Optional[List[str]]=None,
            start:float=0,
            end:float=5,
            num_step:Optional[int]=None,
            num_point:Optional[int]=None,
            time_course_id:Optional[str]=None,
            title:Optional[str]=None,
            algorithm:Optional[str]=None,
            is_plot:bool=True,
            **parameter_dct):
        """Creates a time course simulation

        Args:
            model_ref: reference to the model
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")
            display_variables: variables to be plotted and included the report
            start: start time
            end: end time
            num_step: number of steps
            time_course_id: ID of the time course simulation
            algorithm: algorithm to use for the simulation
            title: title of the plot
            is_plot: if True, plot the results
            parameter_dct: dictionary of parameters whose values are changed

        Returns:
            SingleModelTimeCourse: a time course simulation object
        """
        super().__init__()
        #
        if time_course_id is None:
            time_course_id = TIME_COURSE
        model_id = f"{time_course_id}_model"
        sim_id = f"{time_course_id}_sim"
        task_id = f"{time_course_id}_task"
        if title is None:
            title = ""
        #
        self.addModel(model_id, model_ref, ref_type=ref_type, is_overwrite=True, **parameter_dct)
        this_model = self.model_dct[model_id]
        if display_variables is None:
            display_variables = list(this_model.getInformation().floating_species_dct.keys())
            display_variables.insert(0, "time")   # type: ignore
        self.addSimulation(sim_id, "uniform", start=start, end=end, num_step=num_step, num_point=num_point,
                            algorithm=algorithm)
        self.addTask(task_id, model_id, sim_id)
        self.addReport(*display_variables, title=title)
        x1_var = display_variables[0]
        y_vars = display_variables[1:]
        self.addPlot(x1_var, y_vars, title=title, is_plot=is_plot)