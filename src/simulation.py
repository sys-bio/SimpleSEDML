'''Simulation directives for PhraSEDML'''
import constants as cn # type: ignore

from typing import Optional

# Simulation types
ST_UNIFORM = "uniform"
ST_STOCHASTIC = "stochastic"
ST_ONESTEP = "onestep"


class Simulation:
    def __init__(self, id:str, simulation_type:str,
            start:float=0,
            end:float=5,
            num_step:Optional[int]=None,
            num_point:Optional[int]=None,
            time_interval:float=0.5, # required for onestep
            absolute_tolerance:Optional[float]=None,
            algorithm:Optional[str]=None,
            initial_time_step:Optional[float]=None,
            maximum_adams_order:Optional[int]=None,
            maximum_bdf_order:Optional[int]=None,
            maximum_iterations:Optional[int]=None,
            maximum_num_steps:Optional[int]=None,
            maximum_time_step:Optional[float]=None,
            minimum_damping:Optional[float]=None,
            minimum_time_step:Optional[float]=None,
            relative_tolerance:Optional[float]=None,
            seed:Optional[int]=None,
            variable_step_size:Optional[bool]=None):
        """Simulation class for SED-ML
        Args: 
            id (str): identifier for the simulation
            simulation_type (str): type of simulation
                - "uniform": uniform simulation
                - "stochastic": stochastic simulation
                - "onestep": one-step simulation
            start (float): start time for the simulation
            end (float): end time for the simulation
            num_step (int): number of steps for the simulation
            num_point (int): number of points for the simulation must be num_step + 1
            time_interval (float): time interval for the simulation
            algorithm (str): algorithm to use for the simulation. Defaults are:
                - "CVODE": CVODE algorithm
                - "gillespie": Gillespie algorithm
        """
        self.id = id
        self.simulation_type = simulation_type
        self.start = start
        self.end = end
        self.time_interval = time_interval
        # Calculate the number of steps
        if (num_step is None) and (num_point is None):
            self.num_step = cn.D_NUM_STEP
        elif (num_step is None) and (num_point is not None):
            self.num_step = num_point - 1
        elif (num_step is not None) and (num_point is None):
            self.num_step = num_step
        else:
            if num_step != num_point - 1:  # type: ignore
                raise ValueError("num_point must be num_step + 1")
            self.num_step = num_step
        #
        if algorithm is None:
            if simulation_type == ST_UNIFORM:
                algorithm = cn.D_ALGORITHM
            elif simulation_type == ST_STOCHASTIC:
                algorithm = "gillespie"
        self.algorithm = algorithm
        # Setup the options
        self.option_dct =  dict(
                absolute_tolerance=absolute_tolerance,
                algorithm=algorithm,
                initial_time_step=initial_time_step,
                maximum_adams_order=maximum_adams_order,
                maximum_bdf_order=maximum_bdf_order,
                maximum_iterations=maximum_iterations,
                maximum_num_steps=maximum_num_steps,
                maximum_time_step=maximum_time_step,
                minimum_damping=minimum_damping,
                minimum_time_step=minimum_time_step,
                relative_tolerance=relative_tolerance,
                seed=seed,
                variable_step_size=variable_step_size
            )

    def getPhraSEDML(self)->str:
        if self.simulation_type == ST_UNIFORM:
            simulate_arg = "simulate uniform"
        elif self.simulation_type == ST_STOCHASTIC:
            simulate_arg = "simulate uniform_stochastic"
        if self.simulation_type == ST_ONESTEP:
            line = f'{self.id} = simulate onestep({self.time_interval})'
        else:
            line = f'{self.id} = {simulate_arg}({self.start}, {self.end}, {self.num_step})'
        # Include the options
        option_lines = [f"{self.id}.algorithm.{k} = {str(v)} " for k, v in self.option_dct.items() 
                if (v is not None) and (k != "algorithm")]
        option_lines.append(f"{self.id}.algorithm = {self.algorithm}")
        section = line + "\n" + "\n".join(option_lines)
        return section
    
    def __str__(self)->str:
        return self. getPhraSEDML()