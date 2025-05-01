from src.model import Model
from src.simulation import Simulation
from src.task import Task, RepeatedTask
from plot2d import Plot2D
from src.report import Report

import phrasedml # type: ignore
import tellurium as te  # type: ignore
from typing import Optional, List, Tuple, Union

"""
PhraSED-ML is strctured as a series of sections, each of which specifies a Model, Simulation, Task or repeated task.

A model section contains one or more references to models. Some of these may be indirect in that they reference a reference.
A model section may contain changes to parameters, initial conditions or other model components.


Restrictions:
  - No local variables (because this is an API)
  - No formulas (because this is an API)
"""


class SimpleSBML(object):
    """A directive can consist of many sections each of which species a Model, Simulation, Task or repeated task,
    and an action (plot or report).

    Args:
        object (_type_): _description_
    """
    def __init__(self)->None:
        # Dictionary of script elements, indexed by their section ID
        self.models:List[Model] = []
        self.simulations:List[Simulation] = []
        self.tasks:List[Task] = []
        self.repeated_tasks:List[RepeatedTask] = []
        self.reports:List[Report] = []
        self.plot2ds:List[Plot2D] = []

    def __str__(self)->str:
        sections = [
            *[str(m) for m in self.models],
            *[str(s) for s in self.simulations],
            *[str(t) for t in self.tasks],
            *[str(rt) for rt in self.repeated_tasks],
            *[str(r) for r in self.reports],
            *[str(p) for p in self.plot2ds],
        ]
        return "\n".join(sections)
    
    def toSEDML(self)->str:
        """Converts the script to a SED-ML string

        Returns:
            str: SED-ML string
        """
        result = phrasedml.convertString(str(self))
        if result is None:
            #import pdb; pdb.set_trace()
            print(phrasedml.getLastPhrasedError())
            return ""
        else:
            return result

    @property 
    def sedml_str(self)->str:
        """Converts the script to a SED-ML string

        Returns:
            str: SED-ML string
        """
        return phrasedml.convertString(str(self))

    def addModel(self, id:str, model_ref:str, ref_type:Optional[str]=None,
          model_source_path:Optional[str]=None, is_overwrite:bool=False):
        """Adds a model to the script

        Args:
            id: ID of the model
            model_ref: reference to the model
            ref_type: type of the reference (e.g. "sbml_str", "ant_str", "sbml_file", "ant_file", "sbml_url")
            model_source_path: path to the model source file
            is_overwrite: if True, overwrite the model if it already exists
        """
        model = Model(id, model_ref, ref_type=ref_type,
              model_source=model_source_path, is_overwrite=is_overwrite)
        self.models.append(model)

    def addSimulation(self, id:str, start:float, end:float, steps:int, algorithm:Optional[str]=None): 
        """Adds a simulation to the script

        Args:
            simulation: Simulation object
        """
        self.simulations.append(Simulation(id, start, end, steps, algorithm))

    def addTask(self, id, model:Model, simulation:Simulation):
        """Adds a task to the script

        Args:
            id: ID of the task
            model: Model object
            simulation: Simulation object
        """
        self.tasks.append(Task(id, model, simulation))

    def addRepeatedTask(self, id:str, change_dct:dict, subtask:Task, reset:bool=True, nested_repeats=None):
        """Adds a repeated task to the script

        Args:
            repeated_task: RepeatedTask object
        """
        self.repeated_tasks.append(RepeatedTask(id, change_dct, subtask, reset=reset, nested_repeats=nested_repeats))

    def addPlot(self, plot2d:Plot2D):
        """Adds a plot to the script

        Args:
            plot2d: Plot2D object
        """
        self.plot2ds.append(plot2d)

    def addReport(self, report:Report):
        """Adds a report to the script

        Args:
            report: Report object
        """
        self.reports.append(report)