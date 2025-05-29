'''Manage variables in SED-ML documents.'''

"""
Display variables are used in plots and reports.
Parameters are used in parameter scans to specify values for the simulation.
Find default display variables.
Find display names for display variables.
Modify SEDML to use display names for display variables.
"""

import SimpleSEDML.constants as cn # type:ignore
from SimpleSEDML.model_information import ModelInformation # type:ignore
from SimpleSEDML.model import Model # type:ignore
import SimpleSEDML.utils as utils # type:ignore

import libsbml # type:ignore
from typing import Optional, List, Dict


class VariableCollection(object):

    def __init__(self,
                model:Model,
                display_variables:Optional[List[str]]=None,
                parameters:Optional[List[str]]=None) -> None:
        """
        Args:
            model (Model): _description_
            display_variables (Optional[List[str]], optional): _description_. Defaults to None.
            parameters (Optional[List[str]], optional): _description_. Defaults to None.
        """
        if parameters is None:
            parameters = []
        #
        self.model = model
        self._display_variables = display_variables
        self.parameters:List[str] = parameters
        #
        self.scope:Optional[str] = None

    @property
    def display_variables(self)->List[str]:
        """Returns list of display variables. If unspecified, use all variables
        from the first model.

        Returns:
            Optional[List[str]]: list of display variables
        """
        if self._display_variables is None:
            model_info = ModelInformation.getFromModel(self.model)
            self._display_variables = list(model_info.floating_species_dct.keys())
            if not cn.TIME in self._display_variables:
                self._display_variables.insert(0, cn.TIME)   # type: ignore
        return self._display_variables

    def addParameters(self, variable_names:List[str]) -> None:
        self.parameters.extend(variable_names)

    def addDisplayVariables(self, variable_names:List[str]) -> None:
        self.display_variables.extend(variable_names)

    def getScopedVariables(self, 
            scope_str:str,
            is_time:bool=True, 
            is_parameters:bool=True,
            is_display_variables:bool=True) -> Dict[str, str]:
        """Adds scope to the variables requested

        Args:
            scope_str (str): string used to scope variables
            is_time (bool, optional): Include time
            is_parameters (bool, optional): Include parameters (from repeated task)
            is_display_variables (bool, optional): Include display variables

        Returns:
            Dict[str, str]: Dictionary of scoped variables
                key: variable name
                value: scoped variable name
        """
        ##
        def addScopeStr(variables:List[str])->Dict[str, str]:
            """Adds scope to the variables"""
            return {v: f"{scope_str}{cn.SCOPE_INDICATOR}{v}" for v in variables}
        ##
        variables = []
        if is_parameters:
            variables.extend(self.parameters)
        if is_display_variables:
            variables.extend(self.display_variables)
        if not is_time:
            if cn.TIME in variables:
                variables.remove(cn.TIME)
        return addScopeStr(variables)
    
    def getDisplayNameDct(self, scope_str:Optional[str]=None, is_time:bool=True) -> Dict[str, str]:
        """Finds the display names in a model.
        If an element does not have a display name, its element id is used.

        Args:
            scope_str (str): string used to scope variables
            is_time (bool, optional): Include time in the display names. Defaults to True. 

        Returns:
            Dict[str, str]: Dictionary of display names
                key: scoped element_id
                value: display name
        """
        # Map element ids to display names
        dct = utils.makeDisplayNameDct(self.model.source)
        if not is_time and cn.TIME in dct:
            del dct[cn.TIME]
        # Map variable names to scoped variable names
        if scope_str is None:
            scope_dct = {k: k for k in dct.keys()}  # No scoping
        else:
            scope_dct = self.getScopedVariables(scope_str, is_time=is_time, 
                    is_parameters=False, is_display_variables=True)
        # Map scoped variable names to display names
        result_dct = {scope_dct[k]: v for k, v in dct.items() if k in self.display_variables}
        #
        return result_dct