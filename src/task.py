from src.model import Model
from src.simulation import Simulation

import pandas as pd; # type: ignore
from typing import List


class Task:
    def __init__(self, id:str, model:Model, simulation:Simulation):
        self.id = id
        self.model = model
        self.simulation = simulation

    def __str__(self)->str:
        return f'{self.id} = run {self.simulation.id} on {self.model.id}'


# FIXME: Use DataFrame as argument instead of repeated list of repeat types. Columns must be global parameters.
class RepeatedTask:
    # A RepeatedTask executes a single task with changes in the values of global parameters.
    # Ex: repeat1 = repeat nested_task for S1 in [1, 3, 5], S2 in [0, 10, 3], reset=true
    # Note that it is not necessary to specify functions as in the original phraSED-ML since python provides this.

    def __init__(self, id:str, subtask:Task, parameter_df:pd.DataFrame, reset:bool=True):
        """Repeats a single task with changes in global parameters.

        Args:
            id (str): Identity of repeated task
            subtask (Task): Task to be repeated
            parameter_df (pd.DataFrame): DataFrame with the parameters to be changed. Column names must be global parameters.
            reset (bool, optional): _description_. Defaults to True.
        """
        #
        self.id = id
        self.subtask = subtask
        self.parameter_df = parameter_df
        self.reset = reset

    def _makeChangeValues(self)->str:
        """Creates a string with the changes in the values of global parameters.

        Args:
            ser (pd.Series): Series with the changes in the values of global parameters.

        Returns:
            str: String with the changes in the values of global parameters.
        """
        results = []
        for col in self.parameter_df.columns:
            results.append(f'{col} in {str(list(self.parameter_df[col].values))}')
        return ', '.join(results)

    def __str__(self)->str:
        line = f'{self.id} = repeat {self.subtask.id} for '
        line += self._makeChangeValues()
        line += f', reset={self.reset}'
        return line