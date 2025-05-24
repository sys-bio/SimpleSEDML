import SimpleSEDML.constants as cn # type: ignore

import tempfile
from typing import Union


def makeDefaultProjectDir(project_dir:Union[str, None])->str:
        """Creates a default project directory in a temporary location

        Args:
            project_dir: path to the project directory. If None, a temporary directory is created.

        Returns:
            str: path to the project directory
        """
        if project_dir is not None:
            new_project_dir = str(project_dir)
        else:
            new_project_dir = tempfile.mkdtemp()
        return new_project_dir