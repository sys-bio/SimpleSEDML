from typing import Optional

class Simulation:
    def __init__(self, id:str, start:float, end:float, steps:int, algorithm:Optional[str]=None):
        self.id = id
        self.start = start
        self.end = end
        self.steps = steps
        self.algorithm = algorithm

    def __str__(self)->str:
        lines = [f'{self.id} = simulate uniform({self.start}, {self.end}, {self.steps})']
        if self.algorithm:
            lines.append(f'{self.id}.algorithm = "{self.algorithm}"')
        return "\n".join(lines)