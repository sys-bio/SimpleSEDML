'''Class that handles model definitions and their parameters.'''

import constants as cn # type: ignore

from collections import namedtuple
import codecs
import urllib3
import os
import tellurium as te  # type: ignore
from typing import Optional, List
import warnings


class ModelInformation:
    """Class that holds information about the model.

    Attributes:
        model_name (str): name of the model
        parameters (list): list of global parameters
        floating_species (list): list of floating species
        boundary_species (list): list of boundary species
        num_reaction (int): number of reactions
        num_species (int): number of species
        model_id (str): ID of the model
        roadrunner (object): RoadRunner object for the model
    """
    def __init__(self, roadrunner, model_id:Optional[str]=None):
        ##
        def makeDict(names)->dict:
            dct = {}
            for name in names:
                dct[name] = self.roadrunner[name]
            return dct
        ##
        self.model_id = model_id
        self.roadrunner = roadrunner
        # Extract the model name
        MODEL_NAME = "modelName"
        self.roadrunner = roadrunner
        # Get the model name
        info_str = self.roadrunner.getInfo()
        pos = info_str.find(MODEL_NAME)
        info_str = info_str[pos:]
        pos = info_str.find(":") + 2
        info_str = info_str[pos:]
        end_pos = info_str.find("\n")
        self.model_name = info_str[:end_pos]
        # Extract dictionary information
        self.boundary_species_dct = makeDict(self.roadrunner.getBoundarySpeciesConcentrationIds())
        self.floating_species_dct = makeDict(self.roadrunner.getFloatingSpeciesIds())
        self.parameter_dct = makeDict(self.roadrunner.getGlobalParameterIds())
        self.num_reaction = self.roadrunner.getNumReactions()
        self.num_species = self.roadrunner.getNumFloatingSpecies() + self.roadrunner.getNumBoundarySpecies()
        self.model_id = model_id 

    def __repr__(self):
        """Returns a string representation of the model information"""
        result_str = f"Model: {self.model_name}"
        result_str += f"\nParameters: {self.parameter_dct}"
        result_str += f"\nFloating Species: {self.floating_species_dct}"
        result_str += f"\nBoundary Species: {self.boundary_species_dct}"
        result_str += f"\nNumber of Reactions: {self.num_reaction}"
        result_str += f"\nNumber of Species: {self.num_species}"
        return result_str


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
            ref_type = cn.SBML_FILE
        elif ref_type is None:
            ref_type = cn.SBML_STR
        # id, model_ref, ref_type should all be assigned
        self.id = id
        self.model_ref = model_ref
        self.ref_type = ref_type
        self.param_change_dct = kwargs
        self.is_overwrite = is_overwrite
        #
        self._roadrunner = None
        self.sbml_str = self._getSBMLFromReference()
        self.model_source_path = self._makeModelSource(model_source)

    @property
    def roadrunner(self):
        """Returns the RoadRunner object for the model"""
        if self._roadrunner is None:
            self._roadrunner = te.loadSBMLModel(self.sbml_str)
        self._roadrunner.resetAll()
        return self._roadrunner

    def _makeModelSource(self, source:Optional[str])->str:
        """Saves the model to a file. The file name is the model ID.
        """
        if self.ref_type == cn.MODEL_ID:
            # model_ref is the ID of a previously defined model
            return self.model_ref
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
            self.ref_type (str): One of self.cn.MODEL_self.REF_TYPES

        Returns:
            SBML string
        """
        if self.ref_type in [cn.SBML_FILE, cn.ANT_FILE]:
            with open(self.model_ref, "r") as f:
                lines = f.read()
            if self.ref_type == cn.SBML_FILE:
                sbml_str = lines
            else:
                sbml_str = te.antimonyToSBML(lines)
        elif self.ref_type == cn.SBML_STR:
            sbml_str = self.model_ref
        elif self.ref_type == cn.ANT_STR:
            sbml_str = te.antimonyToSBML(self.model_ref)
        elif self.ref_type == cn.MODEL_ID:
            # self.model_ref is the ID of a previously defined model
            sbml_str = "" 
        else:
            # self.ref_type == cn.SBML_URL
            response = urllib3.request("GET", self.model_ref)
            if response.status == 200:
                sbml_str = codecs.decode(response.data, 'utf-8')
            else:
                raise ValueError(f"Failed to fetch SBML from URL: {self.model_ref}")
        return sbml_str

    def getPhrasedml(self):
        params = ", ".join(f"{param} = {val}" for param, val in self.param_change_dct.items())
        if len(params) > 0:
            params = f" with {params}"
        if self.ref_type == cn.MODEL_ID:
            source = self.id
        else:
            source = f'"{self.model_source_path}"'
        return f'{self.id} = model {source} {params}'
    
    def __str__(self)->str:
        """
        Construct the PhraSED-ML string. This requires:
        """
        return self.getPhrasedml()

    @staticmethod 
    def findReferenceType(model_ref:str, model_ids:List[str], ref_type:Optional[str]=None)->str:
        """Infers the reference type from the model reference.

        Args:
            model_ref (str): reference to the file; reference type is specified separately
            model_ids (List[str]): List of known model IDs
            refer_type (str): One of self.cn.MODEL_REF_TYPES

        Returns:
            str: reference type
        """
        # Use the ref_type if it is specified
        if ref_type is not None:
            return ref_type
        # Check if this is a model ID
        if model_ref in model_ids:
            try:
                is_file = os.path.exists(model_ref)
            except:
                is_file = False
            if is_file:
                warnings.warn(f"Model ID {model_ref} is also a file path. Using model ID.")
            return cn.MODEL_ID
        # Check for Antimony string
        try:
            _ = te.loada(model_ref)
            return cn.ANT_STR
        except:
            pass
        # Check for SBML string
        try:
            _ = te.loadSBMLModel(model_ref)
            if "sbml" in model_ref:
                return cn.SBML_STR
        except:
            pass
        # Check if this is a URL
        if ("http://" in model_ref) or ("https://" in model_ref):
            return cn.SBML_URL
        # Check if this is a file path
        try:
            is_file = os.path.exists(model_ref)
        except:
            is_file = False
        if is_file:
            try:
                with open(model_ref, "r") as f:
                    lines = f.read()
                if lines.startswith("<"):
                    return cn.SBML_FILE
                else:
                    return cn.ANT_FILE
            except:
                pass
        # Report error
        msg = f"Unidentifiable model reference: {model_ref}. "
        msg += f"\nFix the reference and/or specify the reference type.\nMust be one of {cn.MODEL_REF_TYPES}."
        raise ValueError(msg)

    def getInformation(self)->ModelInformation:
        """Returns information about model ID, parameters, floating species and fixed species.

        Args:
            model_id (str):

        Returns: ModelInfo
        """
        return ModelInformation(self.roadrunner, model_id=self.id)