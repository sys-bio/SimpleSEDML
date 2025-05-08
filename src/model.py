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
                 model_source:Optional[str]=None, 
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
            model_source (str): source for the SBML model. If None, the source is a file with the same name as the model ID
                in the current directory.
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
        self.model_ref = model_ref
        self.ref_type = ref_type
        self.param_change_dct = kwargs
        self.is_overwrite = is_overwrite
        #
        self.sbml_str = self._getSBMLFromReference()
        self.model_source_path = self._makeModelSource(model_source)

    def _makeModelSource(self, source:Optional[str])->str:
        """Saves the model to a file. The file name is the model ID.
        """
        if self.ref_type == MODEL_ID:
            # model_ref is the ID of a previously defined model
            return self.model_ref
        # FIXME: Model source should be the filename in the path
        if source is None:
            # Use the current directory
            source = os.getcwd()
            source = os.path.join(source, self.id)
        source = str(source)
        if self.is_overwrite or not os.path.exists(source):
            with open(source, "wb") as f:
                f.write(self.sbml_str.encode('utf-8'))
                f.flush()
                print(f"**Model saved to {source}")
        if (not self.is_overwrite and os.path.exists(source)):
            msg = "*** File {model_source_path} already exists and will be used as model source."
            msg += "\n  Use is_overwrite=True to overwrite."
            warnings.warn(msg)
        return source

    def _getSBMLFromReference(self)->str:
        """Extracts an SBML strong from the model reference

        Args:
            self.model_ref (str): reference to the file; reference type is specified separately
            self.ref_type (str): One of self.MODEL_self.REF_TYPES

        Returns:
            SBML string
        """
        if self.ref_type in [SBML_FILE, ANT_FILE]:
            with open(self.model_ref, "r") as f:
                lines = f.read()
            if self.ref_type == SBML_FILE:
                sbml_str = lines
            else:
                sbml_str = te.antimonyToSBML(lines)
        elif self.ref_type == SBML_STR:
            sbml_str = self.model_ref
        elif self.ref_type == ANT_STR:
            sbml_str = te.antimonyToSBML(self.model_ref)
        elif self.ref_type == MODEL_ID:
            # self.model_ref is the ID of a previously defined model
            sbml_str = "" 
        else:
            # self.ref_type == SBML_URL
            response = urllib3.request("GET", self.model_ref)
            if response.status == 200:
                sbml_str = codecs.decode(response.data, 'utf-8')
            else:
                raise ValueError(f"Failed to fetch SBML from URL: {self.model_ref}")
        return sbml_str

    def __str__(self):
        params = ", ".join(f"{param} = {val}" for param, val in self.param_change_dct.items())
        if len(params) > 0:
            params = f" with {params}"
        if self.ref_type == MODEL_ID:
            source = self.id
        else:
            source = f'"{self.model_source_path}"'
        return f'{self.id} = model {source} {params}'