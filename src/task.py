from src.model import Model
from src.simulation import Simulation

from typing import Optional, List, Tuple



class Task:
    def __init__(self, id:str, model:Model, simulation:Simulation):
        self.id = id
        self.model = model
        self.simulation = simulation

    def __str__(self)->str:
        return f'{self.id} = run {self.simulation} on {self.model}'


class RepeatedTask:
    # Ex: task1 = repeat task0 for k3 in [0.05, 0.1, 0.2, 0.5], reset=true
    def __init__(self, id:str, change_dct:dict, subtask:Task, reset=True, nested_repeats=None):
        """Records information for creating a repeated task

        Args:
            id (str): _description_
            change_dct (dict): key: id that's changing, value: range expression
            subtask (Task): _description_
            reset (bool, optional): _description_. Defaults to True.
            nested_repeats (_type_, optional): _description_. Defaults to None.
        """
        if nested_repeats is not None:
            raise ValueError("nested_repeats is not currently supported.")
        #
        self.id = id
        self.change_dct = change_dct
        self.subtask = subtask  # can be a Task or another RepeatedTask
        self.reset = reset
        if nested_repeats is None:
            self.nested_repeats:list = []
        else:
            self.nested_repeats = nested_repeats

    def __str__(self)->str:
        lines = []
        for nested in self.nested_repeats:
            lines.append(nested.to_string())
        assignments = ", ".join(f"{target} in {expr}" for target, expr in self.change_dct.items())
        reset_str = ", reset=true" if self.reset else ""
        lines.append(f'{self.id} = repeat {self.subtask.id} for {assignments}{reset_str}')
        return "\n".join(lines)