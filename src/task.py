from src.model import Model
from src.simulation import Simulation

from typing import List


class Task:
    def __init__(self, id:str, model:Model, simulation:Simulation):
        self.id = id
        self.model = model
        self.simulation = simulation

    def __str__(self)->str:
        return f'{self.id} = run {self.simulation.id} on {self.model.id}'


class RepeatedTask:
    # A RepeatedTask executes a single task with changes in the values of global parameters.
    # Ex: repeat1 = repeat nested_task for S1 in [1, 3, 5], S2 in [0, 10, 3], reset=true
    # Note that it is not necessary to specify functions as in the original phraSED-ML since python provides this.

    class RepeatType:
        def __init__(self, parameter:str, floats:List[float]):
            self.parameter = parameter
            self.floats = floats

        def __str__(self)->str:
            list_str = str(list(self.floats))
            return f'{self.parameter} in {list_str}'


    def __init__(self, id:str, nested_task: Task, *args, reset:bool=True):
        """Repeats a single task with changes in global parameters.

        Args:
            id (str): Identity of repeated task
            nested_task (Task): Task to be repeated
            *args: An event number of arguments paired as global parameter and a list of floats
            reset (bool, optional): _description_. Defaults to True.
        """
        #
        self.id = id
        self.nested_task = nested_task
        self.reset = reset
        # Construct the RepeatTypes
        if len(args)%2 != 0:
            raise ValueError("Arguments must be in pairs of (target, expr)")
        self.repeated_tasks = [RepeatedTask.RepeatType(args[2*i], args[2*i+1]) for i in range(len(args)//2)]

    def __str__(self)->str:
        line = f'{self.id} = repeat {self.nested_task.id} for '
        line += ', '.join([str(repeated_task) for repeated_task in self.repeated_tasks])
        line += f', reset={self.reset}'
        return line