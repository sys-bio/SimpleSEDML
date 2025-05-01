'''Class that handles model definitions and their parameters.'''

import codecs
import urllib3
import os
import tellurium as te  # type: ignore
from typing import Optional
import warnings

SBML_STR = "sbml_str"
ANT_STR = "ant_str"
SBML_FILE = "sbml_file"
ANT_FILE = "ant_file"
SBML_URL = "sbml_url"
MODEL_ID = "model_id"
MODEL_REF_TYPES = [SBML_STR, ANT_STR, SBML_FILE, ANT_FILE, SBML_URL, MODEL_ID]

"""
Issues
1. To eliminate the warning for urllib3, need to create a virtual environment with a higher version of python.
"""

class Model:
    def __init__(self, id:str, model_ref:Optional[str]=None, ref_type:Optional[str]=None, 
                 model_source_path:Optional[str]=None, 
                 is_overwrite:bool=False,
                 **kwargs):
        """Provide information about the model and a model identifier.

        Args:
            id (str): identifier for the model
            model_ref (str): reference to the file; reference type is specified separately
            ref_type (str):
                - "sbml_str": string representation of the SBML model
                - "ant_str": string representation of the SBML model
                - "sbml_file": file path to the SBML model
                - "ant_file": file path to the Antimony model
                - "sbml_url": URL to the SBML model
                - "model_id": ID of a previously defined model
            is_overwrite (bool): if True, overwrite the model if it already exists
            model_source_path (str): file path to where SBML model is to be stored. If None,
                the model is stored in the current directory.
        """
        # Handle defaults
        if model_ref is None:
            # id is a file path to an SBML model
            model_ref = id
            _, filename = os.path.split(id)
            splits = filename.split(".")
            id = splits[0]
            ref_type = SBML_FILE
        elif ref_type is None:
            ref_type = SBML_STR
        # id, model_ref, ref_type should all be assigned
        self.id = id
        self.ref_type = ref_type
        self.param_change_dct = kwargs
        self.is_overwrite = is_overwrite
        #
        self.model_str = self._getSBMLFromReference(model_ref, ref_type)
        self.model_source_path = self._makeModelSourcePath(model_source_path)

    def _makeModelSourcePath(self, model_source_path:Optional[str])->str:
        """Saves the model to a file. The file name is the model ID with an .xml extension.
        """
        if model_source_path is None:
            # Use the current directory
            model_source_path = os.getcwd()
            model_source_path = os.path.join(model_source_path, self.id + ".xml")
        model_source_path = str(model_source_path)
        if self.is_overwrite or not os.path.exists(model_source_path):
            with open(model_source_path, "w") as f:
                f.write(self.model_str)
        if (not self.is_overwrite and os.path.exists(model_source_path)):
            msg = "*** File {model_source_path} already exists and will be used as model source."
            msg += "\n  Use is_overwrite=True to overwrite."
            warnings.warn(msg)
        return model_source_path

    def _getSBMLFromReference(self, model_ref:str, ref_type:str)->str:
        """Extracts an SBML strong from the model reference

        Args:
            model_ref (str): reference to the file; reference type is specified separately
            ref_type (str): One of MODEL_REF_TYPES

        Returns:
            SBML string
        """
        if ref_type in [SBML_FILE, ANT_FILE]:
            with open(model_ref, "r") as f:
                lines = f.read()
            if ref_type == SBML_FILE:
                sbml_str = lines
            else:
                sbml_str = te.antimonyToSBML(lines)
        elif ref_type == SBML_STR:
            sbml_str = model_ref
        elif ref_type == ANT_STR:
            sbml_str = model_ref
        else:
            # ref_type == SBML_URL
            response = urllib3.request("GET", model_ref)
            if response.status == 200:
                sbml_str = codecs.decode(response.data, 'utf-8')
            else:
                raise ValueError(f"Failed to fetch SBML from URL: {model_ref}")
        return sbml_str

    def __str__(self):
        params = ", ".join(f"{param} = {val}" for param, val in self.param_change_dct)
        if len(params) > 0:
            params = f" with {params}"
        if self.ref_type == MODEL_ID:
            source = self.model_id
        else:
            source = self.model_source_path
        return f'{self.id} = model "{source}" {params}'