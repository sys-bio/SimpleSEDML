'''Makes the example notebook into a script.'''
# Source path (for github actions)
import sys
import os
project_path = os.path.dirname(os.path.abspath("__FILE__"))
src_path = os.path.join(project_path, "src")
sys.path.insert(0, src_path)
#
import SimpleSEDML.constants as cn  # type: ignore

import os
import nbformat # type: ignore
from nbconvert import PythonExporter # type: ignore

NOTEBOOK_NAME = "vingnette"
NOTEBOOK_PATH = os.path.join(cn.EXAMPLE_DIR, NOTEBOOK_NAME + ".ipynb")
SCRIPT_PATH = os.path.join(cn.EXAMPLE_DIR, NOTEBOOK_NAME + ".py")
ENDING_SCRIPT = """
if __name__ == '__main__':                                                  
    main()
"""

# Load the notebook
with open(NOTEBOOK_PATH) as f:
    notebook_content = nbformat.read(f, as_version=4)

# Convert to Python script
python_exporter = PythonExporter()
python_script, _ = python_exporter.from_notebook_node(notebook_content)

#
with open(SCRIPT_PATH, 'w') as f:
    f.write(python_script)