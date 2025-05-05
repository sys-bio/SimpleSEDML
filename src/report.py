from typing import Optional

class Report:
    def __init__(self, metadata:Optional[dict]=None, title:str=""):
        """Reports data after a simulation.

        Args:
            metadata (Optional[dict], optional): A dictionary of values saved in the
                'attrs' attribute of the DataFrame generated.
            title (str, optional): Saved in the SEDML
        """
        self.metadata = metadata
        self.title = title
        self.variables:list = []

    def addVariables(self, *args):
        """
        List of data to report

        Args:
            *args: list of report variables
        """
        self.variables.extend(args)

    def __str__(self)->str:
        return "\n".join([f'report "{self.title}" {", ".join(self.variables)}'])